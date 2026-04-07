#!/bin/bash

# RAG Flow Backend Setup Script

set -e

echo "================================"
echo "RAG Flow Backend Setup"
echo "================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip &> /dev/null

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Configure .env file with your OpenAI API key"
echo "2. Run the application: python -m uvicorn app.main:app --reload"
echo "3. Visit: http://localhost:8000/docs"
echo ""
