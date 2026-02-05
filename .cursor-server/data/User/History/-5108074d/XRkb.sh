#!/bin/bash

# ============================================
# AI Agent - Start Frontend Script
# ============================================
# This script starts the frontend service with Docker
# Domain: ai-agent.bankid-sy.com
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
DOMAIN="ai-agent.bankid-sy.com"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 Starting AI Agent Frontend..."
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

# Start frontend service
echo "📦 Starting frontend container..."
docker-compose -f "$COMPOSE_FILE" up -d frontend

# Wait for frontend to be ready
echo ""
echo "⏳ Waiting for frontend to start..."
sleep 8

# Check frontend status
if docker ps | grep -q "ai-agent-frontend-prod"; then
    echo ""
    echo "✅ Frontend started successfully!"
    echo "========================================"
    echo ""
    echo "📊 Status:"
    docker-compose -f "$COMPOSE_FILE" ps frontend
    echo ""
    echo "🌐 URLs:"
    echo "   Frontend: https://$DOMAIN"
    echo "   Local: http://localhost:3000"
    echo ""
    echo "📝 Logs:"
    echo "   View: docker logs -f ai-agent-frontend-prod"
    echo "   Or: docker-compose -f $COMPOSE_FILE logs -f frontend"
    echo ""
else
    echo ""
    echo "❌ Frontend failed to start!"
    echo "========================================"
    echo ""
    echo "📝 Error logs:"
    docker-compose -f "$COMPOSE_FILE" logs frontend | tail -30
    echo ""
    exit 1
fi

