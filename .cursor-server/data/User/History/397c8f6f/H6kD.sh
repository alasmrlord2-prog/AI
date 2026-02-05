#!/bin/bash
# Kill ALL processes on ports 3000, 3001, 3002 - Ultimate cleanup

echo "🔧 Ultimate Port Cleanup..."

# Stop all Docker containers
docker compose down 2>/dev/null || true
sudo docker compose down 2>/dev/null || true

# Kill all Next.js processes (multiple methods)
echo "🔌 Killing all Next.js processes..."
pkill -9 -f "next-server" 2>/dev/null || true
pkill -9 -f "next dev" 2>/dev/null || true
pkill -9 -f "next" 2>/dev/null || true

# Kill by PID
for pid in $(pgrep -f "next-server" 2>/dev/null); do
    kill -9 $pid 2>/dev/null || sudo kill -9 $pid 2>/dev/null || true
done

# Kill processes on each port (multiple attempts)
for port in 3000 3001 3002; do
    echo "   Cleaning port $port..."
    for attempt in {1..5}; do
        # Method 1: fuser
        if command -v fuser >/dev/null 2>&1; then
            fuser -k ${port}/tcp 2>/dev/null || sudo fuser -k ${port}/tcp 2>/dev/null || true
        fi
        
        # Method 2: lsof
        PIDS=$(lsof -ti:${port} 2>/dev/null)
        if [ -n "$PIDS" ]; then
            echo "$PIDS" | xargs kill -9 2>/dev/null || echo "$PIDS" | xargs sudo kill -9 2>/dev/null || true
        fi
        
        # Method 3: ss + kill
        SS_PIDS=$(ss -tlnp | grep ":${port}" | grep -oP 'pid=\K[0-9]+' | sort -u)
        if [ -n "$SS_PIDS" ]; then
            echo "$SS_PIDS" | xargs kill -9 2>/dev/null || echo "$SS_PIDS" | xargs sudo kill -9 2>/dev/null || true
        fi
        
        sleep 0.5
    done
done

sleep 2

# Final verification
echo ""
echo "📊 Final Port Status:"
for port in 3000 3001 3002; do
    if ss -tlnp | grep -q ":${port}"; then
        echo "   ⚠️  Port $port is STILL in use:"
        ss -tlnp | grep ":${port}"
    else
        echo "   ✅ Port $port is FREE"
    fi
done

echo ""
echo "✅ Ultimate cleanup complete!"

