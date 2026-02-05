#!/bin/bash
# Start Backend Script
# Note: If you encounter issues, use ./start-fixed.sh instead
set -e

echo "🚀 Starting Backend..."
echo "⚠️  If you encounter errors, try: ./start-fixed.sh"

# Check if port is in use
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is in use. Trying to stop existing containers..."
    docker-compose down 2>/dev/null || true
    sleep 2
fi

docker-compose up -d backend postgres

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running!"
    echo "   API: http://localhost:8000"
    echo "   Docs: http://localhost:8000/docs"
else
    echo "⚠️  Backend started but not responding yet."
    echo "   If issues persist, use: ./start-fixed.sh"
fi

echo ""
echo "📝 View logs: docker-compose logs -f backend"
