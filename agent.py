"""AgentVerify AI core — fictional/demo data only."""

import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def check_required_fields(case):
    required = ["patient_name", "dob", "payer", "member_id", "procedure"]
    return [f for f in required if not str(case.get(f, "")).strip()]

def build_payer_questions(case):
    procedure = case.get("procedure") or "the planned service"
    return [
        "Is coverage active on the planned date of service?",
        "What are the annual maximum and remaining benefits?",
        f"What coverage, limitations, waiting periods, and frequency rules apply to {procedure}?",
        "Are deductible, downgrade, missing-tooth, age, or preauthorization rules applicable?",
    ]

def generate_case_summary(case):
    return (
        f"Prepare verification for {case.get('patient_name') or 'demo patient'} "
        f"with {case.get('payer') or 'unknown payer'} for "
        f"{case.get('procedure') or 'unspecified service'}."
    )

TOOLS = {
    "check_required_fields": check_required_fields,
    "build_payer_questions": build_payer_questions,
    "generate_case_summary": generate_case_summary,
}

def run_agent(case):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=key)
    prompt = f"""You are AgentVerify AI, a workflow-preparation agent.
Choose which tools are useful for this FICTIONAL dental insurance case.
Available tools: check_required_fields, build_payer_questions, generate_case_summary.
Return JSON only: {{"tools":["tool_name", ...]}}.
Usually select every tool that adds value, but make the decision from the case.
Never claim benefits are verified.
CASE: {json.dumps(case)}
"""
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
    )
    raw = (response.text or "").strip().replace("```json", "").replace("```", "").strip()
    selected = json.loads(raw).get("tools", [])
    selected = [name for name in selected if name in TOOLS]
    if not selected:
        selected = ["check_required_fields", "build_payer_questions", "generate_case_summary"]

    results = {name: TOOLS[name](case) for name in selected}
    return {"selected_tools": selected, "results": results}
