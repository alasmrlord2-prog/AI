#!/bin/bash
# Restart Backend Script
set -e

echo "🔄 Restarting Backend..."
docker-compose restart backend

echo "✅ Backend restarted!"
echo "📝 View logs: docker-compose logs -f backend"
