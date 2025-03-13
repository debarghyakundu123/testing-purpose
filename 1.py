import os
import time
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from googlesearch import search
from newspaper import Article
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import speech_recognition as sr
import numpy as np
import av

API_KEY = "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"

# Initialize AI client
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
        st.error(f"❌ Error querying AI: {e}")
        return "AI is currently unavailable. Please try again later."

# === NEWS FETCHING FUNCTION ===
def fetch_news_articles(query, num_results=3):
    """Search Google and extract news articles."""
    st.write("🔍 Searching for latest news...")

    try:
        links = list(search(query, num_results=num_results))
    except Exception as e:
        st.error(f"❌ Google search error: {e}")
        return []

    articles = []
    for link in links:
        try:
            article = Article(link)
            article.download()
            article.parse()
            articles.append(article.text)
            st.success(f"✅ Retrieved article from: {link}")
            time.sleep(2)  # Prevent rate limits
        except Exception as e:
            st.warning(f"❌ Failed to fetch {link}: {e}")

    return articles

# === AI + NEWS PROCESSING FUNCTION ===
def get_final_answer(query):
    """Get AI response or fetch news if AI lacks real-time info."""
    ai_answer = ask_groq(query)

    if "do not have information" in ai_answer.lower() or "knowledge cutoff" in ai_answer.lower():
        st.warning("⚠️ AI lacks real-time info. Fetching latest news...")
        articles = fetch_news_articles(query)

        if articles:
            news_summary = " ".join(articles[:2])  # Take first 2 articles
            final_answer = ask_groq(f"Summarize and answer this question based on the latest news: {query}\n\n{news_summary}")
        else:
            final_answer = "❌ No valid articles found. Please try again later."
    else:
        final_answer = ai_answer

    return final_answer

# === STREAMLIT UI ===
st.title("📰 AI-Powered News Assistant")

user_input = st.text_input("Ask something:")

if st.button("Get Answer"):
    if user_input:
        response = get_final_answer(user_input)
        st.write("💬 AI Response:")
        st.success(response)
    else:
        st.warning("⚠️ Please enter a question.")

# === MICROPHONE PERMISSION REQUEST & AUDIO RECORDING ===
st.subheader("🎙️ Ask with Voice")

# Request permission using JavaScript
mic_permission_js = """
<script>
async function requestMicPermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        document.getElementById("mic-status").innerText = "✅ Microphone access granted!";
    } catch (err) {
        document.getElementById("mic-status").innerText = "❌ Microphone access denied!";
    }
}
</script>
<button onclick="requestMicPermission()">Request Microphone Permission</button>
<p id="mic-status">🎤 Click the button to request microphone access.</p>
"""

st.components.v1.html(mic_permission_js, height=100)

# === STREAMLIT WEBRTC FOR AUDIO INPUT ===
st.write("🎤 Click 'Start' to record your voice and convert it to text:")

webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDRECV,
    client_settings=ClientSettings(
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True},
    ),
)

if webrtc_ctx.audio_receiver:
    recognizer = sr.Recognizer()
    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)

    for frame in audio_frames:
        sound = np.frombuffer(frame.to_ndarray(), dtype=np.int16)
        audio_data = sr.AudioData(sound.tobytes(), frame.sample_rate, 2)

        try:
            voice_text = recognizer.recognize_google(audio_data)
            st.write(f"🎙️ Recognized: {voice_text}")
            response = get_final_answer(voice_text)
            st.success(response)
        except sr.UnknownValueError:
            st.error("⚠️ Could not understand the audio.")
        except sr.RequestError:
            st.error("❌ Speech Recognition service unavailable.")
