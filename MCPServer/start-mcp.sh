#!/bin/bash

# Start the MCP server in development mode

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Initialize conda
eval "$(conda shell.bash hook)"

# Activate the virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./setup-env.sh first"
    exit 1
fi


# Run the MCP server in development mode
echo "Starting MCP server in development mode..."
uv run mcp dev server.py
