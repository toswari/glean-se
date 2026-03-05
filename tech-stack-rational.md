# Technology Stack Rationale

This document captures the architectural decisions, trade-offs, and rationale behind the technology choices for the FAQ RAG (Retrieval-Augmented Generation) system. It serves as a reference for understanding why specific technologies were selected and provides a framework for evaluating future technology decisions.

---

## Decision Records

### Decision 1: Vector Database - Weaviate (Dockerized)

**Status:** Accepted

**Context:**
The RAG system requires a vector database to store document embeddings and perform similarity-based retrieval for answering user queries.

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **Weaviate** (Selected) | - Open-source with commercial support<br>- Docker-native deployment<br>- Built-in REST and GraphQL APIs<br>- Hybrid search (vector + keyword)<br>- Schema enforcement<br>- Good Python client<br>- Persistent storage | - More resource-intensive than lightweight options<br>- Learning curve for advanced features |
| **ChromaDB** | - Lightweight and simple<br>- Designed for LLM applications<br>- In-memory option for prototyping<br>- Easy Python integration | - Less mature ecosystem<br>- Limited production deployments<br>- Fewer enterprise features |
| **Qdrant** | - High performance<br>- Rust-based (memory safe)<br>- Good filtering capabilities<br>- Cloud offering available | - Smaller community<br>- Less documentation<br>- Newer ecosystem |
| **Pinecone** | - Fully managed service<br>- No infrastructure to manage<br>- High scalability | - Vendor lock-in<br>- Cost at scale<br>- No self-hosted option |
| **FAISS (Facebook)** | - Extremely fast<br>- Battle-tested at scale<br>- Multiple index types | - Not a database (no persistence)<br>- Requires building infrastructure around it<br>- Steeper learning curve |

**Decision:**
Weaviate was selected because it provides the best balance of:
1. **Ease of deployment** - Docker Compose makes it trivial to run locally
2. **Production readiness** - Proven track record with enterprise deployments
3. **Feature completeness** - Hybrid search, filtering, and schema management
4. **Developer experience** - Good documentation and Python client

**Future Re-evaluation Triggers:**
- If scaling beyond 10M+ vectors requires different architecture
- If cost optimization becomes critical (consider Qdrant or FAISS)
- If managed service becomes a requirement (consider Pinecone)

---

### Decision 2: Document Parser - Docling

**Status:** Accepted

**Context:**
The system needs to parse documents for ingestion into the vector database. Current requirements are markdown files, but future expansion may include PDFs, Word documents, and other formats.

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **Docling** (Selected) | - Multi-format support (PDF, DOCX, MD, HTML, images)<br>- Layout preservation<br>- Table extraction<br>- OCR capabilities<br>- Unified API across formats<br>- Future-proof | - Larger dependency footprint<br>- Overkill for markdown-only use case<br>- Newer project (less battle-tested) |
| **mistune** | - Lightweight<br>- Python-native<br>- Fast for markdown<br>- Well-maintained | - Markdown only<br>- No PDF/DOCX support<br>- Would need multiple libraries for expansion |
| **markdown (Python)** | - Simple and mature<br>- Standard choice for markdown<br>- Extensible | - Markdown only<br>- No complex document support |
| **PyPDF2 / pdfplumber** | - Good PDF support<br>- Mature libraries | - PDF only<br>- Would need separate solution for other formats |
| **Apache Tika (via python-tika)** | - Supports 100+ formats<br>- Industry standard<br>- Very mature | - Requires Java runtime<br>- Heavy dependency<br>- Slower processing<br>- Memory intensive |
| **Unstructured.io** | - Comprehensive format support<br>- Good extraction quality<br>- Active development | - Larger dependency<br>- Some features require paid tier<br>- More complex setup |

**Decision:**
Docling was selected because:
1. **Future expansion** - Ready for PDF, DOCX, and other formats without code changes
2. **Unified API** - Single interface for all document types simplifies codebase
3. **Modern architecture** - Built with RAG use cases in mind
4. **Layout awareness** - Preserves document structure for better chunking

**Trade-offs Accepted:**
- Larger initial dependency size for future flexibility
- Slightly slower than lightweight markdown-only parsers for current use case

