# RAG ReRanking Using LlamaIndex Reranking for Factual Accuracy

A Retrieval-Augmented Generation (RAG) pipeline that leverages **LlamaIndex**, **Qdrant** vector store, and **Sentence Transformer ReRanking** to improve factual accuracy of LLM-generated answers.

---

## Table of Contents

- [RAG ReRanking Using LlamaIndex Reranking for Factual Accuracy](#rag-reranking-using-llamaindex-reranking-for-factual-accuracy)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
    - [Frameworks and Libraries](#frameworks-and-libraries)
    - [Models](#models)
    - [Vector Store](#vector-store)
  - [GitHub Code Repository](#github-code-repository)
  - [How to Use App](#how-to-use-app)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running the App](#running-the-app)
  - [Project Structure](#project-structure)
  - [How It Works](#how-it-works)
  - [License](#license)

---

## Features

- ✅ **RAG Pipeline** — Retrieval-Augmented Generation for grounded, context-aware answers
- ✅ **Sentence Transformer ReRanking** — Re-ranks retrieved documents using a cross-encoder (`ms-marco-MiniLM-L-2-v2`) to boost factual accuracy
- ✅ **Qdrant Vector Store** — In-memory vector database for fast similarity search
- ✅ **HuggingFace Embeddings** — Uses `BAAI/bge-small-en-v1.5` for high-quality document embeddings
- ✅ **Local LLM Inference** — Runs a HuggingFace LLM (`Qwen/Qwen2.5-1.5B-Instruct`) locally without API keys
- ✅ **PDF Document Ingestion** — Reads and indexes PDF documents from the `Data/` directory
- ✅ **Configurable Chunking** — Supports custom chunk sizes for document splitting
- ✅ **Top-K Similarity Search** — Retrieves top 10 candidates, then re-ranks to top 3 for the final answer

---

## Tech Stack

### Frameworks and Libraries

| Library | Purpose |
|---|---|
| [LlamaIndex](https://www.llamaindex.ai/) | RAG orchestration framework |
| [Transformers](https://huggingface.co/docs/transformers) | LLM loading and inference |
| [Sentence Transformers](https://www.sbert.net/) | Embedding and cross-encoder reranking |
| [Accelerate](https://huggingface.co/docs/accelerate) | Efficient model loading |
| [Qdrant Client](https://qdrant.tech/) | Vector store for similarity search |
| [PyTorch](https://pytorch.org/) | Deep learning backend |

### Models

| Model | Role |
|---|---|
| `BAAI/bge-small-en-v1.5` | Document and query embedding |
| `Qwen/Qwen2.5-1.5B-Instruct` | LLM for answer generation |
| `cross-encoder/ms-marco-MiniLM-L-2-v2` | Cross-encoder for reranking |

### Vector Store

| Store | Mode |
|---|---|
| Qdrant | In-memory (`:memory:`) |

---

## GitHub Code Repository

🔗 **Repository URL:** [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

---

## How to Use App

### Prerequisites

- **Python 3.13** (recommended)
- **Git**

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents/RAG-ReRanking-UsingLlamaIndexReranking-FactualAccuracy
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\Activate.ps1
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install llama-index-embeddings-huggingface llama-index-llms-huggingface
   ```

4. **Add your PDF documents** to the `Data/` directory. A sample `arxiv.pdf` is included.

### Running the App

```bash
python agent.py
```

The script will:
1. Load PDF documents from `Data/`
2. Generate embeddings and store them in an in-memory Qdrant collection
3. Run three sample queries with reranking and print the responses with elapsed times

> **Note:** First run will download the models (~3 GB). LLM inference on CPU may take several minutes per query.

---

## Project Structure

```
RAG-ReRanking-UsingLlamaIndexReranking-FactualAccuracy/
├── agent.py            # Main RAG pipeline script
├── requirements.txt    # Python dependencies
├── Data/
│   └── arxiv.pdf       # Sample PDF document for ingestion
└── README.md
```

---

## How It Works

1. **Document Loading** — `SimpleDirectoryReader` reads PDFs from `Data/`
2. **Embedding** — Documents are chunked (512 tokens) and embedded using `BAAI/bge-small-en-v1.5`
3. **Indexing** — Embeddings are stored in an in-memory Qdrant vector store
4. **Retrieval** — For each query, the top 10 most similar chunks are retrieved
5. **ReRanking** — A cross-encoder (`ms-marco-MiniLM-L-2-v2`) re-ranks the 10 candidates and selects the top 3
6. **Generation** — The LLM generates an answer grounded in the top 3 reranked chunks

---

## License

This project is open source. See the repository for license details.
