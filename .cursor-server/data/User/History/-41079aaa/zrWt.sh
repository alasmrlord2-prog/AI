#!/bin/bash

echo "🔧 إصلاح مشكلة المنفذ 80..."
echo "========================================"
echo ""

# 1. إيقاف nginx container من Docker
echo "⏹️  إيقاف nginx container..."
docker stop ai-agent-nginx 2>/dev/null
docker ps -a | grep nginx | awk '{print $1}' | xargs -r docker stop 2>/dev/null

# 2. حذف nginx container
echo "🗑️  حذف nginx container..."
docker rm ai-agent-nginx 2>/dev/null
docker ps -a | grep nginx | awk '{print $1}' | xargs -r docker rm 2>/dev/null

# 3. التحقق من المنفذ 80
echo ""
echo "🔍 التحقق من المنفذ 80..."
if ss -tlnp | grep -q ':80'; then
    echo "⚠️  المنفذ 80 ما زال مستخدم:"
    ss -tlnp | grep ':80'
    echo ""
    echo "💡 قد تحتاج لإيقاف العملية يدوياً:"
    echo "   sudo kill -9 \$(sudo lsof -t -i:80)"
else
    echo "✅ المنفذ 80 متاح الآن"
fi

# 4. تشغيل nginx على السيرفر
echo ""
echo "🚀 تشغيل nginx على السيرفر..."
sudo systemctl start nginx

# 5. التحقق من الحالة
echo ""
echo "📊 حالة nginx:"
sudo systemctl status nginx --no-pager | head -10

echo ""
echo "✅ تم!"
echo ""
echo "💡 إذا كان nginx لا يعمل، تحقق من السجلات:"
echo "   sudo tail -20 /var/log/nginx/error.log"

