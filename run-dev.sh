#!/bin/bash

# Development mode - runs frontend and backend separately

echo "🚀 Starting DocuGen AI in development mode..."

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

# Function to kill background processes on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $(jobs -p) 2>/dev/null
    wait
    echo "✅ Services stopped"
}

trap cleanup EXIT

# Start backend
echo "🐍 Starting backend server..."
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️ Starting frontend development server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Development servers started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for either process to exit
wait