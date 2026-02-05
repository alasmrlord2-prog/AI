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
# Stop any existing containers first (try both with and without sudo)
docker compose down 2>/dev/null || sudo docker compose down 2>/dev/null || true
docker compose stop frontend-dashboard frontend-crm frontend-aaa 2>/dev/null || sudo docker compose stop frontend-dashboard frontend-crm frontend-aaa 2>/dev/null || true
docker compose rm -f frontend-dashboard frontend-crm frontend-aaa 2>/dev/null || sudo docker compose rm -f frontend-dashboard frontend-crm frontend-aaa 2>/dev/null || true

# Kill Next.js processes
pkill -9 -f "next-server" 2>/dev/null || true
pkill -9 -f "next dev" 2>/dev/null || true
pkill -9 -f "next.*3000" 2>/dev/null || true
pkill -9 -f "next.*3001" 2>/dev/null || true
pkill -9 -f "next.*3002" 2>/dev/null || true

# Kill processes by port (try with sudo if needed)
for port in 3000 3001 3002; do
    if command -v fuser >/dev/null 2>&1; then
        fuser -k ${port}/tcp 2>/dev/null || sudo fuser -k ${port}/tcp 2>/dev/null || true
    fi
    PIDS=$(lsof -ti:${port} 2>/dev/null)
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null || sudo kill -9 $PIDS 2>/dev/null || true
    fi
done

sleep 3

# Start all frontend services
# Use sudo if needed
if docker compose up -d frontend-dashboard frontend-crm frontend-aaa 2>&1 | grep -q "permission denied"; then
    echo "⚠️  Using sudo for Docker..."
    sudo docker compose up -d frontend-dashboard frontend-crm frontend-aaa
else
    docker compose up -d frontend-dashboard frontend-crm frontend-aaa
fi

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

