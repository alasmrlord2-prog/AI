#!/bin/bash
# Stop Backend Script (Direct Mode - uvicorn)
set -e

echo "🛑 Stopping Backend..."

# Stop uvicorn processes
if [ "$EUID" -eq 0 ]; then
    # Running as root - no need for sudo
    pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
else
    # Not root - try with sudo
    sudo pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
    sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || true
fi

# Also try Docker if exists
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$(cd "$(dirname "$0")/.." && pwd)/docker-compose.yml" stop backend 2>/dev/null || true
elif command -v docker &> /dev/null; then
    docker compose -f "$(cd "$(dirname "$0")/.." && pwd)/docker-compose.yml" stop backend 2>/dev/null || true
fi

sleep 2
echo "✅ Backend stopped!"
