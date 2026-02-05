#!/bin/bash
# Stop Frontend Services

set -e

cd "$(dirname "$0")"

echo "🛑 Stopping Frontend Services..."

# Stop containers
docker compose stop frontend-dashboard frontend-crm frontend-aaa 2>/dev/null || true

# Remove containers
docker compose rm -f frontend-dashboard frontend-crm frontend-aaa 2>/dev/null || true

# Kill Next.js processes
pkill -9 -f "next-server" 2>/dev/null || true
pkill -9 -f "next dev" 2>/dev/null || true

# Kill processes on ports
for port in 3000 3001 3002; do
    PIDS=$(lsof -ti:${port} 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null || true
    fi
done

echo "✅ Frontend services stopped"
