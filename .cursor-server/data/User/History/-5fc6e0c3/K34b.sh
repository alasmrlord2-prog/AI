#!/bin/bash
# Start Backend Script
set -e

cd "$(dirname "$0")"

echo "🚀 Starting Backend..."

# Check if port is in use
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is in use. Stopping existing containers..."
    docker-compose down 2>/dev/null || true
    sleep 2
fi

docker-compose up -d ollama backend postgres

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running!"
    echo "   API: http://localhost:8000"
    echo "   Docs: http://localhost:8000/docs"
else
    echo "⚠️  Backend started but not responding yet."
    echo "   Check logs: docker-compose logs -f backend"
fi

echo ""
echo "📝 View logs: docker-compose logs -f backend"
