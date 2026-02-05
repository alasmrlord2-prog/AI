#!/bin/bash
# Start Frontend Service (Docker)

set -e

cd "$(dirname "$0")"

echo "🚀 Starting Frontend Service..."

# Remove old containers if they exist
echo "🧹 Cleaning up old containers..."
docker rm -f ai-agent-frontend 2>/dev/null || true

# Kill processes using ports
echo "🔌 Freeing up ports..."
pkill -9 -f "next dev.*3000" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start frontend service
docker-compose up -d frontend

echo "⏳ Waiting for frontend to be ready..."
sleep 10

# Check frontend service
echo ""
echo "✅ Frontend Service Status:"
echo "   AI-Agent (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo '000')"

echo ""
echo "📝 View logs: docker-compose logs -f frontend"

