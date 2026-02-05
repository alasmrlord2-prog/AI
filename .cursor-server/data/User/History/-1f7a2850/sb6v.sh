#!/bin/bash

# ============================================
# AI Agent Frontend - Stop Script
# ============================================
# This script stops the frontend development server
# ============================================

PORT=3000

echo "⏹️  Stopping AI Agent Frontend..."
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

# Step 1: Kill Next.js processes
echo "🔍 Step 1: Finding Next.js processes..."
if kill_processes "next dev" "Next.js dev"; then
    sleep 1
fi

if kill_processes "next-server" "Next.js server"; then
    sleep 1
fi

if kill_processes "node.*next" "Node.js Next"; then
    sleep 1
fi

# Step 2: Kill any process using port 3000
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

# Check for Next.js processes
if pgrep -f "next" > /dev/null 2>&1; then
    echo "   ⚠️  Warning: Some Next.js processes still running"
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
    echo "   You may need to run with sudo: sudo ./stop_frontend.sh"
    echo ""
    echo "   Or manually kill processes:"
    echo "   sudo pkill -9 -f next"
    echo "   sudo lsof -ti:$PORT | xargs sudo kill -9"
else
    echo "✅ All frontend services stopped successfully!"
    echo "========================================"
fi
echo ""

