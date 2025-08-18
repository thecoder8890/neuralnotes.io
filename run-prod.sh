#!/bin/bash

# Production mode - builds frontend and serves everything from backend

echo "🚀 Starting DocuGen AI in production mode..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Copy .env.example to .env and configure it"
    exit 1
fi

# Build frontend
echo "🏗️ Building frontend..."
cd frontend
npm run build
cd ..

# Start backend (which will serve the built frontend)
echo "🐍 Starting production server..."
python main.py

echo "✅ Production server started!"
echo "🌐 Application: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"