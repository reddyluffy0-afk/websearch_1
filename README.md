
# Local News, QA, PDF, Voice & Deep Research App

## Features
- **News**: Fetches latest Indian politics headlines using Tavily API (with caching and fallback).
- **Ask**: Agentic Q&A pipeline (search, LLM answer, citations) using Tavily and Gemini APIs.
- **PDF Translate & Summarize**: Upload a PDF, extract text, translate (Gemini), and summarize (Gemini).
- **Voice Input & Output**: Upload WAV for transcription (Gemini Speech-to-Text) and text-to-speech playback (Gemini TTS).
- **Deep Research**: Multi-step research pipeline (search, summarize, refine, aggregate bullets/citations).

## Quickstart (Run Locally)

1. **Clone the repo and enter the directory:**
   ```bash
   git clone <your-repo-url>
   cd websearch_1
   ```

2. **Create and activate a Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pdfminer.six
   ```

4. **Set your API keys:**
   - Edit `backend/main.py` and set `TAVILY_API_KEY` and `GEMINI_API_KEY` to your free-tier keys.

5. **Run the backend (FastAPI):**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

6. **Run the frontend (Streamlit):**
   ```bash
   streamlit run frontend/app.py --server.port 8501
   ```

7. **Open [http://localhost:8501](http://localhost:8501) in your browser.**

## Usage
- **News**: View latest headlines.
- **Ask**: Enter a question about Indian politics, get LLM answer and citations.
- **PDF**: Upload a PDF, select target language, get translation and summary.
- **Voice**: Upload WAV for transcription, or enter text for TTS playback (sidebar).
- **Deep Research**: Enter a research query, get multi-step summary, bullets, and citations.

## Architecture
- **Streamlit frontend** (port 8501): Mode selector, news/QA/PDF/Research, voice controls, file uploader, result panes.
- **FastAPI backend** (port 8000): Endpoints for /news, /ask, /pdf, /research, /transcribe, /tts. In-process pipelines, Tavily & Gemini HTTP clients, local PDF extraction.

## Notes
- All dependencies run locally, no Docker or cloud required.
- All API keys must be free-tier (no paid Whisper, Gemini, or Tavily required).
- For best results, use short PDFs and clear voice recordings (WAV, 16-bit PCM).
