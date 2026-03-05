"""
API Server for FAQ RAG System

FastAPI-based HTTP server exposing the RAG functionality.
"""

import os
import logging
import time
from typing import Optional, Callable
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from rag_core import ask_faq_core, ingest_docs, is_ingested, get_ingestion_status, delete_all, delete_collection

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")  # Default to DEBUG for comprehensive logging
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"

# Create custom formatter for detailed logging
class DetailedFormatter(logging.Formatter):
    """Custom formatter for detailed API and LLM logging."""
    def format(self, record):
        # Add extra fields for LLM statistics
        if hasattr(record, 'llm_model'):
            record.msg = f"[LLM] {record.msg} | model={record.llm_model}"
        if hasattr(record, 'input_tokens'):
            record.msg = f"{record.msg} | input_tokens={record.input_tokens}"
        if hasattr(record, 'output_tokens'):
            record.msg = f"{record.msg} | output_tokens={record.output_tokens}"
        if hasattr(record, 'elapsed'):
            record.msg = f"{record.msg} | elapsed={record.elapsed:.2f}s"
        if hasattr(record, 'tokens_per_sec'):
            record.msg = f"{record.msg} | tokens/sec={record.tokens_per_sec:.1f}"
        return super().format(record)

# Set root logger level to DEBUG to capture all logs
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True  # Force reconfiguration
)
logger = logging.getLogger(__name__)

# Add custom LLM statistics logger
llm_logger = logging.getLogger('llm_stats')
llm_logger.setLevel(logging.DEBUG)
if not llm_logger.handlers:
    llm_handler = logging.StreamHandler()
    llm_handler.setFormatter(DetailedFormatter('%(message)s'))
    llm_logger.addHandler(llm_handler)

# Create FastAPI app with custom logging
app = FastAPI(
    title="FAQ RAG API",
    description="Retrieval-Augmented Generation API for FAQ documents",
    version="1.0.0"
)

