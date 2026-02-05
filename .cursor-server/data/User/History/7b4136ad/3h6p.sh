#!/bin/bash

# ============================================
# AI Agent - Start Backend Script
# ============================================
# This script starts the backend service with Docker
# Domain: ai-agent.bankid-sy.com
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
DOMAIN="ai-agent.bankid-sy.com"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 Starting AI Agent Backend..."
echo "========================================"
echo "Domain: $DOMAIN"
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

# Start backend service
echo "📦 Starting backend container..."
docker-compose -f "$COMPOSE_FILE" up -d backend

# Wait for backend to be ready
echo ""
echo "⏳ Waiting for backend to start..."
sleep 5

# Check backend status
if docker ps | grep -q "ai-agent-backend-prod"; then
    echo ""
    echo "✅ Backend started successfully!"
    echo "========================================"
    echo ""
    echo "📊 Status:"
    docker-compose -f "$COMPOSE_FILE" ps backend
    echo ""
    echo "🌐 URLs:"
    echo "   API: https://$DOMAIN/api"
    echo "   Docs: https://$DOMAIN/api/docs"
    echo "   Health: https://$DOMAIN/api/health"
    echo ""
    echo "📝 Logs:"
    echo "   View: docker logs -f ai-agent-backend-prod"
    echo "   Or: docker-compose -f $COMPOSE_FILE logs -f backend"
    echo ""
else
    echo ""
    echo "❌ Backend failed to start!"
    echo "========================================"
    echo ""
    echo "📝 Error logs:"
    docker-compose -f "$COMPOSE_FILE" logs backend | tail -30
    echo ""
    exit 1
fi

