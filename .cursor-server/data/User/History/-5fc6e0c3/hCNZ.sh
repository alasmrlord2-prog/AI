#!/bin/bash
# Start Backend Script
set -e

echo "🚀 Starting Backend..."
docker-compose up -d backend postgres

echo "⏳ Waiting for services to be ready..."
sleep 5

echo "✅ Backend is running!"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "📝 View logs: docker-compose logs -f backend"
