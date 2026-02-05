#!/bin/bash

# ============================================
# AI Agent - Server Startup Script
# ============================================
# This script starts all services after server restart
# and restores configuration automatically
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.server_config.json"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "🚀 Starting AI Agent Server..."
echo "========================================"
echo ""

# Step 1: Load saved configuration
echo "📂 Step 1: Loading saved configuration..."
if [ -f "$CONFIG_FILE" ]; then
    echo "   ✅ Found saved configuration"
    SAVED_IP=$(grep -o '"server_ip": "[^"]*"' "$CONFIG_FILE" | cut -d'"' -f4)
    SAVED_HOSTNAME=$(grep -o '"hostname": "[^"]*"' "$CONFIG_FILE" | cut -d'"' -f4)
    echo "   📝 Saved IP: $SAVED_IP"
    echo "   📝 Saved Hostname: $SAVED_HOSTNAME"
else
    echo "   ⚠️  No saved configuration found, using defaults"
    SAVED_IP=""
    SAVED_HOSTNAME=""
fi
echo ""

# Step 2: Get current server information
echo "🔍 Step 2: Detecting current server information..."
CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || hostname -I | awk '{print $1}' || echo "unknown")
CURRENT_HOSTNAME=$(hostname)

echo "   📝 Current IP: $CURRENT_IP"
echo "   📝 Current Hostname: $CURRENT_HOSTNAME"
echo ""

# Step 3: Check if IP changed
if [ -n "$SAVED_IP" ] && [ "$SAVED_IP" != "$CURRENT_IP" ] && [ "$CURRENT_IP" != "unknown" ]; then
    echo "⚠️  Warning: Server IP has changed!"
    echo "   Old IP: $SAVED_IP"
    echo "   New IP: $CURRENT_IP"
    echo ""
    echo "   💡 If you're using a domain, make sure DNS is updated"
    echo "   💡 If you're using IP directly, update frontend configuration"
    echo ""
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   ❌ Startup cancelled"
        exit 1
    fi
    echo ""
fi

# Step 4: Update configuration if needed
echo "💾 Step 3: Updating configuration..."
cat > "$CONFIG_FILE" <<EOF
{
  "server_ip": "$CURRENT_IP",
  "hostname": "$CURRENT_HOSTNAME",
  "backend_port": 8000,
  "frontend_port": 3000,
  "last_startup_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "backend_dir": "$BACKEND_DIR",
  "frontend_dir": "$FRONTEND_DIR"
}
EOF
echo "   ✅ Configuration updated"
echo ""

# Step 5: Check ports availability
echo "🔌 Step 4: Checking ports availability..."
BACKEND_PORT=8000
FRONTEND_PORT=3000

if command -v lsof > /dev/null 2>&1; then
    if lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
        echo "   ⚠️  Port $BACKEND_PORT is in use, trying to free it..."
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    if lsof -ti:$FRONTEND_PORT > /dev/null 2>&1; then
        echo "   ⚠️  Port $FRONTEND_PORT is in use, trying to free it..."
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
fi

echo "   ✅ Ports are available"
echo ""

# Step 6: Start backend
echo "🚀 Step 5: Starting backend services..."
if [ -f "$BACKEND_DIR/start_backend.sh" ]; then
    cd "$BACKEND_DIR"
    bash start_backend.sh
    BACKEND_STARTED=$?
    cd "$SCRIPT_DIR"
    
    if [ $BACKEND_STARTED -eq 0 ]; then
        echo "   ✅ Backend started successfully"
    else
        echo "   ❌ Backend failed to start"
        exit 1
    fi
else
    echo "   ❌ start_backend.sh not found!"
    exit 1
fi
echo ""

# Step 7: Wait for backend to be ready
echo "⏳ Step 6: Waiting for backend to be ready..."
sleep 5

# Check if backend is responding
MAX_RETRIES=10
RETRY_COUNT=0
BACKEND_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        BACKEND_READY=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   ⏳ Waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ "$BACKEND_READY" = true ]; then
    echo "   ✅ Backend is ready"
else
    echo "   ⚠️  Backend may not be fully ready, but continuing..."
fi
echo ""

# Step 8: Start frontend (optional)
echo "🌐 Step 7: Frontend startup..."
echo "   💡 Frontend should be started separately with:"
echo "      cd frontend && npm run dev"
echo "   💡 Or in production:"
echo "      cd frontend && npm run build && npm start"
echo ""

# Step 9: Display server information
echo "✅ Server startup complete!"
echo "========================================"
echo ""
echo "📊 Server Information:"
echo "   IP Address: $CURRENT_IP"
echo "   Hostname: $CURRENT_HOSTNAME"
echo ""
echo "🌐 Service URLs:"
echo "   Backend API: http://$CURRENT_IP:8000"
echo "   Backend Docs: http://$CURRENT_IP:8000/docs"
echo "   Frontend: http://$CURRENT_IP:3000"
echo ""
if [ -n "$SAVED_IP" ] && [ "$SAVED_IP" != "$CURRENT_IP" ] && [ "$CURRENT_IP" != "unknown" ]; then
    echo "⚠️  IP Changed:"
    echo "   Old: http://$SAVED_IP:8000"
    echo "   New: http://$CURRENT_IP:8000"
    echo ""
    echo "   💡 Update your DNS or frontend configuration if needed"
    echo ""
fi
echo "📝 Logs:"
echo "   Backend: tail -f $BACKEND_DIR/backend.log"
echo "   Config: $CONFIG_FILE"
echo ""

