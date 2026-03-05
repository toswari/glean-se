# Debug Logging Implementation Guide

## Lessons Learned from RAG System Debug Implementation

This document provides coding agent instructions for implementing comprehensive debug logging in Python applications, based on lessons learned from implementing debug logging in a RAG (Retrieval-Augmented Generation) system.

---

## 1. Environment-Based Log Level Configuration

**DO:**
```python
# Read log level from environment variable with sensible default
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
logging.basicConfig(
    level=logging.DEBUG,  # Always use DEBUG as base level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True  # Force reconfiguration
)
logger = logging.getLogger(__name__)
```

**DON'T:**
```python
# Don't hardcode log level
logging.basicConfig(level=logging.INFO)  # BAD: Can't be overridden
```

**Why:** Setting `level=logging.DEBUG` in basicConfig allows all log levels to pass through. The actual filtering is controlled by the environment variable, giving runtime flexibility without code changes.

---

## 2. Use Named Loggers for Different Concerns

**DO:**
```python
# Main application logger
logger = logging.getLogger(__name__)

# Specialized logger for specific concerns (e.g., LLM stats)
llm_logger = logging.getLogger('llm_stats')
llm_logger.setLevel(logging.INFO)
if not llm_logger.handlers:
    llm_handler = logging.StreamHandler()
    llm_handler.setFormatter(DetailedFormatter('%(message)s'))
    llm_logger.addHandler(llm_handler)
```

**Why:** Named loggers allow targeted logging configuration. You can route different loggers to different outputs or apply different formatters.

---

## 3. Implement Structured Logging with Context

**DO:**
```python
# Include context in every log message
logger.info(f"[VECTOR-DB] >>> Starting vector search: {len(_CHUNK_EMBEDS)} embeddings, top_k={top_k}")
logger.debug(f"[VECTOR-DB] Query embedding shape: {q_emb.shape}")
logger.debug(f"[VECTOR-DB] Similarity scores computed: min={sims.min():.4f}, max={sims.max():.4f}, mean={sims.mean():.4f}")
```

**Format Pattern:**
- `[COMPONENT]` prefix for easy filtering
- `>>>` for operation start, `<<<` for operation end
- Include relevant parameters and statistics

**Why:** Structured logs are easier to grep, filter, and parse programmatically.

---

## 4. Log at Appropriate Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| `DEBUG` | Detailed diagnostic info for developers | Similarity scores, embedding shapes, batch contents |
| `INFO` | Normal operational messages | Operation start/end, completion status |
| `WARNING` | Unexpected but handled situations | Retry attempts, fallback values |
| `ERROR` | Errors that prevent operation completion | API failures, file not found |

**DO:**
```python
# DEBUG: Detailed technical info
logger.debug(f"[EMBED] Batch 1: Sending {len(batch)} texts to embedding API...")
logger.debug(f"[EMBED] Batch 1 texts (first 100 chars): {batch[0][:100]}...")

# INFO: Operation milestones
logger.info(f"[EMBED] >>> Embedding {len(texts)} texts using model '{embed_model}'...")
logger.info(f"[EMBED] <<< Completed: {len(result)} embeddings, shape={result.shape}")

# WARNING: Recoverable issues
logger.warning(f"[LLM] Call failed (attempt {attempt + 1}/{max_retries}): {error_msg}")

# ERROR: Critical failures
logger.error(f"[LLM] Call failed after {max_retries} attempts: {error_msg}")
```

---

## 5. Use Custom Formatters for Specialized Output

**DO:**
```python
class DetailedFormatter(logging.Formatter):
    """Custom formatter for detailed LLM logging."""
    def format(self, record):
        msg = record.getMessage()
        parts = []
        if hasattr(record, 'llm_model'):
            parts.append(f"model={record.llm_model}")
        if hasattr(record, 'input_tokens'):
            parts.append(f"input_tokens={record.input_tokens}")
        if hasattr(record, 'elapsed'):
            parts.append(f"elapsed={record.elapsed:.2f}s")
        if hasattr(record, 'tokens_per_sec'):
            parts.append(f"tokens/sec={record.tokens_per_sec:.1f}")
        
        if parts:
            return f"{msg} | {' | '.join(parts)}"
        return msg

# Use with extra parameters
llm_logger.info(
    "LLM Call completed",
    extra={
        'llm_model': llm_model,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'elapsed': elapsed,
        'tokens_per_sec': tokens_per_sec
    }
)
```

**Why:** Custom formatters allow rich, structured output without cluttering the main logging logic.

---

## 6. Log Entry and Exit Points with Data Previews

**DO:**
```python
# Log function entry with parameters
logger.info(f"[ASK] >>> Processing question: '{question[:100]}...'")
logger.info(f"[ASK] top_k: {top_k}")

# Log function exit with results
logger.info(f"[ASK] <<< Answer generated")
logger.info(f"[ASK] Sources: {sources_out}")
logger.debug(f"[ASK] Full Answer: {answer}")
```

**Why:** Entry/exit logging creates a clear trace through the code. Data previews help debugging without exposing sensitive full content.

---

## 7. Include Statistics and Metrics