**Future Re-evaluation Triggers:**
- If Docling development stalls or is abandoned
- If specific format support is inadequate
- If performance becomes a bottleneck (consider format-specific parsers)

---

### Decision 3: LLM Provider - Alibaba Cloud Model Studio (DashScope)

**Status:** Accepted

**Context:**
The system requires an LLM for answer generation and embeddings for vector creation. The provider must offer a compatible API, reasonable pricing, and reliable service.

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **Alibaba Cloud (DashScope)** (Selected) | - OpenAI-compatible API (minimal code changes)<br>- Competitive pricing<br>- Qwen models perform well on benchmarks<br>- Multiple regional endpoints<br>- Good for international deployments | - Newer ecosystem<br>- Less community support<br>- Documentation primarily in Chinese |
| **OpenAI** | - Industry standard<br>- Best documentation<br>- Largest community<br>- Proven reliability<br>- GPT-4 class models | - Higher cost at scale<br>- Potential vendor concerns<br>- Rate limits on lower tiers |
| **Anthropic (Claude)** | - Strong reasoning capabilities<br>- Large context windows<br>- Safety-focused | - More expensive<br>- Limited model variety<br>- Stricter usage policies |
| **Google (Vertex AI / Gemini)** | - Strong multimodal capabilities<br>- Google infrastructure<br>- Competitive pricing | - More complex API<br>- Integration overhead<br>- Variable model performance |
| **AWS Bedrock** | - Multiple model providers<br>- AWS integration<br>- Enterprise features | - AWS lock-in<br>- More complex setup<br>- Higher minimum costs |
| **Self-hosted (vLLM, Ollama)** | - Full control<br>- No API costs<br>- Data sovereignty | - Infrastructure overhead<br>- GPU requirements<br>- Operational complexity |

**Decision:**
Alibaba Cloud Model Studio was selected because:
1. **Cost efficiency** - Competitive pricing compared to OpenAI
2. **API compatibility** - OpenAI-compatible endpoint minimizes code changes
3. **Model quality** - Qwen models perform competitively on benchmarks
4. **Regional flexibility** - Multiple endpoints for compliance and latency

**Trade-offs Accepted:**
- Smaller community and less third-party tooling
- Documentation may require translation
- Potential geopolitical considerations for some organizations

**Future Re-evaluation Triggers:**
- If model quality doesn't meet requirements
- If cost advantage diminishes
- If compliance requirements change
- If service reliability issues arise

---

### Decision 3a: LLM Models - Qwen Series

**Status:** Accepted

**Context:**
Alibaba Cloud Model Studio offers multiple LLM models. This decision documents the available models and the rationale for the selected default model.

**Selected Default Model:** `qwen-plus`

**Available LLM Models:**

| Model | Context Window | Best For | Relative Cost | Performance |
|-------|---------------|----------|---------------|-------------|
| **qwen-turbo** | 32K | - High-throughput applications<br>- Simple Q&A tasks<br>- Cost-sensitive deployments | $ | Fast |
| **qwen-plus** (Selected) | 32K | - Balanced workloads<br>- General RAG applications<br>- Production default | $$ | Balanced |
| **qwen-max** | 32K | - Complex reasoning<br>- Multi-step tasks<br>- Highest accuracy needs | $$$ | Best |
| **qwen2.5-72b-instruct** | 32K | - Instruction following<br>- Complex prompts<br>- Specialized tasks | $$$ | Best |

**Model Comparison:**

```
Performance: qwen-max ≈ qwen2.5-72b-instruct > qwen-plus > qwen-turbo
Cost:        qwen-max > qwen2.5-72b-instruct > qwen-plus > qwen-turbo
Speed:       qwen-turbo > qwen-plus > qwen-max ≈ qwen2.5-72b-instruct
```

**Selection Rationale for qwen-plus:**
1. **Balanced performance** - Good enough for most RAG tasks without premium cost
2. **Cost effective** - Significantly cheaper than qwen-max for similar quality on Q&A
3. **Fast response** - Adequate latency for interactive applications
4. **Recommended by Alibaba** - Positioned as the general-purpose model

**When to Change Model:**

