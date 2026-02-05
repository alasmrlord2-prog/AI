#!/bin/bash
# Fix Port Issues - Force cleanup of ports 3000, 3001, 3002

echo "🔧 Fixing port issues..."

# Stop all containers
echo "🛑 Stopping all containers..."
docker compose down 2>/dev/null || sudo docker compose down 2>/dev/null || true

# Remove all frontend containers
echo "🧹 Removing frontend containers..."
docker rm -f ai-agent-frontend-dashboard ai-agent-frontend-crm ai-agent-frontend-aaa 2>/dev/null || \
sudo docker rm -f ai-agent-frontend-dashboard ai-agent-frontend-crm ai-agent-frontend-aaa 2>/dev/null || true

# Kill all processes on ports
echo "🔌 Killing processes on ports 3000, 3001, 3002..."
for port in 3000 3001 3002; do
    echo "   Port $port:"
    # Method 1: fuser
    if command -v fuser >/dev/null 2>&1; then
        fuser -k ${port}/tcp 2>/dev/null && echo "      ✅ Freed with fuser" || \
        sudo fuser -k ${port}/tcp 2>/dev/null && echo "      ✅ Freed with sudo fuser" || true
    fi
    # Method 2: lsof
    PIDS=$(lsof -ti:${port} 2>/dev/null)
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null && echo "      ✅ Freed with kill" || \
        sudo kill -9 $PIDS 2>/dev/null && echo "      ✅ Freed with sudo kill" || true
    fi
done

# Kill Next.js processes (more aggressive - multiple attempts)
echo "🔌 Killing Next.js processes..."
# Multiple attempts to kill all Next.js processes
for attempt in {1..3}; do
    # Kill by process name
    pkill -9 -f "next-server" 2>/dev/null || true
    pkill -9 -f "next dev" 2>/dev/null || true
    pkill -9 -f "next" 2>/dev/null || true
    
    # Find and kill by PID
    for pid in $(pgrep -f "next-server" 2>/dev/null); do
        kill -9 $pid 2>/dev/null && echo "      ✅ Killed next-server PID: $pid (attempt $attempt)" || true
    done
    
    # Also kill by port
    for port in 3000 3001 3002; do
        PIDS=$(lsof -ti:${port} 2>/dev/null)
        if [ -n "$PIDS" ]; then
            echo "$PIDS" | xargs kill -9 2>/dev/null && echo "      ✅ Killed process on port $port (attempt $attempt)" || true
        fi
    done
    
    sleep 1
done

sleep 3

# Verify ports are free
echo ""
echo "📊 Port Status:"
for port in 3000 3001 3002; do
    if ss -tlnp | grep -q ":${port}"; then
        echo "   ⚠️  Port $port is still in use"
        ss -tlnp | grep ":${port}"
    else
        echo "   ✅ Port $port is free"
    fi
done

echo ""
echo "✅ Port cleanup complete!"

