#!/bin/bash
# Restart Backend Script
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🔄 Restarting Backend..."

# Stop first
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" stop ollama backend postgres 2>/dev/null || true
else
    docker compose -f "$PROJECT_ROOT/docker-compose.yml" stop ollama backend postgres 2>/dev/null || true
fi
sleep 2

# Start
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d ollama backend postgres
else
    docker compose -f "$PROJECT_ROOT/docker-compose.yml" up -d ollama backend postgres
fi

echo "⏳ Waiting for services to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend restarted!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend restarted but not responding yet."
        echo "   Check logs: docker-compose -f $PROJECT_ROOT/docker-compose.yml logs -f backend"
    else
        sleep 2
    fi
done

echo ""
echo "📝 View logs: docker-compose -f $PROJECT_ROOT/docker-compose.yml logs -f backend"
