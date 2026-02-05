#!/bin/bash

echo "🔧 إصلاح شامل لجميع المشاكل..."

cd /home/ai/ai-agent

echo "1️⃣ إيقاف جميع العمليات على ports 3000-3002..."
pkill -9 -f "next dev" 2>/dev/null
pkill -9 -f "npm run dev" 2>/dev/null
sleep 2

# Kill any remaining processes
for port in 3000 3001 3002; do
    lsof -ti:$port | xargs kill -9 2>/dev/null
    fuser -k $port/tcp 2>/dev/null
done

sleep 2

echo "2️⃣ التحقق من أن جميع ports متاحة..."
for port in 3000 3001 3002; do
    if ss -tlnp | grep -q ":$port"; then
        echo "⚠️  Port $port لا يزال مستخدم"
    else
        echo "✅ Port $port متاح"
    fi
done

echo "3️⃣ إيقاف جميع Docker containers..."
docker-compose down 2>/dev/null || true

echo "4️⃣ إعادة بناء frontend containers..."
docker-compose build frontend-dashboard frontend-crm frontend-aaa

echo "5️⃣ بدء تشغيل جميع الخدمات..."
docker-compose up -d

echo "6️⃣ انتظار الخدمات للبدء..."
sleep 15

echo "7️⃣ حالة الخدمات:"
docker-compose ps

echo ""
echo "✅ تم إكمال الإصلاح!"
echo ""
echo "🌐 الروابط:"
echo "   Dashboard: http://localhost:3000"
echo "   CRM: http://localhost:3001"
echo "   AAA: http://localhost:3002"
echo "   Backend API: http://localhost:8000"
echo ""
echo "📝 لمراقبة الـ logs:"
echo "   docker-compose logs -f frontend-dashboard"
echo "   docker-compose logs -f backend"

