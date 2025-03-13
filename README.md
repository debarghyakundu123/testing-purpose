#AskMe AI: Your Smart Chat

AskMe AI is an AI-powered chatbot that can answer user queries intelligently. If the AI lacks real-time information, it fetches the latest news from the web and provides an updated response. It also features a typing animation effect to enhance user interaction.

Features

🤖 AI-Powered Responses - Uses the Llama 3.3-70B Versatile model for intelligent answers.

🌍 Real-Time News Fetching - If AI lacks knowledge, it retrieves recent articles from Google.

✍️ Typing Animation - Simulates a human-like typing effect for better engagement.

🔎 Google Search Integration - Fetches top search results for additional context.

Installation

To run this project locally, follow these steps:

1. Clone the Repository

git clone https://github.com/YOUR_GITHUB_USERNAME/AskMe-AI.git
cd AskMe-AI

2. Install Dependencies

pip install -r requirements.txt

3. Set Up API Keys

Replace API_KEY in main.py with your Groq API Key.

Ensure you have Google Search API enabled for fetching news.

4. Run the Application

streamlit run main.py

Usage

Open the app in your browser.

Enter your question in the text box.

Click the Get Answer button.

If AI cannot answer, it fetches news articles for an updated response.

Requirements

Python 3.8+

Streamlit

SpeechRecognition

dotenv

Groq API

Google Search API

Newspaper3k

Future Enhancements

🎙️ Voice Input (Re-enable speech recognition)

🗣️ AI Voice Response (Text-to-Speech output)

📊 Data Analytics Dashboard (Track popular queries and trends)

Contributing

Pull requests are welcome! Feel free to fork the repo and submit changes.

License

This project is MIT Licensed. Feel free to use and modify it!

Made with ❤️ using Python & Streamlit 🚀
