# MongoDB RAG Agent — Hybrid Search with Reciprocal Rank Fusion

An **Agentic RAG (Retrieval-Augmented Generation)** system powered by **MongoDB Atlas Vector Search**, **Pydantic AI**, and **Reciprocal Rank Fusion (RRF)**. The agent ingests multi-format documents (Markdown, PDF, DOCX, audio), chunks them with Docling's HybridChunker, embeds them with OpenAI, stores them in MongoDB Atlas, and answers natural-language questions through a streaming conversational CLI.

---

## Table of Contents

- [MongoDB RAG Agent — Hybrid Search with Reciprocal Rank Fusion](#mongodb-rag-agent--hybrid-search-with-reciprocal-rank-fusion)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [GitHub Code Repository](#github-code-repository)
  - [How to Use App](#how-to-use-app)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
      - [1. Clone the Repository](#1-clone-the-repository)
      - [2. Create a Virtual Environment](#2-create-a-virtual-environment)
      - [3. Install Dependencies](#3-install-dependencies)
      - [4. Configure Environment Variables](#4-configure-environment-variables)
      - [5. Set Up MongoDB Atlas](#5-set-up-mongodb-atlas)
    - [Running the App](#running-the-app)
      - [1. Ingest Documents](#1-ingest-documents)
      - [2. Create Search Indexes](#2-create-search-indexes)
      - [3. Run the Conversational CLI](#3-run-the-conversational-cli)
  - [Project Structure](#project-structure)
  - [Search Architecture](#search-architecture)
    - [Semantic Search](#semantic-search)
    - [Full-Text Search](#full-text-search)
    - [Hybrid Search with RRF](#hybrid-search-with-rrf)
  - [Document Ingestion Pipeline](#document-ingestion-pipeline)
  - [Environment Variables Reference](#environment-variables-reference)
  - [Additional Resources](#additional-resources)
  - [License](#license)

---

## Features

- ✅ **Hybrid Search with Reciprocal Rank Fusion (RRF)** — Combines MongoDB Atlas Vector Search (semantic) and Atlas Full-Text Search (keyword/fuzzy) into a single ranked result set using the RRF algorithm
- ✅ **Agentic RAG with Pydantic AI** — An LLM-powered agent that decides when and how to search the knowledge base, with tool-calling and multi-turn conversation support
- ✅ **Multi-Format Document Ingestion** — Processes Markdown, PDF, DOCX, and audio files (MP3 via OpenAI Whisper transcription) through a unified pipeline
- ✅ **Docling HybridChunker** — Token-aware, structure-preserving chunking that respects headings, paragraphs, tables, and code blocks for higher-quality retrieval
- ✅ **OpenAI Embeddings** — Generates vector embeddings with `text-embedding-3-small` (1536 dimensions) for semantic similarity search
- ✅ **MongoDB Atlas Vector Search** — Stores and queries embeddings using Atlas's native `$vectorSearch` aggregation stage with cosine similarity
- ✅ **MongoDB Atlas Full-Text Search** — Keyword and fuzzy matching via `$search` with the Lucene standard analyzer
- ✅ **Streaming Conversational CLI** — Real-time streamed responses with Rich terminal UI, tool-call visibility, and multi-turn message history
- ✅ **Programmatic Index Creation** — Automatically creates vector search and text search indexes via the MongoDB Atlas API (no manual Atlas UI steps)
- ✅ **Graceful Degradation** — Falls back to semantic-only or text-only search if one pipeline fails, ensuring the agent always returns results
- ✅ **Configurable LLM Provider** — Supports OpenAI, OpenRouter, Ollama, Anthropic, and any OpenAI-compatible API via environment variables
- ✅ **Async Throughout** — Fully asynchronous architecture using `asyncio`, `AsyncMongoClient`, and `openai.AsyncOpenAI` for high throughput
- ✅ **Works on MongoDB Atlas Free Tier (M0)** — All features including hybrid search work on the free M0 cluster — no M10+ required

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Agent Framework** | [Pydantic AI](https://ai.pydantic.dev/) with AG-UI support |
| **LLM** | OpenAI GPT-4o-mini (configurable — any OpenAI-compatible API) |
| **Embeddings** | OpenAI `text-embedding-3-small` (1536 dimensions) |
| **Vector Database** | [MongoDB Atlas](https://www.mongodb.com/atlas) with Vector Search |
| **Full-Text Search** | MongoDB Atlas Search (Lucene-based) |
| **Rank Fusion** | Reciprocal Rank Fusion (RRF, k=60) |
| **Document Processing** | [Docling](https://github.com/DS4SD/docling) (PDF, DOCX, Markdown) |
| **Audio Transcription** | [OpenAI Whisper](https://github.com/openai/whisper) |
| **Chunking** | Docling HybridChunker (token-aware, structure-preserving) |
| **CLI / UI** | [Rich](https://github.com/Textualize/rich) (streaming terminal interface) |
| **Configuration** | [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) + `.env` |
| **Language** | Python 3.10+ (fully async) |
| **Package Management** | pip / uv with `pyproject.toml` |

---

## GitHub Code Repository

```
https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

- **Python 3.10** or higher
- **MongoDB Atlas** account (free M0 cluster works)
- **OpenAI API key** (for LLM inference and embeddings)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
cd agentic-workflows-and-agents
```

#### 2. Create a Virtual Environment

```bash
# Create
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS / Linux)
source .venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=<appName>
MONGODB_DATABASE=your_database_name
MONGODB_COLLECTION_DOCUMENTS=documents
MONGODB_COLLECTION_CHUNKS=chunks

# MongoDB Atlas Search Indexes
MONGODB_VECTOR_INDEX=vector_index
MONGODB_TEXT_INDEX=text_index

# LLM Provider Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1

# Embedding Provider Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_API_KEY=your_openai_api_key
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_BASE_URL=https://api.openai.com/v1

# Search Configuration
DEFAULT_MATCH_COUNT=10
MAX_MATCH_COUNT=50
DEFAULT_TEXT_WEIGHT=0.3
```

#### 5. Set Up MongoDB Atlas

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/) and create a free M0 cluster
2. Create a database user and whitelist your IP address
3. Copy the connection string into `MONGODB_URI` in your `.env` file

> **Note:** Search indexes are created programmatically — no manual Atlas UI steps needed.

### Running the App

#### 1. Ingest Documents

Place your documents (`.md`, `.pdf`, `.docx`, `.mp3`) in the `documents/` folder, then run:

```bash
python -m src.ingestion.ingest -d ./documents
```

This will:
- Convert documents to a unified format via Docling
- Transcribe audio files via OpenAI Whisper
- Chunk documents using Docling HybridChunker (token-aware)
- Generate embeddings with OpenAI `text-embedding-3-small`
- Store documents and chunks in MongoDB Atlas

#### 2. Create Search Indexes

```bash
python src/create_indexes.py
```

This creates:
- **`vector_index`** — Cosine similarity index on the `embedding` field (1536 dimensions)
- **`text_index`** — Lucene standard analyzer index on the `content` field

> Indexes may take 1–5 minutes to build. Check status in the Atlas UI under **Database → Search and Vector Search**.

#### 3. Run the Conversational CLI

```bash
python src/cli.py
```

The CLI will:
- Display a welcome panel with current LLM configuration
- Run demo questions against the knowledge base
- Stream responses in real-time with tool-call visibility
- Show which search tool was called, the query, and result count

---

## Project Structure

```
├── .env                          # Environment variables (not committed)
├── pyproject.toml                # Package configuration and dependencies
├── requirements.txt              # Pinned dependencies for pip install
├── documents/                    # Source documents for ingestion
│   ├── company-overview.md
│   ├── implementation-playbook.md
│   ├── mission-and-goals.md
│   ├── team-handbook.md
│   ├── technical-architecture-guide.pdf
│   ├── q4-2024-business-review.pdf
│   ├── client-review-globalfinance.pdf
│   ├── meeting-notes-2025-01-08.docx
│   ├── meeting-notes-2025-01-15.docx
│   └── Recording1.mp3 ... Recording4.mp3
├── src/
│   ├── agent.py                  # Pydantic AI agent with search tool
│   ├── cli.py                    # Streaming conversational CLI (entry point)
│   ├── create_indexes.py         # Programmatic Atlas search index creation
│   ├── dependencies.py           # MongoDB + OpenAI connection management
│   ├── prompts.py                # System prompt for the RAG agent
│   ├── providers.py              # LLM and embedding model configuration
│   ├── settings.py               # Pydantic Settings with .env loading
│   ├── tools.py                  # Semantic, text, and hybrid search tools
│   └── ingestion/
│       ├── chunker.py            # Docling HybridChunker wrapper
│       ├── embedder.py           # OpenAI embedding generation
│       └── ingest.py             # Document ingestion pipeline
├── examples/                     # Standalone examples and Docling tutorials
│   ├── docling_basics/           # Docling processing examples
│   └── ingestion/                # Example ingestion scripts
└── test_scripts/                 # End-to-end and integration tests
    ├── test_agent_e2e.py
    ├── test_rag_pipeline.py
    ├── test_search.py
    └── check_indexes.py
```

---

## Search Architecture

### Semantic Search

Uses MongoDB Atlas `$vectorSearch` to find chunks whose embeddings are closest to the query embedding (cosine similarity). Best for conceptual and thematic queries.

```
Query → OpenAI Embedding → $vectorSearch (cosine) → Ranked Results
```

### Full-Text Search

Uses MongoDB Atlas `$search` with the Lucene standard analyzer for keyword matching with fuzzy support (`maxEdits=2`). Best for specific terms, names, and exact phrases.

```
Query → $search (Lucene, fuzzy) → Ranked Results
```

### Hybrid Search with RRF

Runs both searches concurrently, then merges results using **Reciprocal Rank Fusion**:

```
                    ┌─→ Semantic Search (vector) ─┐
Query ──┤                                          ├──→ RRF Merge ──→ Top N Results
                    └─→ Full-Text Search (keyword) ─┘
```

**RRF Formula:**

$$\text{RRF\_score}(d) = \sum_{i} \frac{1}{k + \text{rank}_i(d)}$$

Where $k = 60$ (standard constant) and $\text{rank}_i(d)$ is the position of document $d$ in result list $i$.

---

## Document Ingestion Pipeline

```
documents/
    ├── .md   ──→ Docling ──→ DoclingDocument ──┐
    ├── .pdf  ──→ Docling ──→ DoclingDocument ──┤
    ├── .docx ──→ Docling ──→ DoclingDocument ──┼──→ HybridChunker ──→ Embedder ──→ MongoDB Atlas
    └── .mp3  ──→ Whisper ──→ Transcript ───────┘
```

1. **Document Conversion** — Docling converts PDF, DOCX, and Markdown into a unified `DoclingDocument` format
2. **Audio Transcription** — OpenAI Whisper transcribes MP3 audio files to text
3. **Chunking** — Docling HybridChunker splits documents into token-aware chunks that respect document structure
4. **Embedding** — OpenAI `text-embedding-3-small` generates 1536-dimensional vectors for each chunk
5. **Storage** — Documents go into the `documents` collection; chunks with embeddings go into the `chunks` collection

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `MONGODB_URI` | Yes | — | MongoDB Atlas connection string |
| `MONGODB_DATABASE` | No | `rag_db` | Database name |
| `MONGODB_COLLECTION_DOCUMENTS` | No | `documents` | Documents collection |
| `MONGODB_COLLECTION_CHUNKS` | No | `chunks` | Chunks collection |
| `MONGODB_VECTOR_INDEX` | No | `vector_index` | Vector search index name |
| `MONGODB_TEXT_INDEX` | No | `text_index` | Text search index name |
| `LLM_PROVIDER` | No | `openrouter` | LLM provider identifier |
| `LLM_API_KEY` | Yes | — | API key for the LLM |
| `LLM_MODEL` | No | `anthropic/claude-haiku-4.5` | Model name |
| `LLM_BASE_URL` | No | `https://openrouter.ai/api/v1` | LLM API base URL |
| `EMBEDDING_PROVIDER` | No | `openai` | Embedding provider |
| `EMBEDDING_API_KEY` | Yes | — | API key for embeddings |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | Embedding model |
| `EMBEDDING_BASE_URL` | No | `https://api.openai.com/v1` | Embedding API base URL |
| `DEFAULT_MATCH_COUNT` | No | `10` | Default search results count |
| `MAX_MATCH_COUNT` | No | `50` | Maximum search results |
| `DEFAULT_TEXT_WEIGHT` | No | `0.3` | Text weight for hybrid search |

---

## Additional Resources

- [MongoDB Atlas Vector Search Documentation](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/)
- [MongoDB Atlas Search Documentation](https://www.mongodb.com/docs/atlas/atlas-search/)
- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [Docling Documentation](https://ds4sd.github.io/docling/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Reciprocal Rank Fusion (Cormack et al., 2009)](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

---

## License

This project is provided as-is for educational and demonstration purposes.
