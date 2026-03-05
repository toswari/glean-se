import os
import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

import numpy as np
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv

# Weaviate client (optional - only used if Weaviate is configured)
try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Configure logging - use DEBUG level to capture all logs
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True  # Force reconfiguration
)
logger = logging.getLogger(__name__)

# Create custom formatter for detailed LLM logging
class DetailedFormatter(logging.Formatter):
    """Custom formatter for detailed LLM logging."""
    def format(self, record):
        # Build formatted message with LLM statistics
        msg = record.getMessage()
        parts = []
        if hasattr(record, 'llm_model'):
            parts.append(f"model={record.llm_model}")
        if hasattr(record, 'input_tokens'):
            parts.append(f"input_tokens={record.input_tokens}")
        if hasattr(record, 'output_tokens'):
            parts.append(f"output_tokens={record.output_tokens}")
        if hasattr(record, 'elapsed'):
            parts.append(f"elapsed={record.elapsed:.2f}s")
        if hasattr(record, 'tokens_per_sec'):
            parts.append(f"tokens/sec={record.tokens_per_sec:.1f}")
        
        if parts:
            return f"{msg} | {' | '.join(parts)}"
        return msg

# Add custom LLM statistics logger
llm_logger = logging.getLogger('llm_stats')
llm_logger.setLevel(logging.INFO)
if not llm_logger.handlers:
    llm_handler = logging.StreamHandler()
    llm_handler.setFormatter(DetailedFormatter('%(message)s'))
    llm_logger.addHandler(llm_handler)

