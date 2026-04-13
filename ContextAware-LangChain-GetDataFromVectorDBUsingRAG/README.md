# ContextAware LangChain — Get Data From Vector DB Using RAG

A context-aware conversational AI agent built with LangChain that retrieves relevant answers from a FAISS vector database using Retrieval-Augmented Generation (RAG). The agent maintains conversation history across multiple queries, enabling follow-up questions and contextual responses.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Run the App](#run-the-app)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [License](#license)

---

## Features

- ✅ Retrieval-Augmented Generation (RAG) for accurate, context-grounded answers
- ✅ FAISS vector database for fast similarity search over document embeddings
- ✅ Conversational memory that retains chat history across multiple queries
- ✅ OpenAI GPT-3.5 Turbo as the underlying LLM for response generation
- ✅ Document chunking with configurable chunk size and overlap
- ✅ Environment variable support via `.env` for secure API key management
- ✅ Lightweight single-file agent — easy to understand and extend

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.13** | Runtime |
| **LangChain** | Orchestration framework for LLM chains and retrieval |
| **LangChain OpenAI** | OpenAI LLM and embedding integrations |
| **FAISS (faiss-cpu)** | Vector similarity search engine |
| **OpenAI GPT-3.5 Turbo** | Large Language Model for generating responses |
| **OpenAI Embeddings** | Text-to-vector embeddings for document indexing |
| **python-dotenv** | Loads environment variables from `.env` file |
| **tiktoken** | Tokenizer for OpenAI models |

---

## GitHub Code Repository

🔗 [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

---

## How to Use App

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key ([get one here](https://platform.openai.com/account/api-keys))

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents/ContextAware-LangChain-GetDataFromVectorDBUsingRAG
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your OpenAI API key:

   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

### Run the App

```bash
python agent.py
```

**Sample Output:**

```
To reset your API key, you can go to settings > security.
Yes, our platform works with Slack.
A 401 error typically indicates invalid API credentials.
A 401 error typically indicates that the request was unauthorized, often due to invalid API credentials.
```

---

## Project Structure

```
ContextAware-LangChain-GetDataFromVectorDBUsingRAG/
├── agent.py            # Main agent script with RAG pipeline
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
├── .env                # Your API keys (git-ignored)
└── .gitignore          # Git ignore rules
```

---

## How It Works

1. **Document Loading** — Sample documents are loaded as LangChain `Document` objects.
2. **Text Splitting** — Documents are split into chunks using `CharacterTextSplitter` (chunk size: 200, overlap: 20).
3. **Embedding & Indexing** — Chunks are embedded via OpenAI Embeddings and stored in a FAISS vector index.
4. **Conversational Retrieval** — User queries are matched against the FAISS index; the most relevant chunks are passed to GPT-3.5 Turbo along with conversation history to generate context-aware answers.
5. **Memory** — `ConversationBufferMemory` retains the full chat history, allowing the agent to handle follow-up questions.

---

## License

This project is open source and available under the [MIT License](LICENSE).
