#!/bin/bash

# ============================================
# AI Agent - Stop Backend Script
# ============================================
# This script stops backend and related services
# Services: backend, ollama, postgres
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
COMPOSE_FILE="docker-compose.prod.yml"

echo "⏹️  Stopping AI Agent Backend..."
echo "========================================"
echo "Services: backend, ollama, postgres"
echo ""

cd "$PROJECT_DIR" || {
    echo "❌ Error: Cannot access project directory: $PROJECT_DIR"
    exit 1
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    exit 1
fi

# Check if docker-compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Error: $COMPOSE_FILE not found!"
    exit 1
fi

# Stop services
echo "⏹️  Stopping services..."
docker-compose -f "$COMPOSE_FILE" stop backend ollama postgres

echo ""
echo "✅ Backend services stopped successfully!"
echo "========================================"
echo ""
echo "📊 Stopped services:"
docker-compose -f "$COMPOSE_FILE" ps backend ollama postgres
echo ""
echo "💡 To start again, run: ./start_backend.sh"
echo ""

