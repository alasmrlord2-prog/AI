#!/bin/bash
# Stop all frontends
set -e

echo "🛑 Stopping all frontends..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGS_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOGS_DIR"

# Stop AI-Agent
if [ -f "$LOGS_DIR/frontend-ai-agent.pid" ]; then
    AI_AGENT_PID=$(cat "$LOGS_DIR/frontend-ai-agent.pid")
    if ps -p $AI_AGENT_PID > /dev/null 2>&1; then
        kill $AI_AGENT_PID
        echo "✅ Stopped AI-Agent (PID: $AI_AGENT_PID)"
    else
        echo "⚠️  AI-Agent process not found"
    fi
    rm -f "$LOGS_DIR/frontend-ai-agent.pid"
else
    echo "⚠️  AI-Agent PID file not found"
fi

# Stop CRM
if [ -f "$LOGS_DIR/frontend-crm.pid" ]; then
    CRM_PID=$(cat "$LOGS_DIR/frontend-crm.pid")
    if ps -p $CRM_PID > /dev/null 2>&1; then
        kill $CRM_PID
        echo "✅ Stopped CRM (PID: $CRM_PID)"
    else
        echo "⚠️  CRM process not found"
    fi
    rm -f "$LOGS_DIR/frontend-crm.pid"
else
    echo "⚠️  CRM PID file not found"
fi

# Stop AAA
if [ -f "$LOGS_DIR/frontend-aaa.pid" ]; then
    AAA_PID=$(cat "$LOGS_DIR/frontend-aaa.pid")
    if ps -p $AAA_PID > /dev/null 2>&1; then
        kill $AAA_PID
        echo "✅ Stopped AAA (PID: $AAA_PID)"
    else
        echo "⚠️  AAA process not found"
    fi
    rm -f "$LOGS_DIR/frontend-aaa.pid"
else
    echo "⚠️  AAA PID file not found"
fi

# Also kill any remaining node processes on these ports
echo "🧹 Cleaning up any remaining processes on ports 3000, 3001, 3002..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
lsof -ti:3002 | xargs kill -9 2>/dev/null || true

echo "✅ All frontends stopped!"