# Middleware for detailed request logging
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """Log all HTTP requests with timing and response status."""
    request_id = f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}"
    start_time = time.time()
    
    # Get client info
    client_host = request.client.host if request.client else "unknown"
    
    # Log request
    logger.info(f"[API] >>> {request.method} {request.url.path} | client={client_host} | request_id={request_id}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate timing
    elapsed = time.time() - start_time
    
    # Log response
    logger.info(f"[API] <<< {request.method} {request.url.path} | status={response.status_code} | elapsed={elapsed:.3f}s | request_id={request_id}")
    
    return response


# Request/Response Models
class AskRequest(BaseModel):
    """Request model for /ask endpoint."""
    question: str = Field(..., description="The question to ask", min_length=1)
    top_k: Optional[int] = Field(default=4, description="Number of chunks to retrieve", ge=1, le=10)
    
    @field_validator('question')
    @classmethod
    def question_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('question must be a non-empty string')
        return v.strip()


class AskResponse(BaseModel):
    """Response model for /ask endpoint."""
    answer: str = Field(..., description="Generated answer")
    sources: list[str] = Field(..., description="List of source filenames")


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""
    status: str = Field(default="ok", description="Health status")


class IngestResponse(BaseModel):
    """Response model for /ingest endpoint."""
    status: str = Field(..., description="Ingestion status")
    num_chunks: int = Field(..., description="Number of chunks created")
    num_sources: int = Field(..., description="Number of source files processed")


class IngestionStatusResponse(BaseModel):
    """Response model for /ingestion/status endpoint."""
    ingested: bool = Field(..., description="Whether documents have been ingested")
    num_chunks: int = Field(..., description="Number of chunks")
    num_sources: int = Field(..., description="Number of source files")
    embed_shape: Optional[list] = Field(default=None, description="Embedding matrix shape")


class DeleteRequest(BaseModel):
    """Request model for /delete endpoint."""
    collection: Optional[str] = Field(default=None, description="Collection name to delete (optional, deletes all if not provided)")


class DeleteResponse(BaseModel):
    """Response model for /delete endpoint."""
    status: str = Field(..., description="Deletion status")
    message: str = Field(..., description="Deletion message")


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.
    
    Returns:
        {"status": "ok"} if the service is healthy
    """
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents():
    """Ingest FAQ documents into the RAG system.
    
    This endpoint loads and chunks all FAQ documents, computes embeddings,
    and stores them in memory for querying.
    
    Returns:
        IngestResponse with ingestion statistics
        
    Raises:
        HTTPException: 500 for internal errors
    """
    try:
        logger.info("Starting document ingestion...")
        ingest_docs()
        status = get_ingestion_status()
        
        logger.info(f"Ingestion complete: {status['num_chunks']} chunks from {status['num_sources']} sources")
        
        return {
            "status": "ok",
            "num_chunks": status["num_chunks"],
            "num_sources": status["num_sources"]
        }
        
    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=DEBUG_MODE)
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")


@app.get("/ingestion/status")
async def ingestion_status():
    """Get the current ingestion status.
    
    Returns:
        Dict with details about ingested documents including Weaviate database status
    """
    status = get_ingestion_status()
    response = {
        "ingested": status["ingested"],
        "num_chunks": status["num_chunks"],
        "num_sources": status["num_sources"],
        "embed_shape": status["embed_shape"]
    }
    # Include Weaviate database info if available
    if "weaviate" in status:
        response["weaviate"] = status["weaviate"]
    return response


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """Ask a question and get an answer with sources.
    
    Args:
        request: AskRequest with question and optional top_k
        
    Returns:
        AskResponse with answer and source filenames
        
    Raises:
        HTTPException: 400 for bad input, 500 for internal errors
    """
    try:
        logger.info(f"[ASK] >>> Processing question: '{request.question}'")
        logger.info(f"[ASK] top_k: {request.top_k}")
        
        result = ask_faq_core(
            question=request.question,
            top_k=request.top_k
        )
        
        logger.info(f"[ASK] <<< Answer generated")
        logger.info(f"[ASK] Sources: {result['sources']}")
        logger.info(f"[ASK] Answer (first 200 chars): {result['answer'][:200]}...")
        logger.debug(f"[ASK] Full Answer: {result['answer']}")
        
        return {
            "answer": result["answer"],
            "sources": result["sources"]
        }
        
    except ValueError as e:
        logger.warning(f"[ASK] Bad request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ASK] Internal error: {e}", exc_info=DEBUG_MODE)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/delete", response_model=DeleteResponse)
async def delete_objects(request: Optional[DeleteRequest] = None):
    """Delete all objects or a specific collection (soft reset).
    
    This endpoint clears all ingested data from memory, effectively
    resetting the RAG system to its initial state.
    
    Args:
        request: Optional DeleteRequest with collection name
        
    Returns:
        DeleteResponse with deletion status
        
    Raises:
        HTTPException: 400 for bad input, 500 for internal errors
    """
    try:
        collection = request.collection if request else None
        
        if collection:
            logger.info(f"Deleting collection: {collection}")
            delete_collection(collection)
            message = f"Collection '{collection}' deleted successfully"
        else:
            logger.info("Deleting all objects")
            delete_all()
            message = "All objects deleted successfully"
        
        return {
            "status": "ok",
            "message": message
        }
        
    except ValueError as e:
        logger.warning(f"Bad request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Delete error: {e}", exc_info=DEBUG_MODE)
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API info."""
    status = get_ingestion_status()
    return {
        "name": "FAQ RAG API",
        "version": "1.0.0",
        "ingested": status["ingested"],
        "endpoints": {
            "GET /health": "Health check",
            "POST /ask": "Ask a question",
            "POST /ingest": "Ingest documents",
            "GET /ingestion/status": "Get ingestion status",
            "POST /delete": "Delete all objects (soft reset)"
        }
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)