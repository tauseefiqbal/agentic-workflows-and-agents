# RAG Query Expansion

A collection of query expansion techniques for Retrieval-Augmented Generation (RAG) systems, powered by OpenAI and LangChain.

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
- [Query Expansion Techniques](#query-expansion-techniques)
  - [Keyword-Based Query Expansion](#1-keyword-based-query-expansion)
  - [BM25 Keyword Extraction](#2-bm25-keyword-extraction)
  - [Context-Aware Query Expansion](#3-context-aware-query-expansion)
  - [HyDE Query Expansion](#4-hyde-query-expansion)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- ✅ **LLM-Powered Keyword Extraction** — Automatically extracts the most relevant keywords from user queries using GPT-4o-mini
- ✅ **Keyword-Based Query Expansion** — Generates natural-sounding query variations incorporating extracted keywords via LangChain LCEL pipelines
- ✅ **BM25 Keyword Extraction** — Extracts keywords from a corpus using the BM25Okapi ranking algorithm for statistical relevance
- ✅ **Context-Aware Query Expansion** — Leverages conversation history to generate contextually relevant query variations using the OpenAI API
- ✅ **HyDE (Hypothetical Document Embeddings) Expansion** — Generates a hypothetical answer first, then uses it as context to produce richer query expansions
- ✅ **Modern LangChain LCEL Pipelines** — Uses LangChain Expression Language (prompt | llm | parser) for clean, composable chains
- ✅ **Configurable Number of Variations** — Control how many expanded queries are generated per input
- ✅ **Environment-Based API Key Management** — Securely loads API keys from a `.env` file using `python-dotenv`

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.13** | Core programming language |
| **OpenAI GPT-4o-mini** | LLM for keyword extraction, query expansion, and hypothetical answer generation |
| **LangChain** | Framework for building LLM chains and pipelines |
| **LangChain LCEL** | Expression Language for composable prompt → LLM → parser chains |
| **OpenAI Python SDK** | Direct API access for context-aware query expansion |
| **BM25Okapi (rank-bm25)** | Statistical keyword extraction from a document corpus |
| **NLTK** | Natural language processing (stopword filtering) |
| **python-dotenv** | Environment variable management |

---

## GitHub Code Repository

🔗 **Repository URL:** [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key ([Get one here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key))

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1     # Windows PowerShell
   # or
   source .venv/bin/activate      # macOS/Linux
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the project root with your OpenAI API key:

```env
OPENAI_API_KEY="your-openai-api-key-here"
```

### Running the App

```bash
python agent.py
```

The script will execute all three query expansion techniques sequentially and print the results to the console.

---

## Query Expansion Techniques

### 1. Keyword-Based Query Expansion

Uses a two-step LangChain LCEL pipeline:
- **Step 1:** Extracts up to 3 relevant keywords from the input query
- **Step 2:** Generates N natural-sounding query variations using the extracted keywords

### 2. BM25 Keyword Extraction

Uses the BM25Okapi algorithm to statistically extract relevant keywords from a document corpus. Useful for non-LLM-based keyword extraction in retrieval pipelines.

### 3. Context-Aware Query Expansion

Uses the OpenAI API directly to generate query variations that are informed by previous conversation history. This ensures expanded queries remain contextually relevant in multi-turn interactions.

### 4. HyDE Query Expansion

Implements Hypothetical Document Embeddings (HyDE):
- **Step 1:** Generates a detailed hypothetical answer to the query
- **Step 2:** Uses the hypothetical answer as context to produce richer, more informed query variations

---

## Project Structure

```
RAG-QueriesExpansion/
├── agent.py             # Main script with all query expansion techniques
├── requirements.txt     # Python dependencies
├── .env                 # API key configuration (not committed)
└── README.md            # Project documentation
```

---

## License

This project is open source and available for educational and research purposes.
