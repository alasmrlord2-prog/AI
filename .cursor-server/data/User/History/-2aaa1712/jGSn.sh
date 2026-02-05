#!/bin/bash
# Complete Backend Restart Script
# This script stops all Backend processes and restarts with identity/crm routes

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "🔄 Restarting Backend..."

# Stop all uvicorn processes on port 8000
echo "🛑 Stopping existing Backend processes..."
sudo pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || true
sleep 3

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

# Verify routers can be imported
echo "🔍 Verifying routers..."
cd "$SCRIPT_DIR/backend"
if ! "$PYTHON311" -c "from app.api.identity_api import router; from app.api.crm_api import router" 2>/dev/null; then
    echo "⚠️  Installing email-validator..."
    "$PYTHON311" -m pip install email-validator 2>/dev/null || true
fi

# Start Backend
echo "🚀 Starting Backend..."
cd "$SCRIPT_DIR/backend"
sudo nohup "$PYTHON311" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend-restart.log 2>&1 &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "📝 Logs: tail -f /tmp/backend-restart.log"

# Wait for Backend to be ready
echo "⏳ Waiting for Backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running!"
        
        # Check routes
        sleep 3
        ROUTES=$(curl -s http://localhost:8000/openapi.json 2>/dev/null | python3 -c "import json, sys; data = json.load(sys.stdin); paths = [p for p in data['paths'].keys() if '/api/identity' in p or '/api/crm' in p]; print(len(paths))" 2>/dev/null || echo "0")
        if [ "$ROUTES" -gt 0 ]; then
            echo "✅ Identity/CRM routes registered: $ROUTES routes"
        else
            echo "⚠️  Identity/CRM routes: $ROUTES (checking logs...)"
            tail -10 /tmp/backend-restart.log
        fi
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend started but not responding."
        echo "   Check logs: tail -f /tmp/backend-restart.log"
    else
        sleep 2
    fi
done

echo ""
echo "📝 Test commands:"
echo "   Health: curl http://localhost:8000/health"
echo "   Login: curl -X POST http://crm.bankid-sy.com/api/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"admin@example.com\",\"password\":\"admin123\"}'"

