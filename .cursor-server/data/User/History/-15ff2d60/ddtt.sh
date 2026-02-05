#!/bin/bash

# ============================================
# AI Agent - Restart Backend Script
# ============================================
# This script restarts backend and all required services
# Domain: ai-agent.bankid-sy.com
# Services: postgres, ollama, backend
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
DOMAIN="ai-agent.bankid-sy.com"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🔄 Restarting AI Agent Backend..."
echo "========================================"
echo "Domain: $DOMAIN"
echo "Services: postgres, ollama, backend"
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
docker-compose -f "$COMPOSE_FILE" restart postgres ollama backend

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to restart..."
sleep 8

# Check backend status
if docker ps | grep -q "ai-agent-backend-prod"; then
    echo ""
    echo "✅ Backend restarted successfully!"
    echo "========================================"
    echo ""
    echo "📊 Status:"
    docker-compose -f "$COMPOSE_FILE" ps postgres ollama backend
    echo ""
    echo "🌐 URLs:"
    echo "   API: https://$DOMAIN/api"
    echo "   Docs: https://$DOMAIN/api/docs"
    echo "   Health: https://$DOMAIN/api/health"
    echo ""
    echo "📝 Logs:"
    echo "   Backend: docker logs -f ai-agent-backend-prod"
    echo "   All: docker-compose -f $COMPOSE_FILE logs -f backend"
    echo ""
else
    echo ""
    echo "❌ Backend failed to restart!"
    echo "========================================"
    echo ""
    echo "📝 Error logs:"
    docker-compose -f "$COMPOSE_FILE" logs backend | tail -30
    echo ""
    exit 1
fi

