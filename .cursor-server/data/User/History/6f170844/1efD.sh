#!/bin/bash

echo "🔄 Force Restarting AI Agent Backend..."

# Find all uvicorn processes
echo "⏹️  Finding uvicorn processes..."
UVICORN_PIDS=$(ps aux | grep "[u]vicorn" | awk '{print $2}')

if [ -z "$UVICORN_PIDS" ]; then
    echo "No uvicorn processes found"
else
    echo "Found processes: $UVICORN_PIDS"
    for PID in $UVICORN_PIDS; do
        echo "Attempting to kill PID: $PID"
        kill -9 $PID 2>/dev/null || echo "Cannot kill $PID (may need sudo)"
    done
    sleep 2
fi

# Kill anything on port 8000
echo "🔌 Freeing port 8000..."
fuser -k 8000/tcp 2>/dev/null || lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Port 8000 is free"

sleep 2

# Navigate to backend directory
cd /home/ai/ai-agent/backend || exit 1

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -q psutil 2>/dev/null || echo "psutil check..."

# Start the backend with correct path
echo "🚀 Starting backend with app.main:app..."
cd /home/ai/ai-agent/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

# Wait for startup
sleep 5

# Check if running
if ps aux | grep "[u]vicorn.*app.main:app" > /dev/null; then
    echo "✅ Backend started successfully!"
    echo "📝 Check logs: tail -f /home/ai/ai-agent/backend/backend.log"
    echo "🌐 API: http://localhost:8000"
    echo ""
    echo "Recent logs:"
    tail -10 backend.log
else
    echo "❌ Backend failed to start. Check logs:"
    tail -30 backend.log
fi

