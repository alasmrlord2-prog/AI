#!/bin/bash

# ============================================
# AI Agent - Restart Frontend Script
# ============================================
# This script restarts frontend and all required services
# Domain: ai-agent.bankid-sy.com
# Services: postgres, ollama, backend, frontend
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
DOMAIN="ai-agent.bankid-sy.com"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🔄 Restarting AI Agent Frontend..."
echo "========================================"
echo "Domain: $DOMAIN"
echo "Services: postgres, ollama, backend, frontend"
echo ""

cd "$PROJECT_DIR" || {
    echo "❌ Error: Cannot access project directory: $PROJECT_DIR"
    exit 1
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "   Please start Docker and try again."
    exit 1
fi

# Check if docker-compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Error: $COMPOSE_FILE not found!"
    exit 1
fi

# Restart services
echo "🔄 Restarting services..."
docker-compose -f "$COMPOSE_FILE" restart postgres ollama backend frontend

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to restart..."
sleep 10

# Check frontend status
if docker ps | grep -q "ai-agent-frontend-prod"; then
    echo ""
    echo "✅ Frontend restarted successfully!"
    echo "========================================"
    echo ""
    echo "📊 Status:"
    docker-compose -f "$COMPOSE_FILE" ps postgres ollama backend frontend
    echo ""
    echo "🌐 URLs:"
    echo "   Frontend: http://$DOMAIN"
    echo "   API: http://$DOMAIN/api"
    echo "   Local: http://localhost:3000"
    echo ""
    echo "📝 Logs:"
    echo "   Frontend: docker logs -f ai-agent-frontend-prod"
    echo "   All: docker-compose -f $COMPOSE_FILE logs -f frontend"
    echo ""
else
    echo ""
    echo "❌ Frontend failed to restart!"
    echo "========================================"
    echo ""
    echo "📝 Error logs:"
    docker-compose -f "$COMPOSE_FILE" logs frontend | tail -30
    echo ""
    exit 1
fi

