#!/bin/bash

# Script to restart the AI Agent Backend

echo "🔄 Restarting AI Agent Backend..."

# Find and kill existing uvicorn processes
echo "⏹️  Stopping existing backend processes..."
pkill -f "uvicorn.*main:app" || pkill -f "uvicorn.*app.main:app" || echo "No existing process found"

# Wait a moment
sleep 2

# Navigate to backend directory
cd /home/ai/ai-agent/backend || exit 1

# Install/update dependencies
echo "📦 Installing/updating dependencies..."
pip install -q psutil 2>/dev/null || echo "psutil already installed"

# Start the backend
echo "🚀 Starting backend..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

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

