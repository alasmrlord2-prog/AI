#!/bin/bash

# Script to restart the AI Agent Backend

echo "🔄 Restarting AI Agent Backend..."

# Find and kill existing uvicorn processes
echo "⏹️  Stopping existing backend processes..."
# Kill all uvicorn processes more aggressively
pkill -9 -f "uvicorn" 2>/dev/null
pkill -9 -f "main:app" 2>/dev/null
pkill -9 -f "app.main:app" 2>/dev/null
# Also find PIDs and kill them
if command -v pgrep > /dev/null 2>&1; then
    UVICORN_PIDS=$(pgrep -f "uvicorn" 2>/dev/null)
    if [ -n "$UVICORN_PIDS" ]; then
        echo "   Found uvicorn processes: $UVICORN_PIDS"
        echo "$UVICORN_PIDS" | xargs kill -9 2>/dev/null
    fi
fi

# Also kill any process using port 8000
echo "🔌 Freeing port 8000..."
if command -v lsof > /dev/null 2>&1; then
    PIDS=$(lsof -ti:8000 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "   Killing processes on port 8000: $PIDS"
        echo "$PIDS" | xargs kill -9 2>/dev/null
    else
        echo "   Port 8000 is free"
    fi
elif command -v fuser > /dev/null 2>&1; then
    fuser -k 8000/tcp 2>/dev/null && echo "   Killed processes on port 8000" || echo "   Port 8000 is free"
else
    echo "⚠️  Cannot check port 8000 (fuser/lsof not available)"
fi

# Wait a moment for processes to die
sleep 3

# Verify port is free
if command -v lsof > /dev/null 2>&1; then
    if lsof -ti:8000 > /dev/null 2>&1; then
        echo "⚠️  Warning: Port 8000 still in use. Trying to force kill..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null
        sleep 2
    fi
fi

# Navigate to backend directory
cd /home/ai/ai-agent/backend || exit 1

# Install/update dependencies
echo "📦 Installing/updating dependencies..."
pip install -q psutil 2>/dev/null || echo "psutil already installed"

# Start the backend
echo "🚀 Starting backend..."
# Try python3.11 first, fallback to python3
if command -v python3.11 > /dev/null 2>&1; then
    PYTHON_CMD="python3.11"
elif command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

nohup $PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

# Wait a moment for it to start
sleep 3

# Check if it's running
if ps aux | grep -E "uvicorn.*app.main:app" | grep -v grep > /dev/null; then
    echo "✅ Backend started successfully!"
    echo "📝 Logs: tail -f /home/ai/ai-agent/backend/backend.log"
    echo "🌐 API: http://localhost:8000"
else
    echo "❌ Backend failed to start. Check logs:"
    tail -20 backend.log
fi

