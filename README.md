# 🤖 AgentVerify AI

**A tool-using AI agent for dental insurance verification preparation.**

AgentVerify AI is the second product in my 21-Day AI Builder sprint. Unlike a simple prompt-response app, the agent chooses which workflow tools to run for a fictional dental insurance case.

> **Safety:** Educational portfolio demo only. Never enter real patient data or PHI. The app prepares a workflow; it does not verify eligibility or benefits.

## Agent tools

- `check_required_fields` — detects missing intake fields
- `build_payer_questions` — creates procedure-focused verification questions
- `generate_case_summary` — produces a concise preparation summary

## Architecture

```text
Fictional case
     ↓
Gemini agent
     ↓
Tool selection
     ↓
Python tools
     ↓
Structured result + downloadable report
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Create a local `.env` (never commit it):

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

## Portfolio goals

- Demonstrate agent/tool-selection concepts
- Show structured, explainable workflow execution
- Practice API security and graceful UI handling
- Deploy a second public AI product after DentalVerify AI

## Next

- Provider fallback
- richer tool trace
- exportable Markdown/PDF report
- office-configurable verification rules
- Streamlit deployment and demo video

Built by **Aneeq** during the 21-Day AI Builder sprint.
