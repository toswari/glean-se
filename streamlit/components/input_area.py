"""
Input Area Component for Streamlit Chatbot
"""
import streamlit as st


def render_input_area(placeholder: str = "Message AI...") -> str:
    """
    Render the chat input area.
    
    Args:
        placeholder: Placeholder text for the input field
        
    Returns:
        User input string or empty string if no input
    """
    return st.chat_input(placeholder) or ""