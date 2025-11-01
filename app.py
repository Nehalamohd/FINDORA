import streamlit as st
import speech_recognition as sr
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Page configuration
st.set_page_config(page_title="Findora", layout="wide")

# 🎨 Custom CSS (background + search bar styling)
custom_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://wallpapers.com/images/hd/dark-gradient-6bly12umg2d4psr2.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    color: white;
}
[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0);
}
h1 {
    text-align: center;
    font-size: 3rem;
    color: #fff;
    font-weight: 900;
    text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.6);
    margin-top: 50px;
}
div[data-baseweb="input"] > div {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 50px !important;
    border: 2px solid #1e3c72 !important;
    padding: 10px 25px !important;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease-in-out;
}
div[data-baseweb="input"] > div:hover {
    box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.5);
}
input[type="text"] {
    color: #1e3c72 !important;
    font-size: 18px !important;
    text-align: center;
}
input::placeholder {
    color: #5c5c5c;
    text-align: center;
}
label[data-testid="stTextInputLabel"] {
    color: white !important;
    font-size: 20px !important;
    font-weight: bold !important;
    text-align: center !important;
    display: block;
    margin-bottom: 10px;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.4);
}
.stButton>button {
    background-color: #1e3c72;
    color: white;
    font-size: 16px;
    font-weight: bold;
    border-radius: 25px;
    padding: 10px 25px;
    border: none;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    background-color: #3f5efb;
    transform: scale(1.05);
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ✅ Get API key safely
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found. Please add it to your .env file.")
    st.stop()

# ✅ UI layout
st.title("🔍 FINDORA")

# 🎙️ Voice + text input
recognizer = sr.Recognizer()
st.write("🎙️ You can type or speak your query below:")

voice_input = ""
if st.button("🎤 Speak"):
    with sr.Microphone() as source:
        st.info("🎧 Listening... Please speak your question.")
        audio = recognizer.listen(source)
        try:
            voice_input = recognizer.recognize_google(audio)
            st.success(f"✅ You said: {voice_input}")
        except sr.UnknownValueError:
            st.error("❌ Sorry, I couldn’t understand your voice.")
        except sr.RequestError:
            st.error("⚠️ Speech service error. Please check your internet connection.")

# 📝 Text input
text_input = st.text_input("Search what you want to know")

# Combine both inputs
query = voice_input or text_input

# 🔗 LangChain setup
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please respond to user queries clearly."),
    ("user", "Question: {question}")
])
llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_api_key)
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# ✅ Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# 💬 Generate response
if query:
    response = chain.invoke({'question': query})
    st.subheader("🧠 Findora says:")
    st.write(response)

    # 💾 Download response
    st.download_button(
        label="💾 Download Answer",
        data=response,
        file_name="findora_response.txt",
        mime="text/plain"
    )

    # ✅ Save history
    st.session_state.history.append({"query": query, "response": response})

# 📊 Sidebar: History + Recommendations
with st.sidebar:
    st.markdown("## 🧭 Your Activity")
    st.write("Recent searches and AI-powered recommendations 👇")

    if len(st.session_state.history) > 0:
        # 🕓 Recent Searches
        st.markdown("### 📜 Recent Searches")
        for item in st.session_state.history[-5:][::-1]:
            st.markdown(f"🔹 **{item['query']}**")

        # 🧠 Generate Recommendations
        all_queries = " ".join([h["query"] for h in st.session_state.history])
        keywords = list(set(all_queries.lower().split()))
        
        st.markdown("### ✨ Recommended Topics")
        common_topics = ["AI", "Machine Learning", "Python", "Data Science", "Cybersecurity", 
                         "Chatbots", "Deep Learning", "LangChain", "Groq", "Streamlit"]
        suggestions = [topic for topic in common_topics if topic.lower() in keywords]

        if suggestions:
            st.info("Based on your interests:")
            for s in suggestions:
                st.markdown(f"- 🔍 {s}")
        else:
            st.warning("Start exploring topics — recommendations will appear here soon! 🤖")
    else:
        st.info("No history yet. Start your first query!")
