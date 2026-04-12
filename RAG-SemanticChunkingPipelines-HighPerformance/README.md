# RAG Semantic Chunking Pipelines — High Performance

A structured memory agent powered by **Pydantic AI**, **OpenAI**, and **Neo4j/Graphiti** with a three-tier memory architecture (short-term, local persistent, and knowledge graph).

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
  - [Core Frameworks](#core-frameworks)
  - [Memory & Storage](#memory--storage)
  - [LLM & Embeddings](#llm--embeddings)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Agent](#running-the-agent)
  - [Slash Commands](#slash-commands)
- [Project Structure](#project-structure)
- [Memory Architecture](#memory-architecture)
  - [Tier 1 — Short-Term Memory](#tier-1--short-term-memory)
  - [Tier 2 — Local Persistent Memory](#tier-2--local-persistent-memory)
  - [Tier 3 — Knowledge Graph](#tier-3--knowledge-graph)
- [License](#license)

---

## Features

- ✅ Three-tier memory architecture (short-term, local persistent, knowledge graph)
- ✅ Streaming LLM responses with rich Markdown rendering in the terminal
- ✅ Automatic graceful fallback when Neo4j is unavailable
- ✅ Persistent local memory stored as JSON across sessions
- ✅ Unified memory search across all tiers with relevance scoring
- ✅ Interactive conversational loop with context-aware prompts
- ✅ Slash commands for memory inspection (`/status`) and manual fact storage (`/remember`)
- ✅ Configurable LLM model via environment variables
- ✅ Built-in test prompts for quick validation on startup
- ✅ Modular design — memory system is fully decoupled from agent logic

---

## Tech Stack

### Core Frameworks

| Technology | Purpose |
|---|---|
| **Pydantic AI** | Agent framework with tool-use and streaming |
| **Pydantic** | Data validation and settings management |
| **Rich** | Terminal Markdown rendering and live output |
| **asyncio** | Asynchronous execution |

### Memory & Storage

| Technology | Purpose |
|---|---|
| **Graphiti Core** | Knowledge graph integration with Neo4j |
| **Neo4j** | Graph database for Tier 3 memory (optional) |
| **JSON** | Local persistent storage for Tier 2 memory |

### LLM & Embeddings

| Technology | Purpose |
|---|---|
| **OpenAI GPT-4.1-mini** | Default LLM for agent responses |
| **Sentence Transformers** | Embedding model for semantic chunking |
| **scikit-learn** | Cosine similarity for semantic search |
| **LangChain Text Splitters** | Text chunking strategies |

---

## GitHub Code Repository

```
https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

- Python 3.10+
- An OpenAI API key ([get one here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key))
- *(Optional)* Neo4j database for knowledge graph support

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Copy the example environment file and add your API key:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your OpenAI API key:

   ```env
   OPENAI_API_KEY=sk-your-key-here
   MODEL_CHOICE=gpt-4.1-mini
   ```

3. *(Optional)* Configure Neo4j if you want Tier 3 knowledge graph memory:

   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your-password
   ```

### Running the Agent

```bash
python agent.py
```

The agent will:
1. Initialize all three memory tiers and report their status
2. Run built-in test prompts to verify connectivity
3. Enter an interactive loop where you can ask questions

### Slash Commands

| Command | Description |
|---|---|
| `/status` | Display the status of all memory tiers |
| `/remember <fact>` | Manually store a fact in persistent memory |
| `exit` | Quit the agent |

---

## Project Structure

```
├── agent.py               # Main agent with tools and conversational loop
├── structured_memory.py   # Three-tier memory system implementation
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
└── memory_store.json      # Auto-generated local memory (Tier 2)
```

---

## Memory Architecture

### Tier 1 — Short-Term Memory

In-session buffer that holds recent conversation facts. Capped at 100 entries (configurable). Lost when the process exits.

### Tier 2 — Local Persistent Memory

JSON-backed store (`memory_store.json`) that persists across sessions. Facts are written immediately on storage.

### Tier 3 — Knowledge Graph

Neo4j via Graphiti Core. Provides semantic graph-based retrieval. The agent gracefully degrades if Neo4j is unavailable — Tier 1 and Tier 2 continue to operate normally.

---

## License

This project is open source and available under the [MIT License](LICENSE).
