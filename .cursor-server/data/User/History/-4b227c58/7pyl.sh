#!/bin/bash
# Fix Backend Issues - Rebuild and Restart

set -e

cd "$(dirname "$0")"

echo "🔧 Fixing Backend Issues..."
echo ""

# 1. Rebuild backend to install pydantic[email]
echo "1️⃣ Rebuilding Backend container (installing pydantic[email])..."
docker compose build backend

# 2. Restart backend
echo ""
echo "2️⃣ Restarting Backend..."
docker compose restart backend

# 3. Wait for backend to be ready
echo ""
echo "3️⃣ Waiting for Backend to be ready..."
sleep 10

# 4. Check if routers are loaded
echo ""
echo "4️⃣ Checking if routers are loaded..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        # Check if CRM endpoint exists
        CRM_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/crm/tenants 2>/dev/null || echo "000")
        if [ "$CRM_CODE" != "000" ] && [ "$CRM_CODE" != "404" ]; then
            echo "   ✅ CRM router loaded (HTTP $CRM_CODE)"
            break
        fi
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  Backend started but routers may not be loaded yet"
        echo "   Check logs: docker compose logs backend | grep -i 'error\|crm\|identity'"
    else
        sleep 2
    fi
done

echo ""
echo "✅ Backend fix complete!"
echo ""
echo "📝 Check endpoints: ./check-endpoints.sh"

