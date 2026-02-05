#!/bin/bash
# Stop Backend Script (Direct Mode - uvicorn)
set -e

echo "🛑 Stopping Backend..."

# Stop uvicorn processes
sudo pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || true

# Also try Docker if exists
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$(cd "$(dirname "$0")/.." && pwd)/docker-compose.yml" stop backend 2>/dev/null || true
elif command -v docker &> /dev/null; then
    docker compose -f "$(cd "$(dirname "$0")/.." && pwd)/docker-compose.yml" stop backend 2>/dev/null || true
fi

sleep 2
echo "✅ Backend stopped!"
