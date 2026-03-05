"""
FAQ Agent MCP Server

An MCP server that provides FAQ RAG capabilities using the beeai framework
and the FAQ RAG API service.
"""
import asyncio
import os
import traceback
from typing import Any, Optional

from pydantic import ValidationError

from beeai_framework.agents.types import AgentExecutionConfig
from beeai_framework.backend.chat import ChatModel
from beeai_framework.backend.message import UserMessage
from beeai_framework.memory import UnconstrainedMemory

from beeai_framework.emitter.types import EmitterOptions
from beeai_framework.emitter.emitter import Emitter, EventMeta

# Import agent components
from beeai_framework.workflows.agent import AgentWorkflow, AgentWorkflowInput
from beeai_framework.workflows.workflow import WorkflowError

# MCP Tool
from beeai_framework.tools.mcp_tools import MCPTool
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"

# Get API URL from environment
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Create connection to FAQ RAG API Server via MCP
# The MCP server provides tools for interacting with the FAQ RAG system
faq_server_params = StdioServerParameters(
    command="python",
    args=[
        "faq_mcp_server.py",  # MCP server that wraps the FAQ RAG API
    ],
    env={"API_URL": API_URL},
)


async def tools_from_faq_server() -> MCPTool:
    """Connect to the FAQ MCP server and retrieve tools."""
    async with (
        stdio_client(faq_server_params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        return await MCPTool.from_client(session, faq_server_params)


async def process_agent_events(
    event_data: dict[str, Any], event_meta: EventMeta
) -> None:
    """Process agent events and log appropriately"""

    if event_meta.name == "error":
        print("Agent 🤖 : ", event_data["error"])
    elif event_meta.name == "retry":
        print("Agent 🤖 : ", "retrying the action...")
    elif event_meta.name == "update":
        print(
            f"Agent({event_data['update']['key']}) 🤖 : ",
            event_data["update"]["parsedValue"],
        )
    elif event_meta.name == "newToken":
        print(event_data["value"].get_text_content(), end="")


async def observer(emitter: Emitter) -> None:
    """Set up event observer for agent workflow."""
    emitter.on("*.*", process_agent_events, EmitterOptions(match_nested=True))


async def main() -> None:
    """Main entry point for the FAQ Agent."""
    # Initialize the language model
    llm = ChatModel.from_name("ollama:granite3.1-dense:8b")
    
    try:
        # Create workflow with FAQ agent
        workflow = AgentWorkflow(name="FAQ Assistant")
        
        # Add the FAQ agent with RAG capabilities
        workflow.add_agent(
            agent=AgentWorkflowInput(
                model_config={"stream": True},
                name="FAQAssistant",
                instructions="""You are an FAQ assistant that helps answer questions based on the company's FAQ documents.
                
Guidelines:
1. Use the ask_question tool to retrieve answers from the FAQ knowledge base
2. Always provide accurate information based on the retrieved context
3. If the context doesn't contain the answer, clearly state that
4. Be concise and helpful in your responses
5. Cite sources when available
""",
                tools=await tools_from_faq_server(),
                llm=llm,
                execution=AgentExecutionConfig(max_iterations=3),
            )
        )

        # Sample question for testing
        prompt = "How do I reset my password?"
        
        # Initialize memory with user prompt
        memory = UnconstrainedMemory()
        await memory.add(UserMessage(content=prompt))
        
        # Run the workflow
        await workflow.run(messages=memory.messages).observe(observer)

    except WorkflowError:
        traceback.print_exc()
    except ValidationError:
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())