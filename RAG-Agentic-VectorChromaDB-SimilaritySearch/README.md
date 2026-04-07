# Agentic RAG System — Vector ChromaDB Similarity Search

An agentic RAG (Retrieval-Augmented Generation) system powered by DeepSeek R1 and HuggingFace Smolagents. It combines a reasoning LLM with efficient document retrieval via ChromaDB to deliver context-aware, accurate answers from your PDF documents.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
    - [Using HuggingFace (Cloud API)](#using-huggingface-cloud-api)
    - [Using Ollama (Local Inference)](#using-ollama-local-inference)
  - [Setting Up Ollama Models](#setting-up-ollama-models)
  - [Running the App](#running-the-app)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Notes](#notes)

---

## Features

- ✅ Agentic RAG with dual-LLM architecture — a reasoning model and a tool-calling model
- ✅ PDF document ingestion with automatic chunking and embedding
- ✅ Vector similarity search using ChromaDB
- ✅ Embeddings via `sentence-transformers/all-mpnet-base-v2`
- ✅ Supports both HuggingFace Inference API (cloud) and Ollama (local)
- ✅ Built with HuggingFace Smolagents framework
- ✅ Custom Ollama model configurations with extended context windows
- ✅ Gradio web interface for interactive Q&A

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | [HuggingFace Smolagents](https://huggingface.co/docs/smolagents) |
| Reasoning LLM | DeepSeek R1 (distilled / local) |
| Tool-Calling LLM | Qwen 2.5 / Llama 3.3 |
| Embeddings | `sentence-transformers/all-mpnet-base-v2` |
| Vector Database | [ChromaDB](https://www.trychroma.com/) |
| Document Loader | LangChain (PyPDFLoader) |
| Text Splitter | LangChain RecursiveCharacterTextSplitter |
| Local Inference | [Ollama](https://ollama.ai) |
| Cloud Inference | [HuggingFace Inference API](https://huggingface.co/inference-api) |
| Web UI | Gradio |
| Language | Python |

---

## GitHub Code Repository

🔗 [https://github.com/tauseefiqbal/agentic-workflows-and-agents](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

---

## How to Use App

### Prerequisites

- Python 3.10+
- (Optional) [Ollama](https://ollama.ai) installed for local inference
- (Optional) [HuggingFace API token](https://huggingface.co/settings/tokens) for cloud inference

### Installation

1. Clone the repository:

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
cd agentic-workflows-and-agents
```

2. Create and activate a virtual environment:

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

#### Using HuggingFace (Cloud API)

```env
USE_HUGGINGFACE=yes
HUGGINGFACE_API_TOKEN=your_token_here
REASONING_MODEL_ID=deepseek-ai/DeepSeek-R1-Distill-Qwen-32B
TOOL_MODEL_ID=meta-llama/Llama-3.3-70B-Instruct
```

#### Using Ollama (Local Inference)

```env
USE_HUGGINGFACE=no
HUGGINGFACE_API_TOKEN=
REASONING_MODEL_ID=deepseek-r1:7b-8k
TOOL_MODEL_ID=qwen2.5:14b-instruct-8k
```

### Setting Up Ollama Models

1. Install Ollama from [ollama.ai](https://ollama.ai).

2. Pull the base models:

```bash
ollama pull deepseek-r1:7b
ollama pull qwen2.5:14b-instruct-q4_K_M
```

3. Create custom models with extended context windows:

```bash
# Windows / Linux
ollama create deepseek-r1:7b-8k -f ollama_models/Deepseek-r1-7b-8k
ollama create qwen2.5:14b-instruct-8k -f ollama_models/Qwen-14b-Instruct-8k

# macOS (use --from)
ollama create deepseek-r1:7b-8k --from ollama_models/Deepseek-r1-7b-8k
ollama create qwen2.5:14b-instruct-8k --from ollama_models/Qwen-14b-Instruct-8k
```

You can experiment with other models or context sizes by modifying files in the `ollama_models/` directory.

### Running the App

1. Place your PDF documents in the `data/` directory.

2. Ingest the PDFs to build the vector database:

```bash
python ingest_pdfs.py
```

3. Run the RAG agent:

```bash
python r1_smolagent_rag.py
```

---

## Project Structure

```
├── r1_smolagent_rag.py    # Main RAG agent with Gradio UI
├── ingest_pdfs.py         # PDF ingestion and vector store creation
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── chroma_db/             # Persisted ChromaDB vector store
├── data/                  # PDF documents directory
└── ollama_models/         # Custom Ollama model configurations
    ├── Deepseek-r1-7b-8k
    ├── Qwen-14b-Instruct-8k
    └── Qwen-7b-Instruct-8k
```

---

## How It Works

1. **Document Ingestion** (`ingest_pdfs.py`)
   - Loads PDFs from the `data/` directory
   - Splits documents into chunks of 1000 characters with 200 character overlap
   - Creates embeddings using `sentence-transformers/all-mpnet-base-v2`
   - Stores vectors in a ChromaDB database

2. **RAG Agent** (`r1_smolagent_rag.py`)
   - Uses two LLMs: a reasoning model for answering and a tool-calling model for orchestration
   - Retrieves the top 3 relevant document chunks via similarity search
   - Generates responses grounded in the retrieved context

---

## Notes

- The vector store is persisted in the `chroma_db/` directory
- Default chunk size is 1000 characters with 200 character overlap
- The system retrieves a maximum of 3 relevant chunks per query
- Ollama models run locally — no data leaves your machine
- HuggingFace API offers broader model selection but requires an internet connection
