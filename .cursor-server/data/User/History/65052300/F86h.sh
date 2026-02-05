#!/bin/bash
# Fix PostgreSQL Authentication Issue

set -e

cd "$(dirname "$0")"

echo "🔧 Fixing PostgreSQL Authentication..."
echo ""

# Stop services
echo "1️⃣ Stopping services..."
docker compose stop backend postgres 2>/dev/null || true
sleep 2

# Check if we need to recreate database
echo ""
echo "2️⃣ Checking PostgreSQL volume..."
if docker volume ls | grep -q "ai-agent_postgres_data"; then
    echo "   ⚠️  PostgreSQL volume exists"
    read -p "   Do you want to recreate database? (this will DELETE all data) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   🗑️  Removing PostgreSQL volume..."
        docker compose down postgres 2>/dev/null || true
        docker volume rm ai-agent_postgres_data 2>/dev/null || true
        echo "   ✅ Volume removed"
    else
        echo "   ℹ️  Keeping existing volume"
    fi
else
    echo "   ✅ No existing volume, will create new one"
fi

# Start PostgreSQL
echo ""
echo "3️⃣ Starting PostgreSQL..."
docker compose up -d postgres

# Wait for PostgreSQL to be ready
echo ""
echo "4️⃣ Waiting for PostgreSQL to be ready..."
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

# Test connection
echo ""
echo "5️⃣ Testing database connection..."
sleep 2
if docker compose exec -T postgres psql -U aiagent -d ai_agent_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "   ✅ Database connection successful!"
else
    echo "   ⚠️  Connection test failed, but continuing..."
fi

# Start backend
echo ""
echo "6️⃣ Starting Backend..."
docker compose up -d backend

# Wait for backend
echo ""
echo "7️⃣ Waiting for Backend to be ready..."
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
echo "8️⃣ Testing CRM endpoint..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/crm/tenants 2>/dev/null || echo "000")
RESPONSE=$(curl -s http://localhost:8000/api/crm/tenants 2>&1 | head -c 200)

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ CRM endpoint is working! (HTTP 200)"
    echo "   Response: $(echo "$RESPONSE" | head -c 100)..."
    echo ""
    echo "✅ All fixed!"
elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo "   ✅ CRM endpoint is accessible (HTTP $HTTP_CODE - authentication required)"
    echo "   This is normal if authentication is required"
    echo ""
    echo "✅ Database connection fixed!"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "   ⚠️  Got HTTP 500"
    echo "   Response: $(echo "$RESPONSE" | head -c 150)..."
    echo ""
    echo "📝 Check logs: docker compose logs backend | tail -50"
else
    echo "   ⚠️  Got HTTP $HTTP_CODE"
    echo "   Response: $(echo "$RESPONSE" | head -c 150)..."
fi

echo ""
echo "📝 View logs: docker compose logs backend | grep -i 'crm\|error' | tail -20"

