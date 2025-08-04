#!/bin/bash

echo "🚀 AI Sales MCP Demo - Setup Script"
echo "==================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Please install it first:"
    echo "   Mac/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Windows: powershell -c 'irm https://astral.sh/uv/install.sh | iex'"
    exit 1
fi

echo "✅ Found uv"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

echo ""
echo "✅ Setup complete!"
echo ""
echo "📁 Project structure created:"
echo "   servers/ - MCP servers will go here"
echo "   client/  - UI and client code will go here"
echo "   data/    - Local database storage"
echo "   tests/   - Test files"
echo ""
echo "🎯 Next: Run Batch 2 to create your first MCP server!"
