#!/bin/bash
# Fix permissions and start CRM and AAA services

echo "🔧 Fixing permissions..."

# Fix .next directory ownership (requires sudo)
sudo chown -R ai:ai /home/ai/ai-agent/frontend/.next 2>/dev/null || {
    echo "⚠️  Cannot fix ownership without sudo. Please run:"
    echo "   sudo chown -R ai:ai /home/ai/ai-agent/frontend/.next"
    echo ""
    echo "Or remove .next directory:"
    echo "   sudo rm -rf /home/ai/ai-agent/frontend/.next"
    exit 1
}

echo "✅ Permissions fixed"

# Kill existing processes
echo "🛑 Stopping existing services..."
pkill -f "next dev -p 3001" 2>/dev/null
pkill -f "next dev -p 3002" 2>/dev/null
sleep 2

# Clear ports
fuser -k 3001/tcp 3002/tcp 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null
lsof -ti:3002 | xargs kill -9 2>/dev/null
sleep 2

echo "✅ Ports cleared"

# Start CRM
echo "🚀 Starting CRM on port 3001..."
cd /home/ai/ai-agent/frontend
PORT=3001 NEXT_PUBLIC_API_URL=http://localhost:8000 nohup npm run dev -- -p 3001 > /home/ai/crm-service.log 2>&1 &
CRM_PID=$!
echo "   CRM PID: $CRM_PID"

# Wait a bit
sleep 3

# Start AAA
echo "🚀 Starting AAA on port 3002..."
PORT=3002 NEXT_PUBLIC_API_URL=http://localhost:8000 nohup npm run dev -- -p 3002 > /home/ai/aaa-service.log 2>&1 &
AAA_PID=$!
echo "   AAA PID: $AAA_PID"

echo ""
echo "✅ Services started!"
echo ""
echo "📝 View logs:"
echo "   CRM: tail -f /home/ai/crm-service.log"
echo "   AAA: tail -f /home/ai/aaa-service.log"
echo ""
echo "⏳ Waiting for services to compile (this may take 2-3 minutes)..."
echo ""

# Wait and check
for i in {1..30}; do
    sleep 10
    CRM_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:3001 2>/dev/null)
    AAA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:3002 2>/dev/null)
    
    if [ "$CRM_STATUS" = "200" ] && [ "$AAA_STATUS" = "200" ]; then
        echo "✅ Both services are ready!"
        echo "   CRM: http://crm.bankid-sy.com (Status: $CRM_STATUS)"
        echo "   AAA: http://aaa.bankid-sy.com (Status: $AAA_STATUS)"
        exit 0
    fi
    
    echo "   Attempt $i/30: CRM=$CRM_STATUS, AAA=$AAA_STATUS (still compiling...)"
done

echo "⚠️  Services are taking longer than expected. Check logs for details."
echo "   They may still be compiling. Please wait a few more minutes."

