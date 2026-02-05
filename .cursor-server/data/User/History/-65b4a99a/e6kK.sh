#!/bin/bash
# Create Database Tables - Fixed Version

set -e

cd "$(dirname "$0")"

echo "🔧 Creating database tables..."
echo ""

# Create Python script file
cat > /tmp/create_tables.py << 'PYTHON_SCRIPT'
from app.core.database import Base, engine
from app.identity.models import *
from app.subscription.models import *
from app.audit.models import *
from app.access.models import *
from app.policy.models import *

try:
    print("📦 Creating database tables...")
    Base.metadata.create_all(engine)
    print("✅ All tables created successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_SCRIPT

# Copy script to container and run it
echo "1️⃣ Copying script to container..."
docker compose cp /tmp/create_tables.py backend:/tmp/create_tables.py

echo ""
echo "2️⃣ Running script in container..."
docker compose exec -T backend python3 /tmp/create_tables.py

if [ $? -eq 0 ]; then
    echo ""
    echo "3️⃣ Testing CRM endpoint..."
    sleep 2
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/crm/tenants 2>/dev/null || echo "000")
    RESPONSE=$(curl -s http://localhost:8000/api/crm/tenants 2>&1 | head -c 300)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ CRM endpoint is working! (HTTP 200)"
        echo "   Response: $(echo "$RESPONSE" | head -c 150)..."
        echo ""
        echo "✅ All fixed! Database tables created successfully!"
    elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo "   ✅ CRM endpoint accessible (HTTP $HTTP_CODE - auth required)"
        echo ""
        echo "✅ Database tables created successfully!"
    else
        echo "   ⚠️  Got HTTP $HTTP_CODE"
        echo "   Response: $(echo "$RESPONSE" | head -c 200)..."
        echo ""
        echo "📝 Check if there are other errors"
    fi
else
    echo ""
    echo "❌ Failed to create tables. Check errors above."
    exit 1
fi

# Cleanup
rm -f /tmp/create_tables.py

