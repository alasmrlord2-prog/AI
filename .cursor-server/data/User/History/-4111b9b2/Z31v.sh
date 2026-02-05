#!/bin/bash
# Script to reload nginx with new backend port

echo "=== إعادة تحميل Nginx ==="
echo ""
echo "⚠️  يلزم صلاحيات root"
echo ""
echo "الرجاء تشغيل:"
echo "  sudo nginx -t"
echo "  sudo systemctl reload nginx"
echo ""
echo "أو:"
echo "  sudo systemctl restart nginx"
echo ""
echo "بعد إعادة التحميل، جرب:"
echo "  curl -X POST http://localhost/api/chat \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -H 'Host: ai-agent.bankid-sy.com' \\"
echo "    -d '{\"message\":\"test\"}'"
echo ""

