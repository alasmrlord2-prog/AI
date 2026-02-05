#!/bin/bash
# Comprehensive Docker Fix Script
set -e

echo "🔧 Docker Issues Fix Script"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Stop all containers
echo -e "${YELLOW}Step 1: Stopping all containers...${NC}"
cd backend
docker-compose down --remove-orphans 2>/dev/null || true
cd ../frontend
docker-compose down --remove-orphans 2>/dev/null || true
cd ..

# Stop containers by name
docker stop ai-agent-backend ai-agent-backend-prod ai-agent-frontend ai-agent-frontend-prod ai-agent-postgres 2>/dev/null || true
docker rm -f ai-agent-backend ai-agent-backend-prod ai-agent-frontend ai-agent-frontend-prod ai-agent-postgres 2>/dev/null || true

echo -e "${GREEN}✅ Containers stopped${NC}"
echo ""

# Step 2: Kill processes on ports
echo -e "${YELLOW}Step 2: Killing processes on ports...${NC}"
for port in 8000 3000 3001 3002 5432; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "   Killing process on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
done
echo -e "${GREEN}✅ Ports cleared${NC}"
echo ""

# Step 3: Clean Docker
echo -e "${YELLOW}Step 3: Cleaning Docker...${NC}"
docker system prune -f
echo -e "${GREEN}✅ Docker cleaned${NC}"
echo ""

# Step 4: Remove problematic volumes (optional)
read -p "Do you want to remove volumes? This will delete all data! (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing volumes...${NC}"
    cd backend
    docker-compose down -v 2>/dev/null || true
    cd ../frontend
    docker-compose down -v 2>/dev/null || true
    docker volume prune -f
    echo -e "${GREEN}✅ Volumes removed${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping volume removal${NC}"
fi
echo ""

# Step 5: Rebuild (optional)
read -p "Do you want to rebuild containers? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Rebuilding containers...${NC}"
    cd backend
    docker-compose build --no-cache 2>/dev/null || echo "⚠️  Backend build failed or not needed"
    cd ../frontend
    docker-compose build --no-cache 2>/dev/null || echo "⚠️  Frontend build failed or not needed"
    echo -e "${GREEN}✅ Containers rebuilt${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping rebuild${NC}"
fi
echo ""

# Step 6: Summary
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Cleanup completed!${NC}"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Start Backend:"
echo "   cd backend && ./start-fixed.sh"
echo ""
echo "2. Start Frontends (choose one):"
echo "   - Using PM2: cd frontend && ./pm2-start.sh"
echo "   - Using start-all.sh: cd frontend && ./start-all.sh"
echo ""
echo "3. Check status:"
echo "   docker ps"
echo "   docker-compose ps"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"

