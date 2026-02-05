#!/bin/bash

# ============================================
# AI Agent - Start Nginx Script
# ============================================
# This script starts nginx service
# Domain: ai-agent.bankid-sy.com
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 Starting Nginx..."
echo "========================================"
echo ""

cd "$PROJECT_DIR" || {
    echo "❌ Error: Cannot access project directory: $PROJECT_DIR"
    exit 1
}

# Check if SSL certificates exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    echo "⚠️  SSL certificates not found!"
    echo "   Generating self-signed certificates..."
    if [ -f "nginx/generate-ssl.sh" ]; then
        cd nginx && ./generate-ssl.sh && cd ..
    else
        echo "   ❌ generate-ssl.sh not found!"
        exit 1
    fi
fi

# Start nginx
echo "📦 Starting nginx container..."
docker-compose -f "$COMPOSE_FILE" up -d nginx

# Wait for nginx to be ready
echo ""
echo "⏳ Waiting for nginx to start..."
sleep 3

# Check nginx status
if docker ps | grep -q "ai-agent-nginx"; then
    echo ""
    echo "✅ Nginx started successfully!"
    echo "========================================"
    echo ""
    echo "📊 Status:"
    docker-compose -f "$COMPOSE_FILE" ps nginx
    echo ""
    echo "🌐 URLs:"
    echo "   Main Site: https://ai-agent.bankid-sy.com"
    echo "   API: https://ai-agent.bankid-sy.com/api"
    echo "   Health: https://ai-agent.bankid-sy.com/health"
    echo ""
    echo "📝 Logs:"
    echo "   View: docker logs -f ai-agent-nginx"
    echo ""
else
    echo ""
    echo "❌ Nginx failed to start!"
    echo "========================================"
    echo ""
    echo "📝 Error logs:"
    docker-compose -f "$COMPOSE_FILE" logs nginx | tail -30
    echo ""
    exit 1
fi

