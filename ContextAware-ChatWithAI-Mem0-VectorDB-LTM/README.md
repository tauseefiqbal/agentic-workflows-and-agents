# ContextAware — Mem0 Memory + Vector DB Long-Term Memory Chat with AI

A context-aware AI chatbot that leverages **Mem0** for memory management and **Qdrant** as a vector database to deliver persistent, long-term memory conversations powered by **OpenAI GPT-4o-mini**.

---

## Table of Contents

- [ContextAware — Mem0 Memory + Vector DB Long-Term Memory Chat with AI](#contextaware--mem0-memory--vector-db-long-term-memory-chat-with-ai)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [GitHub Code Repository](#github-code-repository)
  - [How to Use App](#how-to-use-app)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Running the App](#running-the-app)
      - [CLI Mode (optional)](#cli-mode-optional)
  - [Graphical User Interface (GUI)](#graphical-user-interface-gui)
    - [Launching the GUI](#launching-the-gui)
    - [Using the Chat UI](#using-the-chat-ui)
    - [Sharing the GUI (optional)](#sharing-the-gui-optional)
    - [Stopping the GUI](#stopping-the-gui)
  - [Project Structure](#project-structure)
  - [How It Works](#how-it-works)
  - [License](#license)

---

## Features

- ✅ **Long-Term Memory** — Retains conversation context across sessions using Mem0 and Qdrant vector database
- ✅ **Context-Aware Responses** — Retrieves relevant past memories to generate informed, personalized answers
- ✅ **Streaming Output** — Real-time, token-by-token streamed AI responses for a smooth chat experience
- ✅ **Vector Similarity Search** — Finds the most relevant memories using embedding-based semantic search
- ✅ **On-Disk Vector Storage** — Persists memory data locally via Qdrant so conversations survive restarts
- ✅ **OpenAI GPT-4o-mini Integration** — Uses the latest cost-efficient OpenAI model for high-quality responses
- ✅ **Gradio Web UI** — Browser-based chat interface powered by `gr.ChatInterface` for an interactive experience
- ✅ **Optional CLI Mode** — Interactive terminal-based chat loop also available via `main()`
- ✅ **Automatic Memory Saving** — Every user–assistant exchange is automatically stored for future recall
- ✅ **Configurable & Extensible** — Easy to swap models, vector stores, or add new features
- ✅ **Environment Variable Management** — Secure API key handling via `.env` file

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **OpenAI API (GPT-4o-mini)** | LLM for generating AI responses |
| **Mem0** | Memory layer for storing and retrieving conversation memories |
| **Qdrant** | Vector database for embedding-based similarity search |
| **Gradio** | Web-based chat UI (`gr.ChatInterface`) |
| **dotenv** | Environment variable management |

---

## GitHub Code Repository

🔗 [https://github.com/tauseefiqbal/agentic-workflows-and-agents.git](https://github.com/tauseefiqbal/agentic-workflows-and-agents.git)

---

## How to Use App

### Prerequisites

- Python 3.10+
- An OpenAI API key

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your API keys:

   ```
   OPENAI_API_KEY=your-openai-api-key
   MEM0_API_KEY=your-mem0-api-key
   ```

### Running the App

Launch the Gradio web UI:

```bash
python agent.py
```

You will see output similar to:

```
* Running on local URL:  http://127.0.0.1:7860
```

Open the URL shown in your terminal in a browser. A chat window labeled **"Chat with AI"** will appear — type your message and press Enter to chat. Each exchange is automatically stored as long-term memory and reused as context in future turns.

> **Tip:** Relevant memories retrieved for each query are also printed to the terminal for visibility/debugging.

#### CLI Mode (optional)

The original terminal chat loop is still available via the `main()` function in `agent.py` if you prefer a CLI experience — call it directly instead of launching the Gradio interface.

---

## Graphical User Interface (GUI)

The app ships with a browser-based chat GUI built on **[Gradio](https://www.gradio.app/)** using `gr.ChatInterface`, giving you a clean, ChatGPT-style experience out of the box.

### Launching the GUI

From the project root, with your virtual environment activated:

```bash
python agent.py
```

Gradio prints a local URL such as:

```
* Running on local URL:  http://127.0.0.1:7860
```

Open it in any modern browser (Chrome, Edge, Firefox, Safari).

### Using the Chat UI

- **Title bar:** *Chat with AI*
- **Message box:** Type your question and press **Enter** (or click **Submit**).
- **Streaming responses:** Replies appear in the chat window; token-by-token streaming is also visible in the terminal.
- **Conversation history:** Previous turns in the current session are shown in the chat panel above the input box.
- **Long-term memory:** Each user–assistant exchange is automatically embedded and stored in Qdrant via Mem0, so the assistant remembers facts across sessions — even after restarting the app.
- **Memory debug view:** The retrieved relevant memories for every query are printed in the terminal where you launched `agent.py`, making it easy to see what context was injected.

### Sharing the GUI (optional)

To expose a temporary public link (useful for demos), edit the launch call in `agent.py`:

```python
gr.ChatInterface(fn=chat, title="Chat with AI").launch(share=True)
```

### Stopping the GUI

Press `Ctrl + C` in the terminal where the app is running.

---

## Project Structure

```
├── agent.py            # Main application — chat loop, memory, and OpenAI integration
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
├── .gitignore          # Git ignore rules
└── qdrant_data/        # On-disk Qdrant vector database storage
```

---

## How It Works

1. **User sends a message** via the Gradio web UI (or optional CLI).
2. **Memory search** — Mem0 queries Qdrant for the top 3 most relevant past memories using vector similarity.
3. **Prompt construction** — Retrieved memories are injected into the system prompt as context.
4. **LLM response** — OpenAI GPT-4o-mini generates a streamed response informed by both the query and past memories.
5. **Memory storage** — The full user–assistant exchange is saved back into Mem0/Qdrant for future recall.

---

## License

This project is open source. See the repository for license details.
