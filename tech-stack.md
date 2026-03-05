# Technology Stack - FAQ RAG System

This document outlines the technology stack required to implement the FAQ RAG (Retrieval-Augmented Generation) system with Dockerized Weaviate vector database and Docling for document parsing.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Client        │────▶│   FastAPI Server │────▶│   RAG Core      │
│   (curl/HTTP)   │     │   (API Layer)    │     │   (Logic)       │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                    ┌─────────────────────────────────────┼─────────────────────────────────────┐
                    │                                     │                                     │
                    ▼                                     ▼                                     ▼
           ┌─────────────────┐                  ┌─────────────────┐                  ┌─────────────────┐
           │   Docling       │                  │   Weaviate      │                  │   Alibaba Cloud │
           │   (Parsing)     │                  │   (Vector DB)   │                  │   Model Studio  │
           └─────────────────┘                  └─────────────────┘                  │   (LLM/Embed)   │
                                                                                     └─────────────────┘
```

## Core Technologies

### 1. Programming Language & Runtime

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Runtime | Python | 3.10+ | Main application language |
| Package Manager | pip | - | Python dependency management |
| Virtual Environment | venv | - | Isolated Python environment |

### 2. API Framework

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Web Framework | FastAPI | 0.111.0+ | High-performance async API framework |
| ASGI Server | Uvicorn | 0.30.0+ | Lightning-fast ASGI server |
| Data Validation | Pydantic | 2.0.0+ | Data validation and settings management |

### 3. Vector Database (Dockerized)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Vector DB | Weaviate | 4.x+ | Vector similarity search and storage |
| Containerization | Docker | 24.0+ | Container runtime for Weaviate |
| Orchestration | Docker Compose | 2.20+ | Multi-container orchestration |

**Weaviate Docker Configuration:**
```yaml
# docker-compose.yml
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:1.25.0
    ports:
      - "8080:8080"
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
      - DEFAULT_VECTORIZER_MODULE=none
      - CLUSTER_HOSTNAME=weaviate
    volumes:
      - weaviate_data:/var/lib/weaviate

volumes:
  weaviate_data:
```

### 4. Document Parsing (Docling)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Document Parser | Docling | 2.x+ | Multi-format document parsing (PDF, DOCX, MD, HTML, images) |

**Selected: Docling for Future Expansion**

This project uses **Docling** as the document parsing solution to support future expansion beyond markdown files. While the current FAQ corpus consists of `.md` files, Docling provides the flexibility to easily add support for additional document formats without code changes.

**Supported Formats:**
| Format | Extension | Use Case |
|--------|-----------|----------|
| Markdown | `.md`, `.markdown` | Current FAQ documents |
| PDF | `.pdf` | Future: Policy documents, manuals, reports |
| Microsoft Word | `.docx` | Future: HR documents, guides |
| HTML | `.html`, `.htm` | Future: Web content, help pages |
| Images | `.png`, `.jpg`, `.tiff`, `.bmp` | Future: Screenshots, diagrams (with OCR) |
| PowerPoint | `.pptx` | Future: Training slides |
| Excel | `.xlsx` | Future: Data tables, spreadsheets |

**Docling Integration:**
```python
from docling.document_converter import DocumentConverter
from pathlib import Path

# Initialize the converter
converter = DocumentConverter()

# Convert any supported document to text
def parse_document(filepath: str) -> str:
    """Parse a document and return its text content."""
    result = converter.convert(filepath)
    return result.document.export_to_text()

# Example: Process all documents in a directory
def load_all_documents(doc_dir: str) -> list[str]:
    """Load and parse all documents from a directory."""
    documents = []
    for ext in ["*.md", "*.pdf", "*.docx", "*.html"]:
        for filepath in Path(doc_dir).glob(ext):
            text = parse_document(str(filepath))
            documents.append(text)
    return documents
```

**Key Features:**
- ✅ **Unified API**: Same interface for all document types
- ✅ **Layout Preservation**: Maintains document structure and hierarchy
- ✅ **Table Extraction**: Accurately extracts tables from PDFs and spreadsheets
- ✅ **OCR Support**: Extracts text from images and scanned PDFs
- ✅ **Metadata Extraction**: Preserves document metadata when available
- ✅ **Future-Proof**: Easy to add new document types as needs evolve

**Why Docling for This Project:**
1. **Current**: Handles markdown files efficiently
2. **Future**: Ready for PDF policies, Word documents, training materials
3. **Scalability**: No code changes needed to add new document types
4. **Consistency**: Single parsing pipeline for all document sources

### 5. AI/ML Components (Alibaba Cloud)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| LLM Provider | Alibaba Cloud Model Studio (DashScope) | - | Qwen series models for answer generation |
| Embedding Model | Alibaba DashScope | - | text-embedding-v3 for vector embeddings |
| Vector Operations | NumPy | 1.26.0+ | Efficient matrix operations for similarity |

**Alibaba Cloud Models:**

| Model Type | Model Name | Description |
|------------|------------|-------------|
| LLM | `qwen-turbo` | Fast, cost-effective model |
| LLM | `qwen-plus` | Balanced performance and cost (recommended) |
| LLM | `qwen-max` | Most capable model |
| LLM | `qwen2.5-72b-instruct` | Large instruction-tuned model |
| Embedding | `text-embedding-v2` | Previous generation embedding model |
| Embedding | `text-embedding-v3` | Latest embedding model with improved performance |

**Regional Endpoints:**

| Region | Endpoint |
|--------|----------|
| International | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Asia Pacific | `https://dashscope-ap-southeast-1.aliyuncs.com/compatible-mode/v1` |
| China | `https://dashscope.aliyuncs.com/compatible-mode/v1` |

