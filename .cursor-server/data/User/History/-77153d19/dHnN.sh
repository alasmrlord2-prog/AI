#!/bin/bash

# ============================================
# AI Agent - Start Services Script
# ============================================
# This script starts all other services (nginx, postgres, ollama, etc.)
# Domain: ai-agent.bankid-sy.com
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
DOMAIN="ai-agent.bankid-sy.com"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 Starting AI Agent Services..."
echo "========================================"
echo "Domain: $DOMAIN"
echo "Services: nginx, postgres, ollama, prometheus, grafana, loki, promtail"
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

# Check if SSL certificates exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    echo "⚠️  SSL certificates not found!"
    echo "   Generating self-signed certificates..."
    if [ -f "nginx/generate-ssl.sh" ]; then
        cd nginx && ./generate-ssl.sh && cd ..
    else
        echo "   ❌ generate-ssl.sh not found!"
        echo "   Please generate SSL certificates manually."
        exit 1
    fi
fi

# Start all services
echo "📦 Starting services..."
docker-compose -f "$COMPOSE_FILE" up -d nginx postgres ollama prometheus grafana loki promtail

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check services status
echo ""
echo "✅ Services started!"
echo "========================================"
echo ""
echo "📊 Status:"
docker-compose -f "$COMPOSE_FILE" ps
echo ""
echo "🌐 URLs:"
echo "   Main Site: https://$DOMAIN"
echo "   API: https://$DOMAIN/api"
echo "   Health: https://$DOMAIN/health"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3001"
echo "   Loki: http://localhost:3100"
echo ""
echo "📝 Logs:"
echo "   Nginx: docker logs -f ai-agent-nginx"
echo "   All: docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "💡 To start backend and frontend:"
echo "   ./start_backend.sh"
echo "   ./start_frontend.sh"
echo ""

