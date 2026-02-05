#!/bin/bash

# ============================================
# AI Agent - Complete Startup Script
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "🚀 AI Agent - Starting All Services"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running!"
    exit 1
fi

print_status "Docker is ready"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p backend/app/logs
mkdir -p backend/app/memory
mkdir -p prometheus
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
mkdir -p loki
mkdir -p promtail
mkdir -p alertmanager
touch backend/app/logs/chat.log 2>/dev/null || true
print_status "Directories created"

# Step 1: Start Ollama (if not running)
echo ""
echo "Step 1: Starting Ollama..."
if docker ps | grep -q "ollama"; then
    print_status "Ollama is already running"
else
    if docker ps -a | grep -q "ollama"; then
        docker start ollama
        print_status "Ollama started"
    else
        print_warning "Ollama container not found. Starting from agent-compose.yml..."
        if [ -f "agent-compose.yml" ]; then
            docker compose -f agent-compose.yml up -d ollama
            print_status "Ollama started"
        else
            print_warning "agent-compose.yml not found. Skipping Ollama..."
        fi
    fi
fi

# Step 2: Start Backend
echo ""
echo "Step 2: Starting Backend..."
cd backend
if [ -f "backend-compose.yml" ]; then
    docker compose -f backend-compose.yml down 2>/dev/null || true
    docker compose -f backend-compose.yml up -d --build
    print_status "Backend started"
else
    print_error "backend-compose.yml not found!"
    exit 1
fi
cd ..

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health &>/dev/null || curl -s http://localhost:8000/api/monitor &>/dev/null; then
        print_status "Backend is ready"
        break
    fi
    sleep 1
done

# Step 3: Start Monitoring Stack (Prometheus, Grafana, Loki, Promtail, Alertmanager)
echo ""
echo "Step 3: Starting Monitoring Stack..."
if [ -f "prometheus-grafana-compose.yml" ]; then
    docker compose -f prometheus-grafana-compose.yml down 2>/dev/null || true
    docker compose -f prometheus-grafana-compose.yml up -d
    print_status "Monitoring stack started"
else
    print_error "prometheus-grafana-compose.yml not found!"
    exit 1
fi

# Wait for services
echo "Waiting for services to be ready..."
sleep 5

# Step 4: Check Services Status
echo ""
echo "=========================================="
echo "📊 Services Status"
echo "=========================================="
echo ""

services=(
    "ollama:11434"
    "ai-backend:8000"
    "prometheus:9090"
    "grafana:3001"
    "loki:3100"
    "alertmanager:9093"
)

for service in "${services[@]}"; do
    name="${service%%:*}"
    port="${service##*:}"
    if curl -s "http://localhost:${port}" &>/dev/null || curl -s "http://localhost:${port}/ready" &>/dev/null || curl -s "http://localhost:${port}/-/healthy" &>/dev/null; then
        print_status "$name (port $port) - Running"
    else
        print_warning "$name (port $port) - Starting..."
    fi
done

# Step 5: Display Access URLs
echo ""
echo "=========================================="
echo "🌐 Access URLs"
echo "=========================================="
echo ""
echo "Frontend:        http://$(hostname -I | awk '{print $1}'):3000"
echo "Backend API:     http://$(hostname -I | awk '{print $1}'):8000"
echo "Backend Docs:    http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "Prometheus:      http://$(hostname -I | awk '{print $1}'):9090"
echo "Prometheus Alerts: http://$(hostname -I | awk '{print $1}'):9090/alerts"
echo "Grafana:         http://$(hostname -I | awk '{print $1}'):3001"
echo "  - Username:    admin"
echo "  - Password:    admin123"
echo "Loki:            http://$(hostname -I | awk '{print $1}'):3100"
echo "Alertmanager:    http://$(hostname -I | awk '{print $1}'):9093"
echo ""

# Step 6: Show Container Status
echo "=========================================="
echo "🐳 Docker Containers"
echo "=========================================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAME|ollama|ai-backend|prometheus|grafana|loki|promtail|alertmanager" || docker ps

echo ""
echo "=========================================="
echo "✅ All services started!"
echo "=========================================="
echo ""
echo "To stop all services:"
echo "  ./stop-all.sh"
echo ""
echo "To view logs:"
echo "  docker compose -f backend/backend-compose.yml logs -f"
echo "  docker compose -f prometheus-grafana-compose.yml logs -f"
echo ""

