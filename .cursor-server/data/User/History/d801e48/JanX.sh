#!/bin/bash
# Complete setup script for all three services
set -e

echo "🚀 Setting up all three services (AI-Agent, CRM, AAA)..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root for NGINX operations
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Some operations require sudo. You may be prompted for password.${NC}"
fi

# Step 1: Setup NGINX
echo -e "${GREEN}Step 1: Setting up NGINX configurations...${NC}"
if [ -f "nginx-ai-agent-complete.conf" ]; then
    sudo cp nginx-ai-agent-complete.conf /etc/nginx/sites-available/ai-agent.bankid-sy.com
    echo "✅ Copied ai-agent.bankid-sy.com config"
else
    echo -e "${RED}❌ nginx-ai-agent-complete.conf not found!${NC}"
    exit 1
fi

if [ -f "nginx-aaa-complete.conf" ]; then
    sudo cp nginx-aaa-complete.conf /etc/nginx/sites-available/aaa.bankid-sy.com
    echo "✅ Copied aaa.bankid-sy.com config"
else
    echo -e "${RED}❌ nginx-aaa-complete.conf not found!${NC}"
    exit 1
fi

if [ -f "nginx-crm-complete.conf" ]; then
    sudo cp nginx-crm-complete.conf /etc/nginx/sites-available/crm.bankid-sy.com
    echo "✅ Copied crm.bankid-sy.com config"
else
    echo -e "${RED}❌ nginx-crm-complete.conf not found!${NC}"
    exit 1
fi

# Enable sites
sudo ln -sf /etc/nginx/sites-available/ai-agent.bankid-sy.com /etc/nginx/sites-enabled/ 2>/dev/null || true
sudo ln -sf /etc/nginx/sites-available/aaa.bankid-sy.com /etc/nginx/sites-enabled/ 2>/dev/null || true
sudo ln -sf /etc/nginx/sites-available/crm.bankid-sy.com /etc/nginx/sites-enabled/ 2>/dev/null || true

echo "✅ Enabled all NGINX sites"
echo ""

# Step 2: Test NGINX configuration
echo -e "${GREEN}Step 2: Testing NGINX configuration...${NC}"
if sudo nginx -t; then
    echo "✅ NGINX configuration is valid"
else
    echo -e "${RED}❌ NGINX configuration test failed!${NC}"
    exit 1
fi
echo ""

# Step 3: Reload NGINX
echo -e "${GREEN}Step 3: Reloading NGINX...${NC}"
if sudo systemctl reload nginx; then
    echo "✅ NGINX reloaded successfully"
else
    echo -e "${RED}❌ Failed to reload NGINX!${NC}"
    exit 1
fi
echo ""

# Step 4: Check if backend is running
echo -e "${GREEN}Step 4: Checking backend...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
else
    echo -e "${YELLOW}⚠️  Backend is not running on port 8000${NC}"
    echo "   Start it with: cd backend && ./start.sh"
fi
echo ""

# Step 5: Check ports availability
echo -e "${GREEN}Step 5: Checking port availability...${NC}"
for port in 3000 3001 3002; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
    else
        echo "✅ Port $port is available"
    fi
done
echo ""

# Step 6: Summary
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Setup completed!${NC}"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Start Backend (if not running):"
echo "   cd backend && ./start.sh"
echo ""
echo "2. Start Frontends (choose one method):"
echo ""
echo "   Method A - Using start-all.sh:"
echo "   cd frontend && ./start-all.sh"
echo ""
echo "   Method B - Using PM2:"
echo "   cd frontend && ./pm2-start.sh"
echo ""
echo "   Method C - Manual (3 terminals):"
echo "   Terminal 1: cd frontend && ./start-ai-agent.sh"
echo "   Terminal 2: cd frontend && ./start-crm.sh"
echo "   Terminal 3: cd frontend && ./start-aaa.sh"
echo ""
echo "3. Test the services:"
echo "   curl http://ai-agent.bankid-sy.com/health"
echo "   curl http://crm.bankid-sy.com/health"
echo "   curl http://aaa.bankid-sy.com/health"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"

