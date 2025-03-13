import os
import time
import streamlit as st
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from googlesearch import search
from newspaper import Article
from groq import Groq

# ✅ API Key for AI Model
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
    st.write("🔍 Searching for latest news...")

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
            st.success(f"✅ Found: {link}")
            time.sleep(2)  # Prevent rate limits
        except:
            pass

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

# === MICROPHONE RECORDING (WITHOUT PYAUDIO) ===
st.subheader("🎙️ Ask with Voice")

def record_audio(duration=5, fs=44100):
    """Records audio using sounddevice and saves it as a .wav file."""
    st.write("🎤 Recording...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()  # Wait until recording is finished
    wav.write("temp_audio.wav", fs, audio_data)
    st.success("✅ Recording complete!")

if st.button("🎙️ Start Recording"):
    record_audio()  # Record and save as 'temp_audio.wav'

    # Recognize speech
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp_audio.wav") as source:
        st.write("🔄 Processing audio...")
        audio = recognizer.record(source)

    try:
        voice_text = recognizer.recognize_google(audio)
        st.write(f"🎙️ Recognized: {voice_text}")
        response = get_final_answer(voice_text)
        st.success(response)
    except sr.UnknownValueError:
        st.error("⚠️ Could not understand the audio.")
    except sr.RequestError:
        st.error("❌ Speech Recognition service unavailable.")
