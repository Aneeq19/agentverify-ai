import streamlit as st
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
# HEADER
# =========================================================

st.title("🦷 AgentVerify AI v1.0")

st.caption(
    "An AI agent that chooses tools for dental verification preparation"
)

st.markdown("---")

# =========================================================
# FICTIONAL PATIENT DATA
# =========================================================

st.subheader("Fictional Patient Data")

st.info(
    "Demo only — use fictional patient information. "
    "Do not enter real patient or protected health information."
)

col1, col2 = st.columns(2)

with col1:
    patient_name = st.text_input(
        "Patient Name",
        value="John Demo"
    )

    dob = st.text_input(
        "Date of Birth",
        value="01/01/1995"
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

# Build patient dictionary
data = {
    "patient_name": patient_name,
    "dob": dob,
    "member_id": member_id,
    "group_number": group_number,
    "procedure": procedure,
    "notes": notes
}

st.markdown("---")

# =========================================================
# AGENT REQUEST
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

    if not user_request.strip():

        st.warning(
            "Please tell the agent what you want it to do."
        )

    else:

        with st.spinner(
            "Agent is thinking and choosing a tool..."
        ):

            response = run_agent(
                user_request,
                data
            )

        # =================================================
        # SUCCESS
        # =================================================

        if response.get("success"):

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

            # Show AI provider
            st.info(
                f"**AI provider used:** `{provider}`"
            )

            # Show selected tool
            st.info(
                f"**Tool selected by agent:** `{tool_used}`"
            )

            # Result
            st.markdown("### Result")

            st.markdown(
                response.get(
                    "result",
                    "No result returned."
                )
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
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "AgentVerify AI v1.0 • Fictional data only • "
    "Gemini primary + Cloudflare Workers AI backup • "
    "Built for learning AI agents"
)