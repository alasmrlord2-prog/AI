#!/bin/bash

# Script to rebuild and restart all services with fixes

echo "🔄 إعادة بناء وإعادة تشغيل جميع الخدمات..."

cd /home/ai/ai-agent

echo "📦 إعادة بناء frontend containers..."
docker-compose build frontend-dashboard frontend-crm frontend-aaa

echo "🛑 إيقاف جميع الخدمات..."
docker-compose down

echo "🚀 بدء تشغيل جميع الخدمات..."
docker-compose up -d

echo "⏳ انتظار 10 ثوانٍ للخدمات للبدء..."
sleep 10

echo "📊 حالة الخدمات:"
docker-compose ps

echo ""
echo "✅ تم إعادة تشغيل جميع الخدمات!"
echo ""
echo "📝 لمراقبة الـ logs:"
echo "   docker-compose logs -f frontend-dashboard"
echo "   docker-compose logs -f backend"
echo ""
echo "🌐 الروابط:"
echo "   Dashboard: http://localhost:3000"
echo "   CRM: http://localhost:3001"
echo "   AAA: http://localhost:3002"
echo "   Backend API: http://localhost:8000"

