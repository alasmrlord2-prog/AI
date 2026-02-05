#!/bin/bash
# Restart Backend Script
# Note: If you encounter issues, use ./restart-fixed.sh instead
set -e

echo "🔄 Restarting Backend..."
echo "⚠️  If you encounter errors, try: ./restart-fixed.sh"

# Try to restart
if docker-compose restart backend 2>/dev/null; then
    echo "✅ Backend restarted!"
else
    echo "⚠️  Restart failed. Trying stop and start..."
    docker-compose stop backend 2>/dev/null || true
    sleep 2
    docker-compose up -d backend
    echo "✅ Backend restarted!"
fi

echo "📝 View logs: docker-compose logs -f backend"
