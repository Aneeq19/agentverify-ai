import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

# =========================================================
# API CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

client = genai.Client(api_key=GEMINI_API_KEY)

CLOUDFLARE_MODEL = "@cf/meta/llama-3.1-8b-instruct"

KNOWLEDGE_BASE_PATH = Path(__file__).parent / "knowledge_base.md"


# =========================================================
# AGENT TOOLS
# =========================================================

def check_required_fields(data: dict) -> str:
    """Check whether the basic patient verification fields are present."""

    required = [
        "patient_name",
        "dob",
        "member_id",
        "group_number",
        "procedure",
    ]

    missing = [
        field for field in required
        if not data.get(field)
    ]

    if missing:
        return f"Missing fields: {', '.join(missing)}"

    return "All required fields are present."


def build_payer_questions(data: dict) -> str:
    """Build questions that should be asked to the insurance payer."""

    questions = []

    if not data.get("member_id"):
        questions.append("What is the Member ID?")

    if not data.get("group_number"):
        questions.append("What is the Group Number?")

    if not data.get("dob"):
        questions.append("What is the Date of Birth?")

    if not data.get("procedure"):
        questions.append("What procedure is being requested?")

    if not questions:
        return "No additional questions needed."

    return "Questions to ask the payer:\n- " + "\n- ".join(questions)


def generate_case_summary(data: dict) -> str:
    """Generate a concise summary of the fictional verification case."""

    summary = f"""
**Case Summary**

- Patient Name : {data.get('patient_name', 'Not provided')}
- Date of Birth: {data.get('dob', 'Not provided')}
- Member ID    : {data.get('member_id', 'Not provided')}
- Group Number : {data.get('group_number', 'Not provided')}
- Procedure    : {data.get('procedure', 'Not provided')}
- Notes        : {data.get('notes', 'None')}
"""

    return summary.strip()


def search_knowledge_base(query: str) -> str:
    """
    Search the local fictional/non-PHI workflow knowledge base.

    This is lightweight local RAG retrieval. It returns the most
    relevant knowledge-base sections based on query keywords.
    """

    if not KNOWLEDGE_BASE_PATH.exists():
        return "Knowledge base is unavailable."

    content = KNOWLEDGE_BASE_PATH.read_text(
        encoding="utf-8"
    )

    # Split Markdown into sections.
    sections = [
        section.strip()
        for section in content.split("\n---\n")
        if section.strip()
    ]

    query_words = {
        word.strip(".,:;!?()[]{}").lower()
        for word in query.split()
        if len(word) > 2
    }

    scored_sections = []

    for section in sections:
        section_lower = section.lower()

        score = sum(
            1 for word in query_words
            if word in section_lower
        )

        if score > 0:
            scored_sections.append((score, section))

    scored_sections.sort(
        key=lambda item: item[0],
        reverse=True
    )

    if not scored_sections:
        return (
            "No specific knowledge-base section matched the request. "
            "Benefits must still be confirmed directly with the payer."
        )

    # Return up to three most relevant sections.
    relevant_sections = [
        section
        for _, section in scored_sections[:3]
    ]

    return "\n\n---\n\n".join(relevant_sections)


# =========================================================
# CLOUDFLARE BACKUP
# =========================================================

def get_cloudflare_decision(prompt: str) -> str:
    """Use Cloudflare Workers AI when Gemini fails."""

    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        raise RuntimeError("Cloudflare credentials are not configured.")

    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/{CLOUDFLARE_MODEL}"
    )

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise RuntimeError(
            f"Cloudflare API error: {result.get('errors')}"
        )

    ai_result = result.get("result", {})

    if ai_result.get("response"):
        return ai_result["response"].strip()

    choices = ai_result.get("choices", [])

    if choices:
        message = choices[0].get("message", {})
        content = message.get("content")

        if content:
            return content.strip()

    raise RuntimeError("Cloudflare returned no usable response.")


# =========================================================
# AGENT
# =========================================================

def run_agent(user_input: str, data: dict) -> dict:
    """
    AgentVerify AI v1.2

    Flow:
    Fictional case
        -> local RAG knowledge retrieval
        -> AI tool decision
        -> existing preparation tool
        -> grounded preparation result
    """

    # =====================================================
    # RAG RETRIEVAL
    # =====================================================

    rag_query = " ".join(
        [
            user_input,
            data.get("procedure", ""),
            data.get("notes", ""),
        ]
    )

    knowledge_context = search_knowledge_base(rag_query)

    prompt = f"""
You are AgentVerify, an AI agent for dental insurance
verification workflow preparation.

This system uses fictional patient data only.

The following context was retrieved from the local
workflow knowledge base:

--- KNOWLEDGE BASE CONTEXT ---

{knowledge_context}

--- END KNOWLEDGE BASE CONTEXT ---

User request:
"{user_input}"

Procedure:
"{data.get('procedure', '')}"

You have exactly three ACTION tools available:

1. check_required_fields
Use when the user wants to know whether required patient
or verification information is missing.

2. build_payer_questions
Use when the user wants questions to prepare for the
insurance payer.

3. generate_case_summary
Use when the user wants a summary of the fictional case.

The knowledge-base context is guidance only.
Never invent patient-specific eligibility, percentages,
dollar amounts, coverage, frequencies, or benefits.

Benefits must be confirmed directly with the payer.

Choose the SINGLE best ACTION tool.

Reply with ONLY one exact tool name:

check_required_fields
build_payer_questions
generate_case_summary
"""

    provider = "Gemini"

    # =====================================================
    # PRIMARY PROVIDER: GEMINI
    # =====================================================

    try:
        if not GEMINI_API_KEY:
            raise RuntimeError("Gemini API key is not configured.")

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        decision = response.text.strip().lower()

    # =====================================================
    # BACKUP PROVIDER: CLOUDFLARE
    # =====================================================

    except Exception:
        try:
            decision = get_cloudflare_decision(prompt).lower()
            provider = "Cloudflare fallback"

        except Exception:
            return {
                "success": False,
                "tool_used": None,
                "provider": None,
                "knowledge_source": "knowledge_base.md",
                "knowledge_context": knowledge_context,
                "result": (
                    "AI service is temporarily unavailable. "
                    "Both the primary and backup providers could not "
                    "complete the request. Please try again later."
                ),
            }

    # =====================================================
    # ACTION TOOL ROUTING
    # =====================================================

    if "check_required_fields" in decision:
        tool_name = "check_required_fields"
        action_result = check_required_fields(data)

    elif "build_payer_questions" in decision:
        tool_name = "build_payer_questions"
        action_result = build_payer_questions(data)

    elif "generate_case_summary" in decision:
        tool_name = "generate_case_summary"
        action_result = generate_case_summary(data)

    else:
        return {
            "success": False,
            "tool_used": None,
            "provider": provider,
            "knowledge_source": "knowledge_base.md",
            "knowledge_context": knowledge_context,
            "result": (
                "The AI could not select a valid action tool. "
                "Please rephrase your request and try again."
            ),
        }

    # =====================================================
    # GROUNDED RESULT
    # =====================================================

    result = f"""
{action_result}

### Relevant workflow guidance

{knowledge_context}

**Important:** This is verification preparation only.
Benefits and eligibility must be confirmed directly with the payer.
""".strip()

    return {
        "success": True,
        "tool_used": tool_name,
        "provider": provider,
        "knowledge_source": "knowledge_base.md",
        "knowledge_context": knowledge_context,
        "result": result,
    }