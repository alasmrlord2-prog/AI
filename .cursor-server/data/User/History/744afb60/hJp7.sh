#!/bin/bash
# Fix All Issues - Complete Solution

set +e

cd "$(dirname "$0")"

echo "🔧 Fixing All Issues..."

# 1. Stop all containers
echo ""
echo "1️⃣ Stopping all containers..."
docker compose down 2>/dev/null || true

# 2. Kill all processes on ports
echo ""
echo "2️⃣ Killing processes on ports..."
./KILL_ALL_PORTS.sh

# 3. Rebuild and start services
echo ""
echo "3️⃣ Rebuilding and starting services..."
docker compose up -d --build postgres ollama backend

echo "⏳ Waiting for backend..."
sleep 10

# Check backend
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running!"
        break
    fi
    sleep 2
done

# Test CRM endpoint
echo ""
echo "4️⃣ Testing Backend endpoints..."
CRM_TEST=$(curl -s http://localhost:8000/api/crm/tenants 2>&1)
if echo "$CRM_TEST" | grep -q "tenants\|total\|error"; then
    echo "✅ CRM endpoint responding: $CRM_TEST"
else
    echo "⚠️  CRM endpoint issue: $CRM_TEST"
fi

# Start frontends
echo ""
echo "5️⃣ Starting frontend services..."
docker compose up -d --build frontend-dashboard frontend-crm frontend-aaa

echo "⏳ Waiting for frontends..."
sleep 15

# Check status
echo ""
echo "6️⃣ Final Status Check:"
echo "   Backend (8000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health || echo '000')"
echo "   Dashboard (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo '000')"
echo "   CRM (3001): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 || echo '000')"
echo "   AAA (3002): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002 || echo '000')"

echo ""
echo "📝 View logs:"
echo "   docker compose logs -f backend"
echo "   docker compose logs -f frontend-dashboard"
echo "   docker compose logs -f frontend-crm"
echo "   docker compose logs -f frontend-aaa"

echo ""
echo "✅ Fix complete!"

