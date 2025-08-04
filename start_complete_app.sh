#!/bin/bash

echo "🚀 Starting AI Sales Intelligence Platform..."
echo "=============================================="

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "✅ Using uv for Python environment management"
    PYTHON_CMD="uv run python"
    STREAMLIT_CMD="uv run streamlit"
else
    echo "⚠️  uv not found, using system Python"
    PYTHON_CMD="python"
    STREAMLIT_CMD="streamlit"
fi

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
}

# Check if API Gateway port is available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Please stop any existing API Gateway."
    echo "   You can kill the process using: lsof -ti:8000 | xargs kill -9"
    exit 1
fi

# Check if Streamlit port is available
if check_port 8501; then
    echo "⚠️  Port 8501 is already in use. Please stop any existing Streamlit app."
    echo "   You can kill the process using: lsof -ti:8501 | xargs kill -9"
    exit 1
fi

echo ""
echo "📋 Starting services..."
echo ""

# Start API Gateway in background
echo "🔧 Starting API Gateway on port 8000..."
$PYTHON_CMD api_gateway.py &
API_PID=$!

# Wait a moment for API Gateway to start
sleep 3

# Check if API Gateway started successfully
if ! check_port 8000; then
    echo "❌ Failed to start API Gateway"
    exit 1
fi

echo "✅ API Gateway started successfully!"

# Start Streamlit app
echo ""
echo "🎨 Starting Streamlit app on port 8501..."
echo "   Opening browser automatically..."
$STREAMLIT_CMD run streamlit_app_complete.py --server.port 8501 --server.headless false

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $API_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Trap Ctrl+C to cleanup
trap cleanup INT

# Wait for background processes
wait 