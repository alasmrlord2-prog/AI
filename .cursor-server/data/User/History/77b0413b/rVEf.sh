#!/bin/bash
# Start Backend Services (PostgreSQL, Ollama, Backend API)

set -e

cd "$(dirname "$0")"

echo "🚀 Starting Backend Services..."

# Clean up old containers
echo "🧹 Cleaning up old containers..."
docker rm -f ai-backend ai-agent-postgres ai-agent-ollama 2>/dev/null || true

# Free up ports
echo "🔌 Freeing up ports..."
for port in 8000 5432 11434; do
    PIDS=$(lsof -ti:${port} 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null || true
    fi
done
sleep 2

# Start services
echo "🚀 Starting PostgreSQL, Ollama, and Backend..."
docker compose up -d postgres ollama backend

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
        echo "   Check logs: docker compose logs backend"
    else
        sleep 2
    fi
done

echo ""
echo "📝 View logs: docker compose logs -f backend"
