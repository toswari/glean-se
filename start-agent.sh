#!/bin/bash

# Start the single flow agent with MCP server integration

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

# Run the agent
echo "Starting single flow agent..."
python  singleflowagent.py
