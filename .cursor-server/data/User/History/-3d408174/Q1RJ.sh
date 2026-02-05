#!/bin/bash

# ============================================
# AI Agent - Stop All Services
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "🛑 AI Agent - Stopping All Services"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Stop Backend
echo "Stopping Backend..."
cd backend
if [ -f "backend-compose.yml" ]; then
    docker compose -f backend-compose.yml down
    print_status "Backend stopped"
fi
cd ..

# Stop Monitoring Stack
echo "Stopping Monitoring Stack..."
if [ -f "prometheus-grafana-compose.yml" ]; then
    docker compose -f prometheus-grafana-compose.yml down
    print_status "Monitoring stack stopped"
fi

# Stop Ollama (optional - keep it running if you want)
read -p "Stop Ollama? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if docker ps | grep -q "ollama"; then
        docker stop ollama
        print_status "Ollama stopped"
    fi
else
    print_warning "Keeping Ollama running"
fi

echo ""
echo "=========================================="
echo "✅ All services stopped!"
echo "=========================================="

