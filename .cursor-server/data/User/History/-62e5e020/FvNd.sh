#!/bin/bash
# Restart Backend directly (without Docker)
# This script restarts the Backend using uvicorn directly

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Restarting Backend (Direct Mode)..."

# Kill all uvicorn processes on port 8000
echo "🛑 Stopping existing Backend processes..."
pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Find Python 3.11
PYTHON311=$(which python3.11 || echo "/usr/bin/python3.11")
if [ ! -f "$PYTHON311" ]; then
    PYTHON311=$(find /usr -name python3.11 2>/dev/null | head -1)
fi

if [ -z "$PYTHON311" ]; then
    echo "❌ Python 3.11 not found!"
    exit 1
fi

echo "✅ Using Python: $PYTHON311"

# Start Backend
echo "🚀 Starting Backend..."
cd "$SCRIPT_DIR"
nohup "$PYTHON311" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend-direct.log 2>&1 &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "📝 Logs: tail -f /tmp/backend-direct.log"

# Wait for Backend to be ready
echo "⏳ Waiting for Backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running!"
        echo "   API: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        
        # Check if routes are registered
        sleep 2
        ROUTES=$(curl -s http://localhost:8000/openapi.json | python3 -c "import json, sys; data = json.load(sys.stdin); paths = [p for p in data['paths'].keys() if '/api/identity' in p or '/api/crm' in p]; print(len(paths))" 2>/dev/null || echo "0")
        if [ "$ROUTES" -gt 0 ]; then
            echo "✅ Identity/CRM routes registered: $ROUTES routes"
        else
            echo "⚠️  Identity/CRM routes not yet registered (may need a moment)"
        fi
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend started but not responding yet."
        echo "   Check logs: tail -f /tmp/backend-direct.log"
    else
        sleep 2
    fi
done

echo ""
echo "📝 Useful commands:"
echo "   View logs: tail -f /tmp/backend-direct.log"
echo "   Stop: pkill -f 'uvicorn.*8000'"
echo "   Health: curl http://localhost:8000/health"

