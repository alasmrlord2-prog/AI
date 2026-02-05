#!/bin/bash

# Script to restart the AI Agent Backend

echo "🔄 Restarting AI Agent Backend..."

# Find and kill existing uvicorn processes
echo "⏹️  Stopping existing backend processes..."
pkill -f "uvicorn.*main:app" || pkill -f "uvicorn.*app.main:app" || echo "No existing process found"

# Also kill any process using port 8000
echo "🔌 Freeing port 8000..."
if command -v fuser > /dev/null 2>&1; then
    fuser -k 8000/tcp 2>/dev/null || echo "Port 8000 is free"
elif command -v lsof > /dev/null 2>&1; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Port 8000 is free"
else
    echo "⚠️  Cannot check port 8000 (fuser/lsof not available)"
fi

# Wait a moment
sleep 2

# Navigate to backend directory
cd /home/ai/ai-agent/backend || exit 1

# Install/update dependencies
echo "📦 Installing/updating dependencies..."
pip install -q psutil 2>/dev/null || echo "psutil already installed"

# Start the backend
echo "🚀 Starting backend..."
echo "⚠️  Note: If port 8000 is in use, stop the old process first:"
echo "   sudo fuser -k 8000/tcp"
echo ""
nohup python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

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

