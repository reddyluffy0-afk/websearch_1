# LangGraph Deep Research pipeline: search → summarize → refine → aggregate bullets
def deep_research_pipeline(query):
    # Step 1: Initial search
    search_answer, results = search_tavily(query)
    context = "\n".join([r.get("content", "") for r in results])
    # Step 2: Summarize context
    summary = gemini_summarize(context)
    # Step 3: Refine query and search again (simulate refinement)
    refined_query = f"{query} (in more detail)"
    _, refined_results = search_tavily(refined_query)
    refined_context = "\n".join([r.get("content", "") for r in refined_results])
    refined_summary = gemini_summarize(refined_context)
    # Aggregate bullets with inline citations
    bullets = []
    for r in (results + refined_results):
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")
        if content:
            bullets.append(f"- {content} ([{title}]({url}))")
    return {
        "query": query,
        "summary": summary,
        "refined_summary": refined_summary,
        "bullets": bullets[:10],
        "citations": [{"title": r.get("title"), "url": r.get("url")} for r in (results + refined_results)]
    }

class ResearchRequest(BaseModel):
    query: str

@app.post("/research")
async def research_endpoint(req: ResearchRequest):
    result = deep_research_pipeline(req.query)
    return result
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Simple in-memory cache
_news_cache = {"data": None, "timestamp": 0}
_CACHE_TTL = 300  # 5 minutes

TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"  # TODO: Replace with your real key or use env var
TAVILY_URL = "https://api.tavily.com/search"

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # TODO: Replace with your real key or use env var
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def fetch_tavily_news():
    payload = {
        "query": "latest Indian politics news",
        "search_depth": "basic",
        "include_answer": False,
        "include_images": False,
        "max_results": 5
    }
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    try:
        resp = requests.post(TAVILY_URL, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Map Tavily results to expected format
        news = []
        for item in data.get("results", [])[:5]:
            news.append({
                "title": item.get("title", "No Title"),
                "source": item.get("url", ""),
                "timestamp": item.get("published", "")
            })
        return news
    except Exception as e:
        print(f"Tavily fetch error: {e}")
        return None

def search_tavily(query):
    payload = {
        "query": query,
        "search_depth": "basic",
        "include_answer": True,
        "include_images": False,
        "max_results": 5
    }
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    try:
        resp = requests.post(TAVILY_URL, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("answer", ""), data.get("results", [])
    except Exception as e:
        print(f"Tavily search error: {e}")
        return "", []

def gemini_ask(question, context=""):
    headers = {"Content-Type": "application/json"}
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    prompt = f"Answer the following question using the provided context.\n\nContext:\n{context}\n\nQuestion: {question}\n\nCite sources if possible."
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        return answer
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Sorry, I couldn't get an answer right now."

# LangGraph "Ask" pipeline: search -> synthesize answer
def ask_pipeline(question):
    search_answer, results = search_tavily(question)
    # Optionally, concatenate snippets for context
    context = "\n".join([r.get("content", "") for r in results])
    answer = gemini_ask(question, context)
    return {
        "question": question,
        "search_answer": search_answer,
        "llm_answer": answer,
        "citations": [{"title": r.get("title"), "url": r.get("url")} for r in results]
    }


@app.get("/news")
def get_news():
    now = time.time()
    if _news_cache["data"] and now - _news_cache["timestamp"] < _CACHE_TTL:
        return {"news": _news_cache["data"]}
    news = fetch_tavily_news()
    if news:
        _news_cache["data"] = news
        _news_cache["timestamp"] = now
        return {"news": news}
    # Fallback to dummy data if API fails
    return JSONResponse(status_code=503, content={"news": [
        {"title": "Dummy Headline 1", "source": "Example.com", "timestamp": "2025-07-26T10:00:00Z"},
        {"title": "Dummy Headline 2", "source": "Example.com", "timestamp": "2025-07-26T09:00:00Z"},
        {"title": "Dummy Headline 3", "source": "Example.com", "timestamp": "2025-07-26T08:00:00Z"},
        {"title": "Dummy Headline 4", "source": "Example.com", "timestamp": "2025-07-26T07:00:00Z"},
        {"title": "Dummy Headline 5", "source": "Example.com", "timestamp": "2025-07-26T06:00:00Z"}
    ], "error": "Failed to fetch real news, showing cached/dummy data."})


from fastapi import Request, UploadFile, File, Form
from pydantic import BaseModel
import io
from typing import Optional

try:
    from pdfminer.high_level import extract_text
except ImportError:
    extract_text = None

class AskRequest(BaseModel):
    question: str

class PDFRequest(BaseModel):
    target_language: Optional[str] = "en"

@app.post("/ask")
async def ask_endpoint(req: AskRequest):
    result = ask_pipeline(req.question)
    return result


# PDF translate + summarize pipeline
def gemini_translate(text, target_language):
    headers = {"Content-Type": "application/json"}
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    prompt = f"Translate the following text to {target_language}.\n\nText:\n{text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini translate error: {e}")
        return text

def gemini_summarize(text):
    headers = {"Content-Type": "application/json"}
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    prompt = f"Summarize the following text in 5-7 bullet points.\n\nText:\n{text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini summarize error: {e}")
        return text

# Gemini Speech-to-Text (Transcribe) and Text-to-Speech (TTS) endpoints (free tier)
@app.post("/transcribe")
async def transcribe_endpoint(audio: UploadFile = File(...)):
    # Gemini Speech-to-Text API endpoint (replace with actual endpoint if available)
    GEMINI_SPEECH_API = "https://speech.googleapis.com/v1/speech:recognize"
    API_KEY = GEMINI_API_KEY
    try:
        audio_bytes = await audio.read()
        # Google expects base64-encoded audio
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        payload = {
            "config": {
                "encoding": "LINEAR16",
                "languageCode": "en-US"
            },
            "audio": {
                "content": audio_b64
            }
        }
        resp = requests.post(f"{GEMINI_SPEECH_API}?key={API_KEY}", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        transcript = data["results"][0]["alternatives"][0]["transcript"]
        return {"transcript": transcript}
    except Exception as e:
        print(f"Transcribe error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/tts")
async def tts_endpoint(text: str = Form(...)):
    # Gemini Text-to-Speech API endpoint (replace with actual endpoint if available)
    GEMINI_TTS_API = "https://texttospeech.googleapis.com/v1/text:synthesize"
    API_KEY = GEMINI_API_KEY
    try:
        payload = {
            "input": {"text": text},
            "voice": {"languageCode": "en-US", "ssmlGender": "FEMALE"},
            "audioConfig": {"audioEncoding": "MP3"}
        }
        resp = requests.post(f"{GEMINI_TTS_API}?key={API_KEY}", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        audio_content = data["audioContent"]
        import base64
        audio_bytes = base64.b64decode(audio_content)
        from fastapi.responses import StreamingResponse
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/pdf")
async def pdf_endpoint(file: UploadFile = File(...), target_language: str = Form("en")):
    if extract_text is None:
        return JSONResponse(status_code=500, content={"error": "pdfminer.six is not installed."})
    try:
        contents = await file.read()
        text = extract_text(io.BytesIO(contents))
        if not text.strip():
            return JSONResponse(status_code=400, content={"error": "No text found in PDF."})
        translated = gemini_translate(text, target_language)
        summary = gemini_summarize(translated)
        return {"summary": summary, "translated_text": translated}
    except Exception as e:
        print(f"PDF processing error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
