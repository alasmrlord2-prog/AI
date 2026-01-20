#!/bin/bash
# Stop All Services (Backend + Frontend)

set -e

cd "$(dirname "$0")"

echo "🛑 إيقاف جميع الخدمات (Backend + Frontend)..."

# Stop frontend first
echo "🛑 إيقاف Frontend..."
./frontend-stop.sh

# Stop backend
echo "🛑 إيقاف Backend..."
./backend-stop.sh

# Stop monitoring services
echo "🛑 إيقاف خدمات المراقبة..."
docker compose stop prometheus grafana loki promtail 2>/dev/null || true

echo ""
echo "✅ تم إيقاف جميع الخدمات!"

