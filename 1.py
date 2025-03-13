

import os
import time
import streamlit as st
import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq
from googlesearch import search
from newspaper import Article

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav


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
        links = list(search(query, num_results=num_results))  # FIXED HERE
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

# === VOICE INPUT ===
st.subheader("🎙️ Ask with Voice")
if st.button("Start Recording"):
    recognizer = sr.Recognizer()
    
    # Record audio using sounddevice
    duration = 5  # Record for 5 seconds
    samplerate = 44100  # Sample rate
    st.write("🎤 Listening...")
    
    try:
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
        sd.wait()  # Wait for recording to finish
        
        # Save audio as WAV file
        wav.write("temp_audio.wav", samplerate, audio_data)
        
        # Use SpeechRecognition to process the WAV file
        with sr.AudioFile("temp_audio.wav") as source:
            audio = recognizer.record(source)
        
        # Recognize speech
        voice_text = recognizer.recognize_google(audio)
        st.write(f"🎙️ Recognized: {voice_text}")
        response = get_final_answer(voice_text)
        st.success(response)

    except Exception as e:
        st.error(f"❌ Error capturing voice: {e}")

