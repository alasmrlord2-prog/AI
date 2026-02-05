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

# Check if Docker container is running
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "ai-agent-backend-prod"; then
    echo "🐳 Docker container is already running"
    echo "   Using existing Docker container..."
    docker ps --filter "name=ai-agent-backend-prod" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    exit 0
fi

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

# Check and install dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo "   Installing missing dependencies..."
    python3 -m pip install -q -r requirements.txt 2>&1 | grep -v "already satisfied" || true
fi

# Start backend
echo "📦 Starting backend server..."
# Use a log file in the project directory instead of /tmp
LOG_FILE="$PROJECT_DIR/backend.log"
touch "$LOG_FILE" 2>/dev/null || LOG_FILE="/tmp/backend_$$.log"
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload > "$LOG_FILE" 2>&1 &
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
    echo "📝 Logs: tail -f $LOG_FILE"
    echo ""
else
    echo "❌ Backend failed to start!"
    echo "📝 Check logs: tail -f $LOG_FILE"
    exit 1
fi

