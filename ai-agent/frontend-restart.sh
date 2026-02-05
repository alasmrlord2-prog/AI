#!/bin/bash
# Restart Frontend Services

set -e

cd "$(dirname "$0")"

echo "🔄 Restarting Frontend Services..."

# Stop first
./frontend-stop.sh

# Wait a bit
sleep 3

# Start again
./frontend-start.sh

echo "✅ Frontend services restarted"
