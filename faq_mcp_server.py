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
import asyncio
from typing import Any

import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure server
server = Server("faq-rag-server")

# Get API URL from environment
API_URL = os.getenv("API_URL", "http://localhost:8000")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available FAQ RAG tools."""
    return [
        Tool(
            name="ask_question",
            description="Ask a question to the FAQ RAG system and get an answer with sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the FAQ system"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of chunks to retrieve (1-10, default: 4)",
                        "default": 4
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="get_ingestion_status",
            description="Get the current status of document ingestion",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="ingest_documents",
            description="Ingest FAQ documents into the RAG system",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls for FAQ RAG operations."""
    
    try:
        if name == "ask_question":
            question = arguments.get("question", "")
            top_k = arguments.get("top_k", 4)
            
            if not question or not question.strip():
                return [TextContent(
                    type="text",
                    text="Error: Question cannot be empty"
                )]
            
            # Call the FAQ RAG API
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
                
                return [TextContent(type="text", text=formatted_response)]
            else:
                return [TextContent(
                    type="text",
                    text=f"Error: API returned status {response.status_code}"
                )]
        
        elif name == "get_ingestion_status":
            response = requests.get(f"{API_URL}/ingestion/status", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                status_text = (
                    f"Ingestion Status:\n"
                    f"- Ingested: {result.get('ingested', False)}\n"
                    f"- Chunks: {result.get('num_chunks', 0)}\n"
                    f"- Sources: {result.get('num_sources', 0)}"
                )
                return [TextContent(type="text", text=status_text)]
            else:
                return [TextContent(
                    type="text",
                    text=f"Error: API returned status {response.status_code}"
                )]
        
        elif name == "ingest_documents":
            response = requests.post(f"{API_URL}/ingest", timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                status_text = (
                    f"Ingestion Complete:\n"
                    f"- Status: {result.get('status', 'unknown')}\n"
                    f"- Chunks: {result.get('num_chunks', 0)}\n"
                    f"- Sources: {result.get('num_sources', 0)}"
                )
                return [TextContent(type="text", text=status_text)]
            else:
                return [TextContent(
                    type="text",
                    text=f"Error: API returned status {response.status_code}"
                )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
    
    except requests.exceptions.ConnectionError:
        return [TextContent(
            type="text",
            text=f"Error: Cannot connect to FAQ RAG API at {API_URL}"
        )]
    except requests.exceptions.Timeout:
        return [TextContent(
            type="text",
            text="Error: Request timed out"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())