| Scenario | Recommended Model |
|----------|-------------------|
| Cost is primary concern | `qwen-turbo` |
| Maximum accuracy needed | `qwen-max` |
| Complex reasoning required | `qwen-max` or `qwen2.5-72b-instruct` |
| High-throughput batch processing | `qwen-turbo` |
| General RAG/Q&A (default) | `qwen-plus` |

**Configuration:**
```bash
# Environment variable to switch models
export LLM_CHOICE=qwen-plus  # or qwen-turbo, qwen-max, qwen2.5-72b-instruct
```

**Future Re-evaluation Triggers:**
- New model releases from Alibaba
- Significant price changes
- Performance benchmarks show clear winner
- Specific use case requires different model characteristics

---

### Decision 3b: Embedding Models - Alibaba DashScope

**Status:** Accepted

**Context:**
The system requires an embedding model to convert text into vectors for similarity search in Weaviate.

**Selected Model:** `text-embedding-v3`

**Available Embedding Models:**

| Model | Dimensions | Max Input | Performance | Use Case |
|-------|------------|-----------|-------------|----------|
| **text-embedding-v2** | 1536 | 512 tokens | Good | Legacy support, smaller vectors |
| **text-embedding-v3** (Selected) | 1536 | 8192 tokens | Best | General purpose, latest model |

**Model Details:**

**text-embedding-v3:**
- **Dimensions:** 1536 (compatible with most vector databases)
- **Max Input:** 8192 tokens (supports long documents)
- **Languages:** Multi-language support (100+ languages)
- **Training:** Trained on diverse corpus for general-purpose embeddings
- **Performance:** Improved semantic understanding over v2

**text-embedding-v2:**
- **Dimensions:** 1536
- **Max Input:** 512 tokens
- **Languages:** Multi-language support
- **Use Case:** When compatibility with existing v2 embeddings is needed

**Embedding Model Comparison with Alternatives:**

| Provider | Model | Dimensions | Cost/1K | Performance |
|----------|-------|------------|---------|-------------|
| **Alibaba** | text-embedding-v3 | 1536 | $ | Good |
| **OpenAI** | text-embedding-ada-002 | 1536 | $$ | Very Good |
| **OpenAI** | text-embedding-3-large | 3072 | $$$ | Best |
| **OpenAI** | text-embedding-3-small | 1536 | $ | Good |

**Selection Rationale for text-embedding-v3:**
1. **Provider alignment** - Same provider as LLM (simplified billing, API)
2. **Cost effective** - Lower cost than OpenAI embeddings
3. **Long context** - 8192 tokens supports chunking larger documents
4. **Dimension compatibility** - 1536 dimensions works well with Weaviate
5. **Multi-language** - Supports international FAQ content

**Configuration:**
```bash
# Environment variable for embedding model
export EMBEDDING_MODEL=text-embedding-v3  # or text-embedding-v2
```

**Weaviate Schema Configuration:**
```python
# When creating the collection in Weaviate
client.collections.create(
    name="FAQ",
    vectorizer_config=Configure.Vectorizer.none(),  # We provide embeddings
    vector_index_config=Configure.VectorIndex.hnsw(
        distance_metric=DistanceMetric.COSINE
    )
)
```

**Embedding Pipeline:**
```
Document → Chunk → text-embedding-v3 → 1536-d vector → Weaviate
                                                    ↓
Query → text-embedding-v3 → 1536-d vector → Cosine Similarity Search
```

**Future Re-evaluation Triggers:**
- New embedding model releases with better performance/cost
- Need for different vector dimensions
- Switch to self-hosted embeddings (e.g., sentence-transformers)
- Multi-vector approaches become necessary (e.g., ColBERT)

---

### Decision 4: API Framework - FastAPI

**Status:** Accepted

**Context:**
The system needs an HTTP API to expose RAG functionality to clients.

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **FastAPI** (Selected) | - Automatic OpenAPI documentation<br>- Type validation with Pydantic<br>- Async support<br>- High performance<br>- Modern Python features | - Relatively newer (but mature)<br>- Async can be complex for beginners |
| **Flask** | - Mature and stable<br>- Large ecosystem<br>- Simple for basic use cases | - No async support<br>- Manual validation<br>- Slower performance<br>- No built-in OpenAPI |
| **Django REST Framework** | - Full-featured framework<br>- ORM included<br>- Admin interface<br>- Battle-tested | - Heavy for simple API<br>- Steeper learning curve<br>- Overkill for this use case |
| **Starlette** | - Lightweight async framework<br>- FastAPI is built on top<br>- Minimal dependencies | - Less batteries-included<br>- More boilerplate required |

