# Chatbot Specification - Streamlit FAQ RAG Bot

## Overview

This document specifies the design and implementation of a Streamlit-based chatbot interface for the FAQ RAG (Retrieval-Augmented Generation) system. The chatbot provides a modern, user-friendly interface similar to AI chat platforms with sample question cards and seamless API integration.

---

## Features

### Core Features
- **Chat Interface**: Modern conversation-style UI for asking questions
- **Sample Question Cards**: Pre-defined suggestion cards to help users get started
- **API Integration**: Direct integration with `/ask` endpoint for real-time answers
- **Source Attribution**: Display source documents used to generate answers
- **Conversation History**: Maintain chat history within session
- **Loading States**: Visual feedback during API calls

### UI Components (Based on Reference Screenshot)

```
┌─────────────────────────────────────────────────────────────────┐
│  💬 Chat    [Model Selector ▼]                                  │
├─────────────────────────────────────────────────────────────────┤
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  🤖 Model Name                                            │   │
│  │     model / provider                                      │  │
│  │     Model description text...                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │ Sample Question │ │ Sample Question │ │ Sample Question │    │
│  │ Card 1          │ │ Card 2          │ │ Card 3          │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
│                                                                 │
│  [Chat messages area - empty state or conversation history]     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Message AI...                              [+]    [↑]  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
streamlit/
├── chatbot-spec.md          # This specification document
├── app.py                   # Main Streamlit application
├── components/
│   ├── __init__.py
│   ├── sidebar.py           # Sidebar configuration
│   ├── chat_interface.py    # Chat message display
│   ├── sample_cards.py      # Sample question cards component
│   └── input_area.py        # Message input area
├── services/
│   ├── __init__.py
│   └── api_client.py        # API service client
└── utils/
    ├── __init__.py
    └── config.py            # Configuration utilities
```

---

## Implementation Details

### 1. Main Application (`app.py`)

```python
"""
Streamlit Chatbot for FAQ RAG System
"""
import streamlit as st
import requests
import os

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
    
    /* Sample question cards */
    .sample-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 16px;
        margin: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .sample-card:hover {
        background: #e9ecef;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .sample-card p {
        margin: 0;
        font-size: 14px;
        color: #333;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        margin: 8px 0;
    }
    
    /* Input area styling */
    .stChatInputContainer {
        padding: 1rem;
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_url" not in st.session_state:
    st.session_state.api_url = os.getenv("API_URL", "http://localhost:8000")

# Header
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("💬 Chat")
with col2:
    st.selectbox(
        "Model",
        ["Qwen3.5-35B-A3B-FP8", "Default Model"],
        label_visibility="collapsed"
    )

# Sample Questions Section
st.markdown("### Try asking...")

# Sample questions based on FAQ categories
SAMPLE_QUESTIONS = [
    {
        "category": "Authentication",
        "questions": [
            "How do I reset my password?",
            "What authentication methods are supported?",
            "How do I enable two-factor authentication?"
        ]
    },
    {
        "category": "Employee",
        "questions": [
            "How do I update my employee profile?",
            "What are the company holiday policies?",
            "How do I request time off?"
        ]
    },
    {
        "category": "SSO",
        "questions": [
            "How do I log in with SSO?",
            "What do I do if SSO login fails?",
            "Can I use multiple SSO providers?"
        ]
    },
    {
        "category": "General",
        "questions": [
            "Explain the document retrieval process",
            "How accurate are the answers?",
            "What sources are used for answers?"
        ]
    }
]

# Display sample question cards in columns
cols = st.columns(4)
for idx, category_data in enumerate(SAMPLE_QUESTIONS):
    with cols[idx % 4]:
        with st.container():
            st.markdown(f"**{category_data['category']}**")
            for question in category_data['questions'][:2]:
                if st.button(
                    question,
                    key=f"sample_{idx}_{question[:20]}",
                    use_container_width=True,
                    help=f"Click to ask: {question}"
                ):
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.rerun()

st.divider()

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.markdown(f"- {source}")

# Chat input
if prompt := st.chat_input("Message AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{st.session_state.api_url}/ask",
                    json={"question": prompt, "top_k": 4},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                st.markdown(data["answer"])
                
                if data.get("sources"):
                    with st.expander("📚 Sources"):
                        for source in data["sources"]:
                            st.markdown(f"- {source}")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["answer"],
                    "sources": data["sources"]
                })
                
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API server. Please ensure the API is running.")
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.text_input(
        "API URL",
        value=st.session_state.api_url,
        key="api_url_input",
        help="Base URL for the FAQ RAG API"
    )
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # API Status check
    try:
        health_response = requests.get(f"{st.session_state.api_url}/health", timeout=2)
        if health_response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.warning("⚠️ API responding but unhealthy")
    except:
        st.error("❌ API Offline")
    
    # Ingestion status
    try:
        status_response = requests.get(f"{st.session_state.api_url}/ingestion/status", timeout=2)
        if status_response.status_code == 200:
            status_data = status_response.json()
            st.info(f"📚 Documents: {status_data.get('num_chunks', 0)} chunks indexed")
    except:
        pass
```

