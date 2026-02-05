#!/bin/bash
# Restart Frontend Script
# Note: If you encounter issues, use ./restart-fixed.sh instead
set -e

echo "🔄 Restarting Frontend..."
echo "⚠️  If you encounter errors, try: ./restart-fixed.sh"

# Try to restart
if docker-compose restart frontend 2>/dev/null; then
    echo "✅ Frontend restarted!"
else
    echo "⚠️  Restart failed. Trying stop and start..."
    docker-compose stop frontend 2>/dev/null || true
    sleep 2
    docker-compose up -d frontend
    echo "✅ Frontend restarted!"
fi

echo "📝 View logs: docker-compose logs -f frontend"
