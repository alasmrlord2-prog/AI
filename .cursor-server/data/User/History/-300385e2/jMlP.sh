#!/bin/bash
# Stop Backend Script - Fixed version
set -e

cd "$(dirname "$0")"

echo "🛑 Stopping Backend..."

# Stop all related containers
docker-compose stop backend postgres 2>/dev/null || true
docker-compose down 2>/dev/null || true

# Also stop any containers with similar names
docker stop ai-agent-backend ai-agent-backend-prod ai-agent-postgres 2>/dev/null || true
docker rm -f ai-agent-backend ai-agent-backend-prod ai-agent-postgres 2>/dev/null || true

# Kill any process on port 8000
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Killing process on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "✅ Backend stopped!"

