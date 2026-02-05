#!/bin/bash
# Rebuild Backend to ensure CRM router is included

set -e

cd "$(dirname "$0")"

echo "🔨 Rebuilding Backend Container..."
echo ""

# Stop backend
echo "1️⃣ Stopping Backend..."
docker compose stop backend 2>/dev/null || true
sleep 2

# Rebuild backend
echo ""
echo "2️⃣ Rebuilding Backend (this may take a few minutes)..."
docker compose build backend

# Start backend
echo ""
echo "3️⃣ Starting Backend..."
docker compose up -d backend

# Wait for backend to be ready
echo ""
echo "4️⃣ Waiting for Backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Backend is responding"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  Backend not responding after 30 attempts"
    else
        sleep 2
    fi
done

# Check CRM endpoint
echo ""
echo "5️⃣ Checking CRM endpoint..."
sleep 5
for i in {1..10}; do
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/crm/tenants 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo "   ✅ CRM endpoint is working! (HTTP $HTTP_CODE)"
        echo ""
        echo "✅ Backend rebuild complete and CRM router is working!"
        exit 0
    elif [ "$HTTP_CODE" != "404" ]; then
        echo "   ⚠️  Got HTTP $HTTP_CODE (not 404, progress!)"
    fi
    
    if [ $i -lt 10 ]; then
        sleep 2
    fi
done

echo ""
echo "   ❌ CRM endpoint still returning 404"
echo ""
echo "📝 Check logs:"
echo "   docker compose logs backend | grep -i 'crm\|error\|main' | tail -50"
echo ""
echo "📝 Or check if routes are registered:"
echo "   curl http://localhost:8000/openapi.json | python3 -m json.tool | grep -i crm"

