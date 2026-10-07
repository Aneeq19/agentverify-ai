"""Behavioral safety checks; no network calls or patient information."""
import json
from types import SimpleNamespace as NS
import pytest
from demo_cases import BASE_CASE, BENEFITS, load_demo
from llm_client import enhance_review
from report import render_report, review_rows
from retrieval import retrieve_workflow_guidance
from schemas import AIPriorities, CaseInput
from workflow import input_errors, normalize_source, prepare_review, run_preparation_tool


def fixture(name="Synthetic dental benefits"):
    demo = load_demo(name)
    return prepare_review(CaseInput(**demo["case"]), demo["raw"], demo["format"], demo["source"])


def field(review, name):
    return next(f for f in review.fields if f.name == name)


def test_missing_member_id_and_no_source():
    review = fixture("Incomplete crown case")
    assert review.missing_fields == ["member_id"]
    assert review.source_status == "not_supplied"
    assert all(f.value is None for f in review.fields)


def test_unknown_is_not_zero_or_invented_frequency():
    review = fixture()
    assert field(review, "Annual maximum").value.startswith("$1,500")
    assert field(review, "Maximum remaining").value is None
    assert field(review, "Crown replacement frequency").value is None
    assert any("replacement frequency" in q for q in review.questions)


def test_medical_deductible_and_active_eligibility_are_separate():
    review = fixture("Medical-only response")
    assert field(review, "Overall eligibility").value == "Active"
    assert field(review, "Dental coverage").value is None
    assert field(review, "Dental deductible").value is None
    assert "$250" not in render_report(review)


def test_source_error_suppresses_all_benefits():
    review = fixture("Source error")
    assert review.source_status == "error"
    assert all(f.value is None and f.status == "source_error" for f in review.fields)
    assert "$1,500" not in render_report(review)


@pytest.mark.parametrize("raw", [[], {"schema": "wrong"},
    {"schema": "agentverify-demo-v1", "benefits": "bad"},
    {"schema": "agentverify-demo-v1", "benefits": [{"field": "Annual maximum", "scope": "dental", "value": 1500}]}])
def test_malformed_source_fails_closed(raw):
    fields, status, errors = normalize_source(raw, "demo")
    assert status == "error" and errors
    assert all(f.value is None for f in fields)


def test_conflict_preserves_evidence_and_does_not_select_a_winner():
    review = fixture("Conflicting annual maximum")
    maximum = field(review, "Annual maximum")
    assert maximum.status == "conflicting"
    assert len(maximum.evidence) == 2
    assert any("Resolve conflicting annual maximum" in q for q in review.questions)


def test_retrieval_cites_section_and_abstains_on_unrelated_query():
    matches = retrieve_workflow_guidance("crown replacement frequency")
    assert matches[0].title == "Crown Verification Checklist"
    assert matches[0].source_id.endswith("#crown-verification-checklist")
    assert matches[0].version
    assert retrieve_workflow_guidance("volcano astrophysics") == []


def test_report_and_json_match_factual_values():
    review = fixture()
    serialized = json.loads(review.model_dump_json())
    rows = review_rows(review)
    for f, row, saved in zip(review.fields, rows, serialized["fields"]):
        assert saved["value"] == f.value
        if f.value is not None:
            assert f.value == row["Value"]
            assert f.value in render_report(review)


def test_disallowed_tool_rejected():
    with pytest.raises(ValueError):
        run_preparation_tool("send_patient_data", fixture())


def test_dob_format_and_future_date():
    assert input_errors(CaseInput(**{**BASE_CASE, "dob": "13/50/1995"}))
    assert input_errors(CaseInput(**{**BASE_CASE, "dob": "01/01/2999"}))


class FakeResponses:
    def __init__(self, tool="build_payer_questions", guidance=None, fail=False):
        self.tool, self.guidance, self.fail = tool, guidance, fail
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        if self.fail:
            raise TimeoutError
        return NS(status="completed", output=[NS(type="function_call", name=self.tool,
                    arguments="{}", call_id="demo-call")],
                  usage=NS(input_tokens=10, output_tokens=3))

    def parse(self, **kwargs):
        self.requests.append(kwargs)
        return NS(status="completed",
                  output_parsed=AIPriorities(guidance_ids=self.guidance or [],
                                            question_indices=[1, 0]),
                  usage=NS(input_tokens=20, output_tokens=5))


def test_openai_tool_and_priorities_keep_source_facts_unchanged():
    review = fixture()
    responses = FakeResponses(guidance=[review.guidance[0].source_id])
    result = enhance_review(review, "Prepare payer questions", NS(responses=responses), "test-model")
    assert result.provider == "OpenAI"
    assert result.selected_tool == "build_payer_questions"
    assert result.fields == review.fields
    assert set(result.questions) == set(review.questions)
    assert result.usage == {"input_tokens": 30, "output_tokens": 8}
    assert BASE_CASE["member_id"] not in responses.requests[0]["input"]
    assert all(r["store"] is False for r in responses.requests)


@pytest.mark.parametrize("responses", [
    FakeResponses(fail=True), FakeResponses(tool="execute_shell"),
    FakeResponses(guidance=["fabricated-source"]),
])
def test_bad_ai_output_or_timeout_retains_offline_review(responses):
    review = fixture()
    result = enhance_review(review, "Prepare payer questions", NS(responses=responses), "test-model")
    assert result.provider == "Offline rules"
    assert result.fields == review.fields and result.questions == review.questions
    assert "offline review retained" in result.ai_status


def test_missing_api_config_retains_offline_review(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    result = enhance_review(fixture(), "Prepare payer questions")
    assert result.provider == "Offline rules"
    assert "configure" in result.ai_status
