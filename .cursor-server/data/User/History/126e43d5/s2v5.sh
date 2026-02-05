#!/bin/bash
# Check backend logs and diagnose issues
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🔍 Checking Backend Status..."
echo ""

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    DOCKER_CMD="docker"
    DOCKER_COMPOSE_CMD="docker-compose"
else
    DOCKER_CMD="sudo docker"
    DOCKER_COMPOSE_CMD="sudo docker-compose"
fi

# Check container status
echo "📦 Container Status:"
$DOCKER_CMD ps -a | grep ai-agent-backend || echo "Container not found"
echo ""

# Check if container is running
if $DOCKER_CMD ps | grep -q ai-agent-backend; then
    echo "✅ Container is running"
    
    # Get container logs
    echo ""
    echo "📝 Last 50 lines of logs:"
    echo "----------------------------------------"
    $DOCKER_CMD logs ai-agent-backend --tail=50 2>&1
    echo "----------------------------------------"
    echo ""
    
    # Check if uvicorn is running inside container
    echo "🔍 Checking processes inside container:"
    $DOCKER_CMD exec ai-agent-backend ps aux 2>&1 | grep -E "(uvicorn|python)" || echo "Cannot check processes"
    echo ""
    
    # Try to check if app can be imported
    echo "🔍 Testing Python imports:"
    $DOCKER_CMD exec ai-agent-backend python -c "from app.main import app; print('✅ App imported successfully')" 2>&1 || echo "❌ Failed to import app"
    echo ""
    
    # Check port binding
    echo "🔍 Port binding:"
    $DOCKER_CMD port ai-agent-backend 2>&1 || echo "Cannot check port binding"
    echo ""
    
    # Check network connectivity
    echo "🔍 Network connectivity:"
    $DOCKER_CMD exec ai-agent-backend ping -c 1 postgres 2>&1 | head -3 || echo "Cannot ping postgres"
    $DOCKER_CMD exec ai-agent-backend ping -c 1 ollama 2>&1 | head -3 || echo "Cannot ping ollama"
    echo ""
    
else
    echo "❌ Container is not running"
    echo ""
    echo "📝 Last 50 lines of logs (from stopped container):"
    echo "----------------------------------------"
    $DOCKER_CMD logs ai-agent-backend --tail=50 2>&1 || echo "Cannot get logs"
    echo "----------------------------------------"
fi

# Check port from host
echo "🔍 Port 8000 status on host:"
netstat -tlnp 2>/dev/null | grep 8000 || ss -tlnp 2>/dev/null | grep 8000 || echo "Port 8000 not listening"
echo ""

# Try to connect
echo "🔍 Testing connection:"
timeout 3 curl -v http://localhost:8000/health 2>&1 | head -20 || echo "Connection failed"
echo ""

echo "💡 Suggestions:"
echo "   1. If container is not running: cd backend && ./restart.sh"
echo "   2. If there are import errors: Check requirements.txt and rebuild"
echo "   3. If database connection fails: Check postgres container"
echo "   4. View full logs: $DOCKER_COMPOSE_CMD -f $PROJECT_ROOT/docker-compose.yml logs -f backend"

