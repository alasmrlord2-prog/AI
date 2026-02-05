#!/bin/bash
# Start Frontend Services (Docker)

set -e

cd "$(dirname "$0")"

echo "🚀 Starting Frontend Services..."

# Remove old containers if they exist
echo "🧹 Cleaning up old containers..."
docker rm -f ai-agent-frontend 2>/dev/null || true
docker rm -f ai-agent-frontend-dashboard 2>/dev/null || true
docker rm -f ai-agent-frontend-crm 2>/dev/null || true
docker rm -f ai-agent-frontend-aaa 2>/dev/null || true

# Kill processes using ports
echo "🔌 Freeing up ports..."
pkill -9 -f "next dev.*3000" 2>/dev/null || true
pkill -9 -f "next dev.*3001" 2>/dev/null || true
pkill -9 -f "next dev.*3002" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
lsof -ti:3002 | xargs kill -9 2>/dev/null || true
sleep 2

# Start all frontend services
docker compose up -d frontend-dashboard frontend-crm frontend-aaa

echo "⏳ Waiting for frontends to be ready..."
sleep 10

# Check frontend services
echo ""
echo "✅ Frontend Services Status:"
echo "   Dashboard (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo '000')"
echo "   CRM (3001): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 || echo '000')"
echo "   AAA (3002): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002 || echo '000')"

echo ""
echo "📝 View logs:"
echo "   Dashboard: docker compose logs -f frontend-dashboard"
echo "   CRM: docker compose logs -f frontend-crm"
echo "   AAA: docker compose logs -f frontend-aaa"