**Decision:**
FastAPI was selected because:
1. **Developer experience** - Automatic documentation and type validation
2. **Performance** - One of the fastest Python web frameworks
3. **Modern** - Async support and type hints
4. **Appropriate scope** - More than Flask, less than Django

---

### Decision 5: Containerization - Docker + Docker Compose

**Status:** Accepted

**Context:**
The system needs consistent deployment across development and production environments.

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **Docker + Compose** (Selected) | - Industry standard<br>- Universal support<br>- Simple local development<br>- Production-ready<br>- Large ecosystem | - Can be verbose<br>- Image sizes can grow large |
| **Podman** | - Rootless by default<br>- Docker-compatible<br>- Lighter weight | - Smaller ecosystem<br>- Less IDE support<br>- Newer tooling |
| **Kubernetes** | - Production orchestration<br>- Auto-scaling<br>- Self-healing | - Overkill for single-service<br>- Complex setup<br>- Operational overhead |
| **No containers** | - Simplest setup<br>- No container overhead | - Environment inconsistencies<br>- Harder deployments<br>- Less portable |

**Decision:**
Docker Compose was selected because:
1. **Simplicity** - Single command to run entire stack
2. **Consistency** - Same configuration for dev and production
3. **Weaviate support** - Official Docker images available
4. **Team familiarity** - Industry standard tooling

---

## Decision Framework for Future Technology Choices

When evaluating new technologies for this project, consider the following criteria:

### Evaluation Criteria

| Criterion | Weight | Questions to Ask |
|-----------|--------|------------------|
| **Functionality** | High | Does it solve the problem? Does it meet requirements? |
| **Maintainability** | High | Is it well-documented? Is there community support? |
| **Complexity** | Medium | Does it add unnecessary complexity? Can the team support it? |
| **Cost** | Medium | What are the licensing/hosting costs? Is there a free tier? |
| **Performance** | Medium | Does it meet performance requirements? |
| **Security** | High | Are there known vulnerabilities? Is it actively maintained? |
| **Vendor Lock-in** | Medium | How difficult would it be to switch providers? |
| **Scalability** | Low-Medium | Will it work at 10x current scale? |

### Decision Process

1. **Identify the problem** - Clearly articulate what needs to be solved
2. **Research alternatives** - Find at least 3 options to compare
3. **Evaluate against criteria** - Score each option objectively
4. **Consider trade-offs** - Document what you're giving up
5. **Make a decision** - Choose and document the rationale
6. **Set re-evaluation triggers** - When should this decision be revisited?

### Documentation Template

For future technology decisions, use this template:

```markdown
### Decision N: [Technology Name]

**Status:** [Accepted | Rejected | Deprecated]

**Context:**
[What problem are we solving?]

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| [Option 1] | ... | ... |
| [Option 2] | ... | ... |

**Decision:**
[Why was this option selected?]

**Trade-offs Accepted:**
[What are we giving up?]

**Future Re-evaluation Triggers:**
[When should we revisit this decision?]
```

---

## Summary of Technology Decisions

| Component | Selected Technology | Key Reason |
|-----------|--------------------|------------|
| Vector Database | Weaviate (Dockerized) | Best balance of features, ease of use, and production readiness |
| Document Parser | Docling | Future-proof multi-format support with unified API |
| LLM Provider | Alibaba Cloud (DashScope) | Cost-effective with OpenAI-compatible API |
| API Framework | FastAPI | Modern, fast, with automatic documentation |
| Containerization | Docker + Compose | Industry standard with simple multi-service orchestration |

---

## References

- [Weaviate Documentation](https://weaviate.io/developers/)
- [Docling Documentation](https://ds4sd.github.io/docling/)
- [Alibaba Cloud Model Studio](https://help.aliyun.com/zh/model-studio/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)