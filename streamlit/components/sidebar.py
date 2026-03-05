"""
Sidebar Component for Streamlit Chatbot

With comprehensive debug logging following DEBUG.md guide.
"""
import streamlit as st
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def render_sidebar() -> dict:
    """
    Render the sidebar with settings and status information.
    
    Returns:
        dict with 'api_url' and 'clear_history' keys
    """
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API URL configuration
        api_url = st.text_input(
            "API URL",
            value=st.session_state.get("api_url", "http://localhost:8000"),
            key="api_url_input",
            help="Base URL for the FAQ RAG API"
        )
        
        st.divider()
        
        # Clear chat history button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # API Status check
        st.subheader("📊 Status")
        
        try:
            logger.debug(f"[SIDEBAR] >>> Checking API health: {api_url}/health")
            health_start = datetime.now()
            health_response = requests.get(f"{api_url}/health", timeout=2)
            health_elapsed = (datetime.now() - health_start).total_seconds()
            logger.debug(f"[SIDEBAR] <<< API health check: status={health_response.status_code}, elapsed={health_elapsed:.3f}s")
            
            if health_response.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.warning("⚠️ API responding but unhealthy")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[SIDEBAR] API connection error: {e}")
            st.error("❌ API Offline")
        except requests.exceptions.Timeout as e:
            logger.error(f"[SIDEBAR] API timeout: {e}")
            st.error("❌ API Timeout")
        except Exception as e:
            logger.error(f"[SIDEBAR] API check error: {e}")
            st.error("❌ API Offline")
        
        # Ingestion status
        try:
            logger.debug(f"[SIDEBAR] >>> Getting ingestion status: {api_url}/ingestion/status")
            status_start = datetime.now()
            status_response = requests.get(f"{api_url}/ingestion/status", timeout=2)
            status_elapsed = (datetime.now() - status_start).total_seconds()
            logger.debug(f"[SIDEBAR] <<< Ingestion status: elapsed={status_elapsed:.3f}s")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                ingested = status_data.get('ingested', False)
                num_chunks = status_data.get('num_chunks', 0)
                
                if ingested:
                    st.success(f"📚 {num_chunks} chunks indexed")
                    logger.info(f"[SIDEBAR] Ingestion status: {num_chunks} chunks indexed")
                else:
                    st.warning("⚠️ No documents indexed")
                    logger.warning(f"[SIDEBAR] No documents indexed")
                    if st.button("📥 Ingest Documents"):
                        logger.info(f"[SIDEBAR] >>> Triggering document ingestion")
                        try:
                            ingest_start = datetime.now()
                            ingest_response = requests.post(f"{api_url}/ingest", timeout=60)
                            ingest_elapsed = (datetime.now() - ingest_start).total_seconds()
                            
                            if ingest_response.status_code == 200:
                                st.success("Documents ingested!")
                                logger.info(f"[SIDEBAR] <<< Document ingestion completed: elapsed={ingest_elapsed:.2f}s")
                                st.rerun()
                            else:
                                st.error("Failed to ingest documents")
                                logger.error(f"[SIDEBAR] Document ingestion failed: status={ingest_response.status_code}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            logger.error(f"[SIDEBAR] Document ingestion error: {e}")
        except Exception as e:
            logger.error(f"[SIDEBAR] Get ingestion status error: {e}")
        
        return {
            "api_url": api_url,
            "clear_history": False
        }