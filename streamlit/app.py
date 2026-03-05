"""
Streamlit Chatbot for FAQ RAG System

A modern chatbot interface with sample question cards and API integration.
"""
import streamlit as st
import requests
import os
import sys
import logging
from datetime import datetime

# Configure logging based on environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True
)
logger = logging.getLogger(__name__)

# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Use relative imports from the streamlit package directory
from services.api_client import FAQAPIClient
from utils.config import get_api_url, get_sample_questions
from components import render_sample_cards, render_chat_messages, render_sidebar


def process_question(prompt: str):
    """Process a question and get response from API."""
    # Log entry point
    logger.info(f"[STREAMLIT] >>> Processing question: '{prompt[:100]}...'")
    logger.debug(f"[STREAMLIT] Full question: {prompt}")
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get assistant response and add to history (will be displayed by render_chat_messages)
    with st.spinner("Thinking..."):
        start_time = datetime.now()
        try:
            logger.info(f"[STREAMLIT] Calling API: {st.session_state.api_url}/ask")
            logger.debug(f"[STREAMLIT] Request: question='{prompt[:50]}...', top_k=4")
            
            result = api_client.ask(question=prompt, top_k=4)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            answer = result["answer"]
            sources = result.get("sources", [])
            
            logger.info(f"[STREAMLIT] <<< API response received: elapsed={elapsed:.2f}s")
            logger.debug(f"[STREAMLIT] Answer (first 200 chars): {answer[:200]}...")
            logger.debug(f"[STREAMLIT] Sources: {sources}")
            
            # Add assistant message to history (will be displayed by render_chat_messages)
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })
            
            logger.info(f"[STREAMLIT] Response added to chat history")
            
            # Force rerun to display the new messages
            st.rerun()
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[STREAMLIT] Connection error: {e}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "❌ Cannot connect to API server. Please ensure the API is running."
            })
            st.rerun()
        except requests.exceptions.Timeout as e:
            logger.error(f"[STREAMLIT] Timeout error: {e}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "❌ Request timed out. Please try again."
            })
            st.rerun()
        except Exception as e:
            logger.error(f"[STREAMLIT] Unexpected error: {e}", exc_info=True)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Error: {str(e)}"
            })
            st.rerun()


def handle_question_selected(question: str):
    """Handle sample question card click - sends question to API and displays response."""
    process_question(question)


# Page configuration
st.set_page_config(
    page_title="FAQ Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        padding: 2rem;
    }
    
    /* Sample question cards - dark theme compatible */
    .stButton > button {
        border-radius: 12px;
        border: 1px solid #374151;
        background-color: #1f2937;
        color: #e5e7eb;
        padding: 12px 16px;
        font-size: 13px;
        text-align: left;
        height: auto;
        min-height: 60px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #374151;
        border-color: #4b5563;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Sidebar button - Clear Chat History */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1e40af;
        color: #ffffff;
        border: 1px solid #1e3a8a;
        text-align: center;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #1e3a8a;
        border-color: #172554;
        color: #ffffff;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        margin: 8px 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Category headers */
    h4 {
        color: #e5e7eb;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_url" not in st.session_state:
    st.session_state.api_url = get_api_url()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("💬 Chat")
with col2:
    st.selectbox(
        "Model",
        ["Qwen3.5-35B-A3B-FP8"],
        label_visibility="collapsed"
    )

# Render sidebar and get updated settings
sidebar_result = render_sidebar()
st.session_state.api_url = sidebar_result["api_url"]

# Create API client
api_client = FAQAPIClient(base_url=st.session_state.api_url)

# Sample Questions Section
categories = get_sample_questions()
render_sample_cards(categories, handle_question_selected)

st.divider()

# Chat history
render_chat_messages(st.session_state.messages)

# Chat input
if prompt := st.chat_input("Message AI..."):
    process_question(prompt)
