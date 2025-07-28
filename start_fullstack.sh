#!/bin/bash

echo "🚀 Starting Full Stack Application..."
echo "=================================="

# Function to check if a port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Kill existing processes on our ports
echo "🧹 Cleaning up existing processes..."
if check_port 8000; then
    echo "Killing process on port 8000..."
    kill -9 $(lsof -t -i:8000) 2>/dev/null || true
fi

if check_port 3000; then
    echo "Killing process on port 3000..."
    kill -9 $(lsof -t -i:3000) 2>/dev/null || true
fi

# Start backend
echo "🐍 Starting FastAPI Backend (Port 8000)..."
cd js_backend
./start_server.sh &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if check_port 8000; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "⚛️  Starting React Frontend (Port 3000)..."
cd ../js_frontend
./start_frontend.sh &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 10

if check_port 3000; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🎉 Application started successfully!"
echo "=================================="
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📝 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user interrupt
trap 'echo ""; echo "🛑 Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0' INT

# Keep script running
wait
