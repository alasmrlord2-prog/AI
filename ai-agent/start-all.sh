#!/bin/bash
# Start All Services (Backend + Frontend)

set -e

cd "$(dirname "$0")"

echo "🚀 تشغيل جميع الخدمات (Backend + Frontend)..."

# Start backend first
echo "📦 بدء تشغيل Backend..."
./backend-start.sh

# Wait for backend to be ready
sleep 5

# Start frontend
echo "📦 بدء تشغيل Frontend..."
./frontend-start.sh

echo ""
echo "📊 حالة جميع الخدمات:"
docker compose ps

echo ""
echo "✅ تم تشغيل جميع الخدمات!"
echo ""
echo "🌐 الروابط:"
echo "   Dashboard: http://localhost:3000"
echo "   CRM: http://localhost:3001"
echo "   AAA: http://localhost:3002"
echo "   Backend API: http://localhost:8000"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3003"