# --- Config ---
FAQ_DIR = os.getenv("FAQ_DIR", str(Path(__file__).parent / "faqs"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-ada-002")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "200"))
TOP_K_DEFAULT = int(os.getenv("TOP_K_DEFAULT", "4"))

# Initialize the OpenAI client for Alibaba Cloud (fail fast if key missing)
# Using Alibaba Cloud Model Studio with OpenAI-compatible API
_API_KEY = os.getenv("ALIBABA_API_KEY") or os.getenv("OPENAI_API_KEY")
if not _API_KEY:
    raise RuntimeError("ALIBABA_API_KEY or OPENAI_API_KEY is not set")

_BASE_URL = os.getenv("ALIBABA_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
client = OpenAI(api_key=_API_KEY, base_url=_BASE_URL)

# Globals (loaded on-demand via ingest_docs())
_CHUNKS: List[str] = []
_SOURCES: List[str] = []
_CHUNK_EMBEDS: np.ndarray | None = None  # shape: (N, d)

# Flag to track if documents have been ingested
_DOCS_INGESTED: bool = False

# ---------------- Core utilities ----------------
def _chunk_text(text: str, size: int = CHUNK_SIZE) -> List[str]:
    """Split text into fixed-size chunks, preserving sentence boundaries when possible.
    
    Args:
        text: The text to chunk
        size: Maximum chunk size in characters (default: CHUNK_SIZE)
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + size
        
        # If we're at the end of the text, just take what's left
        if end >= len(text):
            chunks.append(text[start:].strip())
            break
        
        # Try to find a sentence boundary (period, newline, etc.)
        chunk_text = text[start:end]
        
        # Look for sentence endings in reverse order
        for sep in ['.\n', '. ', '\n\n', '\n', '  ', ' ']:
            last_sep = chunk_text.rfind(sep)
            if last_sep > size // 2:  # Only split if we're past halfway
                end = start + last_sep + len(sep)
                break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end
    
    return [c for c in chunks if c]  # Filter out empty chunks

def _load_and_chunk_faqs(faq_dir: str) -> Tuple[List[str], List[str]]:
    """Load all .md files from faq_dir, chunk each, and return (chunks, source_filenames).
    
    Args:
        faq_dir: Directory containing FAQ markdown files
    
    Returns:
        Tuple of (list of text chunks, list of corresponding source filenames)
    """
    chunks = []
    sources = []
    
    faq_path = Path(faq_dir)
    if not faq_path.exists():
        raise FileNotFoundError(f"FAQ directory not found: {faq_dir}")
    
    md_files = sorted(faq_path.glob("*.md"))
    if not md_files:
        raise ValueError(f"No .md files found in {faq_dir}")
    
    for md_file in tqdm(md_files, desc="Loading FAQ files"):
        try:
            content = md_file.read_text(encoding="utf-8")
            file_chunks = _chunk_text(content)
            
            for chunk in file_chunks:
                chunks.append(chunk)
                sources.append(md_file.name)
        except Exception as e:
            print(f"Warning: Failed to process {md_file.name}: {e}")
    
    return chunks, sources

def _embed_texts(texts: List[str]) -> np.ndarray:
    """Create embeddings for texts using Alibaba Cloud embedding model.
    
    Args:
        texts: List of texts to embed
    
    Returns:
        (N, d) float32 numpy array of embeddings, L2-normalized
    """
    if not texts:
        logger.info("[EMBED] No texts to embed")
        return np.array([], dtype=np.float32).reshape(0, 0)
    
    embed_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
    embeddings = []
    
    logger.info(f"[EMBED] >>> Embedding {len(texts)} texts using model '{embed_model}'...")
    
    # Process in batches to avoid rate limits
    batch_size = 10
    for i in tqdm(range(0, len(texts), batch_size), desc="Embedding texts"):
        batch = texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        try:
            logger.debug(f"[EMBED] Batch {batch_num}: Sending {len(batch)} texts to embedding API...")
            logger.debug(f"[EMBED] Batch {batch_num} texts (first 100 chars): {batch[0][:100]}...")
            
            response = client.embeddings.create(
                model=embed_model,
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
            
            logger.debug(f"[EMBED] Batch {batch_num}: Received {len(batch_embeddings)} embeddings, dim={len(batch_embeddings[0]) if batch_embeddings else 0}")
            
        except Exception as e:
            logger.error(f"[EMBED] Batch {batch_num} error: {e}")
            # Fill with zeros for failed embeddings
            embeddings.extend([np.zeros(1536).tolist() for _ in batch])
    
    # Convert to numpy array and normalize
    result = np.array(embeddings, dtype=np.float32)
    
    # L2 normalize each row for cosine similarity
    norms = np.linalg.norm(result, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    result = result / norms
    
    logger.info(f"[EMBED] <<< Completed: {len(result)} embeddings, shape={result.shape}")
    
    return result

def _embed_query(q: str) -> np.ndarray:
    """Create an embedding for the query using Alibaba Cloud embedding model.
    
    Args:
        q: Query text to embed
    
    Returns:
        (d,) float32 numpy array of embedding, L2-normalized
    """
    embed_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
    
    logger.debug(f"[EMBED-QUERY] >>> Embedding query: '{q[:100]}...'")
    
    try:
        response = client.embeddings.create(
            model=embed_model,
            input=[q]
        )
        embedding = response.data[0].embedding
        result = np.array(embedding, dtype=np.float32)
        
        # L2 normalize for cosine similarity
        norm = np.linalg.norm(result)
        if norm > 0:
            result = result / norm
        
        logger.debug(f"[EMBED-QUERY] <<< Received embedding, dim={len(embedding)}")
        
        return result
    except Exception as e:
        logger.error(f"[EMBED-QUERY] Error: {e}")
        # Return zero vector as fallback
        return np.zeros(1536, dtype=np.float32)

def _generate_answer(context: str, question: str) -> str:
    """Call the LLM to answer using only provided context and cite filenames.
    
    Implements retry logic with exponential backoff and logs call statistics.
    
    Args:
        context: Retrieved context chunks with source filenames
        question: User's question
    
    Returns:
        Generated answer string
    """
    import time
    
    llm_model = os.getenv("LLM_CHOICE", "qwen-plus")
    max_retries = 3
    base_delay = 1.0  # seconds
    
    # Build the full prompt
    system_prompt = "Answer questions using only the provided context. Cite source filenames."
    user_prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided context.
Use the context below to answer the question. If the answer cannot be found in the context, say so.
Always cite the source filenames when referencing information.

Context:
{context}

Question: {question}

Answer (cite sources like [filename.md]):"""

    for attempt in range(max_retries):
        start_time = time.time()
        
        try:
            # Log the request details
            logger.info(f"[LLM] >>> Calling {llm_model}...")
            logger.debug(f"[LLM] System: {system_prompt}")
            logger.debug(f"[LLM] Question: {question}")
            logger.debug(f"[LLM] Context (first 500 chars): {context[:500]}...")
            
            response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1024,
                stream=False
            )
            
            # Get timing and token info
            elapsed = time.time() - start_time
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            tokens_per_sec = output_tokens / elapsed if elapsed > 0 else 0
            
            # Get the answer
            answer = response.choices[0].message.content
            
            # Log detailed statistics to llm_stats logger
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
            
            # Log full request/response details
            logger.info(f"[LLM] <<< Response received")
            logger.info(f"[LLM] Statistics: model={llm_model}, input={input_tokens} tokens, output={output_tokens} tokens, {elapsed:.2f}s, {tokens_per_sec:.1f} tokens/sec")
            logger.info(f"[LLM] Answer (first 200 chars): {answer[:200]}...")
            logger.debug(f"[LLM] Full Answer: {answer}")
            
            return answer.strip()
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"[LLM] Call failed (attempt {attempt + 1}/{max_retries}): {error_msg}")
            logger.debug(f"[LLM] Error details:", exc_info=True)
            
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logger.info(f"[LLM] Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"[LLM] Call failed after {max_retries} attempts: {error_msg}")
                return f"Error generating answer: {error_msg}"
    
    return "Error: Failed to generate answer after retries"

# ---------------- Public API ----------------
def ask_faq_core(question: str, top_k: int = TOP_K_DEFAULT) -> Dict[str, object]:
    """Ask a question and get an answer with sources.
    
    This function performs:
    1. Query embedding
    2. Vector similarity search against stored embeddings
    3. Top-k retrieval
    4. LLM answer generation
    
    Args:
        question: The question to ask
        top_k: Number of chunks to retrieve (default: TOP_K_DEFAULT)
    
    Returns:
        Dict with 'answer' and 'sources' keys
        
    Raises:
        ValueError: If question is empty
    """
    q = (question or "").strip()
    if not q:
        raise ValueError("question is required")
    if top_k <= 0:
        top_k = TOP_K_DEFAULT

    # If not yet implemented, return a safe placeholder so wrappers run.
    if _CHUNK_EMBEDS is None or len(_CHUNKS) == 0:
        logger.warning("[VECTOR-DB] No embeddings available for search")
        return {
            "answer": "Placeholder: implement retrieval + grounded generation with citations.",
            "sources": ["faq_auth.md", "faq_employee.md"],
        }

    logger.info(f"[VECTOR-DB] >>> Starting vector search: {len(_CHUNK_EMBEDS)} embeddings, top_k={top_k}")
    
    # Embed the query
    q_emb = _embed_query(q)
    logger.debug(f"[VECTOR-DB] Query embedding shape: {q_emb.shape}")
    
    # Compute cosine similarity (dot product since vectors are normalized)
    sims = _CHUNK_EMBEDS @ q_emb
    logger.debug(f"[VECTOR-DB] Similarity scores computed: min={sims.min():.4f}, max={sims.max():.4f}, mean={sims.mean():.4f}")
    
    # Get top-k indices (sorted by similarity, highest first)
    top_idx = np.argsort(sims)[-top_k:][::-1]
    top_sims = sims[top_idx]
    
    logger.info(f"[VECTOR-DB] <<< Retrieved {len(top_idx)} chunks")
    for i, (idx, sim) in enumerate(zip(top_idx, top_sims)):
        logger.debug(f"[VECTOR-DB]   #{i+1}: {_SOURCES[idx]} (similarity={sim:.4f})")
    
    # Build context from retrieved chunks
    top_files = [_SOURCES[i] for i in top_idx]
    context_parts = [f"From {_SOURCES[i]}:\n{_CHUNKS[i]}" for i in top_idx]
    context = "\n\n".join(context_parts)
    
    logger.debug(f"[VECTOR-DB] Context built: {len(context)} chars from {len(set(top_files))} sources")

    # Generate answer using LLM
    answer = _generate_answer(context, q)
    distinct_sources = sorted(list({f for f in top_files}))
    sources_out = distinct_sources[:2] if len(distinct_sources) >= 2 else distinct_sources
    return {"answer": answer, "sources": sources_out}

# ---------------- Document ingestion ----------------
def ingest_docs() -> None:
    """Load and chunk FAQs, compute embeddings, L2-normalize rows, assign globals.
    
    This function should be called explicitly to ingest documents.
    It is NOT called automatically at module import.
    """
    global _CHUNKS, _SOURCES, _CHUNK_EMBEDS, _DOCS_INGESTED
    
    print("Loading FAQ documents...")
    _CHUNKS, _SOURCES = _load_and_chunk_faqs(FAQ_DIR)
    print(f"Loaded {len(_CHUNKS)} chunks from {len(set(_SOURCES))} files")
    
    if _CHUNKS:
        print("Computing embeddings...")
        _CHUNK_EMBEDS = _embed_texts(_CHUNKS)
        print(f"Embeddings shape: {_CHUNK_EMBEDS.shape}")
        _DOCS_INGESTED = True
        print("Document ingestion complete.")
    else:
        print("No chunks to embed")
        _CHUNK_EMBEDS = np.array([], dtype=np.float32).reshape(0, 0)
        _DOCS_INGESTED = False


def is_ingested() -> bool:
    """Check if documents have been ingested."""
    return _DOCS_INGESTED


def get_weaviate_object_count() -> Optional[int]:
    """Query Weaviate to get the total number of objects via REST API.
    
    Returns:
        Number of objects in Weaviate, or None if Weaviate is not configured/available
    """
    if not WEAVIATE_AVAILABLE:
        logger.debug("[WEAVIATE] Weaviate client not available")
        return None
    
    weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    logger.debug(f"[WEAVIATE] >>> Querying Weaviate at {weaviate_url}...")
    
    try:
        import urllib.request
        import json
        
        # Get schema to list collections
        schema_url = f"{weaviate_url}/v1/schema"
        logger.debug(f"[WEAVIATE] GET {schema_url}")
        req = urllib.request.Request(schema_url)
        with urllib.request.urlopen(req, timeout=5) as response:
            schema_data = json.loads(response.read().decode())
        
        classes = schema_data.get("classes", [])
        logger.debug(f"[WEAVIATE] Found {len(classes)} collections: {[c.get('class', '') for c in classes]}")
        
        if not classes:
            # No collections exist yet
            logger.debug("[WEAVIATE] No collections found")
            return 0
        
        # Aggregate count from all collections
        total_count = 0
        for cls in classes:
            class_name = cls.get("class", "")
            if class_name:
                # Use aggregate endpoint for each class
                agg_url = f"{weaviate_url}/v1/schema/{class_name}/aggregate"
                logger.debug(f"[WEAVIATE] GET {agg_url}")
                req = urllib.request.Request(agg_url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    agg_data = json.loads(response.read().decode())
                    if "aggregate" in agg_data:
                        aggregate = agg_data["aggregate"]
                        if isinstance(aggregate, list) and len(aggregate) > 0:
                            meta = aggregate[0].get("meta", {})
                            count = meta.get("count", 0)
                            total_count += count
                            logger.debug(f"[WEAVIATE] Collection '{class_name}': {count} objects")
        
        logger.info(f"[WEAVIATE] <<< Total objects: {total_count}")
        return total_count
        
    except Exception as e:
        logger.debug(f"[WEAVIATE] Query failed (may not be configured or no collections): {e}")
        return 0


def get_ingestion_status() -> Dict[str, object]:
    """Get detailed ingestion status including Weaviate database status.
    
    This function checks both in-memory storage and Weaviate vector database
    (if configured) to provide a complete picture of ingested data.
    """
    try:
        embed_shape = list(_CHUNK_EMBEDS.shape) if _CHUNK_EMBEDS is not None else None
    except Exception:
        embed_shape = None
    
    # Check Weaviate for actual stored objects
    weaviate_count = get_weaviate_object_count()
    
    return {
        "ingested": _DOCS_INGESTED or (weaviate_count is not None and weaviate_count > 0),
        "num_chunks": len(_CHUNKS),
        "num_sources": len(set(_SOURCES)),
        "embed_shape": embed_shape,
        "weaviate": {
            "configured": WEAVIATE_AVAILABLE,
            "object_count": weaviate_count
        } if weaviate_count is not None else {
            "configured": False,
            "object_count": None
        }
    }


def delete_all() -> None:
    """Delete all ingested objects (soft reset).
    
    This function clears all ingested data including chunks, sources,
    and embeddings, effectively resetting the RAG system to its initial state.
    """
    global _CHUNKS, _SOURCES, _CHUNK_EMBEDS, _DOCS_INGESTED
    
    logger.info("Deleting all ingested objects...")
    
    _CHUNKS = []
    _SOURCES = []
    _CHUNK_EMBEDS = None
    _DOCS_INGESTED = False
    
    logger.info("All objects deleted. System reset complete.")


def delete_collection(collection_name: str) -> None:
    """Delete all objects from a specific collection.
    
    Note: This implementation treats all data as a single collection
    since the current in-memory storage doesn't support multiple collections.
    
    Args:
        collection_name: Name of the collection to delete
        
    Raises:
        ValueError: If collection_name is empty
    """
    if not collection_name or not collection_name.strip():
        raise ValueError("collection_name must be a non-empty string")
    
    logger.info(f"Deleting collection: {collection_name}")
    
    # For the current in-memory implementation, we delete all data
    # In a future version with Weaviate/DB support, this would filter by collection
    delete_all()
    
    logger.info(f"Collection '{collection_name}' deleted.")

# ---------------- Optional CLI runner ----------------
def main_cli():
    q = input("Enter your question: ")
    print(json.dumps(ask_faq_core(q), indent=2))

if __name__ == "__main__":
    main_cli()
