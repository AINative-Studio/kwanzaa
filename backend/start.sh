#!/bin/bash

# Kwanzaa Backend Startup Script

set -e

echo "Starting Kwanzaa API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please configure .env with your settings before running again."
    exit 1
fi

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run tests
if [ "$1" = "--test" ]; then
    echo "Running tests..."
    pytest
    exit 0
fi

# Start server
echo "Starting FastAPI server..."
if [ "$1" = "--dev" ]; then
    echo "Development mode: Hot reload enabled"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo "Production mode"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi
