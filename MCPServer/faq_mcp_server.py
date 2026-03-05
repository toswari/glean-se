"""
FAQ MCP Server

An MCP server that wraps the FAQ RAG API endpoints as MCP tools.
This server provides tools for:
- Asking questions to the FAQ RAG system
- Getting ingestion status
- Ingesting documents
"""
import os
import json
import logging
from typing import List

from mcp.server.fastmcp import FastMCP
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="mcp_server.log",
    filemode="a"
)

# Create the server
mcp = FastMCP("faq_rag")

# Get API URL from environment
API_URL = os.getenv("API_URL", "http://localhost:8000")


@mcp.tool()
def ask_question(question: str, top_k: int = 4) -> str:
    """Ask a question to the FAQ RAG system and get an answer with sources.
    
    Args:
        question: The question to ask the FAQ system
        top_k: Number of chunks to retrieve (1-10, default: 4)
    
    Returns:
        str: The answer with sources
    """
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question.strip(), "top_k": top_k},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "No answer generated")
            sources = result.get("sources", [])
            
            # Format the response
            formatted_response = f"Answer: {answer}"
            if sources:
                formatted_response += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)
            
            return formatted_response
        else:
            return f"Error: API returned status {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return f"Error: Cannot connect to FAQ RAG API at {API_URL}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_ingestion_status() -> str:
    """Get the current status of document ingestion.
    
    Returns:
        str: The ingestion status
    """
    try:
        response = requests.get(f"{API_URL}/ingestion/status", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            status_text = (
                f"Ingestion Status:\n"
                f"- Ingested: {result.get('ingested', False)}\n"
                f"- Chunks: {result.get('num_chunks', 0)}\n"
                f"- Sources: {result.get('num_sources', 0)}"
            )
            return status_text
        else:
            return f"Error: API returned status {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return f"Error: Cannot connect to FAQ RAG API at {API_URL}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def ingest_documents() -> str:
    """Ingest FAQ documents into the RAG system.
    
    Returns:
        str: The ingestion result
    """
    try:
        response = requests.post(f"{API_URL}/ingest", timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            status_text = (
                f"Ingestion Complete:\n"
                f"- Status: {result.get('status', 'unknown')}\n"
                f"- Chunks: {result.get('num_chunks', 0)}\n"
                f"- Sources: {result.get('num_sources', 0)}"
            )
            return status_text
        else:
            return f"Error: API returned status {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return f"Error: Cannot connect to FAQ RAG API at {API_URL}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")