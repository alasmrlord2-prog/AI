#!/bin/bash

echo "🔄 Final Backend Restart Script"
echo "================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script needs root privileges to kill processes"
    echo "   Please run: sudo ./FINAL_RESTART.sh"
    exit 1
fi

# Step 1: Kill all uvicorn processes
echo "⏹️  Step 1: Stopping all uvicorn processes..."
pkill -9 -f "uvicorn" 2>/dev/null
sleep 2

# Step 2: Free port 8000
echo "🔌 Step 2: Freeing port 8000..."
fuser -k 8000/tcp 2>/dev/null || echo "Port 8000 is free"
sleep 2

# Step 3: Navigate to backend
cd /home/ai/ai-agent/backend || exit 1

# Step 4: Install dependencies
echo "📦 Step 3: Checking dependencies..."
python3.11 -m pip install -q psutil 2>/dev/null || echo "psutil check..."

# Step 5: Start backend with python3.11
echo "🚀 Step 4: Starting backend with python3.11..."
nohup python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

# Wait for startup
sleep 5

# Step 6: Check status
echo ""
echo "📊 Step 5: Checking status..."
echo ""

if ps aux | grep "[u]vicorn.*app.main:app" > /dev/null; then
    echo "✅ Backend started successfully!"
    echo ""
    echo "📝 Recent logs:"
    tail -15 backend.log | grep -E "✅|⚠️|started|Uvicorn|Application startup|Tools imported|ERROR" || tail -10 backend.log
    echo ""
    echo "🌐 API: http://localhost:8000"
    echo "📖 Docs: http://localhost:8000/docs"
    echo ""
    echo "💡 To view logs: tail -f /home/ai/ai-agent/backend/backend.log"
else
    echo "❌ Backend failed to start!"
    echo ""
    echo "📝 Error logs:"
    tail -30 backend.log
    echo ""
    echo "💡 Check the logs above for errors"
fi

