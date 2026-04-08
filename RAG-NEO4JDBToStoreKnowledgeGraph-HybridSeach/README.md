# RAG with Neo4j Knowledge Graph & Hybrid Search

An AI agent powered by **Pydantic AI**, **Graphiti**, and **Neo4j** that uses a three-tier structured memory architecture with hybrid search for intelligent knowledge retrieval. The agent gracefully degrades when Neo4j is unavailable, falling back to local persistent and in-memory storage.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
  - [Core Libraries](#core-libraries)
  - [Infrastructure](#infrastructure)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Agent](#running-the-agent)
  - [Slash Commands](#slash-commands)
- [Project Structure](#project-structure)
  - [File Descriptions](#file-descriptions)
- [Three-Tier Memory Architecture](#three-tier-memory-architecture)
  - [Tier 1: Short-Term Memory](#tier-1-short-term-memory)
  - [Tier 2: Long-Term Local Memory](#tier-2-long-term-local-memory)
  - [Tier 3: Knowledge Graph Memory](#tier-3-knowledge-graph-memory)
- [Agent Tools](#agent-tools)
- [License](#license)

---

## Features

- ✅ **Three-Tier Structured Memory** — Short-term (session), local persistent (JSON), and knowledge graph (Neo4j) memory working together
- ✅ **Graceful Degradation** — Agent continues operating with local + short-term memory when Neo4j is unavailable
- ✅ **Hybrid Search** — Combines semantic similarity and BM25 text retrieval across all memory tiers
- ✅ **Knowledge Graph with Temporal Data** — Tracks facts over time with valid/invalid timestamps via Graphiti
- ✅ **Streaming Responses** — Real-time markdown-rendered output using Rich live display
- ✅ **Automatic Deduplication** — Search results merged across tiers with duplicate removal by highest relevance
- ✅ **Persistent Local Memory** — Facts survive across restarts via `memory_store.json` without requiring Neo4j
- ✅ **Interactive Chat Interface** — Conversational loop with slash commands for memory management
- ✅ **LLM Evolution Tracking** — Demonstrates temporal knowledge updates as LLM rankings change over time
- ✅ **Pydantic AI Agent Framework** — Type-safe agent with structured tool definitions and dependency injection
- ✅ **Center Node Reranking** — Graph-distance-based reranking for contextually relevant search results
- ✅ **Node Hybrid Search Recipes** — Pre-configured search strategies via Graphiti's `NODE_HYBRID_SEARCH_RRF`

---

## Tech Stack

### Core Libraries

| Library | Purpose |
|---------|---------|
| **Pydantic AI** | Agent framework with typed tools and dependency injection |
| **Graphiti Core** | Knowledge graph episode management and hybrid search |
| **OpenAI GPT-4.1 Mini** | LLM for reasoning and response generation |
| **Pydantic** | Data validation and structured models |
| **Rich** | Terminal markdown rendering and live streaming output |
| **python-dotenv** | Environment variable management |

### Infrastructure

| Component | Purpose |
|-----------|---------|
| **Neo4j** | Graph database for knowledge graph storage |
| **Python 3.13+** | Runtime |
| **JSON file storage** | Local persistent memory tier |

---

## GitHub Code Repository

🔗 **Repository URL:** [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

- **Python 3.13+** installed
- **Neo4j Desktop** installed and a local DBMS running (optional — agent works without it)
- **OpenAI API Key** ([get one here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key))

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the project root (or copy from `.env.example`):

```dotenv
# OpenAI API Key
OPENAI_API_KEY="your-openai-api-key-here"

# LLM model to use
MODEL_CHOICE=gpt-4.1-mini

# Neo4j connection details
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```

### Running the Agent

**Main agent with structured memory:**

```bash
python agent.py
```

On startup, the agent reports memory tier status:

```
Memory Tier Status:
  [OK] short_term
  [OK] local
  [OK] knowledge_graph       ← shows [--] if Neo4j is down
```

**Quickstart (Graphiti basics):**

```bash
python quickstart.py
```

**LLM evolution demo (temporal knowledge updates):**

```bash
python llm_evolution.py
```

### Slash Commands

| Command | Description |
|---------|-------------|
| `/status` | Check the status of all three memory tiers |
| `/remember <fact>` | Store a fact in persistent local memory |
| `exit` | Quit the agent |

---

## Project Structure

```
├── agent.py                 # Main agent with three-tier structured memory
├── structured_memory.py     # Structured memory module (3 tiers)
├── quickstart.py            # Graphiti quickstart demo (hybrid search, node search)
├── llm_evolution.py         # Temporal knowledge evolution demo
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not committed)
├── .env.example             # Template for environment variables
├── memory_store.json        # Local persistent memory (auto-created at runtime)
└── README.md                # This file
```

### File Descriptions

| File | Description |
|------|-------------|
| `agent.py` | Interactive chat agent with `search_memory`, `remember_fact`, and `memory_status` tools |
| `structured_memory.py` | Three-tier memory manager: `ShortTermMemory`, `LocalMemory`, `KnowledgeGraphMemory`, and the unified `StructuredMemory` class |
| `quickstart.py` | Demonstrates adding episodes (text + JSON), hybrid search, center-node reranking, and node search recipes |
| `llm_evolution.py` | Multi-phase demo showing how the knowledge graph handles temporal updates (GPT-4.1 → Claude 4 → MLMs) |

---

## Three-Tier Memory Architecture

```
┌─────────────────────────────────────────────────────┐
│                  StructuredMemory                    │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Tier 1      │  │  Tier 2       │  │  Tier 3    │ │
│  │  Short-Term  │  │  Local        │  │  Knowledge │ │
│  │  (in-memory) │  │  (JSON file)  │  │  Graph     │ │
│  │              │  │               │  │  (Neo4j)   │ │
│  │  Always ON   │  │  Always ON    │  │  Optional  │ │
│  └─────────────┘  └──────────────┘  └────────────┘ │
│                                                     │
│         Search → Merge → Deduplicate → Rank         │
└─────────────────────────────────────────────────────┘
```

### Tier 1: Short-Term Memory

- **Storage:** In-memory deque (bounded to 100 entries)
- **Lifetime:** Current session only
- **Use case:** Conversation context, recent queries, working facts

### Tier 2: Long-Term Local Memory

- **Storage:** `memory_store.json` on disk
- **Lifetime:** Persists across restarts
- **Use case:** Important facts, user preferences, learned information
- **Always available** — no external dependencies

### Tier 3: Knowledge Graph Memory

- **Storage:** Neo4j via Graphiti
- **Lifetime:** Persistent with temporal tracking (valid_at / invalid_at)
- **Use case:** Rich relational data, entity relationships, temporal evolution
- **Optional** — agent gracefully falls back to Tiers 1 + 2 when unavailable

---

## Agent Tools

| Tool | Description |
|------|-------------|
| `search_memory` | Searches across all three memory tiers and returns merged, deduplicated results ranked by relevance |
| `remember_fact` | Stores a fact in both short-term and local persistent memory with an optional category |
| `memory_status` | Reports the current state of each memory tier (entry count, connection status) |

---

## License

This project uses components licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).
