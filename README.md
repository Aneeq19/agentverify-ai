# 🦷 AgentVerify AI — Dental Workflow Assistant by Aneeq Jawed

Prepare complete fictional dental verification cases, review source-backed benefits, and generate payer follow-up questions without inventing missing information.

[Existing live app](https://agentverify-ai.streamlit.app/) · [Demo walkthrough](docs/DEMO.md) · [Sample review](docs/sample-review.txt) · [Implementation notes](docs/IMPLEMENTATION.md)

The existing live URL is separate from this branch's release status. See the pull request or branch history before assuming the upgraded app is deployed.

## What works

- Offline preparation without API keys: five one-click fictional scenarios.
- Required-field checks with separate input-format and completeness status.
- Dental benefits table with reported, missing, conflicting and source-error states.
- Separate overall eligibility and dental coverage; medical deductible excluded.
- Procedure-specific follow-up questions and section-cited keyword retrieval.
- Human-review status, matching TXT and JSON exports.
- Patient-free checklist generator, knowledge search and payer-call practice.
- Saved Stedi synthetic example through a narrow nonCovered adapter.
- Optional OpenAI function calling and Structured Outputs for prioritizing existing evidence and questions.

All example benefit amounts are authored fictional fixtures, not real payer results.

## Example

A fictional crown fixture reports an annual maximum of $1,500 and no maximum-used value. The review preserves $1,500 with its source locator, keeps remaining maximum and crown frequency unknown, and prepares questions to obtain them. A separate medical-only fixture reports overall active eligibility but does not produce dental coverage or a dental deductible.

## Architecture

1. Pydantic validates input shape; deterministic rules identify missing prerequisites.
2. A source adapter normalizes explicit dental values and their evidence.
3. Markdown section retrieval supplies workflow guidance with section ID and content version.
4. Optional OpenAI selects one allowlisted preparation tool and returns validated evidence/question IDs.
5. The reviewer sees the same normalized values exported to TXT and JSON.

Workflow guidance supports preparation, not patient-specific coverage. No vector database is required for this small curated knowledge base.

## Run locally

Tested with Python 3.12.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The default mode works offline. Select a scenario, press **Prepare review**, inspect its evidence/questions, then download the review sheet.

For the original Gemini/Cloudflare interface:

```bash
python -m streamlit run legacy_app.py
```

## Optional OpenAI mode

Copy .env.example to .env. Set OPENAI_API_KEY and OPENAI_MODEL to an account-accessible model that supports Responses, function calling and Structured Outputs. Equivalent Streamlit secrets are supported. Credentials stay out of Git.

Choose **OpenAI assisted**, prepare a review, select a task, then press **Prioritize with OpenAI**.

- Exactly one allowlisted tool call, then one structured priority response.
- Invalid tools, arguments, citations and indices are rejected.
- The model cannot overwrite factual benefit fields or remove unresolved questions.
- Patient names, birth dates, member IDs, group numbers and free-text notes are excluded from OpenAI requests.
- Selected existing guidance and questions are rendered instead of unvalidated model prose.
- No usable key/model, timeout or invalid output leaves the offline review intact.

This release's OpenAI integration has been tested with mocked provider responses. A live authenticated OpenAI call was not performed during development.

Official references: [Responses](https://developers.openai.com/api/reference/responses/overview) and [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).

## Tools and schemas

- check_required_fields: missing preparation prerequisites.
- build_payer_questions: unanswered/conflicting benefit questions.
- generate_case_summary: normalized factual case summary.
- retrieve_workflow_guidance: local section retrieval, used deterministically.

See schemas.py and docs/IMPLEMENTATION.md. A benefit field has a nullable value, status, scope and evidence. Missing is not zero. No remaining-maximum arithmetic is performed on incomplete or ambiguously scoped amounts.

## Tests and evaluation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python evaluate.py
```

Development results on 2026-10-07: **26 automated tests passed** and the **10-case legacy evaluation passed**. Tests cover malformed/source-error responses, medical/dental separation, conflicts, unknown frequency, report consistency, tool allowlists, bad AI output, offline fallback, Streamlit scenario interactions and review state.

The legacy suite checks preparation tools and keyword retrieval; its 10/10 score is not an evaluation of live model reliability or real insurance accuracy. CI reruns both suites.

## Costs and operational limits

Offline mode makes no provider calls. OpenAI mode uses up to two requests per explicit action, with bounded output and no automatic retries. The UI caches identical successful actions and limits attempts to three per loaded example. Reloading a scenario/session resets this limit, so it is a demo control, not a global spend cap or public abuse protection. An exposed paid deployment needs server-side quotas/authentication before enabling provider calls broadly.

## Limitations

- Fictional demonstration only; no production PHI workflow.
- No live payer eligibility request, automatic phone call, claim processing or benefit guarantee.
- The saved Stedi adapter reads dental nonCovered entries only; it is not a comprehensive Stedi benefits parser.
- Basic keyword retrieval has no semantic/vector search.
- Manual reviewer confirmation is essential; reviewed status is a demo acknowledgement.
- New OpenAI mode does not automatically fall back to Gemini; it falls back to offline rules.
- Legacy provider behavior is retained in legacy_app.py and agent.py.

## Routine value

Use patient-free procedure checklists for daily preparation, practice fictional payer calls, review common workflow gaps, demonstrate source handling in interviews, or train teammates on fictional examples.

## Roadmap

Live authenticated OpenAI smoke test; broader documented source adapters; timed usability evaluation; then authorized production data handling and access controls if a real pilot needs them.

## Developer

Built by **Aneeq Jawed** · [GitHub](https://github.com/Aneeq19).

This dental workflow project is distinct from similarly named academic agent-verification frameworks. No academic authorship or third-party accuracy claims are asserted here.

No software license is currently declared in this repository.
