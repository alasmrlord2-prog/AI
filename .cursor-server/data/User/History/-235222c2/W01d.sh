#!/bin/bash
# Stop Frontend Script - Fixed version
set -e

cd "$(dirname "$0")"

PORT=${1:-3000}

echo "🛑 Stopping Frontend..."

# Stop all related containers
docker-compose stop frontend 2>/dev/null || true
docker-compose down 2>/dev/null || true

# Also stop any containers with similar names
docker stop ai-agent-frontend ai-agent-frontend-prod 2>/dev/null || true
docker rm -f ai-agent-frontend ai-agent-frontend-prod 2>/dev/null || true

# Kill any process on port
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "⚠️  Killing process on port $PORT..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "✅ Frontend stopped!"

