#!/bin/bash
# Restart Frontend Script
set -e

echo "🔄 Restarting Frontend..."
docker-compose restart frontend

echo "✅ Frontend restarted!"
echo "📝 View logs: docker-compose logs -f frontend"
