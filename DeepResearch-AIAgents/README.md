# 📘 Deep Research Agent with OpenAI Agents SDK and Firecrawl

A powerful research assistant that leverages OpenAI's Agents SDK and Firecrawl to perform comprehensive web research on any topic, synthesize findings, and generate enhanced reports — all through an interactive Streamlit UI.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the App](#running-the-app)
  - [Using the App](#using-the-app)
- [How It Works](#how-it-works)
  - [Research Agent](#research-agent)
  - [Elaboration Agent](#elaboration-agent)
- [Example Research Topics](#example-research-topics)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- ✅ **Deep Web Research** — Automatically searches the web, extracts content from multiple sources, and synthesizes findings
- ✅ **Multi-Agent Pipeline** — Uses a Research Agent to gather data and an Elaboration Agent to enhance the report with deeper insights
- ✅ **Interactive Streamlit UI** — Clean, wide-layout interface with sidebar API key configuration
- ✅ **Real-Time Progress** — Spinners and status updates as research and analysis proceed
- ✅ **Downloadable Reports** — Export enhanced research findings as markdown files
- ✅ **Source Citations** — All reports include proper citations with source URLs
- ✅ **Configurable Research Parameters** — Adjustable depth, time limits, and number of URLs to analyze

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.8+** | Core programming language |
| **OpenAI Agents SDK** | Agent orchestration, tool integration, and LLM-powered research/elaboration |
| **Firecrawl** | Web search and content scraping |
| **Streamlit** | Interactive web UI |

---

## GitHub Code Repository

```
https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### Prerequisites

- Python 3.8 or higher
- An [OpenAI API key](https://platform.openai.com/account/api-keys)
- A [Firecrawl API key](https://www.firecrawl.dev/)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
   cd agentic-workflows-and-agents
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Create a `.env` file at the project root with your API keys:

   ```dotenv
   OPENAI_API_KEY=your-openai-api-key
   FIRECRAWL_API_KEY=your-firecrawl-api-key
   ```

### Running the App

```bash
streamlit run deep_research_openai.py
```

Or, if `streamlit` is not on your PATH:

```bash
python -m streamlit run deep_research_openai.py
```

The app will open in your browser at `http://localhost:8501`.

### Using the App

1. Enter your **OpenAI API Key** and **Firecrawl API Key** in the sidebar
2. Type your research topic in the main input field
3. Click **Start Research**
4. Wait for the research and elaboration phases to complete
5. View the initial report (expandable) and the enhanced final report
6. Click **Download Report** to save the result as a markdown file

---

## How It Works

The application uses a two-agent pipeline powered by the OpenAI Agents SDK:

### Research Agent

- Takes the user's topic and invokes the `deep_research` tool
- Uses Firecrawl to **search** the web for relevant URLs and **scrape** content from top sources
- Organizes raw findings into a structured initial report with citations

### Elaboration Agent

- Receives the initial report and enhances it with:
  - Detailed explanations of complex concepts
  - Real-world examples and case studies
  - Latest trends and future predictions
  - Practical implications for stakeholders
- Maintains academic rigor and factual accuracy

---

## Example Research Topics

- "Latest developments in quantum computing"
- "Impact of climate change on marine ecosystems"
- "Advancements in renewable energy storage"
- "Ethical considerations in artificial intelligence"
- "Emerging trends in remote work technologies"

---

## Project Structure

```
├── deep_research_openai.py   # Main application
├── requirements.txt           # Python dependencies
├── .env                       # API keys (not committed)
├── README.md                  # This file
└── README-old.md              # Previous README
```

---

## License

This project is open source and available under the [MIT License](LICENSE).
