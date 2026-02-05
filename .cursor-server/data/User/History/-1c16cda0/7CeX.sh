#!/bin/bash
# Comprehensive fix for backend not responding issue
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🔧 Fixing Backend Issue..."
echo ""

cd "$PROJECT_ROOT"

# Step 1: Stop everything
echo "1️⃣  Stopping all services..."
cd backend
./stop.sh 2>/dev/null || true
cd ..
sleep 3

# Step 2: Fix port 8000
echo ""
echo "2️⃣  Fixing port 8000..."
./FIX_PORT_8000.sh

# Step 3: Check if we need to rebuild
echo ""
echo "3️⃣  Checking if rebuild is needed..."
REBUILD=false

# Check if image exists
if ! docker images | grep -q "ai-agent-backend"; then
    echo "   Image not found, will rebuild..."
    REBUILD=true
fi

# Step 4: Rebuild if needed or forced
if [ "$1" == "--rebuild" ] || [ "$REBUILD" == true ]; then
    echo ""
    echo "4️⃣  Rebuilding backend image..."
    docker-compose -f docker-compose.yml build --no-cache backend
else
    echo ""
    echo "4️⃣  Skipping rebuild (use --rebuild to force rebuild)"
fi

# Step 5: Start services
echo ""
echo "5️⃣  Starting services..."
cd backend
./start.sh
cd ..

# Step 6: Wait and check
echo ""
echo "6️⃣  Waiting for backend to be ready..."
sleep 15

# Try multiple times
MAX_RETRIES=10
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is responding!"
        SUCCESS=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Attempt $RETRY_COUNT/$MAX_RETRIES failed, retrying..."
    sleep 3
done

if [ "$SUCCESS" == false ]; then
    echo ""
    echo "❌ Backend still not responding after $MAX_RETRIES attempts"
    echo ""
    echo "📝 Debugging steps:"
    echo "   1. Check logs: sudo docker logs ai-agent-backend --tail=100"
    echo "   2. Test import: cd backend && ./test-startup.sh"
    echo "   3. Rebuild: ./FIX_BACKEND_ISSUE.sh --rebuild"
    echo "   4. Check database: sudo docker logs ai-agent-postgres --tail=20"
    exit 1
fi

echo ""
echo "✅ Backend is working!"
echo ""
echo "📋 Test endpoints:"
echo "   Health: curl http://localhost:8000/health"
echo "   Docs:   http://localhost:8000/docs"
echo "   Root:   curl http://localhost:8000/"

