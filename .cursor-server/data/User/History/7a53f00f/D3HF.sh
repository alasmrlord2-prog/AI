#!/bin/bash

# ============================================
# AI Agent - Server Restart Script
# ============================================
# This script restarts all services
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHUTDOWN_SCRIPT="$SCRIPT_DIR/shutdown_server.sh"
STARTUP_SCRIPT="$SCRIPT_DIR/startup_server.sh"

echo "🔄 Restarting AI Agent Server..."
echo "========================================"
echo ""

# Step 1: Shutdown
echo "⏹️  Step 1: Shutting down services..."
if [ -f "$SHUTDOWN_SCRIPT" ]; then
    bash "$SHUTDOWN_SCRIPT"
else
    echo "❌ Error: shutdown_server.sh not found!"
    exit 1
fi

echo ""
echo "⏳ Waiting for clean shutdown..."
sleep 5

# Step 2: Startup
echo ""
echo "🚀 Step 2: Starting services..."
if [ -f "$STARTUP_SCRIPT" ]; then
    bash "$STARTUP_SCRIPT"
else
    echo "❌ Error: startup_server.sh not found!"
    exit 1
fi

echo ""
echo "✅ Server restart complete!"
echo "========================================"

