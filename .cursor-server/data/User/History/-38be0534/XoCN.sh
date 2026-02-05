#!/bin/bash
# Clean up old containers and free ports

echo "🧹 Cleaning up old containers and ports..."

# Remove old backend containers
docker rm -f ai-backend 2>/dev/null && echo "✅ Removed ai-backend" || echo "⚠️  ai-backend not found"
docker rm -f ai-agent-backend 2>/dev/null && echo "✅ Removed ai-agent-backend" || echo "⚠️  ai-agent-backend not found"

# Remove old frontend containers
docker rm -f ai-agent-frontend 2>/dev/null && echo "✅ Removed ai-agent-frontend" || echo "⚠️  ai-agent-frontend not found"
docker rm -f ai-agent-frontend-dashboard 2>/dev/null && echo "✅ Removed ai-agent-frontend-dashboard" || echo "⚠️  ai-agent-frontend-dashboard not found"
docker rm -f ai-agent-frontend-crm 2>/dev/null && echo "✅ Removed ai-agent-frontend-crm" || echo "⚠️  ai-agent-frontend-crm not found"
docker rm -f ai-agent-frontend-aaa 2>/dev/null && echo "✅ Removed ai-agent-frontend-aaa" || echo "⚠️  ai-agent-frontend-aaa not found"

# Kill processes using ports
echo ""
echo "🔌 Freeing up ports..."

# Kill all Next.js processes (more aggressive)
pkill -9 -f "next-server" 2>/dev/null && echo "✅ Killed next-server processes" || true
pkill -9 -f "next dev" 2>/dev/null && echo "✅ Killed next dev processes" || true
pkill -9 -f "next.*3000" 2>/dev/null && echo "✅ Killed next on 3000" || true
pkill -9 -f "next.*3001" 2>/dev/null && echo "✅ Killed next on 3001" || true
pkill -9 -f "next.*3002" 2>/dev/null && echo "✅ Killed next on 3002" || true

# Kill uvicorn processes
pkill -9 -f "uvicorn.*8000" 2>/dev/null && echo "✅ Killed uvicorn on 8000" || true

# Kill processes by port using fuser (more reliable)
for port in 3000 3001 3002 8000 5432 11434; do
    if command -v fuser >/dev/null 2>&1; then
        fuser -k ${port}/tcp 2>/dev/null && echo "✅ Freed port $port (fuser)" || true
    fi
    # Also try with lsof
    PIDS=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null && echo "✅ Freed port $port (lsof)" || true
    fi
done

# Additional cleanup: kill any remaining node processes related to frontend
pkill -9 -f "node.*frontend.*300" 2>/dev/null && echo "✅ Killed frontend node processes" || true

sleep 2

echo ""
echo "✅ Cleanup complete!"

