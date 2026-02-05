#!/bin/bash
# Restart Backend to Fix CRM Router Issue

set -e

cd "$(dirname "$0")"

echo "🔧 Restarting Backend to Fix CRM Router..."
echo ""

# Restart backend container
echo "1️⃣ Restarting Backend container..."
docker compose restart backend

# Wait for backend to be ready
echo ""
echo "2️⃣ Waiting for Backend to be ready..."
sleep 10

# Check if CRM endpoint is now available
echo ""
echo "3️⃣ Checking CRM endpoint..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        CRM_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/crm/tenants 2>/dev/null || echo "000")
        if [ "$CRM_CODE" = "200" ] || [ "$CRM_CODE" = "401" ] || [ "$CRM_CODE" = "403" ]; then
            echo "   ✅ CRM router is now working! (HTTP $CRM_CODE)"
            break
        elif [ "$CRM_CODE" != "404" ]; then
            echo "   ⚠️  CRM endpoint returned HTTP $CRM_CODE"
            break
        fi
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ CRM router still not available after 30 attempts"
        echo "   Check logs: docker compose logs backend | grep -i 'crm\|error'"
    else
        sleep 2
    fi
done

echo ""
echo "✅ Backend restart complete!"
echo ""
echo "📝 Check endpoints: ./check-endpoints.sh"

