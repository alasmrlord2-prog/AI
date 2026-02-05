#!/bin/bash

# ============================================
# AI Agent Frontend - Restart Script
# ============================================
# This script restarts the frontend development server
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STOP_SCRIPT="$SCRIPT_DIR/stop_frontend.sh"
START_SCRIPT="$SCRIPT_DIR/start_frontend.sh"

echo "🔄 Restarting AI Agent Frontend..."
echo "========================================"
echo ""

# Step 1: Stop frontend
echo "⏹️  Step 1: Stopping frontend..."
if [ -f "$STOP_SCRIPT" ]; then
    bash "$STOP_SCRIPT"
else
    echo "❌ Error: stop_frontend.sh not found!"
    exit 1
fi

echo ""
echo "⏳ Waiting for processes to fully stop..."
sleep 3

# Step 2: Start frontend
echo ""
echo "🚀 Step 2: Starting frontend..."
if [ -f "$START_SCRIPT" ]; then
    bash "$START_SCRIPT"
else
    echo "❌ Error: start_frontend.sh not found!"
    exit 1
fi

echo ""
echo "✅ Restart complete!"
echo "========================================"

