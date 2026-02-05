#!/bin/bash
# Script to start everything in the correct order

echo "🚀 Starting SHIFTWAVE AI Platform..."
echo ""

# Step 1: Check NGINX
echo "1️⃣  Checking NGINX configuration..."
if [ ! -f "/etc/nginx/sites-enabled/ai-agent.bankid-sy.com" ]; then
    echo "⚠️  NGINX not configured. Run: sudo ./setup-all-services.sh"
    echo ""
else
    echo "✅ NGINX is configured"
    echo ""
fi

# Step 2: Start Backend
echo "2️⃣  Starting Backend (Ollama + Postgres + Backend)..."
cd backend

# Clear port 8000 if in use
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is in use. Clearing..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    pkill -9 -f "uvicorn.*8000" 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    sleep 2
fi

./start.sh
cd ..

# Step 3: Wait a bit
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Step 4: Check Ollama model
echo ""
echo "3️⃣  Checking Ollama model..."
if docker exec ai-agent-ollama ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
    echo "✅ Model llama3.2:1b is installed"
else
    echo "⚠️  Model not found. Installing..."
    echo "   Run: docker exec -it ai-agent-ollama ollama pull llama3.2:1b"
fi

# Step 5: Start Frontends
echo ""
echo "4️⃣  Starting Frontends..."
cd frontend
./pm2-start.sh
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "📋 Check status:"
echo "   Backend:  curl http://localhost:8000/health"
echo "   Ollama:   curl http://localhost:11434/api/tags"
echo "   PM2:      pm2 status"
