#!/bin/bash
# Cleanup script - يحذف الملفات الزائدة ويبقي على الأساسيات فقط

echo "🧹 Cleaning up project files..."

# حذف ملفات .md الزائدة (نحتفظ بـ PROJECT_COMPLETE.md و README.md)
echo "📝 Removing extra .md files..."
find . -maxdepth 1 -type f -name "*.md" ! -name "PROJECT_COMPLETE.md" ! -name "README.md" -delete

# حذف ملفات nginx الزائدة (نحتفظ بـ nginx-crm-site.conf فقط)
echo "🌐 Removing extra nginx config files..."
rm -f nginx-crm.conf nginx-crm-cloudflare.conf setup-nginx-crm.sh

# حذف ملفات cleanup.sh نفسه بعد التنفيذ
echo "✅ Cleanup complete!"
echo ""
echo "📦 Remaining files:"
echo "   - PROJECT_COMPLETE.md (كل التفاصيل)"
echo "   - README.md"
echo "   - nginx-crm-site.conf (NGINX config للـ CRM)"
echo "   - docker-compose.yml"
echo "   - 6 scripts (backend/*.sh + frontend/*.sh)"

