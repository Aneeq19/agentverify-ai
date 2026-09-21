import streamlit as st
from datetime import datetime
from agent import run_agent

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


# =========================================================
# REPORT BUILDER
# =========================================================

def build_report(data, user_request, response):
    """Create a grounded verification-preparation report."""

    provider = response.get("provider", "Unknown")
    tool_used = response.get("tool_used", "Unknown")
    knowledge_source = response.get(
        "knowledge_source",
        "knowledge_base.md"
    )
    result = response.get("result", "No result returned.")

    report = f"""# AgentVerify AI v1.2 - Grounded Verification Preparation Report

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

The local knowledge base contains general workflow guidance only.
It does not contain or confirm patient-specific insurance benefits.

AgentVerify AI does not confirm eligibility, coverage, benefits,
limitations, frequencies, deductibles, maximums, or payment.

All insurance benefits and eligibility must be confirmed directly
with the payer before relying on this information.

This demo uses fictional patient data only.
"""

    return report


# =========================================================
# HEADER
# =========================================================

st.title("🦷 AgentVerify AI v1.2")

st.caption(
    "Grounded RAG-assisted workflow preparation "
    "for dental insurance verification"
)

st.markdown("---")


# =========================================================
# SAFETY NOTICE
# =========================================================

st.info(
    "Demo only — use fictional patient information. "
    "Do not enter real patient information or protected "
    "health information (PHI)."
)


# =========================================================
# FICTIONAL PATIENT DATA
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

    # =====================================================
    # BASIC INPUT VALIDATION
    # =====================================================

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

        # Visible validation PASS state
        st.success(
            "✅ Input Validation PASS"
        )

        with st.spinner(
            "Searching knowledge and selecting the appropriate tool..."
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
                    "The AI service is temporarily unavailable. "
                    "Please try again later."
                )
            )


# =========================================================
# DISPLAY SAVED RESULT
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

    # Visible provider
    st.info(
        f"**AI provider used:** `{provider}`"
    )

    # Visible RAG knowledge source
    st.info(
        f"**Knowledge source used:** `{knowledge_source}`"
    )

    # Visible selected action tool
    st.info(
        f"**Agent selected tool:** `{tool_used}`"
    )

    # Grounded result
    st.markdown(
        "### Grounded Preparation Result"
    )

    st.markdown(
        response.get(
            "result",
            "No result returned."
        )
    )

    # =====================================================
    # PAYER CONFIRMATION WARNING
    # =====================================================

    st.warning(
        "⚠️ Preparation only — AgentVerify does not verify "
        "or confirm insurance benefits. Eligibility, coverage, "
        "limitations, deductibles, maximums, frequencies and "
        "benefits must be confirmed directly with the payer."
    )

    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    if st.session_state.report_text:

        st.download_button(
            label="⬇️ Download Grounded Preparation Report",
            data=st.session_state.report_text,
            file_name="agentverify_v1_2_grounded_report.md",
            mime="text/markdown",
            use_container_width=True
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "AgentVerify AI v1.2 • Grounded RAG workflow • "
    "knowledge_base.md • Fictional data only • "
    "Gemini primary + Cloudflare fallback • "
    "Benefits must be confirmed directly with payer"
)