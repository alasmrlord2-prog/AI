#!/bin/bash
# Restart All Services (Backend + Frontend)

set -e

cd "$(dirname "$0")"

echo "🔄 Restarting All Services..."

# Restart backend first
./backend-restart.sh

echo ""
echo "---"

# Then restart frontend
./frontend-restart.sh

echo ""
echo "✅ All services restarted!"

