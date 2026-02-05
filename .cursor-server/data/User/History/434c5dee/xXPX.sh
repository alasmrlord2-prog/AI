#!/bin/bash
# Restart Backend Services (Docker)

set -e

cd "$(dirname "$0")"

echo "🔄 Restarting Backend Services..."

# Restart backend, postgres, and ollama
docker-compose restart backend postgres ollama

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

