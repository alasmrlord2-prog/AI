#!/bin/bash
# ============================================
# AI Agent - Restart Backend Script
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Restarting AI Agent Backend..."
echo "========================================"

# Stop backend
"$SCRIPT_DIR/stop.sh"

sleep 2

# Start backend
"$SCRIPT_DIR/start.sh"

echo ""
echo "✅ Backend restarted successfully!"

