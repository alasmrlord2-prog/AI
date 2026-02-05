#!/bin/bash
# Start All Services - Fixed version with proper Docker permissions

set +e  # Don't exit on error

cd "$(dirname "$0")"

echo "🚀 Starting All Services (Fixed Version)..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    DOCKER_CMD="docker"
    echo "✅ Running as root - using docker directly"
else
    # Check if user is in docker group
    if groups | grep -q docker; then
        DOCKER_CMD="docker"
        echo "✅ User in docker group - using docker directly"
    else
        DOCKER_CMD="sudo docker"
        echo "⚠️  User not in docker group - will use sudo (may require password)"
    fi
fi

# Clean up first
echo ""
echo "🧹 Cleaning up..."
$DOCKER_CMD compose down 2>/dev/null || true

# Kill processes on ports
echo "🔌 Freeing up ports..."
for port in 3000 3001 3002; do
    if command -v fuser >/dev/null 2>&1; then
        fuser -k ${port}/tcp 2>/dev/null || true
    fi
    PIDS=$(lsof -ti:${port} 2>/dev/null)
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null || true
    fi
done

# Kill Next.js processes
pkill -9 -f "next-server" 2>/dev/null || true
pkill -9 -f "next dev" 2>/dev/null || true
for pid in $(pgrep -f "next-server" 2>/dev/null); do
    kill -9 $pid 2>/dev/null || true
done

sleep 2

# Start backend
echo ""
echo "🚀 Starting Backend Services..."
$DOCKER_CMD compose up -d postgres ollama backend

echo "⏳ Waiting for backend to be ready..."
sleep 5

for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend started but not responding yet."
    else
        sleep 2
    fi
done

# Start frontend
echo ""
echo "🚀 Starting Frontend Services..."
$DOCKER_CMD compose up -d frontend-dashboard frontend-crm frontend-aaa

echo "⏳ Waiting for frontends to be ready..."
sleep 10

# Check status
echo ""
echo "✅ Services Status:"
echo "   Backend (8000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health || echo '000')"
echo "   Dashboard (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo '000')"
echo "   CRM (3001): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 || echo '000')"
echo "   AAA (3002): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002 || echo '000')"

echo ""
echo "📝 View logs: $DOCKER_CMD compose logs -f"

