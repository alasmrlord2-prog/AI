#!/bin/bash
# ============================================
# AI Agent - Stop Backend Script
# ============================================

set -e

PORT=8000

echo "⏹️  Stopping AI Agent Backend..."
echo "========================================"

# Check if running in Docker
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "ai-agent-backend-prod"; then
    echo "🐳 Stopping Docker container..."
    docker stop ai-agent-backend-prod 2>/dev/null || true
    sleep 2
fi

# Stop all uvicorn processes
echo "🛑 Stopping backend processes..."
pkill -f "uvicorn.*app.main" 2>/dev/null || true

# Free port 8000
echo "🔌 Freeing port $PORT..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true

sleep 2

# Verify
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  Port $PORT is still in use. Processes:"
    lsof -ti:$PORT | xargs ps -p
    echo ""
    echo "💡 Try: sudo kill -9 \$(lsof -ti:$PORT)"
else
    echo "✅ Backend stopped successfully"
    echo "   Port $PORT is now free"
fi

