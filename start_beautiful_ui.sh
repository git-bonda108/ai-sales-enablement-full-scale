#!/bin/bash
# Quick start script for beautiful UI

echo "🎨 Installing beautiful UI dependencies..."
pip install -r beautiful_requirements.txt

echo "🚀 Starting beautiful Streamlit app..."
streamlit run beautiful_streamlit_app.py --server.port 8502
