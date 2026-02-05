#!/bin/bash
# Fix port 8000 issue

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🔧 Fixing port 8000..."

# Stop Docker containers first
echo "Stopping Docker containers..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down 2>/dev/null || true
else
    docker compose -f "$PROJECT_ROOT/docker-compose.yml" down 2>/dev/null || true
fi

# Kill all processes on port 8000
echo "Killing processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
pkill -9 -f "python.*8000" 2>/dev/null || true

# Try fuser if available (requires root)
if command -v fuser &> /dev/null; then
    sudo fuser -k 8000/tcp 2>/dev/null || true
fi

sleep 2

# Check if port is free
if lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ Port 8000 still in use. Try running as root:"
    echo "   sudo fuser -k 8000/tcp"
    echo "   sudo lsof -ti:8000 | xargs sudo kill -9"
    exit 1
else
    echo "✅ Port 8000 is now free"
fi