**DO:**
```python
# Log computed statistics
logger.debug(f"[VECTOR-DB] Similarity scores computed: min={sims.min():.4f}, max={sims.max():.4f}, mean={sims.mean():.4f}")

# Log performance metrics
logger.info(f"[LLM] Statistics: model={llm_model}, input={input_tokens} tokens, output={output_tokens} tokens, {elapsed:.2f}s, {tokens_per_sec:.1f} tokens/sec")
```

**Why:** Statistics provide insight into data distributions and performance characteristics.

---

## 8. Handle Output Buffering for Real-Time Debugging

**In shell scripts:**
```bash
# Export PYTHONUNBUFFERED to prevent Python output buffering
export PYTHONUNBUFFERED=1

# Run uvicorn directly (avoid stdbuf which may not be available on all systems)
exec uvicorn api_server:app \
    --host "$HOST" \
    --port "$PORT" \
    --log-level debug \
    2>&1 | tee -a "${API_LOG_FILE}"
```

**Why:** Python buffers output by default, which delays log visibility. `PYTHONUNBUFFERED=1` ensures logs appear immediately in the terminal.

---

## 9. Log External API Calls

**DO:**
```python
# Log request details
logger.debug(f"[EMBED] Batch {batch_num}: Sending {len(batch)} texts to embedding API...")
logger.debug(f"[EMBED] Batch {batch_num} texts (first 100 chars): {batch[0][:100]}...")

# Log response details
logger.debug(f"[EMBED] Batch {batch_num}: Received {len(batch_embeddings)} embeddings, dim={len(batch_embeddings[0]) if batch_embeddings else 0}")

# Log errors with context
logger.error(f"[EMBED] Batch {batch_num} error: {e}")
```

**Why:** External API calls are common failure points. Logging request/response details aids debugging.

---

## 10. Provide Data Previews for Large Content

**DO:**
```python
# Show first N characters of large content
logger.debug(f"[LLM] Context (first 500 chars): {context[:500]}...")
logger.debug(f"[EMBED] Batch texts (first 100 chars): {batch[0][:100]}...")

# Show shapes and dimensions
logger.debug(f"[VECTOR-DB] Query embedding shape: {q_emb.shape}")
logger.debug(f"[EMBED] Received {len(batch_embeddings)} embeddings, dim={len(batch_embeddings[0])}")
```

**Why:** Full content can flood logs. Previews provide enough context for debugging while keeping logs readable.

---

## 11. Use Consistent Log Tagging

**Pattern:**
```
[TIMESTAMP] - [MODULE] - [LEVEL] - [COMPONENT] Message with context
```

**Example Output:**
```
2026-03-05 09:49:36 - rag_core - DEBUG - [VECTOR-DB] Similarity scores computed: min=0.3216, max=0.7834, mean=0.4781
2026-03-05 09:49:36 - rag_core - INFO - [LLM] >>> Calling qwen3.5-flash...
2026-03-05 09:49:40 - rag_core - INFO - [LLM] <<< Response received
```

**Why:** Consistent tagging enables easy filtering with tools like `grep`:
```bash
# Filter by component
tail -f /tmp/api_server.log | grep "\[VECTOR-DB\]"

# Filter by level
tail -f /tmp/api_server.log | grep "DEBUG"

# Filter by operation
tail -f /tmp/api_server.log | grep ">>>"
```

---

## 12. Quick Reference: Complete Example

```python
import os
import logging

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True
)
logger = logging.getLogger(__name__)

def process_data(data, threshold=0.5):
    """Process data with comprehensive logging."""
    # Entry point
    logger.info(f"[PROCESS] >>> Starting processing: {len(data)} items, threshold={threshold}")
    logger.debug(f"[PROCESS] Data preview: {data[:3]}...")
    
    # Processing
    results = []
    for i, item in enumerate(data):
        score = compute_score(item)
        logger.debug(f"[PROCESS] Item {i}: score={score:.4f}")
        if score > threshold:
            results.append(item)
    
    # Statistics
    logger.debug(f"[PROCESS] Scores: min={min_score:.4f}, max={max_score:.4f}, mean={mean_score:.4f}")
    
    # Exit point
    logger.info(f"[PROCESS] <<< Completed: {len(results)}/{len(data)} items passed")
    
    return results
```

---

## Summary Checklist

- [ ] Use environment variable for log level (`LOG_LEVEL`)
- [ ] Set base logging to DEBUG in basicConfig
- [ ] Use named loggers for different concerns
- [ ] Add `[COMPONENT]` prefix to all log messages
- [ ] Log entry (`>>>`) and exit (`<<<`) points
- [ ] Include data previews for large content
- [ ] Log statistics (min, max, mean, shapes)
- [ ] Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Add custom formatters for specialized output
- [ ] Handle output buffering (`PYTHONUNBUFFERED=1`)
- [ ] Log external API calls (request/response)
- [ ] Include timing and performance metrics
- [ ] Use consistent formatting for easy grep/filter

---

## Related Files

- `rag_core.py` - Core RAG logic with comprehensive logging
- `api_server.py` - FastAPI server with request/response logging
- `start-api.sh` - Server startup script with unbuffered output
- `.env` - Environment configuration including `LOG_LEVEL=DEBUG`