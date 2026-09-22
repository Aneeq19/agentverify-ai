# 🦷 AgentVerify AI v1.3
## Evaluated Agentic Dental Verification Assistant

AI-assisted, grounded workflow preparation for dental insurance verification.

[🚀 Live Demo](https://agentverify-ai.streamlit.app/) | 🎥 Demo Video | [🧪 10/10 Evaluation](#evaluation) | [💡 What It Does](#what-it-does) | [🤖 Architecture](#architecture)

> **Evaluation result: 10/10 PASS — 100%**
>
> This means AgentVerify passed its defined fictional evaluation suite.  
> It does **not** establish clinical, insurance, or real-world benefit accuracy.

---

## 🚀 Live Demo

**Try AgentVerify AI:**  
https://agentverify-ai.streamlit.app/

The application is deployed using Streamlit Community Cloud.

---

## 🎥 Demo Video

Final technical demo recorded.

**Demo video link:** Coming soon

The demo shows:

- A fictional Crown case
- Agent tool selection
- RAG retrieval from `knowledge_base.md`
- Grounded workflow guidance
- Downloadable preparation report
- Automated evaluation result: `10/10 PASS — 100%`

---

## 💡 What It Does

AgentVerify AI is an agentic AI project for preparing dental insurance verification workflows using **fictional/non-PHI data**.

The system can:

- Check required case information
- Identify missing information
- Prepare payer questions
- Generate structured case summaries
- Retrieve relevant workflow guidance from a local knowledge base
- Select an appropriate tool based on the user's request
- Fall back to a second AI provider if the primary provider fails
- Produce downloadable preparation reports
- Run an automated fictional evaluation suite

AgentVerify AI does **not** perform or confirm actual insurance verification.

Benefits must be confirmed directly with the payer.

---

## 🤖 Architecture

```text
Fictional Case + User Request
            │
            ▼
     AgentVerify AI
            │
            ▼
  RAG Knowledge Retrieval
    knowledge_base.md
            │
            ▼
     Relevant Context
            │
            ▼
       AI Decision
            │
      ┌─────┴─────┐
      │           │
   Gemini      API Failure
  Primary          │
      │            ▼
      │      Cloudflare Workers AI
      │           Fallback
      └──────┬─────┘
             ▼
      Agent Tool Selection
             │
   ┌─────────┼──────────┐
   ▼         ▼          ▼
Required   Payer       Case
Fields    Questions    Summary
   │         │          │
   └─────────┼──────────┘
             ▼
    Grounded Preparation
             │
             ▼
     Downloadable Report
```

---

## 🛠️ Tools

AgentVerify currently uses these workflow tools:

### `check_required_fields`

Checks whether required case information is available before preparing the verification workflow.

### `build_payer_questions`

Prepares questions that may need to be asked directly to the insurance payer.

### `generate_case_summary`

Creates a structured summary of the fictional case.

### `search_knowledge_base`

Searches the local non-PHI knowledge base for relevant workflow guidance.

---

## 🧠 AI Providers

### Gemini — Primary

Google Gemini is used as the primary AI provider for agent decision-making.

### Cloudflare Workers AI — Fallback

If the primary provider fails, AgentVerify can use Cloudflare Workers AI as its backup provider.

The UI displays which provider was used.

---

## 📚 RAG & Grounding

AgentVerify uses:

`knowledge_base.md`

as a small local workflow knowledge base.

It contains general guidance covering topics such as:

- Eligibility questions
- Annual maximums and deductibles
- Crown verification preparation
- Preventive frequency questions
- Waiting periods
- Downgrades
- Preauthorization/predetermination

The knowledge base intentionally does **not** pretend to know patient-specific insurance benefits.

The UI visibly displays:

`Knowledge source used: knowledge_base.md`

---

## 🔒 Safety

AgentVerify is a workflow-preparation demonstration.

- Use fictional patient information only.
- Do not enter real patient information or PHI.
- Do not assume eligibility or coverage.
- Do not invent patient-specific percentages or dollar amounts.
- Do not treat authorization as a guarantee of payment.
- AgentVerify does not confirm insurance benefits.
- Benefits and eligibility must be confirmed directly with the payer.
- API credentials are stored separately from the public repository.
- `.env` is excluded from GitHub.

---

## 🧪 Evaluation

AgentVerify AI v1.3 includes an automated evaluation suite:

- `eval_cases.json`
- `evaluate.py`

### Result

**10/10 PASS — 100%**

The evaluation uses **10 completely fictional cases**, including:

1. Complete Crown case
2. Crown missing Member ID
3. Crown missing Group Number
4. Preventive cleaning
5. Missing DOB
6. Incomplete payer information
7. Unknown procedure
8. Waiting-period question
9. Deductible/annual maximum question
10. Deliberately vague case

### Evaluation Methodology

The automated suite checks whether:

- Required-field detection works
- Relevant payer questions are produced
- RAG/knowledge-base guidance is retrieved when appropriate
- The output retains the **confirm directly with payer** safety behavior

The final score is calculated automatically by `evaluate.py`.

```text
FINAL RESULT: 10/10 PASS — 100%
```

### Evaluation Limitation

**10/10 does not mean AgentVerify is clinically accurate or that it can accurately determine real insurance benefits.**

It means the system passed the **10 fictional test cases and checks defined in this project's evaluation suite**.

Real eligibility, coverage, limitations, frequencies, deductibles, maximums and benefits must still be confirmed directly with the payer.

---

## 📸 Screenshot

![AgentVerify AI Live Demo](tt.PNG)

---

## 🧰 Tech Stack

- Python
- Streamlit
- Google Gemini API
- Cloudflare Workers AI
- Local Markdown RAG knowledge base
- Requests
- python-dotenv
- Git
- GitHub
- Streamlit Community Cloud

---

## 📈 Project Progression

**v1.0 — Tool-using agent**

Introduced agent-driven tool selection for dental verification preparation.

**v1.1 — Provider fallback + downloadable report**

Added Gemini primary / Cloudflare fallback handling, validation and downloadable reports.

**v1.2 — Grounded RAG knowledge base**

Added `knowledge_base.md` and local knowledge retrieval for grounded workflow guidance.

**v1.3 — Automated evaluation suite**

Added 10 fictional evaluation cases and automated testing with `evaluate.py`.

**Evaluation result: 10/10 PASS — 100%**

---

## ▶️ Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` containing your own API credentials.

Then run:

```bash
streamlit run app.py
```

Run the evaluation suite with:

```bash
python evaluate.py
```

Never commit `.env` or API credentials to GitHub.

---

## 👨‍💻 Developer

Built by **Aneeq Jawed** as an applied AI-agent engineering project.

GitHub: **Aneeq19**

---

## ⚠️ Disclaimer

AgentVerify AI is an educational workflow-preparation project and is not a replacement for direct payer verification.

**All eligibility and benefits must be confirmed directly with the insurance payer.**