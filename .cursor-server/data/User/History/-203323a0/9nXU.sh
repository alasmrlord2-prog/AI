#!/bin/bash
# Force reload backend by touching files and checking

set -e

cd "$(dirname "$0")"

echo "🔄 Forcing Backend Reload..."
echo ""

# Touch main files to trigger reload
echo "1️⃣ Touching files to trigger reload..."
touch backend/app/main.py
touch backend/app/api/crm_api.py
touch backend/app/crm/service.py

echo "   ✅ Files touched"
echo ""

# Wait for reload
echo "2️⃣ Waiting for uvicorn to reload (5 seconds)..."
sleep 5

# Check endpoint
echo ""
echo "3️⃣ Checking CRM endpoint..."
for i in {1..10}; do
    RESPONSE=$(curl -s http://localhost:8000/api/crm/tenants 2>&1)
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/crm/tenants 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo "   ✅ CRM endpoint is working! (HTTP $HTTP_CODE)"
        echo "   Response: $(echo "$RESPONSE" | head -c 100)..."
        exit 0
    elif [ "$HTTP_CODE" != "404" ]; then
        echo "   ⚠️  Got HTTP $HTTP_CODE (not 404, progress!)"
        echo "   Response: $(echo "$RESPONSE" | head -c 100)..."
    fi
    
    if [ $i -lt 10 ]; then
        sleep 2
    fi
done

echo ""
echo "   ❌ CRM endpoint still returning 404"
echo ""
echo "📝 Next steps:"
echo "   1. Check if backend is running: curl http://localhost:8000/health"
echo "   2. Check backend logs for errors"
echo "   3. Try rebuilding: docker compose build backend && docker compose up -d backend"

