# RAG Contextual Retrieval — Anthropic

A production-ready **Retrieval-Augmented Generation (RAG)** pipeline implementing Anthropic's **Contextual Retrieval** technique. This system combines contextual embeddings, hybrid search (semantic + BM25), and reranking to significantly reduce retrieval failures compared to traditional RAG approaches.

---

## Table of Contents

- [Features](#features)
  - [Core Capabilities](#core-capabilities)
  - [Advanced Retrieval](#advanced-retrieval)
  - [Cost Optimization](#cost-optimization)
- [Tech Stack](#tech-stack)
  - [AI & LLM](#ai--llm)
  - [Search & Retrieval](#search--retrieval)
  - [Evaluation & Monitoring](#evaluation--monitoring)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Pipeline](#running-the-pipeline)
- [Architecture](#architecture)
  - [Pipeline Overview](#pipeline-overview)
  - [Project Structure](#project-structure)
- [How It Works](#how-it-works)
  - [Indexing Phase](#indexing-phase)
  - [Query Phase](#query-phase)
- [Cost Analysis](#cost-analysis)
- [License](#license)

---

## Features

### Core Capabilities

- ✅ **Contextual Chunk Generation** — Uses Claude to generate rich, document-aware context for each chunk before embedding
- ✅ **Intelligent Document Chunking** — Preserves semantic boundaries (paragraphs, sentences) with configurable chunk size and overlap
- ✅ **Async Context Generation** — Concurrent API calls with semaphore-based rate limiting for fast, safe processing
- ✅ **End-to-End RAG Pipeline** — Single `ContextualRAGPipeline` class orchestrates indexing, retrieval, and answer generation

### Advanced Retrieval

- ✅ **Hybrid Search** — Combines semantic similarity (Voyage AI embeddings) with lexical matching (BM25) using weighted fusion
- ✅ **Reranking with Cohere** — Two-stage retrieval: retrieve 150 candidates, rerank to top-k with a dedicated reranking model
- ✅ **Configurable Alpha Weighting** — Tune the balance between embedding-based and BM25-based search results
- ✅ **Min-Max Score Normalization** — Ensures fair combination of scores across different retrieval methods

### Cost Optimization

- ✅ **Prompt Caching** — Leverages Anthropic's prompt caching to reduce context generation costs by up to 87%
- ✅ **Extended Cache TTL** — Support for 1-hour ephemeral caching for frequently processed documents
- ✅ **Batch Embedding** — Processes embeddings in batches of 128 for efficient API usage
- ✅ **Free BM25 Indexing** — Lexical search runs locally with zero API cost

---

## Tech Stack

### AI & LLM

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Context Generation | **Anthropic Claude (Sonnet 4.5)** | Generates contextual explanations for chunks |
| Embeddings | **Voyage AI (voyage-2)** | Creates semantic vector embeddings |
| Reranking | **Cohere (rerank-english-v3.0)** | Reranks retrieval candidates by relevance |
| Answer Generation | **Anthropic Claude (Sonnet 4.5)** | Generates final answers from retrieved context |

### Search & Retrieval

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Vector Database | **ChromaDB** | Persistent vector storage with cosine similarity |
| Lexical Search | **BM25 (rank-bm25)** | Keyword-based retrieval via Okapi BM25 |
| Hybrid Fusion | **Custom Implementation** | Weighted combination of semantic + lexical scores |

### Evaluation & Monitoring

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Metrics | **scikit-learn** | Precision, Recall, F1, MRR evaluation |
| Progress | **tqdm** | Async progress bars for context generation |
| Monitoring | **Custom RAGMonitor** | Query latency tracking and anomaly detection |

---

## GitHub Code Repository

🔗 **Repository URL:** [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

- Python 3.10+
- API keys for:
  - [Anthropic](https://console.anthropic.com/) — Claude API
  - [Voyage AI](https://dash.voyageai.com/) — Embedding API
  - [Cohere](https://dashboard.cohere.com/) — Reranking API

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd RAG-ContextualRetrieval-Anthropic
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

3. **Create a `.env` file** in the project root with your API keys:

   ```env
   ANTHROPIC_API_KEY=your-anthropic-api-key
   VOYAGE_API_KEY=your-voyage-api-key
   COHERE_API_KEY=your-cohere-api-key
   ```

4. **(Optional)** Adjust parameters in `config.py`:

   ```python
   CHUNK_SIZE = 800        # Tokens per chunk
   CHUNK_OVERLAP = 100     # Overlap between chunks
   TOP_K_RETRIEVAL = 150   # Candidates from hybrid search
   TOP_K_RERANK = 20       # Final results after reranking
   ```

### Running the Pipeline

5. **Run the main pipeline:**

   ```bash
   python main.py
   ```

   This will:
   - Chunk a sample ACME earnings report
   - Generate contextual embeddings with Claude
   - Store vectors in ChromaDB
   - Build a BM25 index
   - Perform a hybrid search + reranking query
   - Generate a final answer using Claude

**Example Output:**

```
============================================================
INDEXING DOCUMENT
============================================================
Step 1: Chunking document...
Created 1 chunks

Step 2: Generating contexts with Claude...
Generating contexts: 100%|█████████████████████| 1/1 [00:01<00:00]

Step 3: Creating embeddings and storing...
Embedded 1/1 chunks
Added 1 chunks to vector store

Step 4: Building BM25 index...
Built BM25 index with 1 chunks

✓ Document indexed successfully!

============================================================
GENERATING ANSWER
============================================================

Answer: ACME Corporation's revenue in Q2 2023 was $323 million,
representing a 3% increase over Q1 2023's $314 million...
```

---

## Architecture

### Pipeline Overview

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
│  Document   │────▶│  Chunking        │────▶│  Context Gen   │
│  Input      │     │  (800 tokens,    │     │  (Claude API + │
│             │     │   100 overlap)   │     │   Caching)     │
└─────────────┘     └──────────────────┘     └───────┬────────┘
                                                     │
                                          ┌──────────┴──────────┐
                                          │                     │
                                    ┌─────▼─────┐       ┌──────▼──────┐
                                    │ Voyage AI  │       │   BM25      │
                                    │ Embeddings │       │   Index     │
                                    │ + ChromaDB │       │  (Local)    │
                                    └─────┬──────┘       └──────┬──────┘
                                          │                     │
                                          └──────────┬──────────┘
                                                     │
                                              ┌──────▼──────┐
                                              │   Hybrid    │
                                              │   Search    │
                                              │ (α-weighted)│
                                              └──────┬──────┘
                                                     │
                                              ┌──────▼──────┐
                                              │  Cohere     │
                                              │  Reranker   │
                                              │ (Top 20)    │
                                              └──────┬──────┘
                                                     │
                                              ┌──────▼──────┐
                                              │   Claude    │
                                              │   Answer    │
                                              │  Generation │
                                              └─────────────┘
```

### Project Structure

```
RAG-ContextualRetrieval-Anthropic/
├── main.py                      # End-to-end pipeline orchestration
├── config.py                    # Configuration & environment variables
├── chunking.py                  # Intelligent document chunking
├── contextualizer.py            # Claude-powered context generation
├── embeddings.py                # Voyage AI embeddings + ChromaDB storage
├── bm25_index.py                # BM25 lexical search index
├── retriever.py                 # Hybrid search (semantic + BM25)
├── reranker.py                  # Cohere reranking
├── hybrid_search.py             # Alpha weight optimization
├── chunk_size_optimization.py   # Chunk size tuning experiments
├── benchmarks.py                # RAG evaluation metrics (P, R, F1, MRR)
├── performance_matrix.py        # Performance evaluation utilities
├── monitor.py                   # Query latency & anomaly monitoring
├── caching.py                   # Prompt caching strategies
├── cost_analysis.py             # Cost breakdown & optimization notes
├── prompts.py                   # Contextual retrieval prompt templates
├── context_generation_prompts.py# Domain-specific prompt examples
├── requirements.txt             # Python dependencies
├── .env                         # API keys (not committed)
└── Data/                        # Document storage directory
```

---

## How It Works

### Indexing Phase

1. **Chunking** — The document is split into semantically meaningful chunks (800 tokens with 100-token overlap) that respect paragraph and sentence boundaries.
2. **Context Generation** — Claude reads the full document and generates a concise context for each chunk, situating it within the broader document.
3. **Embedding** — Each contextualized chunk (`context + original text`) is embedded using Voyage AI and stored in ChromaDB.
4. **BM25 Indexing** — A BM25 index is built over the contextualized chunks for keyword-based retrieval.

### Query Phase

1. **Hybrid Search** — The query is run against both the vector store (semantic) and BM25 index (lexical). Scores are normalized and combined using a configurable alpha weight.
2. **Reranking** — The top 150 candidates are reranked using Cohere's reranking model to surface the most relevant results.
3. **Answer Generation** — The top-k reranked chunks are passed as context to Claude, which generates a grounded answer.

---

## Cost Analysis

| Component | Without Caching | With Caching | Savings |
|-----------|---------------:|-------------:|--------:|
| Context Generation (1000 docs) | $94.00 | $12.00 | 87% |
| Embeddings (50K chunks) | $0.50 | $0.50 | — |
| BM25 Indexing | Free | Free | — |
| Reranking (100 queries) | ~$3.00 | ~$3.00 | — |
| **Total Indexing** | **$97.50** | **$15.50** | **84%** |
| **Cost per Query** | — | **$0.03** | — |

---

## License

This project is provided as-is for educational and research purposes.
