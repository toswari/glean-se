#!/bin/bash
# Start the FAQ RAG API Server with comprehensive logging

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source environment variables from .env file if it exists
if [ -f "${SCRIPT_DIR}/.env" ]; then
    echo "Loading environment variables from .env..."
    set -a  # Export all variables
    source "${SCRIPT_DIR}/.env"
    set +a
    echo ""
fi

# Configuration (environment variables from .env can override these defaults)
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-DEBUG}"
DEBUG_MODE="${DEBUG_MODE:-true}"

# Log file location
LOG_DIR="${LOG_DIR:-/tmp}"
API_LOG_FILE="${LOG_DIR}/api_server.log"
LLM_LOG_FILE="${LOG_DIR}/llm_calls.log"

# Cleanup: Kill any existing API server process on the same port
echo "Checking for existing API server process..."
EXISTING_PID=$(lsof -ti:$PORT 2>/dev/null || true)
if [ -n "$EXISTING_PID" ]; then
    echo "Found existing process (PID: $EXISTING_PID) on port $PORT, killing..."
    kill $EXISTING_PID 2>/dev/null || true
    sleep 1
    # Force kill if still running
    if kill -0 $EXISTING_PID 2>/dev/null; then
        echo "Force killing process..."
        kill -9 $EXISTING_PID 2>/dev/null || true
    fi
    echo "Previous process terminated."
else
    echo "No existing process found on port $PORT."
fi
echo ""

echo "========================================"
echo "  FAQ RAG API Server"
echo "========================================"
echo ""
echo "Configuration:"
echo "  Host:         ${HOST}"
echo "  Port:         ${PORT}"
echo "  Log Level:    ${LOG_LEVEL}"
echo "  Debug Mode:   ${DEBUG_MODE}"
echo "  API Log:      ${API_LOG_FILE}"
echo "  LLM Log:      ${LLM_LOG_FILE}"
echo ""
echo "Environment Variables:"
echo "  LLM_CHOICE:       ${LLM_CHOICE:-qwen-plus}"
echo "  LLM_MODEL:        ${LLM_MODEL:-gpt-3.5-turbo}"
echo "  EMBEDDING_MODEL:  ${EMBEDDING_MODEL:-text-embedding-v3}"
echo "  CHUNK_SIZE:       ${CHUNK_SIZE:-200}"
echo "  FAQ_DIR:          ${FAQ_DIR:-faqs}"
echo ""
echo "Endpoints:"
echo "  GET  /              - API info"
echo "  GET  /health        - Health check"
echo "  POST /ask           - Ask a question"
echo "  POST /ingest        - Ingest documents"
echo "  GET  /ingestion/status - Get ingestion status"
echo "  POST /delete        - Delete all objects (soft reset)"
echo ""
echo "Quick Test Commands:"
echo "  curl http://${HOST}:${PORT}/health"
echo "  curl -X POST http://${HOST}:${PORT}/ingest"
echo "  curl -X POST http://${HOST}:${PORT}/ask -H 'Content-Type: application/json' -d '{\"question\": \"How do I reset my password?\"}'"
echo "  curl http://${HOST}:${PORT}/ingestion/status"
echo "  curl -X POST http://${HOST}:${PORT}/delete"
echo ""
echo "View Logs:"
echo "  tail -f ${API_LOG_FILE}"
echo "  tail -f ${LLM_LOG_FILE}"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Export environment variables for detailed logging
export LOG_LEVEL="${LOG_LEVEL}"
export DEBUG_MODE="${DEBUG_MODE}"
export PYTHONUNBUFFERED=1

# Create log directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Clear old log files
> "${API_LOG_FILE}"
> "${LLM_LOG_FILE}"

echo "Starting server..."
echo ""

# Start the API server with verbose logging
# Using --log-level debug for uvicorn's internal logging
# The application logging is controlled by LOG_LEVEL environment variable
# PYTHONUNBUFFERED=1 ensures Python doesn't buffer output
exec uvicorn api_server:app \
    --host "$HOST" \
    --port "$PORT" \
    --log-level debug \
    2>&1 | tee -a "${API_LOG_FILE}"
