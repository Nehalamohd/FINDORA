import streamlit as st
import speech_recognition as sr
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import json
import random
from voice_output import speak_text, stop_speaking  # ✅ voice module

# ---------- Load environment ----------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# ---------- Page config ----------
st.set_page_config(page_title="Findora", layout="wide")

# ---------- Persistent History ----------
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error saving history: {e}")

# ---------- Daily Tips ----------
ai_tips = [
    "🤖 AI can learn from data using algorithms like regression, trees, and neural networks.",
    "🧠 Deep learning uses artificial neural networks inspired by the human brain.",
    "📊 Data preprocessing is 80% of any AI or ML project — clean data means better models!",
    "💬 NLP helps machines understand and generate human language.",
    "🧩 Machine learning models improve automatically with experience.",
    "🚀 Reinforcement Learning teaches AI through trial and error, just like humans learn new skills.",
    "🔍 Feature engineering is the secret sauce of strong AI models.",
    "📈 AI is widely used in healthcare, finance, and cybersecurity.",
    "💡 Naive Bayes classifiers are used in spam filtering and sentiment analysis.",
    "🌐 Chatbots use NLP to understand intent and respond like humans."
]
daily_tip = random.choice(ai_tips)

# ---------- Custom CSS ----------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://wallpapers.com/images/hd/dark-gradient-6bly12umg2d4psr2.jpg");
    background-size: cover;
    background-position: center;
    color: white;
}
[data-testid="stHeader"] { background: rgba(0, 0, 0, 0); }
h1 {
    text-align: center; font-size: 3rem; color: #fff; font-weight: 900;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.6); margin-top: 50px;
}
div[data-baseweb="input"] > div {
    background-color: rgba(255,255,255,0.9) !important;
    border-radius: 50px !important; border: 2px solid #1e3c72 !important;
    padding: 10px 25px !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}
input[type="text"] { color: #1e3c72 !important; font-size: 18px !important; text-align: center; }
label[data-testid="stTextInputLabel"] {
    color: white !important; font-size: 20px !important; font-weight: bold !important;
    text-align: center !important;
}
.stButton>button {
    background-color: #1e3c72; color: white; font-size: 16px; font-weight: bold;
    border-radius: 25px; padding: 10px 25px; border: none;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.stButton>button:hover { background-color: #3f5efb; transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.markdown("### 🌈 Daily AI Tip")
st.sidebar.info(daily_tip)

# ---------- Check API Key ----------
if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found. Please add it to your .env file.")
    st.stop()

# ---------- Initialize ----------
st.title("🔍 FINDORA")
st.write("🎙️ You can type or speak your query below:")

recognizer = sr.Recognizer()
if "history" not in st.session_state:
    st.session_state.history = load_history()

# ---------- Voice Input ----------
voice_input = ""
if st.button("🎤 Speak"):
    try:
        with sr.Microphone() as source:
            st.info("🎧 Listening... Please speak your question.")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            voice_input = recognizer.recognize_google(audio)
            st.success(f"✅ You said: {voice_input}")
    except Exception as e:
        st.error(f"🎤 Voice error: {e}")

# ---------- Text Input ----------
text_input = st.text_input("Search what you want to know")

# ---------- Final Query ----------
query = voice_input.strip() if voice_input else text_input.strip() if text_input else ""

# ---------- LangChain Setup ----------
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please respond clearly and concisely."),
    ("user", "Question: {question}")
])
llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_api_key)
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# ---------- Sidebar: History, Recommendations, Clear ----------
with st.sidebar:
    st.markdown("## 🧭 Your Activity")
    st.write("Recent searches and AI-powered recommendations 👇")

    if st.button("🧹 Clear History"):
        st.session_state.history = []
        save_history([])
        st.success("✅ History cleared.")

    if len(st.session_state.history) > 0:
        st.markdown("### 📜 Recent Searches")
        for item in st.session_state.history[-8:][::-1]:
            st.markdown(f"🔹 **{item['query']}**")

        # Recommendations
        all_queries = " ".join([h["query"] for h in st.session_state.history])
        keywords = set(all_queries.lower().split())
        st.markdown("### ✨ Recommended Topics")
        common_topics = ["AI", "Machine Learning", "Python", "Data Science", "Cybersecurity",
                         "Chatbots", "Deep Learning", "LangChain", "Groq", "Streamlit"]
        suggestions = [t for t in common_topics if t.lower() in keywords]
        if suggestions:
            st.info("Based on your searches:")
            for s in suggestions:
                st.markdown(f"- 🔍 {s}")
        else:
            st.info("No strong matches yet — search more to get tailored suggestions!")
    else:
        st.info("No history yet. Start your first query!")

# ---------- Handle Response ----------
if query:
    try:
        response = chain.invoke({'question': query})
        st.subheader("🧠 Findora says:")
        st.write(response)

        # 💾 Download Button
        st.download_button(
            label="💾 Download Answer",
            data=response,
            file_name="findora_response.txt",
            mime="text/plain"
        )

        # 🔊 Speak / Stop Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔊 Speak Answer"):
                speak_text(response)
        with col2:
            if st.button("🛑 Stop Speaking"):
                stop_speaking()

        # 💾 Save history
        st.session_state.history.append({"query": query, "response": response})
        save_history(st.session_state.history)

    except Exception as e:
        st.error(f"⚠️ Error generating response: {e}")
