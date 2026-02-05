#!/bin/bash
# Restart Backend Script - Fixed version
set -e

cd "$(dirname "$0")"

echo "🔄 Restarting Backend..."

# First stop everything
./stop-fixed.sh

# Wait a bit
sleep 2

# Then start
./start-fixed.sh

echo "✅ Backend restarted!"

