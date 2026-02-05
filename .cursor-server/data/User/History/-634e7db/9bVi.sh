#!/bin/bash
# Test backend startup inside container
set -e

echo "🧪 Testing Backend Startup..."
echo ""

# Check if we can run docker commands
if ! docker ps > /dev/null 2>&1; then
    echo "⚠️  Cannot run docker commands. Trying with sudo..."
    DOCKER_CMD="sudo docker"
else
    DOCKER_CMD="docker"
fi

# Check if container exists
if ! $DOCKER_CMD ps -a | grep -q ai-agent-backend; then
    echo "❌ Container ai-agent-backend not found"
    exit 1
fi

# Test Python import
echo "1. Testing Python import..."
$DOCKER_CMD exec ai-agent-backend python -c "
import sys
sys.path.insert(0, '/app')

try:
    print('Importing app.main...')
    from app.main import app
    print('✅ App imported successfully!')
    print(f'App type: {type(app)}')
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 2>&1

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Import test failed. Check the error above."
    exit 1
fi

echo ""
echo "2. Testing database connection..."
$DOCKER_CMD exec ai-agent-backend python -c "
import os
from app.core.config import get_settings

try:
    settings = get_settings()
    print(f'✅ Settings loaded')
    print(f'   DATABASE_URL: {settings.DATABASE_URL[:50]}...')
    print(f'   OLLAMA_URL: {settings.OLLAMA_URL}')
except Exception as e:
    print(f'❌ Settings failed: {e}')
    import traceback
    traceback.print_exc()
" 2>&1

echo ""
echo "3. Checking if uvicorn can start..."
echo "   (This will start uvicorn in background for 5 seconds)"
$DOCKER_CMD exec -d ai-agent-backend sh -c "cd /app && timeout 5 uvicorn app.main:app --host 0.0.0.0 --port 8000 || true" 2>&1
sleep 6

echo ""
echo "4. Testing health endpoint..."
timeout 3 curl -s http://localhost:8000/health 2>&1 || echo "   Connection failed or timeout"

echo ""
echo "✅ Tests completed!"
echo ""
echo "💡 If import failed, check:"
echo "   - Missing dependencies in requirements.txt"
echo "   - Missing files in app/ directory"
echo "   - Syntax errors in Python files"

