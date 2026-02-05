#!/bin/bash
# Start Frontend Script
set -e

echo "🚀 Starting Frontend..."
docker-compose up -d frontend

echo "⏳ Waiting for frontend to be ready..."
sleep 5

echo "✅ Frontend is running!"
echo "   URL: http://localhost:3000"
echo ""
echo "📝 View logs: docker-compose logs -f frontend"
