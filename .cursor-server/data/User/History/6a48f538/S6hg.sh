#!/bin/bash
# Final Fix - Complete Solution

set +e

cd "$(dirname "$0")"

echo "🔧 Final Fix - Complete Solution"
echo ""

# 1. Kill process on port 3001
echo "1️⃣ Killing process on port 3001..."
PIDS=$(ss -tlnp | grep ":3001" | grep -oP 'pid=\K[0-9]+' | sort -u)
if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill -9 2>/dev/null && echo "✅ Killed PIDs: $PIDS" || true
fi
pkill -9 -f "next.*3001" 2>/dev/null || true
sleep 2

# 2. Restart CRM container
echo ""
echo "2️⃣ Restarting CRM container..."
docker compose stop frontend-crm 2>/dev/null || true
docker compose rm -f frontend-crm 2>/dev/null || true
docker compose up -d frontend-crm

echo "⏳ Waiting for CRM to start..."
sleep 10

# 3. Check Backend CRM endpoint
echo ""
echo "3️⃣ Checking Backend CRM endpoint..."
BACKEND_RESPONSE=$(curl -s http://localhost:8000/api/crm/tenants 2>&1)
if echo "$BACKEND_RESPONSE" | grep -q "tenants\|total"; then
    echo "✅ Backend CRM endpoint working!"
elif echo "$BACKEND_RESPONSE" | grep -q "Not Found"; then
    echo "⚠️  Backend CRM endpoint returns 404"
    echo "   Response: $BACKEND_RESPONSE"
    echo ""
    echo "   🔍 Checking if CRM router is registered..."
    docker exec ai-backend python3 -c "
import sys
sys.path.insert(0, '/app')
from app.main import app
routes = [r.path for r in app.routes if hasattr(r, 'path') and '/crm' in r.path]
print('CRM routes found:', len(routes))
if routes:
    for r in routes[:5]:
        print('  -', r)
else:
    print('  ❌ No CRM routes found!')
    print('  Checking if router is imported...')
    try:
        from app.api.crm_api import router
        print('  ✅ CRM router can be imported')
        print('  Prefix:', router.prefix)
    except Exception as e:
        print('  ❌ Error importing CRM router:', e)
" 2>&1
fi

# 4. Final status
echo ""
echo "4️⃣ Final Status:"
echo "   Backend (8000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health || echo '000')"
echo "   Dashboard (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo '000')"
echo "   CRM (3001): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 || echo '000')"
echo "   AAA (3002): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002 || echo '000')"

echo ""
echo "📝 Containers status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "⚠️  Cannot check containers (permission issue)"

echo ""
echo "✅ Final fix complete!"

