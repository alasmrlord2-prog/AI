#!/bin/bash
# Start Backend Script
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🚀 Starting Backend..."

# Check if port is in use
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is in use. Stopping existing processes..."
    
    # Stop Docker containers first
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down 2>/dev/null || true
    else
        docker compose -f "$PROJECT_ROOT/docker-compose.yml" down 2>/dev/null || true
    fi
    
    # Kill any process using port 8000
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    
    # Also kill any uvicorn processes
    pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
    
    sleep 3
    echo "✅ Port 8000 cleared"
fi

# Try with docker-compose first, fallback to docker compose
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d ollama backend postgres
else
    docker compose -f "$PROJECT_ROOT/docker-compose.yml" up -d ollama backend postgres
fi

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
