# Deprecated OpenAI Models — Usage Report

Scan date: 2026-04-25
Scope: All `.py`, `.json`, `.yaml`, `.yml`, `.toml`, `.cfg`, `.ini`, `.txt`, `.env` files
Excluded: `venv/`, `.venv/`, `node_modules/`, `__pycache__/`, `.git/`, `chroma_db/`, `qdrant_data/`, `ollama_models/`, `*.egg-info/`

---

## Summary

| Deprecated Model | # of Files Affected | Files |
|---|---:|---|
| `text-embedding-3-small` | 5 | `RAG-MongoDBRankFusionFeature-HybridSearch/src/settings.py`, `RAG-MongoDBRankFusionFeature-HybridSearch/src/ingestion/embedder.py`, `RAG-MongoDBRankFusionFeature-HybridSearch/src/ingestion/ingest.py`, `RAG-MongoDBRankFusionFeature-HybridSearch/examples/settings.py`, `RAG-MongoDBRankFusionFeature-HybridSearch/examples/ingestion/embedder.py` |
| `gpt-4-0613` (used via the bare `gpt-4` alias, which OpenAI routes to `gpt-4-0613`) | 2 | `FunctionCalling-GPT4/agent.py`, `MultiAgent-OpenAI-Orchistration/agent.py` |

All other models from the deprecation list were **not found** in any project source file.

---

## Detailed Findings

### 1. `text-embedding-3-small`

| # | File Path | Line | Code |
|---|---|---:|---|
| 1 | `RAG-MongoDBRankFusionFeature-HybridSearch/src/settings.py` | 66 | `default="text-embedding-3-small", description="Embedding model to use"` |
| 2 | `RAG-MongoDBRankFusionFeature-HybridSearch/src/settings.py` | 75 | `description="Embedding vector dimension (1536 for text-embedding-3-small)",` |
| 3 | `RAG-MongoDBRankFusionFeature-HybridSearch/src/ingestion/embedder.py` | 49 | `"text-embedding-3-small": {"dimensions": 1536, "max_tokens": 8191},` |
| 4 | `RAG-MongoDBRankFusionFeature-HybridSearch/src/ingestion/ingest.py` | 695 | `print("   - Dimensions: 1536 (for text-embedding-3-small)")` |
| 5 | `RAG-MongoDBRankFusionFeature-HybridSearch/examples/settings.py` | 78 | `default="text-embedding-3-small",` |
| 6 | `RAG-MongoDBRankFusionFeature-HybridSearch/examples/ingestion/embedder.py` | 53 | `"text-embedding-3-small": {"dimensions": 1536, "max_tokens": 8191},` |

**Recommended replacement:** `text-embedding-3-large` or a non-deprecated embedding model.

---

### 2. `gpt-4-0613`

These files explicitly set `model="gpt-4"`. The bare `gpt-4` alias is routed by OpenAI to the snapshot `gpt-4-0613`, which is on the deprecation list. So effectively these files are using the deprecated `gpt-4-0613`.

**Files using `gpt-4-0613`:**

| # | File Path | Line | Code |
|---|---|---:|---|
| 1 | `FunctionCalling-GPT4/agent.py` | 65 | `model="gpt-4",` |
| 2 | `MultiAgent-OpenAI-Orchistration/agent.py` | 12 | `model="gpt-4",` |
| 3 | `MultiAgent-OpenAI-Orchistration/agent.py` | 24 | `model="gpt-4",` |
| 4 | `MultiAgent-OpenAI-Orchistration/agent.py` | 36 | `model="gpt-4",` |
| 5 | `MultiAgent-OpenAI-Orchistration/agent.py` | 47 | `model="gpt-4",` |

**Recommended replacement:** `gpt-4o` or `gpt-4.1`.

---

## Models From the Deprecation List With NO Matches in This Repo

The following models were searched for and **not found** anywhere in project source code:

- computer-use-preview-2025-03-11
- gpt-4o-audio-preview-2024-12-17
- gpt-4o-mini-audio-preview-2024-12-17
- gpt-4o-mini-realtime-preview-2024-12-17
- gpt-4o-mini-search-preview-2025-03-11
- gpt-4o-mini-tts-2025-03-20
- gpt-4o-search-preview-2025-03-11
- gpt-5-chat-latest, gpt-5-codex
- gpt-5.1-chat-latest, gpt-5.1-codex, gpt-5.1-codex-max, gpt-5.1-codex-mini, gpt-5.2-codex
- gpt-audio-mini-2025-10-06
- gpt-realtime-mini-2025-10-06
- o3-deep-research-2025-06-26
- o4-mini-deep-research-2025-06-26
- gpt-3.5-turbo-0125
- gpt-4-0613 (literal string — but `gpt-4` alias is in use, see above)
- gpt-4-1106-preview
- gpt-4-turbo
- gpt-4.1-nano
- gpt-4o-2024-05-13
- gpt-image-1
- o1-2024-12-17
- o1-pro-2025-03-19
- o3-mini-2025-01-31
- o4-mini-2025-04-16
- babbage-002
- davinci-002
- Any fine-tuned variants (no `ft:` model strings present)

---

## Files NOT Affected (Use Non-Deprecated Models)

The following agent files were checked and use only **current/non-deprecated** models (`gpt-4o`, `gpt-4o-mini`, `gpt-4.1-mini`) or local/non-OpenAI models (Ollama, Anthropic Claude, Cohere, HuggingFace, Voyage):

- `ContextAware-ChatWithAI-Mem0-VectorDB-LTM/agent.py` — `gpt-4o-mini`
- `DeepResearch-AIAgents/deep_research_openai.py` — no explicit model (uses SDK defaults)
- `Guardrails-LangGraph-LangChain/*.py` (and `guardrails/`, `langgraph_guards/`, `pipeline/`) — `gpt-4o`, `gpt-4o-mini`
- `MultiAgent--LangGraph-Hierarchical/agent.py` — Groq `llama-3.3-70b-versatile`
- `MultiAgent-CrewAI-Collaborative/agent.py` — `gpt-4o-mini`
- `MultiAgent-LangGraph-Supervisor/agent.py` — Ollama `qwen3:8b`
- `MultiAgent-LangGraph-Workflow/agent.py` — Ollama `llama3.2:latest`
- `MultiAgent-OpenAI-Handoffs/agent.py` — no explicit model (SDK default)
- `RAG-Agentic-VectorChromaDB-SimilaritySearch/r1_smolagent_rag.py` — env-driven model IDs
- `RAG-ContextualRetrieval-Anthropic/*.py` — Claude `claude-sonnet-4-5-20250929`, Voyage `voyage-2`, Cohere `rerank-english-v3.0`
- `RAG-MongoDBRankFusionFeature-HybridSearch/src/settings.py` — LLM: `anthropic/claude-haiku-4.5` (only the embedding model is deprecated, see above)
- `RAG-NEO4JDBToStoreKnowledgeGraph-HybridSeach/agent.py` — env `MODEL_CHOICE` defaults to `gpt-4.1-mini`
- `RAG-QueriesExpansion/agent.py` — `gpt-4o-mini`
- `RAG-ReRanking-UsingLlamaIndexReranking-FactualAccuracy/agent.py` — HuggingFace `Qwen/Qwen2.5-1.5B-Instruct`, `BAAI/bge-small-en-v1.5`
- `RAG-Vectorless-PageIndex-StructuredMemoryApproach/agent.py`, `retriever.py` — `gpt-4o-mini`
