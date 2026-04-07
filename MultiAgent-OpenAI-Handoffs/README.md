# MultiAgent OpenAI Handoffs

A multi-agent system built with the OpenAI Agents SDK that demonstrates agent-to-agent handoffs. A main assistant agent intelligently delegates weather-related queries to a specialized weather agent using the handoff pattern.

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
- [License](#license)

---

## Features

- ✅ Multi-agent architecture with automatic handoffs between agents
- ✅ Main assistant agent that routes queries to specialized agents
- ✅ Dedicated weather agent with custom tool integration
- ✅ Seamless agent-to-agent delegation using OpenAI Agents SDK
- ✅ Function tool support via `@function_tool` decorator
- ✅ Synchronous execution with `Runner.run_sync`
- ✅ Environment variable management with `.env` support
- ✅ Extensible design — easily add more specialized agents and tools

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **OpenAI Agents SDK** (`openai-agents`) | Multi-agent framework with handoffs and tool support |
| **OpenAI API** | LLM backend powering agent responses |
| **python-dotenv** | Environment variable management |

---

## GitHub Code Repository

🔗 [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

---

## How to Use App

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the project root with your OpenAI API key:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### Running the App

```bash
python agent.py
```

The app will ask the assistant agent about the weather in Paris. The assistant detects it is a weather question and hands off to the `WeatherAgent`, which uses the `get_weather` tool to respond.

---

## Project Structure

```
MultiAgent-OpenAI-Handoffs/
├── agent.py            # Main application with agent definitions and execution
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not committed)
├── .env.example        # Example environment file
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## How It Works

1. **AssistantAgent** receives the user query.
2. If the query is weather-related, it **hands off** to **WeatherAgent**.
3. **WeatherAgent** calls the `get_weather` function tool to fetch weather data.
4. The result is returned to the user.

---

## License

This project is open source and available under the [MIT License](LICENSE).
