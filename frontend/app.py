import streamlit as st
import requests

st.title("Indian Politics News & QA")


mode = st.sidebar.selectbox("Mode", ["News", "Ask", "PDF", "Deep Research"])

if mode == "News":
    st.header("Latest Headlines")
    try:
        resp = requests.get("http://localhost:8000/news")
        news = resp.json().get("news", [])
        for item in news:
            st.markdown(f"**{item['title']}**  ")
            st.markdown(f"[Source]({item['source']}) | {item['timestamp']}")
            st.markdown("---")
    except Exception as e:
        st.error(f"Failed to fetch news: {e}")

elif mode == "Ask":
    st.header("Ask a Question (Agentic QA)")
    question = st.text_input("Enter your question about Indian politics:")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            try:
                resp = requests.post("http://localhost:8000/ask", json={"question": question})
                data = resp.json()
                st.subheader("LLM Answer:")
                st.write(data.get("llm_answer", "No answer."))
                st.subheader("Search Answer:")
                st.write(data.get("search_answer", "No search answer."))
                st.subheader("Citations:")
                for cite in data.get("citations", []):
                    st.markdown(f"- [{cite['title']}]({cite['url']})")
            except Exception as e:
                st.error(f"Failed to get answer: {e}")

elif mode == "PDF":
    st.header("PDF Translate & Summarize")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    target_lang = st.selectbox("Target Language", ["en", "hi"])
    if uploaded_file and st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"target_language": target_lang}
                resp = requests.post("http://localhost:8000/pdf", files=files, data=data)
                result = resp.json()
                if resp.status_code == 200:
                    st.subheader("Summary:")
                    st.write(result.get("summary", "No summary."))
                    st.subheader("Translated Text:")
                    st.write(result.get("translated_text", "No translation."))
                else:
                    st.error(result.get("error", "Unknown error."))
            except Exception as e:
                st.error(f"Failed to process PDF: {e}")

elif mode == "Deep Research":
    st.header("Deep Research Mode")
    query = st.text_input("Enter your research query:")
    if st.button("Run Research") and query:
        with st.spinner("Running deep research..."):
            try:
                resp = requests.post("http://localhost:8000/research", json={"query": query})
                data = resp.json()
                st.subheader("Summary:")
                st.write(data.get("summary", "No summary."))
                st.subheader("Refined Summary:")
                st.write(data.get("refined_summary", "No refined summary."))
                st.subheader("Key Points:")
                for bullet in data.get("bullets", []):
                    st.markdown(bullet)
                st.subheader("Citations:")
                for cite in data.get("citations", []):
                    st.markdown(f"- [{cite['title']}]({cite['url']})")
            except Exception as e:
                st.error(f"Failed to run research: {e}")

# Voice Input & Output UI (available in all modes for demo)
st.sidebar.markdown("---")
st.sidebar.header("Voice Input & Output")
audio_file = st.sidebar.file_uploader("Upload WAV for Transcription", type=["wav"])
if st.sidebar.button("Transcribe") and audio_file:
    with st.spinner("Transcribing..."):
        try:
            files = {"audio": (audio_file.name, audio_file.getvalue(), "audio/wav")}
            resp = requests.post("http://localhost:8000/transcribe", files=files)
            result = resp.json()
            if resp.status_code == 200:
                st.sidebar.success(f"Transcript: {result.get('transcript', '')}")
            else:
                st.sidebar.error(result.get("error", "Unknown error."))
        except Exception as e:
            st.sidebar.error(f"Failed to transcribe: {e}")

tts_text = st.sidebar.text_area("Text to Speak")
if st.sidebar.button("Play TTS") and tts_text.strip():
    with st.spinner("Synthesizing speech..."):
        try:
            import streamlit.components.v1 as components
            resp = requests.post("http://localhost:8000/tts", data={"text": tts_text})
            if resp.status_code == 200:
                audio_bytes = resp.content
                st.sidebar.audio(audio_bytes, format="audio/mp3")
            else:
                st.sidebar.error("TTS failed.")
        except Exception as e:
            st.sidebar.error(f"TTS error: {e}")
