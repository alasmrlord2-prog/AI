#!/bin/bash

# ============================================
# AI Agent Frontend - Start Script
# ============================================
# This script starts the frontend development server
# ============================================

set -e  # Exit on error

FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$FRONTEND_DIR/frontend.log"
PORT=3000

echo "🚀 Starting AI Agent Frontend..."
echo "========================================"
echo ""

# Navigate to frontend directory
cd "$FRONTEND_DIR" || {
    echo "❌ Error: Cannot access frontend directory: $FRONTEND_DIR"
    exit 1
}

# Check if frontend is already running
if command -v lsof > /dev/null 2>&1; then
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo "⚠️  Warning: Port $PORT is already in use!"
        echo "   Frontend may already be running."
        echo "   Use './stop_frontend.sh' to stop it first, or './restart_frontend.sh' to restart."
        exit 1
    fi
fi

# Check for running Next.js processes
if pgrep -f "next dev" > /dev/null 2>&1; then
    echo "⚠️  Warning: Frontend process already running!"
    echo "   Use './stop_frontend.sh' to stop it first, or './restart_frontend.sh' to restart."
    exit 1
fi

# Check for Node.js
echo "🔍 Checking Node.js..."
if ! command -v node > /dev/null 2>&1; then
    echo "❌ Error: Node.js is not installed!"
    echo "   Please install Node.js 20+ to continue."
    exit 1
fi

NODE_VERSION=$(node --version)
echo "   ✅ Node.js version: $NODE_VERSION"
echo ""

# Check for npm
if ! command -v npm > /dev/null 2>&1; then
    echo "❌ Error: npm is not installed!"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check for .env.local
if [ ! -f ".env.local" ]; then
    if [ -f "env.example" ]; then
        echo "📝 Creating .env.local from env.example..."
        cp env.example .env.local
        echo "   ⚠️  Please update .env.local with your configuration"
    fi
fi

# Start the frontend
echo "🚀 Starting frontend server..."
echo "   Port: $PORT"
echo "   Logs: $LOG_FILE"
echo ""

# Start Next.js in background
nohup npm run dev > "$LOG_FILE" 2>&1 &

FRONTEND_PID=$!
echo "   Process ID: $FRONTEND_PID"

# Wait for startup
echo ""
echo "⏳ Waiting for frontend to start..."
sleep 8

# Check if it's running
if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    # Double check with port
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo ""
        echo "✅ Frontend started successfully!"
        echo "========================================"
        echo ""
        echo "📊 Status:"
        echo "   PID: $FRONTEND_PID"
        echo "   Port: $PORT"
        echo "   Status: Running"
        echo ""
        echo "🌐 URLs:"
        echo "   Frontend: http://localhost:$PORT"
        echo ""
        echo "📝 Logs:"
        echo "   View: tail -f $LOG_FILE"
        echo "   File: $LOG_FILE"
        echo ""
        echo "💡 Recent startup logs:"
        tail -15 "$LOG_FILE" | grep -E "✅|⚠️|started|ready|compiled|ERROR|WARN" || tail -10 "$LOG_FILE"
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
    echo "❌ Frontend failed to start!"
    echo "========================================"
    echo ""
    echo "📝 Error logs:"
    tail -30 "$LOG_FILE"
    echo ""
    echo "💡 Check the logs above for errors"
    exit 1
fi

