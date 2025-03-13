import os
import time
import streamlit as st
import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq
from googlesearch import search
from newspaper import Article

API_KEY = "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"

# Initialize AI client
client = Groq(api_key=API_KEY)

# === 1️⃣ VOICE INPUT FUNCTION ===
def record_voice():
    """Records voice and returns audio data."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening... Speak now!")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    return audio

# === 2️⃣ AUDIO TO TEXT FUNCTION ===
def voice_to_text(audio):
    """Converts recorded audio to text."""
    recognizer = sr.Recognizer()
    try:
        text = recognizer.recognize_google(audio)
        st.success(f"✅ Recognized: {text}")
        return text
    except sr.UnknownValueError:
        st.error("⚠️ Could not understand the audio.")
        return None
    except sr.RequestError:
        st.error("❌ Speech Recognition service unavailable.")
        return None

# === 3️⃣ PROCESS QUERY TO AI ===
def process_query(query):
    """Sends query to AI and returns answer."""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ AI Error: {e}")
        return "AI is currently unavailable. Please try again later."

# === STREAMLIT UI ===
st.title("🗣️ AI-Powered Voice Assistant")

# Text Input Query
user_input = st.text_input("Type your question:")

if st.button("Get Answer"):
    if user_input:
        response = process_query(user_input)
        st.success(f"🤖 AI Response:\n\n{response}")
    else:
        st.warning("⚠️ Please enter a question.")

# Voice Input Section
st.subheader("🎙️ Use Voice Input")
if st.button("Start Recording"):
    audio = record_voice()
    text = voice_to_text(audio)
    if text:
        response = process_query(text)
        st.success(f"🤖 AI Response:\n\n{response}")
