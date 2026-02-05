#!/bin/bash
# Restart Frontend Script - Fixed version
set -e

cd "$(dirname "$0")"

PORT=${1:-3000}

echo "🔄 Restarting Frontend..."

# First stop everything
./stop-fixed.sh $PORT

# Wait a bit
sleep 2

# Then start
./start-fixed.sh $PORT

echo "✅ Frontend restarted!"

