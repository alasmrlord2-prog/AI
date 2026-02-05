#!/bin/bash

echo "🔧 إصلاح الخدمات..."
echo "========================================"
echo ""

# 1. إعادة تشغيل Backend
echo "🔄 إعادة تشغيل Backend..."
cd /home/ai/ai-agent
./restart_backend.sh

sleep 5

# 2. إعادة تشغيل Frontend
echo ""
echo "🔄 إعادة تشغيل Frontend..."
./restart_frontend.sh

sleep 5

# 3. التحقق من المنافذ
echo ""
echo "🔍 التحقق من المنافذ..."
echo ""
echo "المنفذ 8000 (Backend):"
ss -tlnp | grep ':8000' || echo "  ⚠️  غير متاح"
echo ""
echo "المنفذ 3000 (Frontend):"
ss -tlnp | grep ':3000' || echo "  ⚠️  غير متاح"
echo ""

# 4. اختبار الاتصال
echo "🧪 اختبار الاتصال..."
echo ""
echo "Backend Health:"
curl -s -o /dev/null -w "  HTTP Status: %{http_code}\n" http://localhost:8000/health || echo "  ❌ فشل الاتصال"
echo ""
echo "Frontend:"
curl -s -o /dev/null -w "  HTTP Status: %{http_code}\n" http://localhost:3000 || echo "  ❌ فشل الاتصال"
echo ""

# 5. اختبار nginx
echo "🧪 اختبار nginx..."
echo ""
echo "Nginx Health:"
curl -s -o /dev/null -w "  HTTP Status: %{http_code}\n" http://localhost/health || echo "  ❌ فشل الاتصال"
echo ""
echo "Nginx API:"
curl -s -o /dev/null -w "  HTTP Status: %{http_code}\n" http://localhost/api/health || echo "  ❌ فشل الاتصال"
echo ""

echo "✅ تم!"
echo ""
echo "💡 إذا كانت الخدمات لا تعمل، تحقق من:"
echo "   docker logs ai-agent-backend-prod"
echo "   docker logs ai-agent-frontend-prod"
echo "   sudo tail -20 /var/log/nginx/error.log"

