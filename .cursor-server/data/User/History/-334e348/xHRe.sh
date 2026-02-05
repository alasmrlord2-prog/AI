#!/bin/bash

# ============================================
# AI Agent - Server Shutdown Script
# ============================================
# This script safely shuts down all services
# and saves configuration for later restart
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.server_config.json"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "⏹️  Shutting Down AI Agent Server..."
echo "========================================"
echo ""

# Step 1: Save current configuration
echo "💾 Step 1: Saving current configuration..."

# Get current IP
CURRENT_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || hostname -I | awk '{print $1}')
CURRENT_HOSTNAME=$(hostname)

# Get current environment variables
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Save configuration
cat > "$CONFIG_FILE" <<EOF
{
  "server_ip": "$CURRENT_IP",
  "hostname": "$CURRENT_HOSTNAME",
  "backend_port": $BACKEND_PORT,
  "frontend_port": $FRONTEND_PORT,
  "shutdown_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "backend_dir": "$BACKEND_DIR",
  "frontend_dir": "$FRONTEND_DIR"
}
EOF

echo "   ✅ Configuration saved to: $CONFIG_FILE"
echo "   📝 Server IP: $CURRENT_IP"
echo "   📝 Hostname: $CURRENT_HOSTNAME"
echo ""

# Step 2: Stop backend services
echo "⏹️  Step 2: Stopping backend services..."
if [ -f "$BACKEND_DIR/stop_backend.sh" ]; then
    cd "$BACKEND_DIR"
    bash stop_backend.sh
    cd "$SCRIPT_DIR"
else
    echo "   ⚠️  stop_backend.sh not found, trying manual stop..."
    pkill -9 -f "uvicorn.*app.main:app" 2>/dev/null || true
    if command -v lsof > /dev/null 2>&1; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    fi
fi
echo ""

# Step 3: Stop frontend services
echo "⏹️  Step 3: Stopping frontend services..."
if command -v lsof > /dev/null 2>&1; then
    FRONTEND_PIDS=$(lsof -ti:$FRONTEND_PORT 2>/dev/null)
    if [ -n "$FRONTEND_PIDS" ]; then
        echo "   Found frontend processes on port $FRONTEND_PORT: $FRONTEND_PIDS"
        echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null && echo "   ✅ Frontend stopped" || echo "   ⚠️  Some processes may need manual kill"
    else
        echo "   ✅ Frontend port $FRONTEND_PORT is free"
    fi
fi

# Kill any node/next processes
pkill -9 -f "next" 2>/dev/null || true
pkill -9 -f "node.*3000" 2>/dev/null || true
echo ""

# Step 4: Wait for processes to fully stop
echo "⏳ Step 4: Waiting for processes to fully stop..."
sleep 3

# Step 5: Verify everything is stopped
echo "🔍 Step 5: Verifying all services stopped..."
ALL_STOPPED=true

if pgrep -f "uvicorn" > /dev/null 2>&1; then
    echo "   ⚠️  Warning: Some uvicorn processes still running"
    ALL_STOPPED=false
fi

if command -v lsof > /dev/null 2>&1; then
    if lsof -ti:8000 > /dev/null 2>&1; then
        echo "   ⚠️  Warning: Port 8000 still in use"
        ALL_STOPPED=false
    fi
    if lsof -ti:3000 > /dev/null 2>&1; then
        echo "   ⚠️  Warning: Port 3000 still in use"
        ALL_STOPPED=false
    fi
fi

echo ""
if [ "$ALL_STOPPED" = true ]; then
    echo "✅ All services stopped successfully!"
    echo "========================================"
    echo ""
    echo "💡 To restart, run: ./startup_server.sh"
    echo "   Or manually: cd backend && ./start_backend.sh"
else
    echo "⚠️  Some services may still be running"
    echo "   You may need to run with sudo: sudo ./shutdown_server.sh"
fi
echo ""

