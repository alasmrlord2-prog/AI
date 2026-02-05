#!/bin/bash
# ============================================
# AI Agent - Start Backend Script
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent/backend"
PORT=8000

echo "🚀 Starting AI Agent Backend..."
echo "========================================"

cd "$PROJECT_DIR" || {
    echo "❌ Error: Cannot access backend directory: $PROJECT_DIR"
    exit 1
}

# Check if port is already in use
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use"
    echo "   Stopping existing process..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Create necessary directories
mkdir -p memory logs
touch memory/pending_actions.json 2>/dev/null || true
chmod 666 memory/pending_actions.json 2>/dev/null || true

# Start backend
echo "📦 Starting backend server..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

sleep 5

# Check if backend started
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
    echo ""
    echo "📊 Status:"
    curl -s http://localhost:$PORT/health | python3 -m json.tool 2>/dev/null || echo "   Backend is starting..."
    echo ""
    echo "🌐 URLs:"
    echo "   API: http://localhost:$PORT/api"
    echo "   Docs: http://localhost:$PORT/docs"
    echo "   Health: http://localhost:$PORT/health"
    echo ""
    echo "📝 Logs: tail -f /tmp/backend.log"
    echo ""
else
    echo "❌ Backend failed to start!"
    echo "📝 Check logs: tail -f /tmp/backend.log"
    exit 1
fi

