#!/bin/bash
# Start Backend Services (Docker)

set -e

cd "$(dirname "$0")"

echo "🚀 Starting Backend Services..."

# Remove old containers if they exist
echo "🧹 Cleaning up old containers..."
docker rm -f ai-backend 2>/dev/null || true
docker rm -f ai-agent-backend 2>/dev/null || true

# Kill processes using ports
echo "🔌 Freeing up ports..."
pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5432 | xargs kill -9 2>/dev/null || true
lsof -ti:11434 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend, postgres, and ollama
docker-compose up -d postgres ollama backend

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check backend health
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running!"
        echo "   API: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend started but not responding yet."
        echo "   Check logs: docker-compose logs backend"
    else
        sleep 2
    fi
done

echo ""
echo "📝 View logs: docker-compose logs -f backend"

