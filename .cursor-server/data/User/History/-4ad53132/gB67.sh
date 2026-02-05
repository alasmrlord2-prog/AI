#!/bin/bash
# Restart Frontend Service (Docker)

set -e

cd "$(dirname "$0")"

echo "🔄 Restarting Frontend Service..."

# Restart frontend service
docker-compose restart frontend

echo "⏳ Waiting for frontend to be ready..."
sleep 10

# Check frontend service
echo ""
echo "✅ Frontend Service Status:"
echo "   AI-Agent (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo '000')"

echo ""
echo "📝 View logs: docker-compose logs -f frontend"

