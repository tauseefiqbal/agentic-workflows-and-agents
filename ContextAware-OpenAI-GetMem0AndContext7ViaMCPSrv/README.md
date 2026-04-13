# LongTermMemory — OpenAI Agents + Mem0 + Context7

An AI-powered conversational agent built with the **OpenAI Agents SDK** that combines **long-term memory** (via Mem0) and **real-time documentation retrieval** (via Context7) through MCP (Model Context Protocol) servers.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Agent](#running-the-agent)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- ✅ **Long-Term Memory** — Stores and recalls user-specific facts across sessions using Mem0
- ✅ **Real-Time Documentation Retrieval** — Fetches up-to-date library and framework docs via Context7
- ✅ **MCP Server Integration** — Connects to multiple MCP servers (Context7 + Mem0) as tool providers
- ✅ **OpenAI Agents SDK** — Uses the official OpenAI Agents framework with GPT-4
- ✅ **Interactive Chat Loop** — Conversational terminal interface with graceful shutdown
- ✅ **Async Architecture** — Fully asynchronous with proper context manager cleanup
- ✅ **Environment-Based Configuration** — API keys managed securely via `.env` file

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.13+** | Core language |
| **OpenAI Agents SDK** | Agent framework and runner |
| **OpenAI GPT-4** | Large language model |
| **Mem0 MCP Server** | Long-term memory storage and retrieval |
| **Context7 MCP Server** | Real-time documentation lookup |
| **MCP (Model Context Protocol)** | Standardized tool/server communication |
| **python-dotenv** | Environment variable management |
| **asyncio** | Asynchronous execution |

---

## GitHub Code Repository

🔗 **Repository URL:** [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
cd agentic-workflows-and-agents/LongTermMemory-OpenAI-Mem0+Context7
```

---

## How to Use App

### Prerequisites

- **Python 3.13+** installed
- **Node.js & npm** installed (required for `npx` to run MCP servers)
- **OpenAI API Key** — Get one from [platform.openai.com](https://platform.openai.com/)
- **Mem0 API Key** — Get one from [mem0.ai](https://mem0.ai/)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents/LongTermMemory-OpenAI-Mem0+Context7
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:

   ```env
   OPENAI_API_KEY=your-openai-api-key
   MEM0_API_KEY=your-mem0-api-key
   ```

### Running the Agent

```bash
python agent.py
```

The agent will:
1. Start the Context7 and Mem0 MCP servers
2. Display available tools from each server
3. Present an interactive chat prompt

```
Context7 tools: ['resolve-library-id', 'query-docs']
Mem0 tools: ['add_memory', 'search_memory', 'delete_memory']

Agent ready! Type your message (or 'quit' to exit).

You: _
```

Type your message and press Enter. Type `quit` or press `Ctrl+C` to exit.

---

## Project Structure

```
LongTermMemory-OpenAI-Mem0+Context7/
├── agent.py           # Main agent script
├── requirements.txt   # Python dependencies
├── .env.example       # Example environment variables
├── .env               # Your local API keys (not committed)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

---

## License

This project is open source. See the repository for license details.
