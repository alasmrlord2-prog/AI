#!/bin/bash
# Check all endpoints

echo "🔍 Checking Backend Endpoints..."
echo ""

# Backend health
echo "1. Backend Health:"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>&1)
if [ $? -eq 0 ] && [ -n "$HEALTH_RESPONSE" ]; then
    echo "   ✅ $HEALTH_RESPONSE"
else
    echo "   ❌ Backend not responding"
fi
echo ""

# CRM endpoints
echo "2. CRM Endpoints:"
echo "   /api/crm/tenants:"
CRM_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/crm/tenants 2>&1)
HTTP_CODE=$(echo "$CRM_RESPONSE" | tail -1)
BODY=$(echo "$CRM_RESPONSE" | sed '$d')
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "   ✅ Endpoint exists (HTTP $HTTP_CODE)"
    if [ -n "$BODY" ] && [ "$BODY" != "null" ]; then
        echo "   Response: $(echo "$BODY" | head -c 100)..."
    fi
else
    echo "   ❌ Not found (HTTP $HTTP_CODE)"
fi
echo ""

# Identity endpoints
echo "3. Identity Endpoints:"
echo "   /api/identity/users:"
IDENTITY_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/identity/users 2>&1)
HTTP_CODE=$(echo "$IDENTITY_RESPONSE" | tail -1)
BODY=$(echo "$IDENTITY_RESPONSE" | sed '$d')
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "   ✅ Endpoint exists (HTTP $HTTP_CODE)"
    if [ -n "$BODY" ] && [ "$BODY" != "null" ]; then
        echo "   Response: $(echo "$BODY" | head -c 100)..."
    fi
else
    echo "   ❌ Not found (HTTP $HTTP_CODE)"
fi
echo ""

# Access endpoints
echo "4. Access Endpoints:"
echo "   /api/access/roles:"
ACCESS_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/access/roles 2>&1)
HTTP_CODE=$(echo "$ACCESS_RESPONSE" | tail -1)
BODY=$(echo "$ACCESS_RESPONSE" | sed '$d')
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "   ✅ Endpoint exists (HTTP $HTTP_CODE)"
    if [ -n "$BODY" ] && [ "$BODY" != "null" ]; then
        echo "   Response: $(echo "$BODY" | head -c 100)..."
    fi
else
    echo "   ❌ Not found (HTTP $HTTP_CODE)"
fi
echo ""

# Frontend endpoints
echo "5. Frontend Endpoints:"
DASHBOARD_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo "000")
CRM_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 2>/dev/null || echo "000")
AAA_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002 2>/dev/null || echo "000")

echo "   Dashboard (3000): $DASHBOARD_CODE $([ "$DASHBOARD_CODE" = "200" ] && echo "✅" || echo "❌")"
echo "   CRM (3001): $CRM_CODE $([ "$CRM_CODE" = "200" ] && echo "✅" || echo "❌")"
echo "   AAA (3002): $AAA_CODE $([ "$AAA_CODE" = "200" ] && echo "✅" || echo "❌")"
echo ""

# Summary
echo "📊 Summary:"
BACKEND_OK=$(curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "yes" || echo "no")
if [ "$BACKEND_OK" = "yes" ]; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is not running"
fi

if [ "$DASHBOARD_CODE" = "200" ] && [ "$CRM_CODE" = "200" ] && [ "$AAA_CODE" = "200" ]; then
    echo "   ✅ All Frontends are running"
else
    echo "   ⚠️  Some Frontends may not be running"
fi
