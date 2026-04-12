# MultiAgent CrewAI Collaborative

A multi-agent AI system built with **CrewAI** that orchestrates collaborative agents to perform market analysis and generate go-to-market strategies using sequential task execution.

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
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
  - [Agents](#agents)
  - [Tasks](#tasks)
  - [Execution Flow](#execution-flow)
- [License](#license)

---

## Features

- ✅ Multi-agent collaboration using CrewAI framework
- ✅ Sequential task execution with context passing between agents
- ✅ Market Analyst agent with real-time web search capabilities
- ✅ Strategy Consultant agent for go-to-market planning
- ✅ Serper-powered web search tool integration
- ✅ OpenAI GPT-4o-mini as the underlying LLM
- ✅ Environment variable management via `.env` file
- ✅ Configurable product/topic input for flexible analysis

---

## Tech Stack

| Technology | Purpose |
|---|---|
| [Python](https://www.python.org/) | Programming language |
| [CrewAI](https://www.crewai.com/) | Multi-agent orchestration framework |
| [CrewAI Tools](https://github.com/crewAIInc/crewAI-tools) | Tool integrations for agents |
| [OpenAI GPT-4o-mini](https://platform.openai.com/) | Large Language Model |
| [Serper API](https://serper.dev/) | Google search API for web research |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable management |

---

## GitHub Code Repository

```
https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

Clone the repository:

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
cd agentic-workflows-and-agents
```

---

## How to Use App

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Serper API key](https://serper.dev/)

### Installation

1. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Install `python-dotenv` (included with CrewAI):

   ```bash
   pip install python-dotenv
   ```

### Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your API keys:

   ```env
   OPENAI_API_KEY=your-openai-api-key
   SERPER_API_KEY=your-serper-api-key
   ```

### Running the App

```bash
python agent.py
```

The crew will execute sequentially — the Market Analyst researches the product landscape, then the Strategy Consultant uses that analysis to generate a 3-month launch strategy.

---

## Project Structure

```
├── agent.py           # Main script with agents, tasks, and crew
├── requirements.txt   # Python dependencies
├── .env               # API keys (not committed)
├── .env.example       # Template for environment variables
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

---

## How It Works

### Agents

| Agent | Role | Tools |
|---|---|---|
| **Market Analyst** | Researches market size, competitors, and trends | Serper web search |
| **Strategy Consultant** | Develops go-to-market strategies from analysis | None (reasoning only) |

### Tasks

1. **Analyze Task** — Research current market size, competitors, and trends for the given product.
2. **Strategy Task** — Using the analysis, outline a 3-month launch strategy with KPIs.

### Execution Flow

```
Input (product) → Market Analyst (web search) → Strategy Consultant (strategy) → Output
```

The crew uses `Process.sequential`, meaning each task runs in order and passes its output as context to the next.

---

## License

This project is open source and available under the [MIT License](LICENSE).
