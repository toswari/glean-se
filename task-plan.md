# Task Plan - FAQ RAG System

A step-by-step checklist for implementing the FAQ RAG system. Execute tasks one at a time in order.

---

## Phase 1: Environment Setup

- [x] **Task 1.1: Setup Database**
  - Run: `./setup-database.sh start`
  - Verify: Weaviate is running on http://localhost:8080
  - Test: `curl http://localhost:8080/v1/.well-known/ready`

- [x] **Task 1.2: Configure Environment**
  - Update `.env` with Alibaba Cloud API key
  - Set `LLM_PROVIDER=alibaba`
  - Set `ALIBABA_API_KEY=sk-xxx`
  - Set `ALIBABA_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
  - Set `LLM_CHOICE=qwen3.5-flash`
  - Set `EMBEDDING_MODEL=text-embedding-v3`

- [x] **Task 1.3: Install Dependencies**
  - Run: `pip install -r requirements.txt`
  - Verify: `weaviate-client`, `openai`, `docling` are installed

---

## Phase 2: RAG Core Implementation

- [x] **Task 2.1: Implement `_chunk_text()`**
  - Split text into ~200 character chunks
  - Preserve sentence boundaries when possible
  - Return `List[str]`

- [x] **Task 2.2: Implement `_load_and_chunk_faqs()`**
  - Load all `.md` files from `FAQ_DIR`
  - Chunk each file's content
  - Return `(chunks: List[str], sources: List[str])`

- [x] **Task 2.3: Implement `_embed_texts()`**
  - Use Alibaba `text-embedding-v3` model
  - Return `(N, d)` float32 numpy array
  - Normalize rows for cosine similarity

- [x] **Task 2.4: Implement `_embed_query()`**
  - Use same embedding model as texts
  - Return `(d,)` float32 vector
  - Normalize for cosine similarity

- [x] **Task 2.5: Implement `_generate_answer()`**
  - Use Alibaba `qwen3.5-flash` model
  - Prompt: answer using only provided context
  - Include filename citations in response
  - Handle timeout/retry logic

- [x] **Task 2.6: Implement `_preload()`**
  - Load and chunk all FAQ documents
  - Compute embeddings for all chunks
  - L2-normalize embedding rows
  - Assign to global `_CHUNKS`, `_SOURCES`, `_CHUNK_EMBEDS`

- [x] **Task 2.7: Enable Preload**
  - Uncomment `_preload()` call at module import
  - Test: Run `python rag_core.py` and ask a question

---

## Phase 3: API Server Implementation

- [x] **Task 3.1: Create `api_server.py`**
  - Set up FastAPI application
  - Configure CORS if needed

- [x] **Task 3.2: Implement `GET /health`**
  - Return `{"status": "ok"}`
  - Status code: 200

- [x] **Task 3.3: Implement `POST /ask`**
  - Request body: `{"question": str, "top_k"?: int}`
  - Validate: non-empty question, top_k in range [1, 10]
  - Call `ask_faq_core()` from rag_core
  - Return: `{"answer": str, "sources": List[str]}`
  - Status codes: 200 (success), 400 (bad input), 500 (error)

- [x] **Task 3.4: Add Input Validation**
  - Pydantic model for request body
  - Validate question is non-empty
  - Validate top_k is within reasonable range

- [x] **Task 3.5: Add Error Handling**
  - Catch exceptions in `/ask` endpoint
  - Return appropriate status codes
  - Log errors with details

---

## Phase 4: Logging & Observability

- [x] **Task 4.1: Add LLM Call Logging**
  - Log: model name, input tokens, output tokens
  - Log: time to first token, tokens/second
  - Log: full prompt and response (debug mode)

- [x] **Task 4.2: Add Vector Search Logging**
  - Log: number of chunks searched
  - Log: top_k results with similarity scores
  - Log: search duration

- [x] **Task 4.3: Add Retry Logic**
  - Implement retry on timeout/unavailable
  - Log retry events with attempt number
  - Max 3 retries with exponential backoff

- [x] **Task 4.4: Configure Logging**
  - Use `LOG_LEVEL` from environment
  - Format: timestamp, level, message
  - Separate file for debug logs (optional)

---

## Phase 5: Testing & Verification

- [ ] **Task 5.1: Test Health Endpoint** (Pending - requires running server)
  - Run: `curl http://localhost:8000/health`
  - Expected: `{"status":"ok"}`

- [ ] **Task 5.2: Test Ask Endpoint** (Pending - requires running server)
  - Run: `curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question": "How do I reset my password?", "top_k": 4}'`
  - Expected: Answer with ≥2 source files

- [ ] **Task 5.3: Test Input Validation** (Pending - requires running server)
  - Empty question → 400 error
  - top_k = 0 → 400 error or default
  - top_k > 10 → 400 error or capped

- [ ] **Task 5.4: Test Multiple Questions** (Pending - requires running server)
  - Ask 3-5 different FAQ-related questions
  - Verify answers are relevant and cite sources

- [ ] **Task 5.5: Verify Logs** (Pending - requires running server)
  - Check logs show LLM call statistics
  - Check logs show vector search details
  - Check retry events are logged (if triggered)

---

## Phase 6: Documentation

- [x] **Task 6.1: Update README.md**
  - Add quick start instructions
  - Document environment variables
  - Include API usage examples

- [x] **Task 6.2: Document Design Decisions**
  - Chunk size rationale
  - Model selection rationale
  - Trade-offs made

---

## Quick Reference

### Start Services
```bash
# Start Weaviate
./setup-database.sh start

# Start API server
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### Test Commands
```bash
# Health check
curl http://localhost:8000/health

# Ask question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?", "top_k": 4}'
```

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `ALIBABA_API_KEY` | (required) | Alibaba Cloud API key |
| `ALIBABA_BASE_URL` | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | DashScope endpoint |
| `LLM_CHOICE` | `qwen-plus` | LLM model |
| `EMBEDDING_MODEL` | `text-embedding-v3` | Embedding model |
| `FAQ_DIR` | `./faqs` | FAQ documents directory |
| `CHUNK_SIZE` | `200` | Text chunk size |
| `TOP_K_DEFAULT` | `4` | Default top_k |
| `LOG_LEVEL` | `INFO` | Logging level |