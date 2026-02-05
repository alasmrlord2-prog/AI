#!/bin/bash
# Start Backend Script
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🚀 Starting Backend..."

# Find Python 3.11
PYTHON311=$(which python3.11 || echo "/usr/bin/python3.11")
if [ ! -f "$PYTHON311" ]; then
    PYTHON311=$(find /usr -name python3.11 2>/dev/null | head -1)
fi

if [ -z "$PYTHON311" ] || [ ! -f "$PYTHON311" ]; then
    echo "❌ Python 3.11 not found!"
    exit 1
fi

# Check if port is in use
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is in use. Stopping existing processes..."
    
    # Stop uvicorn processes
    sudo pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
    sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || true
    
    # Also try Docker if exists
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down 2>/dev/null || true
    elif command -v docker &> /dev/null; then
        docker compose -f "$PROJECT_ROOT/docker-compose.yml" down 2>/dev/null || true
    fi
    
    sleep 3
    echo "✅ Port 8000 cleared"
fi

# Verify routers
echo "🔍 Verifying routers..."
cd "$SCRIPT_DIR"
if ! "$PYTHON311" -c "from app.api.identity_api import router; from app.api.crm_api import router" 2>/dev/null; then
    echo "⚠️  Installing email-validator..."
    "$PYTHON311" -m pip install email-validator 2>/dev/null || true
fi

# Start Backend directly
echo "🚀 Starting Backend (Direct Mode)..."
cd "$SCRIPT_DIR"
sudo nohup "$PYTHON311" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if backend is responding
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running!"
        echo "   API: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend started but not responding yet."
        echo "   Check logs: docker-compose -f $PROJECT_ROOT/docker-compose.yml logs -f backend"
    else
        sleep 2
    fi
done

echo ""
echo "📝 View logs: docker-compose -f $PROJECT_ROOT/docker-compose.yml logs -f backend"
