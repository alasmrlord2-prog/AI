#!/bin/bash
# Recreate PostgreSQL Database to Fix Authentication

set -e

cd "$(dirname "$0")"

echo "🗑️  Recreating PostgreSQL Database..."
echo ""
echo "⚠️  WARNING: This will DELETE all database data!"
echo ""
read -p "Are you sure you want to continue? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "1️⃣ Stopping services..."
docker compose stop backend postgres 2>/dev/null || true
sleep 2

echo ""
echo "2️⃣ Removing PostgreSQL container and volume..."
docker compose down postgres 2>/dev/null || true
docker volume rm ai-agent_postgres_data 2>/dev/null || true
sleep 2

echo ""
echo "3️⃣ Starting PostgreSQL with fresh database..."
docker compose up -d postgres

echo ""
echo "4️⃣ Waiting for PostgreSQL to initialize..."
for i in {1..60}; do
    if docker compose exec -T postgres pg_isready -U aiagent > /dev/null 2>&1; then
        echo "   ✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "   ❌ PostgreSQL not ready after 60 attempts"
        exit 1
    fi
    sleep 1
done

echo ""
echo "5️⃣ Testing database connection..."
sleep 2
if docker compose exec -T postgres psql -U aiagent -d ai_agent_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "   ✅ Database connection successful!"
else
    echo "   ⚠️  Connection test failed"
fi

echo ""
echo "6️⃣ Starting Backend..."
docker compose up -d backend

echo ""
echo "7️⃣ Waiting for Backend..."
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

echo ""
echo "8️⃣ Testing CRM endpoint..."
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/crm/tenants 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ CRM endpoint is working! (HTTP 200)"
    echo ""
    echo "✅ Database recreated successfully!"
elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "   ✅ CRM endpoint accessible (HTTP $HTTP_CODE - auth required)"
    echo ""
    echo "✅ Database connection fixed!"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "   ⚠️  Still getting HTTP 500"
    echo "   Check: docker compose logs backend | tail -30"
else
    echo "   ⚠️  Got HTTP $HTTP_CODE"
    echo "   Check: docker compose logs backend | tail -30"
fi

echo ""
echo "📝 Next steps:"
echo "   - Run database migrations if needed"
echo "   - Create initial data if needed"
echo "   - Check: curl http://localhost:8000/api/crm/tenants"

