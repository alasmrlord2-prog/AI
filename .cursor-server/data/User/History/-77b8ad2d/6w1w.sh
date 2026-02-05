#!/bin/bash
# Comprehensive health check for all services
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🔍 Checking all services..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local port=$3
    
    echo -n "Checking $name (port $port)... "
    
    if curl -s --max-time 5 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Function to check docker container
check_docker_container() {
    local name=$1
    
    echo -n "Checking Docker container $name... "
    
    if docker ps --format '{{.Names}}' | grep -q "^${name}$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$name" 2>/dev/null)
        if [ "$status" = "running" ]; then
            echo -e "${GREEN}✅ Running${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Status: $status${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Not running${NC}"
        return 1
    fi
}

# Check Docker containers
echo "📦 Docker Containers:"
check_docker_container "ai-agent-postgres"
check_docker_container "ai-agent-ollama"
check_docker_container "ai-agent-backend"
echo ""

# Check Backend
echo "🔧 Backend Services:"
check_service "Backend Health" "http://localhost:8000/health" "8000"
check_service "Backend API Docs" "http://localhost:8000/docs" "8000"
check_service "Ollama API" "http://localhost:11434/api/tags" "11434"
echo ""

# Check Frontends
echo "🌐 Frontend Services:"
check_service "AI-Agent Frontend" "http://localhost:3000" "3000"
check_service "CRM Frontend" "http://localhost:3001" "3001"
check_service "AAA Frontend" "http://localhost:3002" "3002"
echo ""

# Check PM2 processes
echo "⚙️  PM2 Processes:"
if command -v pm2 &> /dev/null; then
    pm2_status=$(pm2 jlist 2>/dev/null | grep -o '"name":"[^"]*"' | wc -l)
    if [ "$pm2_status" -gt 0 ]; then
        echo -e "${GREEN}✅ PM2 is running ($pm2_status processes)${NC}"
        pm2 status
    else
        echo -e "${YELLOW}⚠️  PM2 is installed but no processes running${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  PM2 is not installed${NC}"
fi
echo ""

# Check Ports
echo "🔌 Port Status:"
for port in 3000 3001 3002 8000 11434 5432; do
    if lsof -i :$port > /dev/null 2>&1; then
        process=$(lsof -ti:$port | head -1)
        echo -e "Port $port: ${GREEN}✅ In use${NC} (PID: $process)"
    else
        echo -e "Port $port: ${RED}❌ Not in use${NC}"
    fi
done
echo ""

# Summary
echo "📊 Summary:"
echo "   Run './backend/start.sh' to start backend services"
echo "   Run './frontend/pm2-start.sh' to start frontend services"
echo "   Run 'docker-compose -f docker-compose.yml ps' to check Docker status"
echo "   Run 'docker-compose -f docker-compose.yml logs -f backend' to view backend logs"

