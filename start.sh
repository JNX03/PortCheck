#!/bin/bash

# Thai Portfolio Analyzer - Startup Script

echo "========================================"
echo "Thai Portfolio Analyzer"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your TYPHOON_API_KEY"
    echo "Get your API key from: https://opentyphoon.ai"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

# Check if TYPHOON_API_KEY is set
source .env
if [ -z "$TYPHOON_API_KEY" ] || [ "$TYPHOON_API_KEY" = "your_typhoon_api_key_here" ]; then
    echo "❌ Error: TYPHOON_API_KEY is not set in .env file"
    echo "Please edit .env and add your Typhoon API key"
    exit 1
fi

echo "✅ Configuration loaded"
echo ""

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "========================================"
echo "Starting Thai Portfolio Analyzer..."
echo "========================================"
echo ""
echo "Access the application at:"
echo "  🌐 http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python main.py
