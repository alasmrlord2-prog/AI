#!/bin/bash
# Restart All Services (Backend + Frontend)

set -e

cd "$(dirname "$0")"

echo "🔄 إعادة تشغيل جميع الخدمات (Backend + Frontend)..."

# Stop all services
echo "🛑 إيقاف جميع الخدمات..."
./backend-stop.sh
./frontend-stop.sh

# Wait a bit
sleep 3

# Start backend first
echo "🚀 بدء تشغيل Backend..."
./backend-start.sh

# Wait for backend to be ready
sleep 5

# Start frontend
echo "🚀 بدء تشغيل Frontend..."
./frontend-start.sh

echo ""
echo "📊 حالة جميع الخدمات:"
docker compose ps

echo ""
echo "✅ تم إعادة تشغيل جميع الخدمات!"
echo ""
echo "🌐 الروابط:"
echo "   Dashboard: http://localhost:3000"
echo "   CRM: http://localhost:3001"
echo "   AAA: http://localhost:3002"
echo "   Backend API: http://localhost:8000"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3003"
echo ""
echo "📝 لمراقبة الـ logs:"
echo "   Backend: docker compose logs -f backend"
echo "   Frontend: docker compose logs -f frontend-dashboard"

