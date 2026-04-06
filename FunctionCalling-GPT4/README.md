# Function Calling with GPT-4 — Agentic Workflow

An AI agent that demonstrates **GPT-4 Function Calling** — the model autonomously decides which tools to invoke, executes them, and composes a final answer from the results.

---

## Table of Contents

- [Function Calling with GPT-4 — Agentic Workflow](#function-calling-with-gpt-4--agentic-workflow)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [GitHub Code Repository](#github-code-repository)
  - [How to Use App](#how-to-use-app)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Running the Agent](#running-the-agent)
  - [Project Structure](#project-structure)
  - [How It Works](#how-it-works)
  - [Available Tools](#available-tools)
  - [License](#license)

---

## Features

- ✅ GPT-4 function calling with the modern OpenAI SDK (v1.0+)
- ✅ Autonomous tool selection — the model decides which functions to call
- ✅ Supports multiple sequential tool calls in a single conversation
- ✅ Agentic loop that keeps calling tools until a final answer is produced
- ✅ Clean tool registration with a name-to-function mapping
- ✅ Handles parallel tool calls returned by the model
- ✅ Environment variable management via `.env` file

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.13+** | Programming language |
| **OpenAI SDK (v2.x)** | GPT-4 API client with function calling |
| **GPT-4** | Large Language Model for reasoning and tool selection |
| **python-dotenv** | Load environment variables from `.env` file |

---

## GitHub Code Repository

🔗 **Repository URL:** [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

- Python 3.10 or higher installed
- An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents/FunctionCalling-GPT4
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the project root and add your OpenAI API key:

```
OPENAI_API_KEY=your-api-key-here
```

### Running the Agent

```bash
python agent.py
```

**Expected output:**

```
Calling get_population({'country': 'France'})
Calling get_wikipedia_summary({'topic': 'France'})
The population of France is approximately 67.5 million...
```

The agent will:
1. Send your query to GPT-4
2. GPT-4 decides which tool(s) to call
3. The agent executes the tool(s) and feeds results back
4. GPT-4 composes a final natural language answer

---

## Project Structure

```
FunctionCalling-GPT4/
├── agent.py                 # Main working agent with GPT-4 function calling
├── FunctionToCall.json      # Function schema definitions
├── requirements.txt         # Python dependencies
├── .env                     # API key configuration (not committed)
└── README.md                # This file
```

---

## How It Works

```
User Query
    │
    ▼
┌──────────────┐
│   GPT-4      │ ◄── Decides which tool(s) to call
└──────┬───────┘
       │ tool_call(s)
       ▼
┌──────────────┐
│ Execute Tool │ ◄── Runs the Python function locally
└──────┬───────┘
       │ result
       ▼
┌──────────────┐
│   GPT-4      │ ◄── Receives result, calls more tools or gives final answer
└──────┬───────┘
       │
       ▼
  Final Answer
```

The agent runs in a **loop** — GPT-4 can call as many tools as needed before producing a final text response.

---

## Available Tools

| Tool | Description | Parameters |
|---|---|---|
| `get_population` | Retrieve the population of a specified country | `country` (string) |
| `get_wikipedia_summary` | Fetch a short Wikipedia summary for a given topic | `topic` (string) |

---

## License

This project is open source and available for educational purposes.
