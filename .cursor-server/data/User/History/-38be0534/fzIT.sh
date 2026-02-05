#!/bin/bash
# Clean up old containers

echo "🧹 Cleaning up old containers..."

# Remove old backend containers
docker rm -f ai-backend 2>/dev/null && echo "✅ Removed ai-backend" || echo "⚠️  ai-backend not found"
docker rm -f ai-agent-backend 2>/dev/null && echo "✅ Removed ai-agent-backend" || echo "⚠️  ai-agent-backend not found"

# Remove old frontend containers
docker rm -f ai-agent-frontend 2>/dev/null && echo "✅ Removed ai-agent-frontend" || echo "⚠️  ai-agent-frontend not found"
docker rm -f ai-agent-frontend-crm 2>/dev/null && echo "✅ Removed ai-agent-frontend-crm" || echo "⚠️  ai-agent-frontend-crm not found"
docker rm -f ai-agent-frontend-aaa 2>/dev/null && echo "✅ Removed ai-agent-frontend-aaa" || echo "⚠️  ai-agent-frontend-aaa not found"

echo ""
echo "✅ Cleanup complete!"

