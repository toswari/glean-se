"""
Chat Interface Component for Streamlit Chatbot
"""
import streamlit as st
from typing import List, Dict


def render_chat_messages(messages: List[Dict[str, any]]) -> None:
    """
    Render chat messages in a conversation format.
    
    Args:
        messages: List of message dicts with 'role', 'content', and optional 'sources' keys
    """
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        sources = message.get("sources", [])
        
        with st.chat_message(role):
            st.markdown(content)
            
            # Display sources if available
            if sources:
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.markdown(f"- {source}")


def render_assistant_response(content: str, sources: List[str] = None) -> None:
    """
    Render an assistant response with optional sources.
    
    Args:
        content: The response content to display
        sources: Optional list of source filenames
    """
    with st.chat_message("assistant"):
        st.markdown(content)
        
        if sources:
            with st.expander("📚 Sources"):
                for source in sources:
                    st.markdown(f"- {source}")


def render_user_message(content: str) -> None:
    """
    Render a user message.
    
    Args:
        content: The message content to display
    """
    with st.chat_message("user"):
        st.markdown(content)