#!/bin/bash

echo "🔧 إصلاح المنافذ..."
echo "========================================"
echo ""

cd /home/ai/ai-agent

# 1. إيقاف وإزالة الحاويات
echo "⏹️  إيقاف وإزالة الحاويات..."
docker stop ai-agent-backend-prod ai-agent-frontend-prod 2>/dev/null
docker rm ai-agent-backend-prod ai-agent-frontend-prod 2>/dev/null

# 2. إعادة إنشاء الحاويات مع المنافذ
echo ""
echo "🔄 إعادة إنشاء الحاويات مع المنافذ..."
docker-compose -f docker-compose.prod.yml up -d backend frontend

# 3. انتظار قليل
echo ""
echo "⏳ انتظار 10 ثواني..."
sleep 10

# 4. التحقق من المنافذ
echo ""
echo "🔍 التحقق من المنافذ..."
echo ""
echo "المنفذ 8000 (Backend):"
if ss -tlnp | grep -q ':8000'; then
    ss -tlnp | grep ':8000'
    echo "  ✅ متاح"
else
    echo "  ⚠️  غير متاح"
fi

echo ""
echo "المنفذ 3000 (Frontend):"
if ss -tlnp | grep -q ':3000'; then
    ss -tlnp | grep ':3000'
    echo "  ✅ متاح"
else
    echo "  ⚠️  غير متاح"
fi

# 5. اختبار الاتصال
echo ""
echo "🧪 اختبار الاتصال..."
echo ""
echo "Backend Health:"
if curl -s -o /dev/null -w "  HTTP Status: %{http_code}\n" http://localhost:8000/health; then
    echo "  ✅ يعمل"
else
    echo "  ❌ فشل"
fi

echo ""
echo "Frontend:"
if curl -s -o /dev/null -w "  HTTP Status: %{http_code}\n" http://localhost:3000; then
    echo "  ✅ يعمل"
else
    echo "  ❌ فشل"
fi

# 6. اختبار nginx
echo ""
echo "🧪 اختبار nginx..."
echo ""
echo "Nginx API:"
if curl -s -o /dev/null -w "  HTTP Status: %{http_code}\n" http://localhost/api/health; then
    echo "  ✅ يعمل"
else
    echo "  ❌ فشل"
fi

echo ""
echo "✅ تم!"
echo ""
echo "💡 إذا كانت المنافذ ما زالت غير متاحة، تحقق من:"
echo "   docker ps | grep -E 'backend|frontend'"
echo "   docker logs ai-agent-backend-prod"
echo "   docker logs ai-agent-frontend-prod"

