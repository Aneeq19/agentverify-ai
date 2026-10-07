"""AgentVerify portfolio review UI. Default mode works without credentials."""
import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from demo_cases import CASES, load_demo
from llm_client import enhance_review
from report import render_report, review_rows
from retrieval import retrieve_workflow_guidance
from schemas import CaseInput
from workflow import input_errors, prepare_review

load_dotenv()
st.set_page_config(page_title="AgentVerify AI by Aneeq Jawed | Dental Review",
                   page_icon="🦷", layout="wide")


def load_case(name):
    demo = load_demo(name)
    st.session_state.demo = demo
    st.session_state.demo_name = name
    for key, value in demo["case"].items():
        st.session_state[key] = value
    st.session_state.review = None
    st.session_state.ai_count = 0
    st.session_state.ai_cache = {}
    st.session_state.reviewed = False


if "demo" not in st.session_state:
    load_case("Incomplete crown case")

st.title("🦷 AgentVerify AI")
st.caption("Dental Verification Preparation & Review Assistant · By Aneeq Jawed")
st.info("Fictional demo only. Use synthetic examples; do not enter real patient information.")

with st.sidebar:
    st.subheader("Try a scenario")
    for name in CASES:
        st.button(name, on_click=load_case, args=(name,), use_container_width=True)
    st.divider()
    mode = st.radio("Preparation mode", ["Offline rules", "OpenAI assisted"])
    st.caption("Offline mode includes checks, benefits review, checklists and downloads.")
    if mode == "OpenAI assisted":
        st.caption("OpenAI chooses a preparation tool and prioritizes existing questions and evidence.")
    st.page_link("https://github.com/Aneeq19/agentverify-ai", label="View project on GitHub")

review_tab, practice_tab, stedi_tab = st.tabs(
    ["Case preparation", "Checklist & practice", "Saved Stedi example"])

with review_tab:
    st.subheader(st.session_state.demo_name)
    with st.form("case_form"):
        left, right = st.columns(2)
        with left:
            st.text_input("Fictional patient name", key="patient_name", max_chars=100)
            st.text_input("Date of birth (MM/DD/YYYY)", key="dob", max_chars=20)
            st.text_input("Member ID", key="member_id", max_chars=100)
        with right:
            st.text_input("Group number", key="group_number", max_chars=100)
            st.text_input("Procedure", key="procedure", max_chars=100)
            st.text_area("Fictional notes", key="notes", max_chars=2000)
        submitted = st.form_submit_button("Prepare review", type="primary",
                                         use_container_width=True)
    if submitted:
        st.session_state.review = None
        st.session_state.reviewed = False
        try:
            case = CaseInput(**{key: st.session_state[key] for key in
                               ("patient_name", "dob", "member_id", "group_number", "procedure", "notes")})
            errors = input_errors(case)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                demo = st.session_state.demo
                st.session_state.review = prepare_review(case, demo["raw"], demo["format"], demo["source"])
        except ValidationError:
            st.error("Some inputs exceed the allowed format or length.")
    review = st.session_state.review
    if review:
        st.success("Input format valid.")
        if review.missing_fields:
            st.warning("Verification information incomplete: " + ", ".join(review.missing_fields))
        else:
            st.success("Verification prerequisites complete.")
        st.caption("Source: " + review.source + " · This example is not a live payer check.")
        if review.case.member_id != st.session_state.demo["case"]["member_id"]:
            st.caption("Edited form values do not modify the separate synthetic benefits fixture.")
        if review.source_errors:
            st.error("Source error: benefit conclusions are unavailable.")
            for error in review.source_errors:
                st.write(error)
        a, b, c = st.columns(3)
        a.metric("Reported fields", sum(f.status == "reported" for f in review.fields))
        b.metric("Unanswered fields", sum(f.status in ("not_returned", "source_error") for f in review.fields))
        c.metric("Conflicting fields", sum(f.status == "conflicting" for f in review.fields))
        st.markdown("#### Benefit review")
        st.dataframe(review_rows(review), hide_index=True, use_container_width=True)
        st.caption("Overall eligibility and dental coverage are separate. Unknown values are never assumed.")
        if mode == "OpenAI assisted":
            task = st.selectbox("AI preparation task", [
                "Prepare payer follow-up questions", "Check missing prerequisites", "Summarize this fictional case"])
            if st.button("Prioritize with OpenAI"):
                fingerprint = review.model_dump_json(exclude={"usage", "latency_ms", "ai_status",
                    "provider", "model", "selected_tool", "review_status"}) + task
                if fingerprint in st.session_state.ai_cache:
                    st.session_state.review = st.session_state.ai_cache[fingerprint].model_copy(deep=True)
                elif st.session_state.ai_count >= 3:
                    st.warning("This example's three-request limit has been reached.")
                else:
                    st.session_state.ai_count += 1
                    # Read optional secrets without showing their values in the UI.
                    try:
                        for key in ("OPENAI_API_KEY", "OPENAI_MODEL"):
                            if key not in os.environ and key in st.secrets:
                                os.environ[key] = st.secrets[key]
                    except FileNotFoundError:
                        pass
                    with st.spinner("Preparing evidence priorities..."):
                        enriched = enhance_review(review, task)
                    st.session_state.ai_cache[fingerprint] = enriched
                    st.session_state.review = enriched
                review = st.session_state.review
            st.caption(review.ai_status)
        st.markdown("#### Follow-up questions")
        for q in review.questions:
            st.write("• " + q)
        st.markdown("#### Cited workflow guidance")
        if not review.guidance:
            st.write("No matching passage found in the supplied workflow knowledge.")
        for guidance in review.guidance:
            with st.expander(guidance.title):
                st.markdown(guidance.text)
                st.caption(guidance.source_id + " · version " + guidance.version)
        reviewed = st.checkbox("I reviewed this fictional example", key="reviewed")
        review.review_status = "Reviewed fictional example" if reviewed else "Needs review"
        st.caption("Review status: " + review.review_status)
        st.caption("Provider: " + review.provider + (" · model: " + review.model if review.model else ""))
        if review.usage:
            st.caption(f"Usage: {review.usage} · latency: {review.latency_ms} ms")
        txt, js = st.columns(2)
        txt.download_button("Download review TXT", render_report(review),
                            "agentverify-fictional-review.txt", "text/plain", use_container_width=True)
        js.download_button("Download review JSON", review.model_dump_json(indent=2),
                           "agentverify-fictional-review.json", "application/json", use_container_width=True)
    else:
        st.write("Choose a scenario and prepare its review. All examples work without an API key.")

