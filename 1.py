import streamlit as st
import numpy as np
import speech_recognition as sr
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from googlesearch import search
from newspaper import Article
from groq import Groq

# ✅ AI API Key
API_KEY = "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"
client = Groq(api_key=API_KEY)

# === AI RESPONSE FUNCTION ===
def ask_groq(question):
    """Ask AI for an answer."""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="llama-3.3-70b-versatile",
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI Error: {e}"

# === NEWS FETCHING FUNCTION ===
def fetch_news_articles(query, num_results=3):
    """Search Google and extract news articles."""
    try:
        links = list(search(query, num_results=num_results))
    except Exception as e:
        return [f"❌ Google search error: {e}"]

    articles = []
    for link in links:
        try:
            article = Article(link)
            article.download()
            article.parse()
            articles.append(article.text[:1000])  # Limit to 1000 chars
        except:
            pass

    return articles

# === AI + NEWS PROCESSING FUNCTION ===
def get_final_answer(query):
    """Get AI response or fetch news if AI lacks real-time info."""
    ai_answer = ask_groq(query)

    if "do not have information" in ai_answer.lower() or "knowledge cutoff" in ai_answer.lower():
        articles = fetch_news_articles(query)
        if articles:
            news_summary = " ".join(articles[:2])  # Take first 2 articles
            final_answer = ask_groq(f"Summarize this news: {query}\n\n{news_summary}")
        else:
            final_answer = "❌ No valid articles found."
    else:
        final_answer = ai_answer

    return final_answer

# === STREAMLIT UI ===
st.title("📰 AI-Powered News Assistant")

# === Text Input ===
user_input = st.text_input("🔍 Ask something:")
if st.button("Get Answer"):
    if user_input:
        response = get_final_answer(user_input)
        st.write("💬 AI Response:")
        st.success(response)
    else:
        st.warning("⚠️ Please enter a question.")

# === MICROPHONE INPUT ===
st.subheader("🎙️ Ask with Voice")

recognizer = sr.Recognizer()

def audio_callback(frame):
    """Processes audio from WebRTC and converts it to text."""
    audio_data = np.frombuffer(frame.to_ndarray(), dtype=np.int16)
    
    # Convert NumPy array into AudioData format
    audio_sample_rate = 16000
    audio_bytes = audio_data.tobytes()

    audio_source = sr.AudioData(audio_bytes, sample_rate=audio_sample_rate, sample_width=2)
    
    try:
        text = recognizer.recognize_google(audio_source)
        st.session_state["recognized_text"] = text  # Store the text so it persists
    except sr.UnknownValueError:
        st.session_state["recognized_text"] = "⚠️ Could not understand the audio."
    except sr.RequestError:
        st.session_state["recognized_text"] = "❌ Speech Recognition service unavailable."

webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_frame_callback=audio_callback,
    media_stream_constraints={"audio": True, "video": False},
)

# === DISPLAY PERSISTENT TEXT ===
if "recognized_text" in st.session_state and st.session_state["recognized_text"]:
    st.write(f"🎙️ Recognized: {st.session_state['recognized_text']}")
    
    # Process the voice input with AI
    response = get_final_answer(st.session_state["recognized_text"])
    st.success(response)