### 6. Weaviate Python Client

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Weaviate Client | weaviate-client | 4.x+ | Python SDK for Weaviate interaction |

### 7. Alibaba Cloud SDK Compatibility

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| OpenAI SDK | openai | 1.30.0+ | Compatible with Alibaba DashScope OpenAI-compatible API |

## Complete Dependencies

### Python Requirements (`requirements.txt`)

```
# API Framework
fastapi>=0.111.0
uvicorn>=0.30.0
pydantic>=2.0.0

# Vector Database Client
weaviate-client>=4.0.0

# Document Parsing
docling>=2.0.0

# AI/ML - Alibaba Cloud (DashScope) compatible
openai>=1.30.0
numpy>=1.26.0

# Utilities
tqdm>=4.66.0
python-dotenv>=1.0.0
```

### Docker Requirements

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml (Full Stack):**
```yaml
version: '3.4'

services:
  weaviate:
    image: semitechnologies/weaviate:1.25.0
    ports:
      - "8080:8080"
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
      - DEFAULT_VECTORIZER_MODULE=none
      - CLUSTER_HOSTNAME=weaviate
    volumes:
      - weaviate_data:/var/lib/weaviate
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/.well-known/ready"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      # Alibaba Cloud Model Studio Configuration
      - LLM_PROVIDER=alibaba
      - ALIBABA_API_KEY=${ALIBABA_API_KEY}
      - ALIBABA_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
      - LLM_CHOICE=qwen-plus
      - EMBEDDING_MODEL=text-embedding-v3
      # Weaviate Configuration
      - WEAVIATE_URL=http://weaviate:8080
      - FAQ_DIR=/app/faqs
    depends_on:
      weaviate:
        condition: service_healthy
    volumes:
      - ./faqs:/app/faqs:ro

volumes:
  weaviate_data:
```

## Configuration & Environment Variables

### Alibaba Cloud Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `alibaba` | Provider selection (alibaba) |
| `ALIBABA_API_KEY` | (required) | Alibaba Cloud Model Studio API key |
| `ALIBABA_BASE_URL` | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | DashScope endpoint |
| `LLM_CHOICE` | `qwen-plus` | LLM model (qwen-turbo, qwen-plus, qwen-max, qwen2.5-72b-instruct) |
| `EMBEDDING_MODEL` | `text-embedding-v3` | Embedding model (text-embedding-v2, text-embedding-v3) |

### General Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WEAVIATE_URL` | `http://localhost:8080` | Weaviate server URL |
| `FAQ_DIR` | `./faqs` | Directory containing FAQ documents |
| `CHUNK_SIZE` | `200` | Text chunk size in characters |
| `TOP_K_DEFAULT` | `4` | Default number of results to retrieve |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check - returns `{"status":"ok"}` |
| POST | `/ask` | Ask a question - returns answer with sources |

**Request/Response Example:**
```bash
# Request
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?", "top_k": 4}'

# Response
{
  "answer": "To reset your password, navigate to...",
  "sources": ["faq_auth.md", "faq_sso.md"]
}
```

## Development Tools

| Tool | Purpose |
|------|---------|
| pytest | Unit and integration testing |
| black | Code formatting |
| flake8 | Linting |
| mypy | Type checking |

## System Requirements

| Requirement | Specification |
|-------------|---------------|
| CPU | 2+ cores recommended |
| RAM | 4GB minimum, 8GB recommended |
| Storage | 1GB+ for Weaviate data |
| Docker | Version 24.0+ |
| Python | 3.10 or higher |

## Quick Start Commands

```bash
# 1. Start Weaviate with Docker
docker-compose up -d weaviate

# 2. Set up Python environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Set environment variables for Alibaba Cloud
export ALIBABA_API_KEY=your-alibaba-api-key-here
export ALIBABA_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
export LLM_CHOICE=qwen-plus
export EMBEDDING_MODEL=text-embedding-v3
export WEAVIATE_URL=http://localhost:8080

# 4. Run the API server
uvicorn api_server:app --host 127.0.0.1 --port 8000

# 5. Test the API
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?", "top_k": 4}'
```

## Technology Summary

| Layer | Technology |
|-------|------------|
| **API** | FastAPI + Uvicorn |
| **Vector DB** | Weaviate (Dockerized) |
| **Document Parsing** | Docling |
| **LLM/Embeddings** | Alibaba Cloud Model Studio (DashScope) |
| **Language** | Python 3.10+ |
| **Containerization** | Docker + Docker Compose |

## References

- [Alibaba Cloud Model Studio Documentation](https://help.aliyun.com/zh/model-studio/)
- [DashScope API Reference](https://help.aliyun.com/zh/model-studio/developer-reference/)
- [Alibaba Cloud Console](https://modelstudio.console.alibabacloud.com/)
