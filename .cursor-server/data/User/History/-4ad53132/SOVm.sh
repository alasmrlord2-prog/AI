#!/bin/bash
# Restart Frontend Services (Docker)

set -e

cd "$(dirname "$0")"

echo "🔄 Restarting Frontend Services..."

# Restart all frontend services
docker-compose restart frontend-ai-agent frontend-crm frontend-aaa

echo "⏳ Waiting for frontends to be ready..."
sleep 10

# Check frontend services
echo ""
echo "✅ Frontend Services Status:"
echo "   AI-Agent (3000): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo '000')"
echo "   CRM (3001): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 || echo '000')"
echo "   AAA (3002): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002 || echo '000')"

echo ""
echo "📝 View logs:"
echo "   AI-Agent: docker-compose logs -f frontend-ai-agent"
echo "   CRM:      docker-compose logs -f frontend-crm"
echo "   AAA:      docker-compose logs -f frontend-aaa"

