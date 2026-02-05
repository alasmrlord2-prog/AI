#!/bin/bash
# Script to properly restart the backend

cd /home/ai/ai-agent/backend

echo "Stopping all uvicorn processes..."
pkill -f "uvicorn.*app.main" || true
pkill -f "uvicorn.*main:app" || true
sleep 3

echo "Checking if port 8000 is free..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo "Preparing logs directory..."
mkdir -p logs
touch logs/chat.log 2>/dev/null || true

echo "Starting backend..."
nohup python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

sleep 5

echo "Checking backend status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running successfully!"
    curl -s http://localhost:8000/health | python3 -m json.tool
else
    echo "❌ Backend failed to start. Check backend.log for errors."
    tail -20 backend.log
fi

