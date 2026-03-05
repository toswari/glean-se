# MCP Server for FAQ RAG System

This directory contains MCP (Model Context Protocol) servers that integrate with the FAQ RAG API service, providing AI agents with tools to query and interact with the FAQ knowledge base.

## 📁 Files Overview

### `faq_mcp_server.py` - FAQ RAG MCP Server
An MCP server that wraps the FAQ RAG API endpoints as MCP tools:

| Tool | API Endpoint | Description |
|------|--------------|-------------|
| `ask_question` | `POST /ask` | Ask a question and get an answer with sources |
| `get_ingestion_status` | `GET /ingestion/status` | Get the current status of document ingestion |
| `ingest_documents` | `POST /ingest` | Ingest FAQ documents into the RAG system |

### `faq_agent.py` - FAQ Agent Client
A beeai framework agent that uses the FAQ MCP server to answer questions using the RAG system:
- **Name**: FAQAssistant
- **Model**: Ollama (granite3.1-dense:8b)
- **Features**: Streaming support, event observer, configurable API URL

### `singleflowagent.py` - Original Single Flow Agent
Template agent using the beeai framework (original from Nick Nochette's BuildMCPServer).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- UV package manager
- FAQ RAG API running on `http://localhost:8000`

### Step 1: Install Dependencies (from project root)
```bash
# From the parent directory
cd ..
pip install -r requirements.txt
```

### Step 2: Start the FAQ RAG API
```bash
# From the parent directory
python api_server.py
# or
./start-api.sh
```

### Step 3: Run the MCP Server
```bash
# From the project root directory
./start-mcp.sh
```

### Step 4: Run the FAQ Agent
```bash
# In a separate terminal, from the project root directory
./start-faq-agent.sh
```

---

## ⚙️ Configuration

### Environment Variables
```bash
export API_URL=http://localhost:8000
export LOG_LEVEL=DEBUG
```

### Sample Question Payload
```json
{
    "question": "How do I reset my password?",
    "top_k": 4
}
```

### Sample API Response
```json
{
    "answer": "To reset your password, go to the login page and click 'Forgot Password'...",
    "sources": ["faq_auth.md", "faq_sso.md"]
}
```

---

## 🔧 Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   FAQ Agent     │────▶│  MCP Server      │────▶│  FAQ RAG API    │
│  (beeai 框架)     │     │  (faq_mcp_server)│     │  (api_server)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Weaviate DB     │
                        │  (embeddings)    │
                        └──────────────────┘
```

---

## 📺 Original Build MCP Server Reference

A complete walkthrough on how to build an MCP server to serve a trained Random Forest model and integrate it with Bee Framework for ReAct interactivity.

### See it live and in action 📺
<a href="https://www.linkedin.com/posts/nicholasrenotte_mcp-servers-make-tools-a-bunch-easier-for-activity-7305748751162163200-dIEn?utm_source=share&utm_medium=member_desktop&rcm=ACoAABbxZgUBrud9C531KZPQHCs2riXCiv9Av2A"><img src="https://i.imgur.com/Y2LN9dd.png"/></a>

### Original Setup Instructions
1. Clone the original repo: `git clone https://github.com/nicknochnack/BuildMCPServer`
2. Run the MCP server:
   ```bash
   cd BuildMCPServer
   uv venv
   source .venv/bin/activate
   uv add .
   uv add ".[dev]"
   uv run mcp dev server.py
   ```
3. Run the agent:
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

### Sample Payload for Original ML Server
```json
[
    {
        "YearsAtCompany": 10,
        "EmployeeSatisfaction": 0.99,
        "Position": "Non-Manager",
        "Salary": 5
    }
]
```

---

## 🔗 References
- [Building MCP Clients](https://github.com/RGGH/mcp-client-x/blob/main/src/client/mcp_client.py)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Original Video where I build the ML server](https://www.youtube.com/watch?v=C82lT9cWQiA&t=1003s)

---

## 📄 License
👨‍💻 Original Author: Nick Renotte <br />
👨‍ FAQ RAG Adaptation: Teddy Oswari <br />
📅 Version: 1.x<br />
📜 License: MIT License

---

## Sample Payloads

### FAQ Question (MCP Tool)
```json
{
    "question": "How do I reset my password?",
    "top_k": 4
}