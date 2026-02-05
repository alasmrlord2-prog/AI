#!/bin/bash
# Stop Backend Services

set -e

cd "$(dirname "$0")"

echo "🛑 Stopping Backend Services..."

# Stop containers
docker compose stop backend postgres redis ollama 2>/dev/null || true

# Remove containers
docker compose rm -f backend postgres redis ollama 2>/dev/null || true

# Kill processes on ports
for port in 8000 5432 6379 11434; do
    PIDS=$(lsof -ti:${port} 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null || true
    fi
done

echo "✅ Backend services stopped"
