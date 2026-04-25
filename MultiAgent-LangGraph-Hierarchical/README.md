# Multi-Agent System with LangGraph Hierarchical Router

A multi-agent application built with LangGraph that uses a **hierarchical router pattern** to classify user queries, fan out to specialized sub-agents in parallel, and synthesize results into a unified response — all powered by Groq's blazing-fast LLM inference.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
  - [Core Framework](#core-framework)
  - [LLM Provider](#llm-provider)
  - [Data & APIs](#data--apis)
  - [Utilities](#utilities)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the App](#running-the-app)
- [Architecture](#architecture)
  - [Agent Flow](#agent-flow)
  - [Graph Structure](#graph-structure)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- ✅ **Hierarchical Multi-Agent Orchestration** — a main agent delegates to specialized sub-agents via tool calls
- ✅ **LangGraph Router Pattern** — classifies queries, fans out to agents in parallel using `Send`, and synthesizes results
- ✅ **Course Recommender Agent** — recommends courses from a curated catalog based on user interests
- ✅ **Institution Recommender Agent** — suggests universities and colleges offering relevant master's programs
- ✅ **Stock Data Tool** — fetches real-time stock quotes via the Finnhub API
- ✅ **Structured Output Classification** — uses Pydantic models with `with_structured_output` for reliable query routing
- ✅ **Groq-Powered LLM Inference** — leverages `llama-3.3-70b-versatile` for fast, high-quality responses
- ✅ **Parallel Agent Execution** — sub-agents run concurrently via LangGraph's `Send` mechanism
- ✅ **Result Synthesis** — an LLM-powered synthesizer merges multi-agent outputs into a coherent final answer

---

## Tech Stack

### Core Framework

| Technology | Purpose |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Agent orchestration, state graphs, and routing |
| [LangChain Core](https://github.com/langchain-ai/langchain) | Tool definitions and message primitives |
| [Pydantic](https://docs.pydantic.dev/) | Structured output models for query classification |

### LLM Provider

| Technology | Purpose |
|---|---|
| [Groq](https://groq.com/) | Ultra-fast LLM inference engine |
| `llama-3.3-70b-versatile` | Large language model used by all agents |
| [langchain-groq](https://python.langchain.com/docs/integrations/chat/groq/) | LangChain integration for Groq |

### Data & APIs

| Technology | Purpose |
|---|---|
| [Finnhub](https://finnhub.io/) | Real-time stock market data |

### Utilities

| Technology | Purpose |
|---|---|
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable management via `.env` files |

---

## GitHub Code Repository

```
https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/keys) (required)
- A [Finnhub API key](https://finnhub.io/register) (optional — only needed for stock data)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your API keys:

   ```env
   GROQ_API_KEY=your-groq-api-key-here
   STOCK_API_KEY=your-finnhub-api-key-here
   ```

### Running the App

```bash
python agent.py
```

The default query is *"Suggest a good college for masters in security"*. The system will:

1. Route the query to the **Course Recommender** and **Institution Recommender** agents in parallel
2. Each agent generates targeted recommendations
3. The synthesizer merges both results into a single, coherent response

---

## Architecture

### Agent Flow

```
User Query
    │
    ▼
┌──────────────┐
│  Main Agent  │  (ReAct agent with tools)
└──────┬───────┘
       │ tool call
       ▼
┌──────────────────┐
│ Recommender Tool │  (LangGraph sub-graph)
└──────┬───────────┘
       │
       ▼
┌──────────────┐
│   Classify   │  (Structured output → routing decisions)
└──────┬───────┘
       │ fan-out via Send
       ├────────────────────┐
       ▼                    ▼
┌──────────────┐   ┌────────────────────┐
│ Course Agent │   │ Institution Agent  │
└──────┬───────┘   └────────┬───────────┘
       │                    │
       └────────┬───────────┘
                ▼
        ┌──────────────┐
        │  Synthesize  │  (Merge & deduplicate results)
        └──────┬───────┘
               │
               ▼
         Final Answer
```

### Graph Structure

| Node | Description |
|---|---|
| `classify` | Classifies the query and determines which sub-agents to invoke |
| `course_agent` | Recommends courses based on a curated catalog |
| `institution_agent` | Recommends institutions offering relevant programs |
| `synthesize` | Combines results from all agents into a unified response |

---

## Project Structure

```
.
├── agent.py           # Main application — agents, tools, graph, and entry point
├── requirements.txt   # Python dependencies
├── .env.example       # Template for required environment variables
├── .env               # Your local API keys (not committed)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

---

## License

This project is open source. See the repository for license details.
