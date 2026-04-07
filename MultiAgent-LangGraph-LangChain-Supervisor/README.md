# MultiAgent Support Ticket Triage — LangGraph & LangChain Supervisor

An intelligent multi-agent system that automates support ticket triage using LangGraph state machines and LangChain tool-calling agents. The system classifies tickets, retrieves relevant knowledge, drafts responses, and self-evaluates with an iterative revision loop.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the App](#running-the-app)
- [Architecture](#architecture)
  - [Graph-Based Workflow](#graph-based-workflow)
  - [Agent-Based Workflow](#agent-based-workflow)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- ✅ **Automatic Ticket Classification** — Classifies support tickets into *Technical Issue*, *Billing Inquiry*, or *General Question*
- ✅ **Knowledge Base Retrieval** — Retrieves relevant knowledge-base articles using vector similarity search
- ✅ **AI-Powered Draft Response** — Generates context-aware draft responses for support tickets
- ✅ **Self-Evaluation & Revision Loop** — Evaluates drafts and iteratively revises them (up to 3 revisions) until quality passes
- ✅ **Conditional Routing** — Uses LangGraph conditional edges for intelligent workflow branching
- ✅ **Stateful Graph Orchestration** — Manages agent state across multi-step workflows with LangGraph `StateGraph`
- ✅ **Tool-Calling Agent** — LangChain agent with bound tools for classify, retrieve, and draft operations
- ✅ **In-Memory Vector Store** — Fast, lightweight vector store powered by FastEmbed embeddings
- ✅ **Local LLM Support** — Runs entirely on a local Ollama model (`qwen3:8b`) — no API keys required

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **LangGraph** | State machine orchestration and conditional workflow routing |
| **LangChain** | Agent framework, prompt templates, and tool integration |
| **LangChain Ollama** | Local LLM integration via Ollama |
| **FastEmbed** | Lightweight, fast text embeddings for vector search |
| **Ollama** | Local model serving (`qwen3:8b`) |
| **InMemoryVectorStore** | Vector similarity search for knowledge retrieval |

---

## GitHub Code Repository

🔗 **Repository URL:** [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

- **Python 3.10+**
- **Ollama** installed and running locally with the `qwen3:8b` model pulled

```bash
# Install Ollama: https://ollama.com/download
ollama pull qwen3:8b
```

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd MultiAgent-LangGraph-LangChain-Supervisor
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Running the App

```bash
python agent.py
```

The app processes a sample ticket (`"My login is broken, please help!"`) and outputs:

- **Classification** — The ticket category
- **Draft Response** — The AI-generated response
- **Evaluation** — PASS/FAIL result with feedback
- **Revision Count** — Number of revision iterations performed

---

## Architecture

### Graph-Based Workflow

The system uses a LangGraph `StateGraph` with the following node pipeline:

```
classify → retrieve → draft → evaluate ─┬─→ END (PASS)
                                         └─→ revise → evaluate (loop, max 3)
```

Each node is a pure function that reads from and writes to a shared `TicketTriageState` dataclass.

### Agent-Based Workflow

A LangChain tool-calling agent wraps the same logic as callable tools (`classify_ticket`, `retrieve_knowledge`, `draft_response`), allowing the LLM to autonomously decide tool invocation order based on an system prompt.

---

## Project Structure

```
MultiAgent-LangGraph-LangChain-Supervisor/
├── agent.py            # Main application — graph workflow + tool-calling agent
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## License

This project is open source. See the repository for license details.
