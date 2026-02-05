#!/bin/bash

echo "🔍 البحث عن العمليات التي تستخدم port 3001..."

# Kill all processes using port 3001
lsof -ti:3001 | xargs kill -9 2>/dev/null
fuser -k 3001/tcp 2>/dev/null

# Kill any node processes related to port 3001
pkill -9 -f "next dev -p 3001" 2>/dev/null
pkill -9 -f "npm run dev.*3001" 2>/dev/null

sleep 2

# Check if port is free
if ss -tulpn | grep -q ":3001"; then
    echo "⚠️  Port 3001 لا يزال مستخدم. محاولة إيقاف جميع عمليات node..."
    pkill -9 node 2>/dev/null
    sleep 2
fi

if ss -tulpn | grep -q ":3001"; then
    echo "❌ Port 3001 لا يزال مستخدم. يرجى التحقق يدوياً."
    ss -tulpn | grep ":3001"
    exit 1
else
    echo "✅ Port 3001 الآن متاح!"
fi


