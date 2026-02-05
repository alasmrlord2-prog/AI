#!/bin/bash
# Debug backend issues - run with sudo if needed
set -e

echo "🔍 Backend Debug Information"
echo "============================"
echo ""

# Check container
echo "1. Container Status:"
sudo docker ps -a | grep ai-agent-backend || echo "   Container not found"
echo ""

# Get logs
echo "2. Backend Logs (last 100 lines):"
echo "----------------------------------------"
sudo docker logs ai-agent-backend --tail=100 2>&1
echo "----------------------------------------"
echo ""

# Check if uvicorn is running
echo "3. Processes in container:"
sudo docker exec ai-agent-backend ps aux 2>&1 | head -10
echo ""

# Check Python/App
echo "4. Testing Python import:"
sudo docker exec ai-agent-backend python -c "
try:
    from app.main import app
    print('✅ App imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    import traceback
    traceback.print_exc()
" 2>&1
echo ""

# Check database connection
echo "5. Testing database connection:"
sudo docker exec ai-agent-backend python -c "
import os
db_url = os.getenv('DATABASE_URL', 'not set')
print(f'DATABASE_URL: {db_url[:50]}...' if len(db_url) > 50 else f'DATABASE_URL: {db_url}')
" 2>&1
echo ""

# Check port
echo "6. Port 8000 status:"
sudo netstat -tlnp 2>/dev/null | grep 8000 || sudo ss -tlnp 2>/dev/null | grep 8000 || echo "   Port not listening"
echo ""

# Try restart
echo "7. Suggestions:"
echo "   - Restart: cd backend && ./restart.sh"
echo "   - Rebuild: docker-compose -f docker-compose.yml build --no-cache backend"
echo "   - Check postgres: docker logs ai-agent-postgres --tail=20"

