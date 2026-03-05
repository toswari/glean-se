"""
Configuration utilities for Streamlit chatbot.
"""
import os
from typing import List, Dict


def get_api_url() -> str:
    """Get API URL from environment variable or return default."""
    return os.getenv("API_URL", "http://localhost:8000")


def get_default_timeout() -> int:
    """Get default timeout in seconds."""
    return int(os.getenv("API_TIMEOUT", "30"))


def get_sample_questions() -> List[Dict[str, any]]:
    """
    Get sample questions organized by category.
    Based on actual FAQ documents in faqs/*.md
    """
    return [
        {
            "name": "Authentication",
            "icon": "🔐",
            "questions": [
                "How do I reset my password?",
            ]
        },
        {
            "name": "Employee",
            "icon": "👥",
            "questions": [
                "What is our unlimited PTO policy?",
                "How does our equity vesting schedule work?",
                "How much PTO is required per year?",
                "How do I request time off?",
            ]
        },
        {
            "name": "SSO",
            "icon": "🔑",
            "questions": [
                "How do I enable SSO?",
                "Who can enable SSO for my account?",
            ]
        },
        {
            "name": "General",
            "icon": "❓",
            "questions": [
                "Explain how the document retrieval works",
                "How accurate are the answers?",
                "What sources are used for generating answers?",
            ]
        }
    ]