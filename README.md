# MCP Server for FAQ RAG System

This directory contains MCP (Model Context Protocol) servers that integrate with the FAQ RAG API service.

## Files Overview

### `faq_mcp_server.py` - FAQ RAG MCP Server
An MCP server that wraps the FAQ RAG API endpoints as MCP tools:
- **ask_question**: Ask a question and get an answer with sources
- **get_ingestion_status**: Get the current status of document ingestion
- **ingest_documents**: Ingest FAQ documents into the RAG system

### `faq_agent.py` - FAQ Agent Client
A beeai framework agent that uses the FAQ MCP server to answer questions using the RAG system.

### `singleflowagent.py` - Original Single Flow Agent
Template agent using the beeai framework (original from Nick Nochette's BuildMCPServer).

## Startup FAQ MCP Server 🚀

### Prerequisites
- Python 3.10+
- UV package manager
- FAQ RAG API running on `http://localhost:8000`

### Run the MCP Server
```bash
cd MCPServer
uv venv
source .venv/bin/activate
uv add mcp requests
uv run faq_mcp_server.py
```

### Run the FAQ Agent
```bash
# In a separate terminal
cd MCPServer
source .venv/bin/activate
uv run faq_agent.py
```

### Environment Variables
```bash
export API_URL=http://localhost:8000
export LOG_LEVEL=DEBUG
```

## API Integration

The MCP server connects to the FAQ RAG API defined in the parent directory:

| MCP Tool | API Endpoint | Description |
|----------|--------------|-------------|
| `ask_question` | `POST /ask` | Ask a question with optional top_k |
| `get_ingestion_status` | `GET /ingestion/status` | Get document ingestion status |
| `ingest_documents` | `POST /ingest` | Trigger document ingestion |

## Sample Question Payload
```json
{
    "question": "How do I reset my password?",
    "top_k": 4
}
```

## Original Build MCP Server Reference

### See it live and in action 📺
<a href="https://www.linkedin.com/posts/nicholasrenotte_mcp-servers-make-tools-a-bunch-easier-for-activity-7305748751162163200-dIEn?utm_source=share&utm_medium=member_desktop&rcm=ACoAABbxZgUBrud9C531KZPQHCs2riXCiv9Av2A"><img src="https://i.imgur.com/Y2LN9dd.png"/></a>

### Startup Original MCP Server
1. Clone the original repo: `git clone https://github.com/nicknochnack/BuildMCPServer`
2. To run the MCP server:
   ```bash
   cd BuildMCPServer
   uv venv
   source .venv/bin/activate
   uv add .
   uv add ".[dev]"
   uv run mcp dev server.py
   ```
3. To run the agent, in a separate terminal:
   ```bash
   source .venv/bin/activate
   uv run singleflowagent.py
   ```

### Startup FastAPI Hosted ML Server 
```bash
git clone https://github.com/nicknochnack/CodeThat-FastML
cd CodeThat-FastML
pip install -r requirements.txt
uvicorn mlapi:app --reload
```
Detailed instructions on how to build it can also be found <a href="https://youtu.be/C82lT9cWQiA?si=dIsL6eM1lUMAVcf0">here</a>

## Other References 🔗
- <a href="https://github.com/RGGH/mcp-client-x/blob/main/src/client/mcp_client.py">Building MCP Clients (used in singleflow agent)</a>
- <a href="https://www.youtube.com/watch?v=C82lT9cWQiA&t=1003s">Original Video where I build the ML server</a>

## Who, When, Why?
👨‍💻 Original Author: Nick Renotte <br />
📅 Version: 1.x<br />
📜 License: This project is licensed under the MIT License

## Sample Payload (Original ML Model)
```json
[
    {
        "YearsAtCompany": 10,
        "EmployeeSatisfaction": 0.99,
        "Position": "Non-Manager",
        "Salary": 5
    }
]