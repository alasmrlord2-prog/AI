#!/bin/bash
# Restart Backend Script
set -e

cd "$(dirname "$0")"

echo "🔄 Restarting Backend..."

# Stop first
docker-compose stop ollama backend postgres 2>/dev/null || true
sleep 2

# Start
docker-compose up -d ollama backend postgres

echo "⏳ Waiting for services to be ready..."
sleep 5

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend restarted!"
else
    echo "⚠️  Backend restarted but not responding yet."
    echo "   Check logs: docker-compose logs -f backend"
fi

echo ""
echo "📝 View logs: docker-compose logs -f backend"
