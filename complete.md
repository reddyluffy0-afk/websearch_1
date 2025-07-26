News Fetch

On‑demand pull of latest Indian‑politics headlines via Tavily API.

Display top 5 items with title, source link, and timestamp.

Agentic QA

Natural‑language questions routed through a LangGraph pipeline that:

Searches via Tavily

Calls Gemini LLM to synthesize and answer

Returns answer with basic citations.

PDF Translate & Summarize

Upload a PDF file.

Choose target language (e.g., Hindi or English).

Extract text locally, translate via Gemini, then summarize via Gemini.

Voice Input & Output

In‑browser microphone capture → backend transcription (Whisper or Gemini speech).

Text answer → browser TTS for playback.

Deep Research Mode

Three‑step iterative pipeline:

Search → 2. Summarize → 3. Refine query

Aggregates bullet points with inline citations.

Streamlit Frontend

Single‑page UI with modes: News, Ask, PDF, Deep Research.

Voice controls, file uploader, and result panes all on localhost.

Simplified Architecture (All Local)
Streamlit app (port 8501)
• Mode selector, displays news/Q&A/PDF/Research
• Voice recorder/player

FastAPI backend (port 8000)
• Endpoints: /news, /ask, /pdf, /research, plus /transcribe & /tts
• In‑process LangGraph runner
• Tavily & Gemini HTTP clients
• Local PDF extraction and (optional) Whisper model

All dependencies live in one Python virtual environment; run both services locally—no Docker, no cloud.

Module Breakdown
Component	Responsibility	Key Tools
News Fetch	Call Tavily & format headlines	Tavily API, caching
Agent QA Pipeline	Orchestrate search → LLM → answer + citations	LangGraph, Gemini API
PDF Processor	Extract, translate & summarize text	pdfminer.six, Gemini API
Voice I/O	Capture/transcribe and TTS playback	Whisper (or Gemini speech), WebSpeech API
Deep Research Pipeline	Iterative search → refine → aggregate bullets	LangGraph
UI	Mode selection, result display, file & voice	Streamlit, streamlit‑webrtc

Six‑Week Local‑First Roadmap
Week	Goals
1	• Project scaffolding: venv, install deps
• Basic FastAPI & Streamlit stubs	
• Stub /news endpoint with dummy data	
• Local README with run instructions	
2	• Implement Tavily client & real /news
• Hook into Streamlit News view	
• Add simple caching & error handling	
3	• Build Gemini LLM client wrapper
• Define LangGraph “Ask” pipeline	
• Expose /ask and connect to Ask mode	
4	• Integrate PDF text extraction locally
• Define PDF translate + summarize pipeline	
• Expose /pdf and test end‑to‑end in Streamlit	
5	• Add local Whisper (or Gemini speech) transcription
• Build /transcribe & /tts endpoints	
• Wire voice record/playback in UI	
6	• Develop Deep Research pipeline & /research
• Polish UI/UX: loading states, error messages	
• Final testing	
• Update README with full “run locally” guide