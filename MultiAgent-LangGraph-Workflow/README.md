# MultiAgent LangGraph Workflow

A multi-agent text processing pipeline built with LangGraph and LangChain, powered by Ollama (Llama 3.2). The workflow orchestrates four specialized AI agents that sequentially classify, extract entities, summarize, and analyze sentiment from any given text.

---

## Table of Contents

- [MultiAgent LangGraph Workflow](#multiagent-langgraph-workflow)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [GitHub Code Repository](#github-code-repository)
  - [How to Use App](#how-to-use-app)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running the App](#running-the-app)
  - [Workflow Architecture](#workflow-architecture)
    - [Agent Nodes](#agent-nodes)
    - [Pipeline Flow](#pipeline-flow)
  - [Sample Output](#sample-output)
  - [Project Structure](#project-structure)
  - [License](#license)

---

## Features

- ✅ **Text Classification** — Automatically classifies input text into News, Blog, Research, or Other categories
- ✅ **Named Entity Recognition** — Extracts Person, Organization, and Location entities from text
- ✅ **Text Summarization** — Generates concise one-sentence summaries of input text
- ✅ **Sentiment Analysis** — Analyzes text sentiment as Positive, Negative, or Neutral with descriptions
- ✅ **Structured Output** — Uses Pydantic models for validated, type-safe LLM responses
- ✅ **Multi-Agent Pipeline** — Chains multiple agents into a sequential LangGraph workflow
- ✅ **Local LLM Support** — Runs entirely on a local Ollama instance with Llama 3.2 (no API keys needed)

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **LangGraph** | Multi-agent workflow orchestration and state management |
| **LangChain** | LLM prompt templates, message schemas, and chain utilities |
| **LangChain-Ollama** | Integration with local Ollama models |
| **Ollama (Llama 3.2)** | Local large language model for inference |
| **Pydantic** | Structured output validation and data modeling |

---

## GitHub Code Repository

🔗 **Repository URL:** [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

1. **Python 3.10+** installed on your system
2. **Ollama** installed and running locally — download from [ollama.com](https://ollama.com)
3. Pull the required model:

```bash
ollama pull llama3.2:latest
```

4. Ensure Ollama is running:

```bash
ollama serve
```

### Installation

1. Clone the repository:

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
cd agentic-workflows-and-agents
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the App

```bash
python agent.py
```

---

## Workflow Architecture

### Agent Nodes

| Node | Description |
|---|---|
| `classification_node` | Classifies text into News, Blog, Research, or Other |
| `entity_extraction` | Extracts Person, Organization, and Location entities |
| `summarization` | Produces a one-sentence summary |
| `sentiment_analysis` | Determines Positive, Negative, or Neutral sentiment |

### Pipeline Flow

```
classification_node → entity_extraction → summarization → sentiment_analysis → END
```

Each node processes the shared state and passes its output to the next node in the pipeline.

---

## Sample Output

```
===== Classification =====
News

===== Entities =====
  Person: ['Emma Johnson', 'Dr. Carlos Mendes']
  Organization: ['GlobalTech Innovations', 'EcoFuture Solutions', 'Stanford University']
  Location: ['San Francisco', 'Berlin', 'São Paulo']

===== Summary =====
Emma Johnson met with executives at GlobalTech Innovations and spoke at a tech summit hosted by Stanford University.

===== Sentiment =====
  Sentiment: Neutral
  Description: The text is informational and does not convey strong positive or negative emotions.
```

---

## Project Structure

```
MultiAgent-LangGraph-Workflow/
├── agent.py            # Main application — defines agents, workflow, and runs the pipeline
├── requirements.txt    # Python package dependencies
└── README.md           # Project documentation
```

---

## License

This project is open source and available for educational and personal use.
