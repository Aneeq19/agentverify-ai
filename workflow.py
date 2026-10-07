"""Factual preparation, narrow source adapters, and follow-up questions."""
from datetime import datetime
from schemas import BenefitField, CaseInput, Review
from retrieval import retrieve_workflow_guidance
from stedi_parser import parse_stedi_response

FIELD_NAMES = [
    "Overall eligibility", "Dental coverage", "Network", "Effective date",
    "Termination date", "Annual maximum", "Maximum used", "Maximum remaining",
    "Dental deductible", "Dental deductible met", "Preventive coverage",
    "Basic coverage", "Major coverage", "Crown replacement frequency",
    "Waiting period", "Downgrade", "Predetermination",
]
REQUIRED = ["patient_name", "dob", "member_id", "group_number", "procedure"]
QUESTION_MAP = {
    "Overall eligibility": "Is the member eligible on the anticipated date of service?",
    "Dental coverage": "Does the source confirm dental coverage for the requested service?",
    "Network": "Is the treating provider in-network for this plan?",
    "Effective date": "What is the coverage effective date?",
    "Termination date": "Is a termination date recorded?",
    "Annual maximum": "What is the dental annual maximum and applicable benefit period?",
    "Maximum used": "How much of the dental annual maximum has been used?",
    "Maximum remaining": "What dental annual maximum remains for this benefit period?",
    "Dental deductible": "What dental deductible applies to this procedure?",
    "Dental deductible met": "How much of the applicable dental deductible has been met?",
    "Preventive coverage": "What preventive benefit applies, and what frequency/history limits apply?",
    "Basic coverage": "What basic benefit applies to the requested procedure?",
    "Major coverage": "What major benefit applies to the requested procedure?",
    "Crown replacement frequency": "What is the crown replacement frequency, and when was the previous crown on this tooth?",
    "Waiting period": "Does a waiting period apply, and has it been satisfied?",
    "Downgrade": "Does an alternate benefit or material downgrade apply?",
    "Predetermination": "Is predetermination required or recommended, and what documentation is needed?",
}


def missing_fields(case: CaseInput) -> list[str]:
    return [name for name in REQUIRED if not getattr(case, name)]


def input_errors(case: CaseInput) -> list[str]:
    if not case.dob:
        return []
    try:
        parsed = datetime.strptime(case.dob, "%m/%d/%Y").date()
        if parsed > datetime.now().date():
            return ["Date of birth cannot be in the future."]
    except ValueError:
        return ["Date of birth must use MM/DD/YYYY."]
    return []


def normalize_source(raw, source_format: str) -> tuple[list[BenefitField], str, list[str]]:
    fields = {name: BenefitField(name=name, scope="overall" if name == "Overall eligibility" else "dental")
              for name in FIELD_NAMES}
    if raw is None:
        return list(fields.values()), "not_supplied", []
    try:
        if not isinstance(raw, dict):
            raise ValueError("Source must be a JSON object.")
        if source_format == "stedi":
            summary = parse_stedi_response(raw)
            errors = summary["errors"]
            if not errors:
                records = summary["dental"]
                for name, values in (
                    ("Dental coverage", [r["status"] for r in records]),
                    ("Network", [r["network"] for r in records
                                 if r["network"] != "Not returned by eligibility source"]),
                ):
                    unique = sorted(set(values))
                    if unique:
                        fields[name] = BenefitField(
                            name=name, value="; ".join(unique),
                            status="conflicting" if len(unique) > 1 else "reported",
                            evidence=[r["source_path"] + (".status = NON_COVERED (from nonCovered collection)"
                                      if name == "Dental coverage" else ".network.indicator = " + r["network"])
                                      for r in records if name == "Dental coverage" or
                                      r["network"] != "Not returned by eligibility source"],
                        )
        elif source_format == "demo":
            if raw.get("schema") != "agentverify-demo-v1":
                raise ValueError("Expected the documented agentverify-demo-v1 fixture schema.")
            errors = raw.get("errors", [])
            if not isinstance(errors, list) or not all(isinstance(e, str) for e in errors):
                raise ValueError("Source errors must be a list of strings.")
            records = raw.get("benefits", [])
            if not isinstance(records, list):
                raise ValueError("Benefits must be an array.")
            if not errors:
                for index, record in enumerate(records):
                    if not isinstance(record, dict):
                        raise ValueError("Benefit entry must be an object.")
                    name = record.get("field")
                    if name not in fields:
                        continue
                    expected_scope = fields[name].scope
                    if record.get("scope") != expected_scope:
                        continue
                    value = record.get("value")
                    if value is None or value == "":
                        continue
                    if not isinstance(value, str):
                        raise ValueError("Demo benefit values must be strings.")
                    locator = f"$.benefits[{index}].value = {value}"
                    field = fields[name]
                    if field.value is not None and field.value != value:
                        field.status = "conflicting"
                        field.value = f"{field.value}; {value}"
                    else:
                        field.value = value
                        if field.status != "conflicting":
                            field.status = "reported"
                    field.evidence.append(locator)
        else:
            raise ValueError("Unknown source format.")
        if errors:
            fields = {name: BenefitField(name=name, status="source_error", scope=f.scope)
                      for name, f in fields.items()}
            return list(fields.values()), "error", errors
        return list(fields.values()), "ok", []
    except (TypeError, ValueError, AttributeError, KeyError) as exc:
        return [BenefitField(name=n, status="source_error", scope=f.scope)
                for n, f in fields.items()], "error", [str(exc)]


def prepare_review(case: CaseInput, raw=None, source_format="demo", source_label="No source supplied") -> Review:
    fields, status, errors = normalize_source(raw, source_format)
    missing = missing_fields(case)
    questions = [f"Obtain {name.replace('_', ' ')} before verification." for name in missing]
    if errors:
        questions.append("Resolve the eligibility source error or obtain a valid response before drawing benefit conclusions.")
    procedure = case.procedure.lower()
    excluded = {"Preventive coverage", "Basic coverage"}
    if any(word in procedure for word in ("clean", "preventive", "exam")):
        excluded = {"Basic coverage", "Major coverage", "Crown replacement frequency", "Downgrade"}
    elif "crown" not in procedure:
        excluded = {"Crown replacement frequency"}
    for field in fields:
        if field.name in excluded:
            continue
        if field.status != "reported":
            question = QUESTION_MAP[field.name]
            if field.status == "conflicting":
                question = f"Resolve conflicting {field.name.lower()} values. " + question
            questions.append(question)
    return Review(
        case=case, source=source_label, source_status=status, source_errors=errors,
        missing_fields=missing, fields=fields, questions=questions,
        guidance=retrieve_workflow_guidance(case.procedure + " " + case.notes),
    )


def run_preparation_tool(tool: str, review: Review) -> dict:
    if tool == "check_required_fields":
        return {"missing_fields": review.missing_fields}
    if tool == "build_payer_questions":
        return {"questions": review.questions}
    if tool == "generate_case_summary":
        return {"procedure": review.case.procedure, "missing_fields": review.missing_fields,
                "source_status": review.source_status,
                "fields": [f.model_dump() for f in review.fields]}
    raise ValueError("Tool is not in the preparation allowlist.")
