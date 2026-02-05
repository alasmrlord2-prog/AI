#!/bin/bash

# ============================================
# AI Agent Backend - Restart Script
# ============================================
# This script restarts all backend services
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STOP_SCRIPT="$SCRIPT_DIR/stop_backend.sh"
START_SCRIPT="$SCRIPT_DIR/start_backend.sh"

echo "🔄 Restarting AI Agent Backend Services..."
echo "========================================"
echo ""

# Step 1: Stop backend
echo "⏹️  Step 1: Stopping backend..."
if [ -f "$STOP_SCRIPT" ]; then
    bash "$STOP_SCRIPT"
else
    echo "❌ Error: stop_backend.sh not found!"
    exit 1
fi

echo ""
echo "⏳ Waiting for processes to fully stop..."
sleep 3

# Step 2: Start backend
echo ""
echo "🚀 Step 2: Starting backend..."
if [ -f "$START_SCRIPT" ]; then
    bash "$START_SCRIPT"
else
    echo "❌ Error: start_backend.sh not found!"
    exit 1
fi

echo ""
echo "✅ Restart complete!"
echo "========================================"
