from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import streamlit as st
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Page configuration
st.set_page_config(page_title="Findora", layout="wide")

# 🎨 Custom CSS (background + search bar styling)
custom_css = """
<style>
/* 🌄 Background styling */
[data-testid="stAppViewContainer"] {
    background-image: url("https://wallpapers.com/images/hd/dark-gradient-6bly12umg2d4psr2.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    color: white;
}

/* Transparent header */
[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0);
}

/* Title styling */
h1 {
    text-align: center;
    font-size: 3rem;
    color: #fff;
    font-weight: 900;
    text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.6);
    margin-top: 50px;
}

/* 🔍 Custom search bar styling */
div[data-baseweb="input"] > div {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 50px !important;
    border: 2px solid #1e3c72 !important;
    padding: 10px 25px !important;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease-in-out;
}

/* Hover effect */
div[data-baseweb="input"] > div:hover {
    box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.5);
}

/* Input text styling */
input[type="text"] {
    color: #1e3c72 !important;
    font-size: 18px !important;
    text-align: center;
}

/* Placeholder text */
input::placeholder {
    color: #5c5c5c;
    text-align: center;
}

/* 🏷️ Change label ("Search what you want to know") styling */
label[data-testid="stTextInputLabel"] {
    color: white !important;
    font-size: 20px !important;
    font-weight: bold !important;
    text-align: center !important;
    display: block;
    margin-bottom: 10px;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.4);
}

/* Center content */
.main {
    display: flex;
    flex-direction: column;
    align-items: center;
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
input_text = st.text_input("Search what you want to know")

# ✅ Define the prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please respond to user queries."),
    ("user", "Question: {question}")
])

# ✅ Groq model
llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_api_key)

# ✅ Output chain
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# ✅ Generate response
if input_text:
    response = chain.invoke({'question': input_text})
    st.write(response)
