# Implementation contract

## Files

| Module | Responsibility |
|---|---|
| app.py | Streamlit review, examples, checklists, practice and exports |
| schemas.py | Case, nullable benefits, evidence and review contracts |
| workflow.py | Deterministic validation, narrow adapters, payer questions |
| retrieval.py | Section keyword retrieval and content version |
| llm_client.py | Optional Responses tool selection and structured prioritization |
| report.py | Shared factual table/export rendering |
| demo_cases.py | Explicitly authored fictional examples |
| stedi_parser.py | Saved dental nonCovered adapter with JSON locators |
| legacy_app.py / agent.py | Previous Gemini/Cloudflare UI and preparation agent |

## Authored fixture schema

```json
{
  "schema": "agentverify-demo-v1",
  "errors": [],
  "benefits": [
    {"field": "Overall eligibility", "scope": "overall", "value": "Active"},
    {"field": "Annual maximum", "scope": "dental", "value": "$1,500"}
  ]
}
```

This is an AgentVerify demo format, not Stedi's API schema. Values are strings; absent/null values remain unknown. Wrong scope is excluded. Contradictory values remain conflicting. Malformed records or source errors suppress all benefit conclusions.

## Evidence boundary

Benefit evidence comes from explicit source records or saved Stedi collection paths. Retrieved Markdown is workflow guidance only. Overall eligibility never automatically becomes dental coverage. The adapter never promotes medical deductible values into dental benefits.

## Optional AI boundary

The first request chooses exactly one parameterless allowlisted preparation function. Functions receive the already-built review from application state. The second request returns only existing guidance IDs and question indices through Pydantic Structured Outputs. Python rejects unknown IDs/indices, excessive lists and invalid responses. Reordering never removes unresolved questions or changes the benefit table.

No model-generated free prose is presented as verified benefit information. This is a deliberate first-release limit. Natural-language note extraction and free-form AI summaries remain future work requiring field-level validation.

## Operational notes

- Fictional form snapshots and reviews stay in Streamlit session state.
- No application database, outbound messages, live eligibility request or patient-data upload is implemented.
- Provider output is not stored as a hosted response (store=False); this is not a claim of zero provider retention.
- Three attempts per loaded example and per-response token bounds are demo controls.
- Curated knowledge version is the SHA-256 prefix of the current Markdown content.
- The existing 10-case evaluation remains intact; the new pytest suite verifies workflow safety and UI interaction.
- Merge/deployment is separate from a feature branch. Streamlit must run app.py to show the new interface.
