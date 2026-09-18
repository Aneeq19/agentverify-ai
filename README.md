# 🦷 AgentVerify AI v1.0

AgentVerify AI is a lightweight AI agent built to demonstrate tool selection for dental insurance verification preparation.

The agent receives fictional patient information and a natural-language request, then decides which verification tool should be used.

It uses **Google Gemini as the primary AI provider** and **Cloudflare Workers AI as a backup provider** if the primary provider is unavailable.

> ⚠️ This project is for educational and demonstration purposes only. Use fictional data only. Do not enter real patient information or Protected Health Information (PHI).

---

## ✨ Features

- AI-powered tool selection
- Natural-language task instructions
- Three dental verification preparation tools
- Google Gemini as the primary AI provider
- Cloudflare Workers AI as an automatic backup
- Visible AI provider selection
- Visible tool selection
- Clean API failure handling
- Simple Streamlit interface
- Fictional-data demo workflow

---

## 🛠️ Available Tools

### `check_required_fields`

Checks whether the basic information required for verification is present.

Examples include:

- Patient name
- Date of birth
- Member ID
- Group number
- Procedure

### `build_payer_questions`

Builds questions for missing information that may need to be obtained before or during payer verification.

### `generate_case_summary`

Creates a concise summary of the fictional verification case.

---

## 🤖 How the Agent Works

```text
User Request
     ↓
Google Gemini
     ↓
Tool Selection
     ↓
Selected Python Tool
     ↓
Result
```

If the primary AI provider fails:

```text
Google Gemini
     ↓
API Failure
     ↓
Cloudflare Workers AI
     ↓
Tool Selection
     ↓
Selected Python Tool
     ↓
Result
```

The AI is responsible for deciding which tool matches the user's request. The selected Python tool then performs the actual task.

---

## 🧪 Example Tasks

The agent can understand requests such as:

```text
Check what information is missing.
```

```text
Build the questions I should ask the payer.
```

```text
Generate a concise verification case summary.
```

AgentVerify then displays both the AI provider and the tool selected for the request.

---

## 💻 Tech Stack

- Python
- Streamlit
- Google Gemini API
- Cloudflare Workers AI
- Requests
- python-dotenv

---

## 📁 Project Structure

```text
agentverify-ai/
│
├── app.py
├── agent.py
├── requirements.txt
├── README.md
└── .gitignore
```

The local `.env` file is intentionally excluded from GitHub.

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd agentverify-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project directory:

```env
GEMINI_API_KEY=your_gemini_api_key
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
```

Never commit API keys or your `.env` file to a public repository.

### 4. Start AgentVerify

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

---

## 🧪 Testing

AgentVerify v1.0 was tested with multiple fictional cases covering:

- Required-field checking
- Payer-question generation
- Case-summary generation
- Primary Gemini API requests
- Cloudflare Workers AI backup requests
- Primary-provider failure and automatic fallback

No real patient data is required for testing.

---

## 🔐 Privacy & Security

AgentVerify AI v1.0 is a learning/demo project and is **not a production dental verification system**.

- Use fictional patient information only.
- Do not submit PHI.
- API credentials should be stored as environment variables or deployment secrets.
- `.env` should remain excluded from version control.

---

## 📌 Version

**AgentVerify AI v1.0**

Built as part of a hands-on AI agent development project.