#!/bin/bash
# Check all endpoints

echo "🔍 Checking Backend Endpoints..."
echo ""

# Backend health
echo "1. Backend Health:"
curl -s http://localhost:8000/health | jq . || echo "   ❌ Backend not responding"
echo ""

# CRM endpoints
echo "2. CRM Endpoints:"
echo "   /api/crm/tenants:"
curl -s http://localhost:8000/api/crm/tenants | jq . || echo "   ❌ Not found"
echo ""

# Identity endpoints
echo "3. Identity Endpoints:"
echo "   /api/identity/users:"
curl -s http://localhost:8000/api/identity/users | jq . || echo "   ❌ Not found"
echo ""

# Access endpoints
echo "4. Access Endpoints:"
echo "   /api/access/roles:"
curl -s http://localhost:8000/api/access/roles | jq . || echo "   ❌ Not found"
echo ""

# Frontend endpoints
echo "5. Frontend Endpoints:"
echo "   Dashboard (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000)"
echo "   CRM (3001): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001)"
echo "   AAA (3002): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002)"
echo ""

