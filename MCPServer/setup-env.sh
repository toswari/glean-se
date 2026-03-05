#!/bin/bash

# Setup environment for BuildMCPServer MCP project
set -e

echo "================================"
echo "Setting up BuildMCPServer"
echo "================================"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3.11+ is available
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Using Python $python_version"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ uv is available: $(uv --version)"

# Create virtual environment using uv
echo "Creating virtual environment with uv..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install project dependencies directly
echo "Installing project dependencies..."
uv pip install beeai-framework mcp requests

echo ""
echo "================================"
echo "✅ Setup complete!"
echo "================================"
echo ""
echo "To activate the environment and run the MCP server:"
echo "  source .venv/bin/activate"
echo "  uv run mcp dev server.py"
echo ""
echo "To run the agent in a separate terminal:"
echo "  source .venv/bin/activate"
echo "  uv run singleflowagent.py"
echo ""
