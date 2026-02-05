#!/bin/bash
# Quick Fix - حل سريع للمشاكل الحالية

set +e

cd "$(dirname "$0")"

echo "🔧 Quick Fix - حل سريع"
echo ""

# 1. قتل process على port 3001
echo "1️⃣ Killing process on port 3001..."
PIDS=$(ss -tlnp 2>/dev/null | grep ":3001" | grep -oP 'pid=\K[0-9]+' | sort -u)
if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill -9 2>/dev/null && echo "✅ Killed PIDs: $PIDS" || true
fi
pkill -9 -f "next.*3001" 2>/dev/null || true
sleep 2

# 2. إعادة تشغيل CRM container
echo ""
echo "2️⃣ Restarting CRM container..."
docker compose stop frontend-crm 2>/dev/null || true
docker compose rm -f frontend-crm 2>/dev/null || true
sleep 1
docker compose up -d frontend-crm

echo "⏳ Waiting 10 seconds..."
sleep 10

# 3. فحص Backend CRM endpoint
echo ""
echo "3️⃣ Testing Backend CRM endpoint..."
RESPONSE=$(curl -s http://localhost:8000/api/crm/tenants 2>&1)
echo "Response: $RESPONSE"

if echo "$RESPONSE" | grep -q "tenants\|total"; then
    echo "✅ Backend CRM endpoint is working!"
elif echo "$RESPONSE" | grep -q "Not Found"; then
    echo "⚠️  Backend CRM endpoint returns 404"
    echo ""
    echo "   🔄 Restarting backend to reload routers..."
    docker compose restart backend
    sleep 5
    echo "   Testing again..."
    curl -s http://localhost:8000/api/crm/tenants
fi

# 4. Final status
echo ""
echo "4️⃣ Final Status:"
echo "   Backend (8000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null || echo '000')"
echo "   Dashboard (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo '000')"
echo "   CRM (3001): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 2>/dev/null || echo '000')"
echo "   AAA (3002): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002 2>/dev/null || echo '000')"

echo ""
echo "✅ Quick fix complete!"
echo ""
echo "📝 If CRM endpoint still returns 404, run:"
echo "   docker compose restart backend"
echo "   docker compose logs backend | grep -i crm"

