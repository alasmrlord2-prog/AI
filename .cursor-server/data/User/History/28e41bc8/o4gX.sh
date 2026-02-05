#!/bin/bash

# ============================================
# AI Agent Backend - Start Script
# ============================================
# This script starts all backend services
# ============================================

set -e  # Exit on error

BACKEND_DIR="/home/ai/ai-agent/backend"
LOG_FILE="$BACKEND_DIR/backend.log"
PORT=8000

echo "🚀 Starting AI Agent Backend Services..."
echo "========================================"
echo ""

# Navigate to backend directory
cd "$BACKEND_DIR" || {
    echo "❌ Error: Cannot access backend directory: $BACKEND_DIR"
    exit 1
}

# Check if backend is already running
if command -v lsof > /dev/null 2>&1; then
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo "⚠️  Warning: Port $PORT is already in use!"
        echo "   Backend may already be running."
        echo "   Use './stop_backend.sh' to stop it first, or './restart_backend.sh' to restart."
        exit 1
    fi
fi

# Check for running uvicorn processes
if pgrep -f "uvicorn.*app.main:app" > /dev/null 2>&1; then
    echo "⚠️  Warning: Backend process already running!"
    echo "   Use './stop_backend.sh' to stop it first, or './restart_backend.sh' to restart."
    exit 1
fi

# Find Python command
echo "🔍 Detecting Python version..."
if command -v python3.11 > /dev/null 2>&1; then
    PYTHON_CMD="python3.11"
    echo "   ✅ Using Python 3.11"
elif command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD="python3"
    echo "   ✅ Using Python 3"
else
    PYTHON_CMD="python"
    echo "   ⚠️  Using default Python (may not be Python 3)"
fi

# Verify Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "   Version: $PYTHON_VERSION"
echo ""

# Install/update dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    $PYTHON_CMD -m pip install -q -r requirements.txt 2>/dev/null || {
        echo "   ⚠️  Some dependencies may need manual installation"
        echo "   Run: pip install -r requirements.txt"
    }
    echo "   ✅ Dependencies installed"
else
    echo "   ⚠️  requirements.txt not found"
fi
echo ""

# Start the backend
echo "🚀 Starting backend server..."
echo "   Host: 0.0.0.0"
echo "   Port: $PORT"
echo "   Logs: $LOG_FILE"
echo ""

# Start uvicorn in background (using main_new.py - refactored version)
nohup $PYTHON_CMD -m uvicorn app.main_new:app \
    --host 0.0.0.0 \
    --port $PORT \
    --reload \
    > "$LOG_FILE" 2>&1 &

BACKEND_PID=$!
echo "   Process ID: $BACKEND_PID"

# Wait for startup
echo ""
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if it's running
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    # Double check with port
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo ""
        echo "✅ Backend started successfully!"
        echo "========================================"
        echo ""
        echo "📊 Status:"
        echo "   PID: $BACKEND_PID"
        echo "   Port: $PORT"
        echo "   Status: Running"
        echo ""
        echo "🌐 URLs:"
        echo "   API: http://localhost:$PORT"
        echo "   Docs: http://localhost:$PORT/docs"
        echo ""
        echo "📝 Logs:"
        echo "   View: tail -f $LOG_FILE"
        echo "   File: $LOG_FILE"
        echo ""
        echo "💡 Recent startup logs:"
        tail -15 "$LOG_FILE" | grep -E "✅|⚠️|started|Uvicorn|Application startup|Tools imported|ERROR|INFO" || tail -10 "$LOG_FILE"
        echo ""
    else
        echo ""
        echo "⚠️  Process started but port $PORT not accessible yet..."
        echo "   Checking logs for errors..."
        tail -20 "$LOG_FILE"
        exit 1
    fi
else
    echo ""
    echo "❌ Backend failed to start!"
    echo "========================================"
    echo ""
    echo "📝 Error logs:"
    tail -30 "$LOG_FILE"
    echo ""
    echo "💡 Check the logs above for errors"
    exit 1
fi

