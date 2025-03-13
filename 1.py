import os
import time
import streamlit as st
import speech_recognition as sr
import requests
from dotenv import load_dotenv
from groq import Groq
from googlesearch import search
from newspaper import Article

# Load API Key
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

# === VOICE INPUT WITH GROQ API ===
def transcribe_with_groq(audio_path):
    """Send recorded audio to Groq Whisper API for transcription."""
    url = "https://api.groq.com/audio/transcribe"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {"file": open(audio_path, "rb")}

    try:
        response = requests.post(url, headers=headers, files=files)
        response_json = response.json()
        return response_json.get("text", "❌ Error transcribing audio.")
    except Exception as e:
        return f"❌ API Error: {e}"
    finally:
        files["file"].close()  # Ensure file is closed

# === RECORD AUDIO AND TRANSCRIBE ===
if st.button("Start Recording"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎙️ Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    audio_path = "temp_audio.wav"
    with open(audio_path, "wb") as f:
        f.write(audio.get_wav_data())

    st.write("🛠️ Transcribing with Groq Whisper API...")
    transcription = transcribe_with_groq(audio_path)

    if transcription and "Error" not in transcription:
        st.write(f"🎙️ Recognized: {transcription}")
        response = get_final_answer(transcription)
        st.success(response)
    else:
        st.error(transcription)
