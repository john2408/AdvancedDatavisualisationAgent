#!/bin/bash

echo "🐳 Building and starting Docker containers..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build backend image
echo "🔧 Building FastAPI Backend..."
docker build -t data-viz-backend ./js_backend

# Build frontend image  
echo "⚛️  Building React Frontend..."
docker build -t data-viz-frontend ./js_frontend

# Run containers with docker-compose
echo "🚀 Starting containers with docker-compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy at http://localhost:8000"
else
    echo "⚠️  Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy at http://localhost:3000"
else
    echo "⚠️  Frontend health check failed"
fi

echo ""
echo "🎉 Docker deployment complete!"
echo "=================================="
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📝 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop containers: docker-compose down"
echo "To view logs: docker-compose logs -f"
