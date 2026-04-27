# Multimodal Reasoning Agent

A Streamlit app that lets you ask questions about **images, videos, PDFs, and YouTube videos** using Google's Gemini models via the [agno](https://github.com/agno-agi/agno) agent framework.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
  - [Languages & Runtime](#languages--runtime)
  - [Core Libraries](#core-libraries)
  - [Models](#models)
- [GitHub Code Repository](#github-code-repository)
- [How to Use App](#how-to-use-app)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Get a Gemini API Key](#3-get-a-gemini-api-key)
  - [4. Run the App](#4-run-the-app)
  - [5. Analyze Media](#5-analyze-media)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- ✅ **Image analysis** — upload `.jpg`, `.jpeg`, or `.png` and ask questions about its contents
- ✅ **Video analysis** — upload `.mp4`, `.mov`, or `.avi` and get an AI-generated breakdown with web research
- ✅ **PDF summarization** — upload a `.pdf` and the agent extracts text (up to 80,000 chars) for Q&A
- ✅ **YouTube video analysis** — paste any YouTube URL and the agent fetches the transcript for reasoning
- ✅ **Unified media input** — single section for both file uploads and YouTube URLs
- ✅ **Last-input-wins** — whichever source you provide most recently is the one analyzed
- ✅ **Inline preview** — uploaded images, videos, PDFs, and YouTube thumbnails are previewed before analysis
- ✅ **Powered by Gemini 2.5 Flash** — fast multimodal reasoning that works on the free tier

---

## Tech Stack

### Languages & Runtime

- **Python 3.10+** (tested on 3.13)
- **Streamlit 1.40.2** for the web UI

### Core Libraries

- **[agno](https://github.com/agno-agi/agno)** `>=2.2.10` — agent orchestration framework
- **google-generativeai** `0.8.3` — Gemini SDK + File API auth
- **PyMuPDF (fitz)** `>=1.24.0` — PDF text extraction
- **youtube-transcript-api** `>=1.0.0` — YouTube transcript fetching

### Models

- **`gemini-2.5-flash`** — multimodal reasoning model (free-tier friendly)

---

## GitHub Code Repository

🔗 **https://github.com/tauseefiqbal/agentic-workflows-and-agents.git**

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
```

---

## How to Use App

### 1. Clone the Repository

```bash
git clone https://github.com/tauseefiqbal/agentic-workflows-and-agents.git
cd agentic-workflows-and-agents
```

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Get a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key — you'll paste it into the app sidebar

### 4. Run the App

On Windows (PowerShell):

```powershell
python -m streamlit run multimodal_reasoning_agent.py
```

On macOS / Linux:

```bash
streamlit run multimodal_reasoning_agent.py
```

The app opens at `http://localhost:8501`.

### 5. Analyze Media

1. Paste your **Gemini API Key** in the sidebar.
2. Either:
   - Paste a **YouTube URL** and click **Submit URL**, **or**
   - Click **Browse files** to upload an image, video, or PDF.
3. Type your question in the text area.
4. Click **Analyze** — the agent will respond using the most recently provided source.

---

## Project Structure

```
.
├── multimodal_reasoning_agent.py   # Main Streamlit app
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── README-old.md                   # Legacy README
```

---

## Requirements

```
agno>=2.2.10
google-generativeai==0.8.3
streamlit==1.40.2
PyMuPDF>=1.24.0
youtube-transcript-api>=1.0.0
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `streamlit is not recognized` (Windows) | Use `python -m streamlit run ...` instead. |
| `403 PERMISSION_DENIED` on video upload | Make sure your Gemini API key is pasted in the sidebar — the app calls `genai.configure(...)` on every run. |
| `429 RESOURCE_EXHAUSTED` on `gemini-2.5-pro` | The free tier has 0 quota for Pro. The app uses `gemini-2.5-flash` by default. For Pro, enable [billing](https://aistudio.google.com/app/billing). |
| `503 UNAVAILABLE` | Transient model overload — wait a moment and retry. |
| YouTube transcript error | The video must have captions enabled (auto or manual). |

---

## License

MIT — see repository for details.
