#!/bin/bash
# ============================================
# AI Agent - Restart Frontend Script
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Restarting AI Agent Frontend..."
echo "========================================"

# Stop frontend
"$SCRIPT_DIR/stop.sh"

sleep 2

# Start frontend
"$SCRIPT_DIR/start.sh"

echo ""
echo "✅ Frontend restarted successfully!"

