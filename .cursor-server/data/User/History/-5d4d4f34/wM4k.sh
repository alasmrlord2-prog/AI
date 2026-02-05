#!/bin/bash
# Fix Database Connection Issue

set -e

cd "$(dirname "$0")"

echo "🔧 Fixing Database Connection..."
echo ""

# Check if postgres is running
echo "1️⃣ Checking PostgreSQL status..."
if docker compose ps postgres | grep -q "Up"; then
    echo "   ✅ PostgreSQL is running"
else
    echo "   ❌ PostgreSQL is not running, starting it..."
    docker compose up -d postgres
    sleep 5
fi

# Restart postgres to reset connection
echo ""
echo "2️⃣ Restarting PostgreSQL to reset connections..."
docker compose restart postgres
sleep 5

# Wait for postgres to be ready
echo ""
echo "3️⃣ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U aiagent > /dev/null 2>&1; then
        echo "   ✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  PostgreSQL not ready after 30 attempts"
    else
        sleep 1
    fi
done

# Restart backend to reconnect
echo ""
echo "4️⃣ Restarting Backend to reconnect to database..."
docker compose restart backend
sleep 5

# Wait for backend to be ready
echo ""
echo "5️⃣ Waiting for Backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  Backend not ready after 30 attempts"
    else
        sleep 1
    fi
done

# Test CRM endpoint
echo ""
echo "6️⃣ Testing CRM endpoint..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/crm/tenants 2>/dev/null || echo "000")
RESPONSE=$(curl -s http://localhost:8000/api/crm/tenants 2>&1 | head -c 200)

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ CRM endpoint is working! (HTTP 200)"
    echo "   Response: $(echo "$RESPONSE" | head -c 100)..."
    echo ""
    echo "✅ Database connection fixed!"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "   ⚠️  Got HTTP 500 - Database connection issue persists"
    echo "   Response: $(echo "$RESPONSE" | head -c 150)..."
    echo ""
    echo "📝 Check database credentials in docker-compose.yml"
    echo "📝 Or try recreating database:"
    echo "   docker compose down postgres"
    echo "   docker volume rm ai-agent_postgres_data"
    echo "   docker compose up -d postgres"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "   ❌ Got HTTP 404 - CRM router not registered"
    echo "   Run: ./rebuild-backend.sh"
else
    echo "   ⚠️  Got HTTP $HTTP_CODE"
    echo "   Response: $(echo "$RESPONSE" | head -c 150)..."
fi

