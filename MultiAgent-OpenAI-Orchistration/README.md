# Multi-Agent OpenAI Orchestration

A multi-agent orchestration system built with the OpenAI Agents SDK that coordinates specialized AI agents to collaboratively plan a time-travel trip to Victorian London to meet Charles Dickens.

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
- [Architecture](#architecture)
  - [Agent Roles](#agent-roles)
  - [Orchestration Flow](#orchestration-flow)
- [License](#license)

---

## Features

- ✅ Multi-agent orchestration using the OpenAI Agents SDK
- ✅ Specialized agents with distinct roles (History, Attire, Schedule)
- ✅ Central planner agent that delegates tasks to specialist agents
- ✅ Agent-as-tool pattern for seamless inter-agent communication
- ✅ Built-in tracing support for observability and debugging
- ✅ Async execution for efficient agent coordination
- ✅ Environment-based API key management via `.env` file
- ✅ Structured logging for monitoring orchestration flow

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.13** | Core programming language |
| **OpenAI Agents SDK** (`openai-agents`) | Multi-agent orchestration framework |
| **OpenAI API** (`openai`) | LLM provider (GPT-4) |
| **python-dotenv** | Environment variable management |
| **asyncio** | Asynchronous execution |

---

## GitHub Code Repository

🔗 [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

---

## How to Use App

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key with access to GPT-4

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install python-dotenv
   ```

### Configuration

Create a `.env` file in the project root with your API keys:

```env
OPENAI_API_KEY=your-openai-api-key-here
```

### Running the App

```bash
python agent.py
```

The orchestration will start and output a detailed time-travel plan to Victorian London.

---

## Project Structure

```
MultiAgent-OpenAI-Orchistration/
├── agent.py           # Main orchestration script with all agent definitions
├── requirements.txt   # Python dependencies
├── .env               # Environment variables (API keys)
└── README.md          # Project documentation
```

---

## Architecture

### Agent Roles

| Agent | Role |
|---|---|
| **TimeTravelPlanner** | Central planner that breaks down the task and delegates to specialist agents |
| **HistoryAgent** | Provides historical facts about Charles Dickens and Victorian London |
| **AttireAgent** | Advises on Victorian-era clothing, accessories, and social etiquette |
| **ScheduleAgent** | Determines ideal dates, locations, and events for meeting Dickens |

### Orchestration Flow

```
User Request
     │
     ▼
TimeTravelPlanner (Orchestrator)
     │
     ├──► HistoryAgent   → Historical research & context
     ├──► AttireAgent     → Victorian clothing & etiquette advice
     └──► ScheduleAgent   → Date, location & event planning
     │
     ▼
Compiled Final Plan
```

The `TimeTravelPlanner` uses the agent-as-tool pattern, where each specialist agent is registered as a callable tool. The planner autonomously decides which agents to invoke based on the user's request.

---

## License

This project is open source. See the repository for license details.
