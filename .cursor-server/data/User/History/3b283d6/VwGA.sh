#!/bin/bash
# Start Frontend Script - Fixed version with error handling
set -e

cd "$(dirname "$0")"

PORT=${1:-3000}
SERVICE_NAME=${2:-"frontend"}

echo "🚀 Starting Frontend on port $PORT..."

# Check if port is in use
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use!"
    echo "   Checking for existing containers..."
    
    # Try to stop existing containers
    docker-compose down 2>/dev/null || true
    docker stop ai-agent-frontend ai-agent-frontend-prod 2>/dev/null || true
    
    # Wait a bit
    sleep 2
    
    # Check again
    if lsof -i :$PORT > /dev/null 2>&1; then
        echo "❌ Port $PORT is still in use. Please stop the process manually:"
        echo "   lsof -i :$PORT"
        echo "   kill -9 <PID>"
        exit 1
    fi
fi

# Clean up orphaned containers
echo "🧹 Cleaning up orphaned containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Remove problematic containers if they exist
echo "🧹 Removing problematic containers..."
docker rm -f ai-agent-frontend 2>/dev/null || true
docker rm -f ai-agent-frontend-prod 2>/dev/null || true

# Wait a bit
sleep 2

# Start service
echo "🚀 Starting service..."
if docker-compose up -d $SERVICE_NAME; then
    echo "⏳ Waiting for service to be ready..."
    sleep 5
    
    # Check if frontend is responding
    if curl -s http://localhost:$PORT > /dev/null 2>&1; then
        echo "✅ Frontend is running on port $PORT!"
        echo "   URL: http://localhost:$PORT"
    else
        echo "⚠️  Frontend started but not responding yet. Check logs:"
        echo "   docker-compose logs -f $SERVICE_NAME"
    fi
else
    echo "❌ Failed to start service. Check logs:"
    echo "   docker-compose logs $SERVICE_NAME"
    exit 1
fi

echo ""
echo "📝 View logs: docker-compose logs -f $SERVICE_NAME"

