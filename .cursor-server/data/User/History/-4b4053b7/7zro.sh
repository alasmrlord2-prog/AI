#!/bin/bash
# Start all three frontends in background
set -e

cd "$(dirname "$0")"

echo "🚀 Starting all frontends..."

# Create logs directory
mkdir -p "$(dirname "$0")/logs"
LOGS_DIR="$(cd "$(dirname "$0")" && pwd)/logs"

# Start AI-Agent on port 3000
echo "Starting AI-Agent on port 3000..."
cd "$(dirname "$0")"
PORT=3000 NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev -- -p 3000 > "$LOGS_DIR/frontend-ai-agent.log" 2>&1 &
AI_AGENT_PID=$!
echo $AI_AGENT_PID > "$LOGS_DIR/frontend-ai-agent.pid"
echo "✅ AI-Agent started (PID: $AI_AGENT_PID)"

# Wait a bit
sleep 2

# Start CRM on port 3001
echo "Starting CRM on port 3001..."
PORT=3001 NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev -- -p 3001 > "$LOGS_DIR/frontend-crm.log" 2>&1 &
CRM_PID=$!
echo $CRM_PID > "$LOGS_DIR/frontend-crm.pid"
echo "✅ CRM started (PID: $CRM_PID)"

# Wait a bit
sleep 2

# Start AAA on port 3002
echo "Starting AAA on port 3002..."
PORT=3002 NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev -- -p 3002 > "$LOGS_DIR/frontend-aaa.log" 2>&1 &
AAA_PID=$!
echo $AAA_PID > "$LOGS_DIR/frontend-aaa.pid"
echo "✅ AAA started (PID: $AAA_PID)"

echo ""
echo "✅ All frontends started!"
echo ""
echo "📝 View logs:"
echo "   AI-Agent: tail -f /tmp/frontend-ai-agent.log"
echo "   CRM:      tail -f /tmp/frontend-crm.log"
echo "   AAA:      tail -f /tmp/frontend-aaa.log"
echo ""
echo "🛑 Stop all: ./stop-all.sh"

