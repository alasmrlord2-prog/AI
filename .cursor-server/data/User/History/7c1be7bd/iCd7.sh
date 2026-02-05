#!/bin/bash
# Setup Database Tables

set -e

cd "$(dirname "$0")"

echo "🔧 Setting up database tables..."
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend is not running. Please start it first."
    exit 1
fi

echo "1️⃣ Creating database tables..."
docker compose exec -T backend python3 << 'PYTHON_SCRIPT'
from app.core.database import Base, engine
from app.identity.models import *
from app.subscription.models import *
from app.audit.models import *
from app.access.models import *
from app.policy.models import *

try:
    Base.metadata.create_all(engine)
    print("✅ All tables created successfully")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    echo ""
    echo "2️⃣ Testing CRM endpoint..."
    sleep 2
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/crm/tenants 2>/dev/null || echo "000")
    RESPONSE=$(curl -s http://localhost:8000/api/crm/tenants 2>&1 | head -c 200)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ CRM endpoint is working! (HTTP 200)"
        echo "   Response: $(echo "$RESPONSE" | head -c 100)..."
        echo ""
        echo "✅ Database setup complete!"
    elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo "   ✅ CRM endpoint accessible (HTTP $HTTP_CODE - auth required)"
        echo ""
        echo "✅ Database setup complete!"
    else
        echo "   ⚠️  Got HTTP $HTTP_CODE"
        echo "   Response: $(echo "$RESPONSE" | head -c 150)..."
        echo ""
        echo "📝 Check logs: docker compose logs backend | tail -30"
    fi
else
    echo ""
    echo "❌ Failed to create tables. Check errors above."
    exit 1
fi

