import json
import streamlit as st
from agent import run_agent

st.set_page_config(page_title="AgentVerify AI", page_icon="🤖", layout="wide")
st.title("🤖 AgentVerify AI")
st.caption("A tool-using AI agent for dental insurance verification preparation")
st.info("Demo only — use fictional data. Benefits must always be confirmed directly with the payer.")

with st.form("case"):
    a, b = st.columns(2)
    with a:
        patient_name = st.text_input("Patient name", "John Demo")
        dob = st.text_input("Date of birth", "01/01/1995")
        payer = st.text_input("Insurance company", "Demo Dental Plan")
    with b:
        member_id = st.text_input("Member ID", "DEMO12345")
        procedure = st.text_input("Procedure / service", "Crown")
        notes = st.text_area("Notes", "New patient; prepare a verification workflow.")
    go = st.form_submit_button("Run Agent", type="primary", use_container_width=True)

if go:
    case = {
        "patient_name": patient_name.strip(), "dob": dob.strip(),
        "payer": payer.strip(), "member_id": member_id.strip(),
        "procedure": procedure.strip(), "notes": notes.strip(),
    }
    try:
        with st.spinner("Agent is choosing and running tools..."):
            output = run_agent(case)
        st.success("Agent workflow complete")
        st.subheader("🧠 Agent selected tools")
        for tool in output["selected_tools"]:
            st.write(f"✓ `{tool}`")

        results = output["results"]
        if "check_required_fields" in results:
            st.subheader("🔎 Missing required fields")
            missing = results["check_required_fields"]
            st.write(", ".join(missing) if missing else "No required demo fields are missing.")
        if "build_payer_questions" in results:
            st.subheader("☎️ Questions for payer")
            for q in results["build_payer_questions"]:
                st.write(f"• {q}")
        if "generate_case_summary" in results:
            st.subheader("📋 Case summary")
            st.write(results["generate_case_summary"])

        report = json.dumps(output, indent=2)
        st.download_button("Download agent report", report, "agentverify_report.json", "application/json")
        with st.expander("Developer view"):
            st.json(output)
    except Exception as exc:
        st.error(f"Agent could not complete the workflow: {exc}")

st.divider()
st.caption("Python • Streamlit • Gemini • GitHub | Fictional data only.")