with practice_tab:
    st.subheader("A daily checklist without patient data")
    procedure = st.selectbox("Practice procedure", ["Crown", "Preventive cleaning", "Basic filling", "Major bridge"])
    guidance = retrieve_workflow_guidance(procedure + " eligibility deductible")
    for passage in guidance:
        st.markdown(passage.text)
        st.caption(passage.source_id + " · version " + passage.version)
    query = st.text_input("Search your workflow knowledge", placeholder="Example: crown replacement frequency")
    if query:
        matches = retrieve_workflow_guidance(query)
        if not matches:
            st.info("Not found in the supplied workflow knowledge.")
        for passage in matches:
            with st.expander(passage.title):
                st.markdown(passage.text)
                st.caption(passage.source_id + " · version " + passage.version)
    st.markdown("#### Practice a payer call")
    st.write("You are preparing a fictional crown case. Coverage was mentioned, but replacement frequency "
             "and previous service date were omitted. What would you ask next?")
    with st.expander("Show suggested questions"):
        st.write("What crown replacement frequency applies? When was the previous crown on this tooth? "
                 "Are there waiting periods, downgrades or documentation requirements?")
    st.download_button("Download procedure checklist",
                       "\n\n".join(p.text + "\nSource: " + p.source_id for p in guidance),
                       "agentverify-procedure-checklist.txt", "text/plain")

with stedi_tab:
    st.subheader("Saved synthetic Stedi example")
    st.caption("Narrow sandbox adapter: reads dental nonCovered entries. No live request or credentials required.")
    if st.button("Review saved Stedi example"):
        raw = json.loads(Path(__file__).with_name("stedi_example_response.json").read_text())
        demo = load_demo("Synthetic dental benefits")
        # Subscriber in this saved fixture is explicitly independent of the other demo form.
        case = CaseInput(**{**demo["case"], "patient_name": "Jane Doe",
                            "dob": "", "member_id": "HUMANA123", "group_number": ""})
        st.session_state.stedi_review = prepare_review(case, raw, "stedi", "Recreated Stedi sandbox example")
    if "stedi_review" in st.session_state:
        saved = st.session_state.stedi_review
        st.dataframe(review_rows(saved), hide_index=True, use_container_width=True)
        st.caption("This adapter does not parse comprehensive Stedi benefits. Unknown fields remain unknown.")
        st.download_button("Download saved-source review", render_report(saved),
                           "agentverify-stedi-example.txt", "text/plain")

st.divider()
st.caption("Workflow preparation and human review. Confirm actual benefits through an authorized payer workflow.")
