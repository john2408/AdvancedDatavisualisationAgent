#!/bin/bash

# Start the FastAPI backend server
echo "🚀 Starting FastAPI Backend Server..."
echo "📂 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"

# Install dependencies
echo "📦 Installing FastAPI dependencies..."
pip install -r requirements.txt

# Start the server
echo "🔥 Starting server on http://localhost:8000"
python main.py
