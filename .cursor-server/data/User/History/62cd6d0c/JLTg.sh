#!/bin/bash
# Script to restart backend with permissions system

echo "🔄 Restarting Backend with Permissions System..."
echo "================================================"

cd /home/ai/ai-agent/backend || exit 1

# Kill all uvicorn processes
echo "⏹️  Stopping existing backend processes..."
pkill -9 -f "uvicorn.*main" 2>/dev/null
sleep 2

# Kill any process using port 8000
echo "🔌 Freeing port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2

# Verify port is free
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "❌ Port 8000 is still in use. Please stop the process manually:"
    lsof -ti:8000 | xargs ps -p
    exit 1
fi

# Start backend
echo "🚀 Starting backend with permissions system..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend_permissions.log 2>&1 &
BACKEND_PID=$!

sleep 5

# Check if backend started
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend started (PID: $BACKEND_PID)"
    echo ""
    echo "🧪 Testing permissions API..."
    sleep 2
    
    # Test health
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Health check: OK"
    else
        echo "❌ Health check: FAILED"
    fi
    
    # Test permissions endpoint
    RESPONSE=$(curl -s http://localhost:8000/api/permissions/list)
    if echo "$RESPONSE" | grep -q "agent_mode\|permissions"; then
        echo "✅ Permissions API: WORKING!"
        echo ""
        echo "📊 Response preview:"
        echo "$RESPONSE" | python3 -m json.tool | head -15
    else
        echo "❌ Permissions API: NOT WORKING"
        echo "Response: $RESPONSE"
        echo ""
        echo "📝 Check logs: tail -f /tmp/backend_permissions.log"
    fi
    
    echo ""
    echo "✅ Backend is running!"
    echo "📝 Logs: tail -f /tmp/backend_permissions.log"
    echo "🌐 API: http://localhost:8000/api"
    echo "📚 Docs: http://localhost:8000/docs"
else
    echo "❌ Failed to start backend"
    echo "📝 Check logs: tail -f /tmp/backend_permissions.log"
    exit 1
fi

