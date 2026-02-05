#!/bin/bash
# ============================================
# AI Agent - Stop Frontend Script
# ============================================

set -e

PORT=3000

echo "⏹️  Stopping AI Agent Frontend..."
echo "========================================"

# Stop all Next.js processes
echo "🛑 Stopping frontend processes..."
pkill -f "next dev" 2>/dev/null || true
pkill -f "next start" 2>/dev/null || true

# Free port 3000
echo "🔌 Freeing port $PORT..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true

sleep 2

# Verify
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  Port $PORT is still in use. Processes:"
    lsof -ti:$PORT | xargs ps -p
    echo ""
    echo "💡 Try: sudo kill -9 \$(lsof -ti:$PORT)"
else
    echo "✅ Frontend stopped successfully"
    echo "   Port $PORT is now free"
fi

