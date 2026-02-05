#!/bin/bash

echo "🔧 إصلاح Firewall..."
echo "========================================"
echo ""

# 1. فتح المنفذ 80
echo "🔓 فتح المنفذ 80..."
sudo ufw allow 80/tcp
sudo ufw allow 'Nginx HTTP' 2>/dev/null || echo "  (Nginx HTTP rule not found, using 80/tcp)"

# 2. إعادة تحميل Firewall
echo ""
echo "🔄 إعادة تحميل Firewall..."
sudo ufw reload

# 3. التحقق من الحالة
echo ""
echo "📊 حالة Firewall:"
sudo ufw status | head -15

# 4. التحقق من المنافذ
echo ""
echo "🔍 المنافذ المفتوحة:"
ss -tlnp | grep ':80' | head -3

# 5. اختبار محلي
echo ""
echo "🧪 اختبار محلي..."
if curl -s -o /dev/null -w "  HTTP Status: %{http_code}\n" --max-time 5 http://localhost/health; then
    echo "  ✅ nginx يعمل محلياً"
else
    echo "  ❌ nginx لا يعمل محلياً"
fi

echo ""
echo "✅ تم!"
echo ""
echo "💡 ملاحظات مهمة:"
echo "   1. تأكد من أن AWS Security Group يسمح بالمنفذ 80"
echo "   2. إذا كان Cloudflare Proxy مفعّل، أزله (DNS Only)"
echo "   3. انتظر 5-10 دقائق بعد إزالة Cloudflare Proxy"
echo ""
echo "🔗 AWS Security Group:"
echo "   EC2 → Security Groups → Inbound Rules"
echo "   يجب أن يكون هناك:"
echo "   - Type: HTTP"
echo "   - Port: 80"
echo "   - Source: 0.0.0.0/0"

