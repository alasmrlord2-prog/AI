#!/bin/bash

set -e

echo "🔧 إصلاح شامل - Dashboard والـ Agent..."

cd /home/ai/ai-agent

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  الخطوة 1: إيقاف جميع العمليات على ports 3000-3002"
echo "═══════════════════════════════════════════════════════════"

# Kill all node/next processes
pkill -9 -f "next dev" 2>/dev/null || true
pkill -9 -f "npm run dev" 2>/dev/null || true
pkill -9 -f "node.*3001" 2>/dev/null || true

# Kill processes on specific ports
for port in 3000 3001 3002; do
    echo "  🔍 التحقق من port $port..."
    PID=$(lsof -ti:$port 2>/dev/null || echo "")
    if [ ! -z "$PID" ]; then
        echo "  ⚠️  إيقاف العملية $PID على port $port..."
        kill -9 $PID 2>/dev/null || true
        sleep 1
    fi
    fuser -k $port/tcp 2>/dev/null || true
done

sleep 3

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  الخطوة 2: التحقق من أن جميع ports متاحة"
echo "═══════════════════════════════════════════════════════════"

for port in 3000 3001 3002; do
    if ss -tlnp 2>/dev/null | grep -q ":$port "; then
        echo "  ❌ Port $port لا يزال مستخدم"
        # Try one more time
        lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        echo "  ✅ Port $port متاح"
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  الخطوة 3: إيقاف جميع Docker containers"
echo "═══════════════════════════════════════════════════════════"

docker-compose down 2>/dev/null || true
sleep 2

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  الخطوة 4: إعادة بناء frontend containers"
echo "═══════════════════════════════════════════════════════════"

docker-compose build --no-cache frontend-dashboard frontend-crm frontend-aaa 2>&1 | tail -5

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  الخطوة 5: بدء تشغيل جميع الخدمات"
echo "═══════════════════════════════════════════════════════════"

docker-compose up -d

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  الخطوة 6: انتظار الخدمات للبدء (30 ثانية)..."
echo "═══════════════════════════════════════════════════════════"

sleep 30

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  الخطوة 7: حالة الخدمات"
echo "═══════════════════════════════════════════════════════════"

docker-compose ps

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  الخطوة 8: اختبار الاتصال"
echo "═══════════════════════════════════════════════════════════"

echo "  🔍 اختبار Backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ Backend يعمل على port 8000"
else
    echo "  ❌ Backend لا يستجيب"
fi

echo "  🔍 اختبار Dashboard..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✅ Dashboard يعمل على port 3000"
else
    echo "  ⚠️  Dashboard لا يزال يبدأ..."
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ تم إكمال الإصلاح!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🌐 الروابط:"
echo "   📊 Dashboard: http://localhost:3000"
echo "   💼 CRM: http://localhost:3001"
echo "   🔐 AAA: http://localhost:3002"
echo "   🔌 Backend API: http://localhost:8000"
echo ""
echo "📝 لمراقبة الـ logs:"
echo "   docker-compose logs -f frontend-dashboard"
echo "   docker-compose logs -f backend"
echo ""
echo "🔍 للتحقق من الأخطاء:"
echo "   docker-compose logs frontend-dashboard | tail -50"
echo "   docker-compose logs backend | tail -50"

