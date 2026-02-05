#!/bin/bash
# Check Backend Status and Fix Issues
set -e

cd "$(dirname "$0")"

echo "🔍 Checking Backend Status..."
echo ""

# Check if containers are running
echo "1. Checking Docker containers..."
if docker ps --format "{{.Names}}" 2>/dev/null | grep -q "ai-agent-backend"; then
    echo "   ✅ Backend container is running"
    BACKEND_RUNNING=true
else
    echo "   ❌ Backend container is NOT running"
    BACKEND_RUNNING=false
fi

if docker ps --format "{{.Names}}" 2>/dev/null | grep -q "ai-agent-postgres"; then
    echo "   ✅ PostgreSQL container is running"
    POSTGRES_RUNNING=true
else
    echo "   ❌ PostgreSQL container is NOT running"
    POSTGRES_RUNNING=false
fi

echo ""

# Check if port 8000 is accessible
echo "2. Checking port 8000..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is responding on port 8000"
    PORT_ACCESSIBLE=true
else
    echo "   ❌ Backend is NOT responding on port 8000"
    PORT_ACCESSIBLE=false
fi

echo ""

# Check what's using port 8000
echo "3. Checking what's using port 8000..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "   Processes using port 8000:"
    lsof -i :8000 | head -5
else
    echo "   ⚠️  Nothing is using port 8000"
fi

echo ""

# Check backend logs
echo "4. Recent Backend logs:"
if [ "$BACKEND_RUNNING" = true ]; then
    docker logs ai-agent-backend --tail=10 2>&1 | tail -5 || echo "   ⚠️  Cannot read logs"
else
    echo "   ⚠️  Container not running, cannot read logs"
fi

echo ""

# Summary and recommendations
echo "═══════════════════════════════════════════════════════════"
echo "📋 Summary:"
echo ""

if [ "$BACKEND_RUNNING" = true ] && [ "$PORT_ACCESSIBLE" = true ]; then
    echo "✅ Backend is working correctly!"
    echo ""
    echo "If you still see 502 errors, check:"
    echo "  1. NGINX configuration"
    echo "  2. NGINX is pointing to correct backend URL"
    echo "  3. CORS settings in backend"
elif [ "$BACKEND_RUNNING" = false ]; then
    echo "❌ Backend container is not running"
    echo ""
    echo "🔧 Fix:"
    echo "  ./start-fixed.sh"
elif [ "$PORT_ACCESSIBLE" = false ]; then
    echo "❌ Backend is not responding"
    echo ""
    echo "🔧 Fix:"
    echo "  1. Check logs: docker logs ai-agent-backend"
    echo "  2. Restart: ./restart-fixed.sh"
    echo "  3. If still failing, rebuild: docker-compose build backend && docker-compose up -d backend"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"

