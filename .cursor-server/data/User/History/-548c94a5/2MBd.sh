#!/bin/bash
# Start Frontend Services (Dashboard, CRM, AAA)

set +e

cd "$(dirname "$0")"

echo "🚀 Starting Frontend Services..."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend is not running. Starting backend first..."
    ./backend-start.sh
    sleep 5
fi

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
sleep 15

# Check frontend services
echo ""
echo "✅ Frontend Services Status:"
for port in 3000 3001 3002; do
    name=""
    case $port in
        3000) name="Dashboard" ;;
        3001) name="CRM" ;;
        3002) name="AAA" ;;
    esac
    status=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:${port} 2>/dev/null || echo '000')
    if [ "$status" = "200" ] || [ "$status" = "000" ]; then
        echo "   ${name} (${port}): http://localhost:${port} [Status: ${status}]"
    else
        echo "   ${name} (${port}): http://localhost:${port} [Status: ${status}]"
    fi
done

echo ""
echo "📝 View logs:"
echo "   Dashboard: docker compose logs -f frontend-dashboard"
echo "   CRM: docker compose logs -f frontend-crm"
echo "   AAA: docker compose logs -f frontend-aaa"
