#!/bin/bash

# ============================================
# AI Agent Backend - Stop Script
# ============================================
# This script stops all backend services
# ============================================

PORT=8000

echo "⏹️  Stopping AI Agent Backend Services..."
echo "========================================"
echo ""

# Function to kill processes
kill_processes() {
    local pattern=$1
    local name=$2
    
    if command -v pgrep > /dev/null 2>&1; then
        PIDS=$(pgrep -f "$pattern" 2>/dev/null)
        if [ -n "$PIDS" ]; then
            echo "   Found $name processes: $PIDS"
            echo "$PIDS" | xargs kill -9 2>/dev/null && echo "   ✅ Killed $name processes" || echo "   ⚠️  Some processes may need sudo"
            return 0
        fi
    fi
    return 1
}

# Step 1: Kill uvicorn processes
echo "🔍 Step 1: Finding uvicorn processes..."
if kill_processes "uvicorn.*app.main_new:app" "uvicorn (app.main_new:app)"; then
    sleep 1
fi

if kill_processes "uvicorn.*app.main:app" "uvicorn (app.main:app)"; then
    sleep 1
fi

if kill_processes "uvicorn.*main:app" "uvicorn (main:app)"; then
    sleep 1
fi

if kill_processes "uvicorn" "uvicorn"; then
    sleep 1
fi

# Step 2: Kill any process using port 8000
echo ""
echo "🔌 Step 2: Freeing port $PORT..."
if command -v lsof > /dev/null 2>&1; then
    PIDS=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "   Found processes on port $PORT: $PIDS"
        echo "$PIDS" | xargs kill -9 2>/dev/null && echo "   ✅ Killed processes on port $PORT" || echo "   ⚠️  Some processes may need sudo"
        sleep 2
    else
        echo "   ✅ Port $PORT is free"
    fi
elif command -v fuser > /dev/null 2>&1; then
    if fuser -k $PORT/tcp 2>/dev/null; then
        echo "   ✅ Killed processes on port $PORT"
        sleep 2
    else
        echo "   ✅ Port $PORT is free"
    fi
else
    echo "   ⚠️  Cannot check port $PORT (lsof/fuser not available)"
fi

# Step 3: Verify everything is stopped
echo ""
echo "🔍 Step 3: Verifying all processes stopped..."
sleep 2

STILL_RUNNING=false

# Check for uvicorn processes
if pgrep -f "uvicorn" > /dev/null 2>&1; then
    echo "   ⚠️  Warning: Some uvicorn processes still running"
    STILL_RUNNING=true
fi

# Check port
if command -v lsof > /dev/null 2>&1; then
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo "   ⚠️  Warning: Port $PORT still in use"
        STILL_RUNNING=true
    fi
fi

echo ""
if [ "$STILL_RUNNING" = true ]; then
    echo "⚠️  Some processes may still be running"
    echo "   You may need to run with sudo: sudo ./stop_backend.sh"
    echo ""
    echo "   Or manually kill processes:"
    echo "   sudo pkill -9 -f uvicorn"
    echo "   sudo lsof -ti:$PORT | xargs sudo kill -9"
else
    echo "✅ All backend services stopped successfully!"
    echo "========================================"
fi
echo ""

