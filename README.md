# FAQ RAG System

A Retrieval-Augmented Generation (RAG) system that answers questions based on FAQ documents using Alibaba Cloud's LLM and embedding models.

## Architecture

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

## Quick Start

### 1. Start Weaviate Database

```bash
./setup-database.sh start
```

### 2. Configure Environment

Edit `.env` file with your Alibaba Cloud API key:

```bash
ALIBABA_API_KEY=sk-your-api-key-here
ALIBABA_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
LLM_CHOICE=qwen3.5-flash
EMBEDDING_MODEL=text-embedding-v3
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API Server

```bash
./start-api.sh

# Or directly with uvicorn
uvicorn api_server:app --host 127.0.0.1 --port 8000
```

### 5. Ingest FAQ Documents

Before asking questions, you must ingest the FAQ documents:

```bash
# Using the ingest script (recommended)
./ingest-docs.sh

# Or via API endpoint
curl -X POST http://localhost:8000/ingest
```

### 6. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Check ingestion status
curl http://localhost:8000/ingestion/status

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?", "top_k": 4}'
```

## API Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

### POST /ingest

Ingest FAQ documents into the RAG system.

**Request:**
```bash
curl -X POST http://localhost:8000/ingest
```

**Response:**
```json
{
  "status": "ok",
  "num_chunks": 42,
  "num_sources": 3
}
```

### GET /ingestion/status

Get the current ingestion status.

**Response:**
```json
{
  "ingested": true,
  "num_chunks": 42,
  "num_sources": 3,
  "embed_shape": [42, 1536]
}
```

### POST /ask

Ask a question and get an answer with sources.

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
  "answer": "Use the reset link on the login page [faq_auth.md].",
  "sources": ["faq_auth.md", "faq_employee.md"]
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input (empty question, out of range top_k)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### POST /delete

Delete all objects or a specific collection (soft reset). Clears all ingested data from memory.

**Request (delete all):**
```bash
curl -X POST http://localhost:8000/delete
```

**Request (delete specific collection):**
```bash
curl -X POST http://localhost:8000/delete \
  -H "Content-Type: application/json" \
  -d '{"collection": "YourCollection"}'
```

**Response:**
```json
{
  "status": "ok",
  "message": "All objects deleted successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid collection name
- `500 Internal Server Error`: Server error

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALIBABA_API_KEY` | (required) | Alibaba Cloud Model Studio API key |
| `ALIBABA_BASE_URL` | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | DashScope endpoint |
| `LLM_CHOICE` | `qwen-plus` | LLM model (qwen-turbo, qwen-plus, qwen-max, qwen2.5-72b-instruct, qwen3.5-flash) |
| `EMBEDDING_MODEL` | `text-embedding-v3` | Embedding model (text-embedding-v2, text-embedding-v3) |
| `FAQ_DIR` | `./faqs` | Directory containing FAQ markdown files |
| `CHUNK_SIZE` | `200` | Text chunk size in characters |
| `TOP_K_DEFAULT` | `4` | Default number of chunks to retrieve |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DEBUG_MODE` | `false` | Enable debug mode for detailed error messages |

## Database Management

The `setup-database.sh` script manages the Weaviate vector database:

```bash
./setup-database.sh start     # Start the database
./setup-database.sh stop      # Stop the database
./setup-database.sh restart   # Restart the database
./setup-database.sh status    # Check status
./setup-database.sh logs      # View logs
./setup-database.sh clean     # Remove container and data
./setup-database.sh help      # Show help
```

## Project Structure

```
glean-se/
├── api_server.py         # FastAPI server
├── rag_core.py           # RAG core logic
├── setup-database.sh     # Database setup script
├── setup-env.sh          # Environment setup script
├── start-api.sh          # API server start script
├── ingest-docs.sh        # Document ingestion script
├── test-all-api.sh       # API test script (excludes ingest/delete)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create from template)
├── faqs/                 # FAQ markdown files
│   ├── faq_auth.md
│   ├── faq_employee.md
│   └── faq_sso.md
└── README.md             # This file
```

## Design Decisions

### Chunk Size (200 characters)
- Small enough to capture focused context
- Large enough to contain meaningful information
- Preserves sentence boundaries when possible

### Model Selection
- **LLM**: qwen3.5-flash - Fast and cost-effective for FAQ answering
- **Embeddings**: text-embedding-v3 - Latest model with improved performance

### Retrieval
- **Cosine similarity** for vector similarity computation
- Embeddings are L2-normalized before storage, allowing dot product to equal cosine similarity
- Query embeddings are also L2-normalized for consistent similarity calculation
- Top-k retrieval (default: 4 chunks)
- Source file tracking for citations

**Cosine Similarity Implementation:**
```python
# L2 normalize embeddings for cosine similarity
norms = np.linalg.norm(result, axis=1, keepdims=True)
result = result / norms

# Compute cosine similarity via dot product (equivalent for normalized vectors)
sims = _CHUNK_EMBEDS @ q_emb  # q_emb is also L2-normalized
```

### Retry Logic
- 3 retries with exponential backoff
- Handles timeouts and transient failures
- Logs retry events for debugging

## Logging

The system logs:
- LLM calls: model, input/output tokens, elapsed time, tokens/second
- Vector search: number of chunks, top_k results
- Retry events: attempt number, error message
- API requests: question, top_k, sources

Example log output:
```
2026-03-04 20:56:59,900 - root - INFO - LLM Call: model=qwen3.5-flash, input_tokens=245, output_tokens=581, elapsed=4.75s, tokens/sec=122.4
```

## Development

### Run Tests

Run the automated test script (tests all endpoints except ingest and delete):

```bash
./test-all-api.sh
```

Or test manually:

```bash
# Health check
curl http://localhost:8000/health

# Test ask endpoint
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?", "top_k": 4}'

# Test input validation (should return 422)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "", "top_k": 4}'

# Test delete endpoint (soft reset)
curl -X POST http://localhost:8000/delete
```

## Troubleshooting

### API Key Error
```
RuntimeError: ALIBABA_API_KEY or OPENAI_API_KEY is not set
```
**Solution**: Set `ALIBABA_API_KEY` in `.env` file or as environment variable.

### Database Connection Error
```
Error: Weaviate is not responding
```
**Solution**: Run `./setup-database.sh start` to start the database.

### Model Not Found
```
Error: Model not found
```
**Solution**: Check `LLM_CHOICE` and `EMBEDDING_MODEL` in `.env` are valid model names.

## License

MIT