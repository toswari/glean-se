#!/bin/bash
# Ingest FAQ documents into the RAG system

set -e

echo "========================================"
echo "  FAQ Document Ingestion"
echo "========================================"
echo ""

# Run the ingestion script
python3 -c "
from rag_core import ingest_docs
ingest_docs()
"

echo ""
echo "========================================"
echo "  Ingestion Complete"
echo "========================================"