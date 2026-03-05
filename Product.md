Objective
Build a minimal Retrieval-Augmented Generation (RAG) prototype that answers questions using a small corpus of FAQ documents, and expose it as a local HTTP API callable on your machine (e.g., via curl or Postman). The emphasis is on sound approach, correctness, and clear trade-offs—not production polish.
Task
Create a basic RAG app that can:

1. Ingest and process a small set of FAQ markdown files from a directory.
2. Accept a natural-language question.
3. Retrieve relevant content using vector similarity.
4. Generate an answer using an LLM and cite at least two source files when available.
5. Create logs that display llm call, and llm call statistics such as time to first token, input tokens, output tokens, token per secconds. similarly for vector search, the statistics, the call, etc.
6. Implement retry when llm call timeout, not available, etc and also log the event.


Then expose this functionality via a local API with:
● Endpoints

○ GET /health → returns {"status":"ok"}
○ POST /ask → accepts {"question": string, "top_k"?: number} and returns:

{
  "answer": "string",
  "sources": ["filename1.md", "filename2.md"]
}

---

RAG Requirements
● Chunk size: ~200 characters; retrieve top 4 chunks.
● Use cosine similarity for retrieval.
● Answer must cite ≥2 distinct source filenames when available (filenames from your FAQ directory).
● Deterministic JSON keys in responses (no extra fields).

API Requirements
● Local HTTP server (any framework/language).
● Input validation for POST /ask (non-empty question; top_k within a reasonable range).
● Clear status codes: 200 (success), 400 (bad input), 500 (internal error).
● Read config (e.g., OPENAI_API_KEY, model names) from environment variables; fail fast if the API key is missing.

Deliverables
● Source code for the RAG core and the API wrapper.

Time Expectation
Open-book, approximately 2–3 hours including testing and refinement. We’re not looking for production-ready code—prioritize a thoughtful implementation and be prepared to discuss your design decisions.

Evaluation Criteria
● Accuracy: The system retrieves relevant context and returns correct answers from the docs.
● Approach: Clear design choices and trade-offs; appropriate simplicity for scope.
● Practicality: Lightweight solution—avoid over-engineering.

Starter Assets (Provided)
● faqs/ directory with a few example markdown files (e.g., authentication, SSO, employee policy).

Notes
● You may use any programming language or stack. A small, readable solution is preferred.
● If you choose to implement extras (timeouts/retries on model calls, minimal logging), keep them concise and document them briefly.
