import streamlit as st
from datetime import datetime
from agent import run_agent
from chatbot_data import CHATBOT_RESPONSES

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AgentVerify AI",
    page_icon="🦷",
    layout="centered"
)

# =========================================================
# SESSION STATE
# =========================================================

if "agent_response" not in st.session_state:
    st.session_state.agent_response = None

if "report_text" not in st.session_state:
    st.session_state.report_text = None

if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

if "chat_answer" not in st.session_state:
    st.session_state.chat_answer = None


# =========================================================
# REPORT BUILDER
# =========================================================

def build_report(data, user_request, response):

    provider = response.get("provider", "Unknown")
    tool_used = response.get("tool_used", "Unknown")
    knowledge_source = response.get(
        "knowledge_source",
        "knowledge_base.md"
    )
    result = response.get("result", "No result returned.")

    report = f"""# AgentVerify AI - Grounded Verification Preparation Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Fictional Patient Information

- Patient Name: {data.get("patient_name") or "Not provided"}
- Date of Birth: {data.get("dob") or "Not provided"}
- Member ID: {data.get("member_id") or "Not provided"}
- Group Number: {data.get("group_number") or "Not provided"}
- Procedure: {data.get("procedure") or "Not provided"}
- Notes: {data.get("notes") or "None"}

## Agent Task

{user_request}

## Agent Decision

- AI Provider: {provider}
- Agent Selected Tool: {tool_used}
- Knowledge Source Used: {knowledge_source}

## Grounded Preparation Result

{result}

## Important Notice

This report is for dental insurance verification preparation only.

AgentVerify AI does not confirm eligibility, coverage, benefits,
limitations, frequencies, deductibles, maximums, or payment.

All insurance benefits and eligibility must be confirmed directly
with the payer.

This demo uses fictional patient data only.
"""

    return report


# =========================================================
# HEADER
# =========================================================

st.title("🦷 AgentVerify AI")

st.caption(
    "Grounded AI-assisted workflow preparation "
    "for dental insurance verification"
)

st.markdown("---")


# =========================================================
# SAFETY
# =========================================================

st.info(
    "Demo only — use fictional patient information. "
    "Do not enter real patient information or protected "
    "health information (PHI)."
)


# =========================================================
# PATIENT DATA
# =========================================================

st.subheader("Fictional Patient Data")

col1, col2 = st.columns(2)

with col1:

    patient_name = st.text_input(
        "Patient Name",
        value="John Demo"
    )

    dob = st.text_input(
        "Date of Birth",
        value="01/01/1995",
        placeholder="MM/DD/YYYY"
    )

    member_id = st.text_input(
        "Member ID",
        value=""
    )

with col2:

    group_number = st.text_input(
        "Group Number",
        value="GRP001"
    )

    procedure = st.text_input(
        "Procedure",
        value="Crown"
    )

    notes = st.text_area(
        "Notes",
        value="New patient - needs verification"
    )


data = {
    "patient_name": patient_name.strip(),
    "dob": dob.strip(),
    "member_id": member_id.strip(),
    "group_number": group_number.strip(),
    "procedure": procedure.strip(),
    "notes": notes.strip()
}

st.markdown("---")


# =========================================================
# AGENT TASK
# =========================================================

st.subheader("Agent Task")

user_request = st.text_input(
    "What should the agent do?",
    value="Check what information is missing"
)


# =========================================================
# RUN AGENT
# =========================================================

if st.button(
    "Run Agent",
    type="primary",
    use_container_width=True
):

    st.session_state.agent_response = None
    st.session_state.report_text = None

    validation_errors = []

    if not patient_name.strip():
        validation_errors.append(
            "Patient Name is required."
        )

    if not dob.strip():
        validation_errors.append(
            "Date of Birth is required."
        )

    if not procedure.strip():
        validation_errors.append(
            "Procedure is required."
        )

    if not user_request.strip():
        validation_errors.append(
            "Please tell the agent what you want it to do."
        )

    if validation_errors:

        st.error(
            "Please fix the following before running the agent:"
        )

        for error in validation_errors:
            st.write(f"- {error}")

    else:

        st.success("✅ Input Validation PASS")

        with st.spinner(
            "Searching knowledge and selecting "
            "the appropriate tool..."
        ):

            response = run_agent(
                user_request,
                data
            )

        if response.get("success"):

            st.session_state.agent_response = response

            st.session_state.report_text = build_report(
                data,
                user_request,
                response
            )

        else:

            st.error(
                "AgentVerify could not complete the request."
            )

            st.warning(
                response.get(
                    "result",
                    "The AI service is temporarily unavailable."
                )
            )


# =========================================================
# DISPLAY AGENT RESULT
# =========================================================

if st.session_state.agent_response:

    response = st.session_state.agent_response

    st.success(
        "Agent finished successfully!"
    )

    provider = response.get(
        "provider",
        "Unknown"
    )

    tool_used = response.get(
        "tool_used",
        "Unknown"
    )

    knowledge_source = response.get(
        "knowledge_source",
        "knowledge_base.md"
    )

    st.info(
        f"**AI provider used:** `{provider}`"
    )

    st.info(
        f"**Knowledge source used:** `{knowledge_source}`"
    )

    st.info(
        f"**Agent selected tool:** `{tool_used}`"
    )

    st.markdown(
        "### Grounded Preparation Result"
    )

    st.markdown(
        response.get(
            "result",
            "No result returned."
        )
    )

    st.warning(
        "⚠️ Preparation only — AgentVerify does not verify "
        "or confirm insurance benefits. Eligibility, coverage, "
        "limitations, deductibles, maximums, frequencies and "
        "benefits must be confirmed directly with the payer."
    )

    if st.session_state.report_text:

        st.download_button(
            label="⬇️ Download Grounded Preparation Report",
            data=st.session_state.report_text,
            file_name="agentverify_grounded_report.md",
            mime="text/markdown",
            use_container_width=True
        )


# =========================================================
# HELP CHATBOT
# =========================================================

# =========================================================
# FLOATING-STYLE HELP CHATBOT
# =========================================================

st.markdown(
    """
    <style>
    div[data-testid="stPopover"] {
        position: fixed;
        right: 24px;
        bottom: 24px;
        z-index: 9999;
    }

    div[data-testid="stPopover"] > button {
        border-radius: 24px;
        padding: 0.65rem 1rem;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(0,0,0,0.20);
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.popover("💬 How can I help you?"):

    st.markdown("### 👋 Hi!")
    st.caption(
        "What would you like to know about AgentVerify?"
    )

    if st.button(
        "🦷 Our Services",
        use_container_width=True,
        key="chat_services"
    ):
        st.session_state.chat_answer = "services"

    if st.button(
        "💰 Pricing",
        use_container_width=True,
        key="chat_pricing"
    ):
        st.session_state.chat_answer = "pricing"

    if st.button(
        "⚙️ How It Works",
        use_container_width=True,
        key="chat_how"
    ):
        st.session_state.chat_answer = "how_it_works"

    if st.button(
        "📩 Contact Us",
        use_container_width=True,
        key="chat_contact"
    ):
        st.session_state.chat_answer = "contact"

    if st.button(
        "🔒 Privacy & Safety",
        use_container_width=True,
        key="chat_privacy"
    ):
        st.session_state.chat_answer = "privacy"

    if st.session_state.chat_answer:

        answer = CHATBOT_RESPONSES.get(
            st.session_state.chat_answer
        )

        if answer:
            st.markdown("---")
            st.markdown(answer)