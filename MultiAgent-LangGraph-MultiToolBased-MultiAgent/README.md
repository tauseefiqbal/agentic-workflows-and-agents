# MultiAgent LangGraph Tool-Based Agent

A tool-calling AI agent built with **LangGraph** and **Groq** (via the OpenAI-compatible API). The agent answers user queries by orchestrating multiple external tools — Wikipedia search, full Wikipedia page fetch, DuckDuckGo web search, and arbitrary URL content fetch — in a stateful graph until it can cite a source.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the App](#running-the-app)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- ✅ Tool-calling agent built on a **LangGraph** state machine (`call_llm` ↔ `use_tool` loop)
- ✅ Powered by **Groq** (`openai/gpt-oss-20b`) via the **OpenAI Python SDK** — fast and free-tier friendly
- ✅ **Wikipedia search + page fetch** tools for cited, verifiable answers
- ✅ **DuckDuckGo web search** via `ddgs` for general queries
- ✅ **Arbitrary URL fetcher** with HTML stripped to plain text
- ✅ **Pydantic models** for typed tool inputs and outputs
- ✅ OpenAI-format tool schemas — easy to swap models/providers
- ✅ Windows-friendly: forces UTF-8 stdout to avoid emoji crashes
- ✅ Quiet, focused logging (suppresses `httpx` and `primp` noise)
- ✅ `.env`-based secret management with `python-dotenv`

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **LangGraph** | Stateful agent graph orchestration |
| **Groq API** | Fast LLM inference (default: `openai/gpt-oss-20b`) |
| **OpenAI Python SDK** (`openai`) | Client used to talk to Groq's OpenAI-compatible endpoint |
| **Pydantic** | Schema validation for state and tool I/O |
| **wikipedia** | Wikipedia search and page retrieval |
| **ddgs** | DuckDuckGo web search |
| **requests** | HTTP fetching for arbitrary URLs |
| **python-dotenv** | Load API keys from `.env` |

---

## GitHub Code Repository

🔗 [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

---

## How to Use App

### Prerequisites

- Python **3.10 or higher** (tested on 3.13)
- A **Groq API key** — get one free at [https://console.groq.com/keys](https://console.groq.com/keys)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents/MultiAgent-LangGraph-ToolBased-MultiAgents
   ```

2. **Create and activate a virtual environment:**

   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in this folder (or copy `.env.example`) and add your Groq key:

```env
GROQ_API_KEY=your-groq-api-key-here
```

### Running the App

```bash
python agent.py
```

You should see the agent take a few tool steps and print a `=== FINAL ANSWER ===` block at the end with the cited answer.

---

## Project Structure

```
MultiAgent-LangGraph-ToolBased-MultiAgents/
├── agent.py            # Main agent: LangGraph build + tools + entry point
├── requirements.txt    # Python dependencies
├── .env                # Your API keys (not committed)
├── .env.example        # Example environment file
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## How It Works

1. **State** — `AgentState` holds a `messages` list (OpenAI-format dicts) accumulated across turns.
2. **`call_llm` node** — sends the conversation + tool schemas to the Groq model. The model either replies with a final answer or emits one or more `tool_calls`.
3. **`should_we_stop` edge** — if the last assistant message contains `tool_calls`, the graph routes to `use_tool`; otherwise it routes to `END`.
4. **`use_tool` node** — executes each requested tool (`search_wikipedia`, `get_wikipedia_page`, `search_duck_duck_go`, `get_page_content`), serializes the Pydantic result to JSON, and appends it back as a `role: "tool"` message.
5. The loop continues until the model produces a final, source-cited answer.

```
START → call_llm ──(no tool calls)──> END
           ▲                │
           │                ▼
           └──── use_tool ──┘
```

---

## Customization

- **Change the model:** edit the `model_name` default in `ToolCallAgent.__init__` in [agent.py](agent.py). Other Groq options include `llama-3.1-8b-instant` and `llama-3.3-70b-versatile` (note: 70B sometimes malformats tool calls).
- **Change the question:** edit the user message in the `if __name__ == "__main__":` block.
- **Add a new tool:** define a Python function that returns a Pydantic model, add a matching JSON schema entry to `TOOL_SCHEMAS`, and pass the function in the `tools=[...]` list when constructing `ToolCallAgent`.
- **Adjust page-fetch sizes:** `get_wikipedia_page` and `get_page_content` default to `max_text_size=4_000` chars to fit Groq free-tier TPM limits — raise this if you upgrade your tier.

---

## Troubleshooting

- **`KeyError: 'GROQ_API_KEY'`** — `.env` missing or key not set. Create `.env` with `GROQ_API_KEY=...`.
- **`429 / rate_limit_exceeded`** — you've hit Groq's free-tier RPM/TPM limit. Wait a minute, lower `max_text_size`, or switch model.
- **`tool call validation failed ... was not in request.tools`** — the model malformatted a tool call. Switch to `openai/gpt-oss-20b` (default) or `llama-3.1-8b-instant`.
- **`UnicodeEncodeError` on Windows** — already mitigated by `sys.stdout.reconfigure(encoding="utf-8")` at the top of `agent.py`.

---

## License

This project is open source and available under the [MIT License](LICENSE).
