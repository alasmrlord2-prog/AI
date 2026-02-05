#!/bin/bash
# Comprehensive fix and start script for all services
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🔧 Fixing and Starting All Services..."
echo ""

# Step 1: Fix port 8000
echo "1️⃣  Fixing port 8000..."
cd "$PROJECT_ROOT"
./FIX_PORT_8000.sh
echo ""

# Step 2: Start Backend
echo "2️⃣  Starting Backend Services..."
cd "$PROJECT_ROOT/backend"
./start.sh
echo ""

# Step 3: Wait for backend to be ready
echo "3️⃣  Waiting for backend to be ready..."
sleep 10

# Step 4: Check backend health
echo "4️⃣  Checking backend health..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  Backend is not responding. Check logs:"
        echo "   docker-compose -f $PROJECT_ROOT/docker-compose.yml logs -f backend"
    else
        sleep 2
    fi
done
echo ""

# Step 5: Check Ollama model
echo "5️⃣  Checking Ollama model..."
if docker exec ai-agent-ollama ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
    echo "✅ Ollama model llama3.2:1b is installed"
else
    echo "⚠️  Ollama model not found. You may need to install it:"
    echo "   docker exec -it ai-agent-ollama ollama pull llama3.2:1b"
fi
echo ""

# Step 6: Start Frontends (optional)
echo "6️⃣  Frontend Services:"
echo "   To start frontends, run:"
echo "   cd frontend && ./pm2-start.sh"
echo ""

# Step 7: Final status check
echo "7️⃣  Final Status Check:"
cd "$PROJECT_ROOT"
./check-all-services.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Useful commands:"
echo "   Check all services: ./check-all-services.sh"
echo "   Backend logs: docker-compose -f docker-compose.yml logs -f backend"
echo "   Stop backend: cd backend && ./stop.sh"
echo "   Restart backend: cd backend && ./restart.sh"

