#!/bin/bash
# Start Backend Script - Fixed version with error handling
set -e

cd "$(dirname "$0")"

echo "🚀 Starting Backend..."

# Check if ports are in use
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use!"
    echo "   Checking for existing containers..."
    
    # Try to stop existing containers
    docker-compose down 2>/dev/null || true
    docker stop ai-agent-backend ai-agent-backend-prod 2>/dev/null || true
    
    # Wait a bit
    sleep 2
    
    # Check again
    if lsof -i :8000 > /dev/null 2>&1; then
        echo "❌ Port 8000 is still in use. Please stop the process manually:"
        echo "   lsof -i :8000"
        echo "   kill -9 <PID>"
        exit 1
    fi
fi

# Check if postgres port is in use
if lsof -i :5432 > /dev/null 2>&1; then
    echo "⚠️  Port 5432 (PostgreSQL) is already in use!"
    echo "   This might be an existing PostgreSQL instance."
    echo "   Continuing anyway..."
fi

# Clean up orphaned containers
echo "🧹 Cleaning up orphaned containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Remove problematic containers if they exist
echo "🧹 Removing problematic containers..."
docker rm -f ai-agent-postgres 2>/dev/null || true
docker rm -f ai-agent-backend 2>/dev/null || true
docker rm -f ai-agent-backend-prod 2>/dev/null || true

# Wait a bit
sleep 2

# Start services
echo "🚀 Starting services..."
if docker-compose up -d backend postgres; then
    echo "⏳ Waiting for services to be ready..."
    sleep 5
    
    # Check if backend is responding
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running!"
        echo "   API: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
    else
        echo "⚠️  Backend started but not responding yet. Check logs:"
        echo "   docker-compose logs -f backend"
    fi
else
    echo "❌ Failed to start services. Trying to fix..."
    
    # Try removing volumes and starting fresh
    echo "🧹 Removing old volumes..."
    docker-compose down -v 2>/dev/null || true
    docker volume prune -f 2>/dev/null || true
    
    echo "🔄 Retrying..."
    docker-compose up -d backend postgres
    
    sleep 5
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running!"
    else
        echo "❌ Still having issues. Check logs:"
        echo "   docker-compose logs backend"
        exit 1
    fi
fi

echo ""
echo "📝 View logs: docker-compose logs -f backend"

