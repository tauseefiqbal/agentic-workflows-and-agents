# MultiAgent Google Swarms

A minimal multi-agent workflow built on **Google's Agent Development Kit (ADK)**. A `Researcher` agent gathers facts via a tool call, then a `TechnicalWriter` agent synthesizes those facts into a polished report — orchestrated as a `SequentialAgent` pipeline and powered by Gemini.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Run the Pipeline](#run-the-pipeline)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
  - [Agents](#agents)
  - [Tools](#tools)
  - [Pipeline](#pipeline)
- [Configuration Reference](#configuration-reference)
- [Troubleshooting](#troubleshooting)
  - [429 RESOURCE_EXHAUSTED](#429-resource_exhausted)
  - [404 Model Not Found](#404-model-not-found)
  - [503 UNAVAILABLE](#503-unavailable)
- [Security Notes](#security-notes)
- [License](#license)

---

## Features

- ✅ Two-agent **Researcher → TechnicalWriter** pipeline
- ✅ Built on **Google ADK** `SequentialAgent` orchestration
- ✅ Custom Python tools wired to each agent (`search_tool`, `formatting_tool`)
- ✅ Session-state handoff between agents via `output_key`
- ✅ Gemini 2.5 Flash model for both agents (configurable)
- ✅ `.env`-based API key loading via `python-dotenv`
- ✅ Streaming event output to the console
- ✅ Single-file, zero-boilerplate entry point (`agent.py`)

---

## Tech Stack

| Layer | Component |
|---|---|
| Language | Python 3.13+ |
| Agent Framework | [Google ADK](https://google.github.io/adk-docs/) (`google-adk`) |
| LLM | Google Gemini 2.5 Flash |
| Runtime | `InMemoryRunner` (asyncio) |
| Config | `python-dotenv` (`.env` file) |
| Optional Server | `uvicorn` (for A2A hosting) |

---

## GitHub Code Repository

**Repository:** https://github.com/tauseefiqbal/agentic-workflows-and-agents.git

Clone it:

```powershell
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
cd agentic-workflows-and-agents
```

---

## How to Use App

### Prerequisites

- Python **3.13** or newer
- A **Google AI Studio API key** — get one free at https://aistudio.google.com/apikey
- Windows PowerShell, macOS Terminal, or Linux shell

### Installation

```powershell
# (Optional) create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install python-dotenv
```

### Configuration

Create a `.env` file in the project root (you can copy `.env.example` if present):

```env
GOOGLE_API_KEY="your-google-ai-studio-api-key"
```

### Run the Pipeline

Run with the default sample query:

```powershell
python agent.py
```

Or pass a custom query:

```powershell
python agent.py "Compare lithium-ion and solid-state batteries."
```

You'll see streamed output from each agent:

```
--- Researcher ---
* Improved Safety: ...
* Higher Energy Density: ...
* Faster Charging: ...

--- TechnicalWriter ---
Professional Report:
Solid-State Batteries: Key Advantages
...
```

---

## Project Structure

```
MultiAgent-Google-Swarms/
├── agent.py            # Main pipeline (Researcher + Writer + Runner)
├── requirements.txt    # Python dependencies
├── .env                # Local secrets (not committed)
├── .env.example        # Template for required env vars
└── README.md
```

---

## How It Works

### Agents

| Agent | Role | Output Key |
|---|---|---|
| `Researcher` | Calls `search_tool` and returns concise bullet-point facts | `research_data` |
| `TechnicalWriter` | Reads `research_data` from session state, calls `formatting_tool`, returns a polished report | `final_report` |

### Tools

- `search_tool(query: str)` — stub that returns canned technical details (replace with a real web/search backend in production).
- `formatting_tool(text: str)` — wraps text as a "Professional Report".

### Pipeline

```
User Query
    │
    ▼
┌────────────────┐      output_key="research_data"
│   Researcher   │ ──────────────────┐
└────────────────┘                   │
                                     ▼
                             session.state
                                     │
┌────────────────┐                   │
│ TechnicalWriter│ ◄─────────────────┘
└────────────────┘
        │
        ▼
   Final Report
```

Orchestrated by `SequentialAgent(name="ResearchWriterPipeline", sub_agents=[researcher, writer])` and executed via `InMemoryRunner.run_async(...)`.

---

## Configuration Reference

Edit constants at the top of `agent.py`:

| Constant | Default | Purpose |
|---|---|---|
| `APP_NAME` | `"research_writer_swarm"` | Used by the runner / session service |
| `USER_ID` | `"local-user"` | Synthetic user id for the session |
| `RESEARCHER_MODEL` | `"gemini-2.5-flash"` | LLM for the researcher agent |
| `WRITER_MODEL` | `"gemini-2.5-flash"` | LLM for the writer agent |

---

## Troubleshooting

### 429 RESOURCE_EXHAUSTED

You hit Gemini's free-tier daily quota (typically **20 requests/day per model**).

- Wait until the daily counter resets (UTC midnight), **or**
- Switch the model in `agent.py` to one with remaining quota (e.g. `gemini-2.5-flash-lite`), **or**
- Enable billing on your Google Cloud project to lift free-tier limits.

### 404 Model Not Found

The model name isn't available on your API version/key. List models available to your key:

```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); from google import genai; c=genai.Client(api_key=os.environ['GOOGLE_API_KEY']); [print(m.name) for m in c.models.list()]"
```

Then update `RESEARCHER_MODEL` / `WRITER_MODEL` accordingly.

### 503 UNAVAILABLE

Model is temporarily overloaded. Retry, or switch to a different Gemini variant.

---

## Security Notes

- **Never commit `.env`.** Add it to `.gitignore`.
- Treat your `GOOGLE_API_KEY` as a secret. If it's ever pasted into chat, screenshots, or pushed to git, **rotate it immediately** at https://aistudio.google.com/apikey.
- Use a dedicated GCP project per app so quotas and billing are isolated.

---

## License

MIT — see `LICENSE` file (add one if you plan to distribute).
