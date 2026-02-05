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
pkill -9 -f "uvicorn.*8000" 2>/dev/null && echo "✅ Killed uvicorn on 8000" || true
pkill -9 -f "next dev.*3000" 2>/dev/null && echo "✅ Killed next on 3000" || true
pkill -9 -f "next dev.*3001" 2>/dev/null && echo "✅ Killed next on 3001" || true
pkill -9 -f "next dev.*3002" 2>/dev/null && echo "✅ Killed next on 3002" || true
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Freed port 8000" || echo "⚠️  Port 8000 already free"
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "✅ Freed port 3000" || echo "⚠️  Port 3000 already free"
lsof -ti:3001 | xargs kill -9 2>/dev/null && echo "✅ Freed port 3001" || echo "⚠️  Port 3001 already free"
lsof -ti:3002 | xargs kill -9 2>/dev/null && echo "✅ Freed port 3002" || echo "⚠️  Port 3002 already free"
lsof -ti:5432 | xargs kill -9 2>/dev/null && echo "✅ Freed port 5432" || echo "⚠️  Port 5432 already free"
lsof -ti:11434 | xargs kill -9 2>/dev/null && echo "✅ Freed port 11434" || echo "⚠️  Port 11434 already free"

sleep 2

echo ""
echo "✅ Cleanup complete!"

