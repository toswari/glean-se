#!/bin/bash
# Streamlit Chatbot Launch Script
# This script starts the Streamlit chatbot application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Starting Streamlit Chatbot..."

# Check if API server is running
check_api_server() {
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API server is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  API server is not running${NC}"
        echo "   Please start the API server first:"
        echo "   $ python api_server.py"
        echo "   or"
        echo "   $ ./start-api.sh"
        return 1
    fi
}

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "📄 Loading environment from .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Check API server status (warning only, don't block)
check_api_server || true

# Set default environment variables if not set
export API_URL=${API_URL:-http://localhost:8000}

# Set LOG_LEVEL for debug logging (default: DEBUG)
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_LEVEL=${LOG_LEVEL:-DEBUG}

echo "📡 API URL: $API_URL"
echo "🔍 LOG_LEVEL: $LOG_LEVEL"

# Change to streamlit directory
cd "$(dirname "$0")/streamlit"

echo "🎨 Starting Streamlit app..."
echo ""

# Start Streamlit with unbuffered output for real-time logging
export PYTHONUNBUFFERED=1

# Start Streamlit
streamlit run app.py --server.headless=true "$@"
