#!/bin/bash
# ============================================
# AI Agent - Start Frontend Script
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent/frontend"
PORT=3000

echo "🚀 Starting AI Agent Frontend..."
echo "========================================"

cd "$PROJECT_DIR" || {
    echo "❌ Error: Cannot access frontend directory: $PROJECT_DIR"
    exit 1
}

# Check if Docker container is running
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "ai-agent-frontend-prod"; then
    echo "🐳 Docker container is already running"
    echo "   Using existing Docker container..."
    docker ps --filter "name=ai-agent-frontend-prod" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    exit 0
fi

# Check if port is already in use
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use"
    echo "   Stopping existing process..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start frontend
echo "📦 Starting frontend server..."
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 5

# Check if frontend started
if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
    echo ""
    echo "🌐 URLs:"
    echo "   Frontend: http://localhost:$PORT"
    echo "   Local: http://127.0.0.1:$PORT"
    echo ""
    echo "📝 Logs: tail -f /tmp/frontend.log"
    echo ""
else
    echo "❌ Frontend failed to start!"
    echo "📝 Check logs: tail -f /tmp/frontend.log"
    exit 1
fi

