#!/bin/bash
# Restart Backend Services

set -e

cd "$(dirname "$0")"

echo "🔄 Restarting Backend Services..."

# Stop first
./backend-stop.sh

# Wait a bit
sleep 2

# Start again
./backend-start.sh

echo "✅ Backend services restarted"