---

### 2. API Client Service (`services/api_client.py`)

```python
"""
API Client for FAQ RAG Service
"""
import requests
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class FAQAPIClient:
    """Client for interacting with the FAQ RAG API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def ask(self, question: str, top_k: int = 4) -> Dict:
        """
        Ask a question and get an answer.
        
        Args:
            question: The question to ask
            top_k: Number of chunks to retrieve (default: 4)
            
        Returns:
            Dict with 'answer' and 'sources' keys
            
        Raises:
            requests.exceptions.RequestException: On API errors
        """
        response = self.session.post(
            f"{self.base_url}/ask",
            json={"question": question, "top_k": top_k},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_ingestion_status(self) -> Dict:
        """Get the current ingestion status."""
        response = self.session.get(
            f"{self.base_url}/ingestion/status",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def ingest_documents(self) -> Dict:
        """Trigger document ingestion."""
        response = self.session.post(
            f"{self.base_url}/ingest",
            timeout=self.timeout * 2  # Longer timeout for ingestion
        )
        response.raise_for_status()
        return response.json()
```

---

### 3. Sample Cards Component (`components/sample_cards.py`)

```python
"""
Sample Question Cards Component
"""
import streamlit as st
from typing import List, Dict


def render_sample_cards(
    categories: List[Dict[str, any]],
    on_question_selected: callable
) -> None:
    """
    Render sample question cards in a grid layout.
    
    Args:
        categories: List of category dicts with 'name' and 'questions' keys
        on_question_selected: Callback when a question is selected
    """
    st.markdown("### 💡 Try asking...")
    
    # Create grid layout
    cols_per_row = 4
    total_cards = sum(len(cat['questions']) for cat in categories[:4])
    
    # Use columns for card layout
    cols = st.columns(min(4, len(categories)))
    
    for idx, category in enumerate(categories[:4]):
        with cols[idx]:
            st.markdown(f"#### {category.get('icon', '❓')} {category['name']}")
            
            for question in category['questions'][:2]:
                # Create card-like button
                card = st.container()
                with card:
                    if st.button(
                        question,
                        key=f"sample_{idx}_{hash(question)}",
                        use_container_width=True,
                        help=f"Ask: {question}"
                    ):
                        on_question_selected(question)
```

---

## Sample Questions by Category

Based on the actual FAQ documents in the project (`faqs/*.md`):

### Authentication (`faq_auth.md`)
- "How do I reset my password?"

### Employee (`faq_employee.md`)
- "What is our unlimited PTO policy?"
- "How does our equity vesting schedule work?"
- "How much PTO is required per year?"
- "How do I request time off?"
- "What is the notice period for PTO requests?"
- "When are equity grants reviewed?"

### SSO (`faq_sso.md`)
- "How do I enable SSO?"
- "Who can enable SSO for my account?"

### General/Technical
- "Explain how the document retrieval works"
- "How accurate are the answers?"
- "What sources are used for generating answers?"

---

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ask` | POST | Ask a question |


### `/ask` Request/Response

**Request:**
```json
{
  "question": "How do I reset my password?",
  "top_k": 4
}
```

**Response:**
```json
{
  "answer": "To reset your password, follow these steps...",
  "sources": ["faq_auth.md", "faq_sso.md"]
}
```

---

## Running the Application

### Prerequisites
1. Ensure the API server is running:
   ```bash
   python api_server.py
   # or
   ./start-api.sh
   ```

2. Install Streamlit dependencies:
   ```bash
   pip install streamlit requests
   ```

### Start the Chatbot
```bash
cd streamlit
streamlit run app.py
```

### Environment Variables
```bash
# Optional: Configure API URL
export API_URL="http://localhost:8000"

# Optional: Configure Streamlit port
export STREAMLIT_SERVER_PORT="8501"
```

---

## Future Enhancements

- [ ] Streaming responses for real-time answer generation
- [ ] Multi-model selection
- [ ] Conversation export functionality
- [ ] Feedback mechanism for answer quality
- [ ] Advanced search filters
