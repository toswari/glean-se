"""
API Client for FAQ RAG Service

With comprehensive debug logging following DEBUG.md guide.
"""
import requests
from typing import Optional, List, Dict
import logging
from datetime import datetime

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
            logger.debug(f"[API-CLIENT] >>> Health check: {self.base_url}/health")
            start_time = datetime.now()
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.debug(f"[API-CLIENT] <<< Health check: status={response.status_code}, elapsed={elapsed:.3f}s")
            return response.status_code == 200
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[API-CLIENT] Health check connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"[API-CLIENT] Health check failed: {e}")
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
        logger.info(f"[API-CLIENT] >>> Calling /ask endpoint: question='{question[:50]}...', top_k={top_k}")
        logger.debug(f"[API-CLIENT] Request URL: {self.base_url}/ask")
        logger.debug(f"[API-CLIENT] Request JSON: question='{question[:100]}...', top_k={top_k}")
        
        start_time = datetime.now()
        try:
            response = self.session.post(
                f"{self.base_url}/ask",
                json={"question": question, "top_k": top_k},
                timeout=self.timeout
            )
            elapsed = (datetime.now() - start_time).total_seconds()
            
            logger.debug(f"[API-CLIENT] Response status: {response.status_code}")
            logger.debug(f"[API-CLIENT] Response time: {elapsed:.3f}s")
            
            response.raise_for_status()
            result = response.json()
            
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            
            logger.info(f"[API-CLIENT] <<< /ask completed: elapsed={elapsed:.2f}s, sources={len(sources)}")
            logger.debug(f"[API-CLIENT] Answer preview: {answer[:200]}...")
            logger.debug(f"[API-CLIENT] Sources: {sources}")
            
            return result
            
        except requests.exceptions.Timeout as e:
            logger.error(f"[API-CLIENT] /ask timeout after {self.timeout}s: {e}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"[API-CLIENT] /ask HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"[API-CLIENT] /ask error: {e}")
            raise
    
    def get_ingestion_status(self) -> Dict:
        """Get the current ingestion status."""
        logger.debug(f"[API-CLIENT] >>> Getting ingestion status")
        start_time = datetime.now()
        try:
            response = self.session.get(
                f"{self.base_url}/ingestion/status",
                timeout=self.timeout
            )
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.debug(f"[API-CLIENT] <<< Ingestion status: elapsed={elapsed:.3f}s")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[API-CLIENT] Get ingestion status error: {e}")
            raise
    
    def ingest_documents(self) -> Dict:
        """Trigger document ingestion."""
        logger.info(f"[API-CLIENT] >>> Triggering document ingestion")
        start_time = datetime.now()
        try:
            response = self.session.post(
                f"{self.base_url}/ingest",
                timeout=self.timeout * 2  # Longer timeout for ingestion
            )
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"[API-CLIENT] <<< Document ingestion completed: elapsed={elapsed:.2f}s")
            response.raise_for_status()
            result = response.json()
            logger.debug(f"[API-CLIENT] Ingestion result: {result}")
            return result
        except Exception as e:
            logger.error(f"[API-CLIENT] Document ingestion error: {e}")
            raise
