#!/bin/bash
# Stop All Services (Backend + Frontend)

set -e

cd "$(dirname "$0")"

echo "🛑 Stopping All Services..."

# Stop frontend first
./frontend-stop.sh

echo ""
echo "---"

# Then stop backend
./backend-stop.sh

echo ""
echo "✅ All services stopped!"

