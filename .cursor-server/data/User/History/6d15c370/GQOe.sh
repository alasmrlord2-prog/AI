#!/bin/bash
# Restart Backend Script (Direct Mode - uvicorn)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Restarting Backend..."

# Find Python 3.11
PYTHON311=$(which python3.11 || echo "/usr/bin/python3.11")
if [ ! -f "$PYTHON311" ]; then
    PYTHON311=$(find /usr -name python3.11 2>/dev/null | head -1)
fi

if [ -z "$PYTHON311" ] || [ ! -f "$PYTHON311" ]; then
    echo "❌ Python 3.11 not found!"
    exit 1
fi

echo "✅ Using Python: $PYTHON311"

# Stop existing processes
echo "🛑 Stopping existing Backend processes..."
# Kill all uvicorn processes (both main:app and app.main:app)
pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
pkill -9 -f "uvicorn.*main" 2>/dev/null || true
# Kill any process using port 8000
if command -v lsof &> /dev/null; then
    lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
elif command -v fuser &> /dev/null; then
    fuser -k 8000/tcp 2>/dev/null || true
fi
# Also kill by port using ss
if command -v ss &> /dev/null; then
    for pid in $(ss -tlnp | grep :8000 | grep -oP 'pid=\K[0-9]+' | sort -u); do
        kill -9 $pid 2>/dev/null || true
    done
fi
# Wait and verify port is free
sleep 3
if ss -tlnp | grep -q :8000; then
    echo "⚠️  Port 8000 still in use, forcing kill..."
    fuser -k 8000/tcp 2>/dev/null || true
    sleep 2
fi
echo "✅ Port 8000 cleared"

# Verify routers can be imported
echo "🔍 Verifying routers..."
if ! "$PYTHON311" -c "from app.api.identity_api import router; from app.api.crm_api import router" 2>/dev/null; then
    echo "⚠️  Installing email-validator..."
    "$PYTHON311" -m pip install email-validator 2>/dev/null || true
fi

# Start Backend
echo "🚀 Starting Backend..."
LOG_FILE="$SCRIPT_DIR/backend.log"
if [ "$EUID" -eq 0 ]; then
    # Running as root - no need for sudo
    nohup "$PYTHON311" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_FILE" 2>&1 &
else
    # Not root - use sudo
    sudo nohup "$PYTHON311" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_FILE" 2>&1 &
fi
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "📝 Logs: tail -f $LOG_FILE"

# Wait for Backend to be ready
echo "⏳ Waiting for Backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend restarted!"
        echo "   API: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend restarted but not responding yet."
        echo "   Check logs: tail -f $LOG_FILE"
    else
        sleep 2
    fi
done

echo ""
echo "📝 View logs: tail -f $LOG_FILE"
