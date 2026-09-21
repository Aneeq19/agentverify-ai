# 🦷 AgentVerify AI v1.1

**AI-assisted workflow preparation for dental insurance verification**

[🚀 Live Demo](https://agentverify-ai.streamlit.app/) | 🎥 Demo Video | 🛠️ Agent Architecture | 🔒 Safety

---

## 🚀 Live Demo

**Try AgentVerify AI:**  
https://agentverify-ai.streamlit.app/

The deployed application runs on Streamlit Community Cloud.

---

## 🎥 Demo Video

Demo video coming soon.

---

## 💡 What It Does

AgentVerify AI is an AI agent designed to demonstrate how AI-assisted tool selection can help prepare dental insurance verification workflows.

The user enters **fictional patient information** and gives the agent a natural-language task.

The agent then:

- analyzes the request
- selects an appropriate verification-preparation tool
- checks required information
- generates payer questions when needed
- creates a structured case summary
- displays which AI provider and tool were selected
- produces a downloadable verification-preparation report

AgentVerify AI **does not perform or confirm actual insurance verification**.

---

## 🤖 Agent Architecture

```text
User Request + Fictional Patient Data
              │
              ▼
       AgentVerify AI
              │
              ▼
       Google Gemini
       (Primary AI)
              │
       ┌──────┴──────┐
       │             │
    Success       API Error
       │             │
       │             ▼
       │      Cloudflare Workers AI
       │          (Backup)
       │             │
       └──────┬──────┘
              ▼
       Agent selects tool
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
 Required   Payer     Case
 Fields    Questions  Summary
      │       │        │
      └───────┼────────┘
              ▼
      Preparation Result
              │
              ▼
      Downloadable Report

```

---

## 📸 Screenshot

![AgentVerify AI v1.1 Live Demo](tt.PNG)

---
## Evaluation

AgentVerify AI v1.3 includes an automated evaluation suite using 10 completely fictional, non-PHI test cases.

The evaluation checks:

- Required-field detection
- Relevant payer-question generation
- Knowledge-base / RAG retrieval when appropriate
- Retention of the "confirm directly with payer" safety behavior

### Evaluation Result

**10/10 PASS — 100%**

The test suite includes complete and incomplete Crown cases, preventive cleaning, missing patient information, incomplete payer information, an unknown procedure, waiting-period questions, deductible/maximum questions, and a deliberately vague case.

The score is calculated automatically by `evaluate.py` from `eval_cases.json` and is not hard-coded.

## Project Progression

- **v1.0** — Tool-using agent
- **v1.1** — Provider fallback + downloadable report
- **v1.2** — Grounded RAG knowledge base
- **v1.3** — Automated evaluation suite