#!/bin/bash
# Start Frontend Services (Dashboard, CRM, AAA)

set +e

cd "$(dirname "$0")"

echo "🚀 Starting Frontend Services..."

# Clean up old containers
echo "🧹 Cleaning up old containers..."
docker rm -f ai-agent-frontend-dashboard ai-agent-frontend-crm ai-agent-frontend-aaa 2>/dev/null || true

# Free up ports
echo "🔌 Freeing up ports..."
for port in 3000 3001 3002; do
    # Kill Next.js processes
    pkill -9 -f "next.*${port}" 2>/dev/null || true
    pkill -9 -f "next-server.*${port}" 2>/dev/null || true
    
    # Kill processes on port
    PIDS=$(lsof -ti:${port} 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null || true
    fi
done
sleep 3

# Start frontend services
echo "🚀 Starting frontend containers..."
docker compose up -d frontend-dashboard frontend-crm frontend-aaa

echo "⏳ Waiting for frontends to be ready..."
sleep 10

# Check frontend services
echo ""
echo "✅ Frontend Services Status:"
echo "   Dashboard (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo '000')"
echo "   CRM (3001): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 2>/dev/null || echo '000')"
echo "   AAA (3002): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002 2>/dev/null || echo '000')"

echo ""
echo "📝 View logs:"
echo "   Dashboard: docker compose logs -f frontend-dashboard"
echo "   CRM: docker compose logs -f frontend-crm"
echo "   AAA: docker compose logs -f frontend-aaa"
