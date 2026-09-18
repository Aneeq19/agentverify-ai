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
# Keeps the result visible after clicking Download
# =========================================================

if "agent_response" not in st.session_state:
    st.session_state.agent_response = None

if "report_text" not in st.session_state:
    st.session_state.report_text = None


# =========================================================
# REPORT BUILDER
# =========================================================

def build_report(data, user_request, response):
    """
    Create a clean Markdown verification-preparation report.
    This report does NOT confirm insurance benefits.
    """

    provider = response.get("provider", "Unknown")
    tool_used = response.get("tool_used", "Unknown")
    result = response.get("result", "No result returned.")

    report = f"""# AgentVerify AI - Verification Preparation Report

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

## Preparation Result

{result}

## Important Notice

This report is for dental insurance verification preparation only.

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

st.title("🦷 AgentVerify AI v1.1")

st.caption(
    "AI-assisted workflow preparation for dental insurance verification"
)

st.markdown("---")


# =========================================================
# SAFETY NOTICE
# =========================================================

st.info(
    "Demo only — use fictional patient information. "
    "Do not enter real patient information or protected health information (PHI)."
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

    # Reset previous result
    st.session_state.agent_response = None
    st.session_state.report_text = None

    # =====================================================
    # BASIC INPUT VALIDATION
    # =====================================================

    validation_errors = []

    if not patient_name.strip():
        validation_errors.append("Patient Name is required.")

    if not dob.strip():
        validation_errors.append("Date of Birth is required.")

    if not procedure.strip():
        validation_errors.append("Procedure is required.")

    if not user_request.strip():
        validation_errors.append(
            "Please tell the agent what you want it to do."
        )

    if validation_errors:

        st.error("Please fix the following before running the agent:")

        for error in validation_errors:
            st.write(f"- {error}")

    else:

        with st.spinner(
            "Agent is thinking and selecting the appropriate tool..."
        ):

            response = run_agent(
                user_request,
                data
            )

        # =================================================
        # SUCCESS
        # =================================================

        if response.get("success"):

            st.session_state.agent_response = response

            st.session_state.report_text = build_report(
                data,
                user_request,
                response
            )

        # =================================================
        # CLEAN FAILURE
        # =================================================

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

    # Visible provider
    st.info(
        f"**AI provider used:** `{provider}`"
    )

    # Visible agent-selected tool
    st.info(
        f"**Agent selected tool:** `{tool_used}`"
    )

    # Result
    st.markdown("### Preparation Result")

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
        "⚠️ Preparation only — AgentVerify does not verify or confirm "
        "insurance benefits. Eligibility, coverage, limitations, "
        "deductibles, maximums and benefits must be confirmed "
        "directly with the payer."
    )

    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    if st.session_state.report_text:

        st.download_button(
            label="⬇️ Download Verification Preparation Report",
            data=st.session_state.report_text,
            file_name="agentverify_verification_report.md",
            mime="text/markdown",
            use_container_width=True
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "AgentVerify AI v1.1 • Fictional data only • "
    "Gemini primary + Cloudflare Workers AI backup • "
    "Verification preparation only"
)