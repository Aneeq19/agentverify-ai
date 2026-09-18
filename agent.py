import os
import requests
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

# =========================================================
# API CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

# Gemini = Primary AI provider
client = genai.Client(api_key=GEMINI_API_KEY)

# Cloudflare = Backup AI provider
CLOUDFLARE_MODEL = "@cf/meta/llama-3.1-8b-instruct"


# =========================================================
# AGENT TOOLS
# =========================================================

def check_required_fields(data: dict) -> str:
    """
    Check whether the basic patient verification fields are present.
    """

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
    """
    Build questions that should be asked to the insurance payer.
    """

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
    """
    Generate a concise summary of the fictional verification case.
    """

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


# =========================================================
# CLOUDFLARE BACKUP
# =========================================================

def get_cloudflare_decision(prompt: str) -> str:
    """
    Ask Cloudflare Workers AI to select an agent tool.
    Used only when Gemini fails.
    """

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

    # Cloudflare may return the generated text in "response".
    if ai_result.get("response"):
        return ai_result["response"].strip()

    # Handle OpenAI-style choices response if returned.
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
    AgentVerify AI v1.0

    Gemini is the primary AI provider.
    Cloudflare Workers AI is the automatic backup.

    The AI selects one of the available Python tools.
    """

    prompt = f"""
You are AgentVerify, a dental insurance verification AI agent.

The user will give you a task.

User request:
"{user_input}"

You have exactly three tools available:

1. check_required_fields
Use this when the user wants to know whether required patient
or verification information is missing.

2. build_payer_questions
Use this when the user wants questions to ask the insurance payer.

3. generate_case_summary
Use this when the user wants a summary of the verification case.

Choose the SINGLE best tool for the user's request.

Reply with ONLY one of these exact tool names:

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

            provider = "Cloudflare Workers AI"

        except Exception:

            return {
                "success": False,
                "tool_used": None,
                "provider": None,
                "result": (
                    "AI service is temporarily unavailable. "
                    "Both the primary and backup providers could not "
                    "complete the request. Please try again later."
                ),
            }

    # =====================================================
    # TOOL ROUTING
    # =====================================================

    if "check_required_fields" in decision:

        tool_name = "check_required_fields"

        result = check_required_fields(data)

    elif "build_payer_questions" in decision:

        tool_name = "build_payer_questions"

        result = build_payer_questions(data)

    elif "generate_case_summary" in decision:

        tool_name = "generate_case_summary"

        result = generate_case_summary(data)

    else:

        return {
            "success": False,
            "tool_used": None,
            "provider": provider,
            "result": (
                "The AI could not select a valid tool. "
                "Please rephrase your request and try again."
            ),
        }

    # =====================================================
    # SUCCESS RESPONSE
    # =====================================================

    return {
        "success": True,
        "tool_used": tool_name,
        "provider": provider,
        "result": result,
    }