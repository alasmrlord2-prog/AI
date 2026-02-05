#!/bin/bash
# Stop Frontend Service (Docker)

set -e

cd "$(dirname "$0")"

echo "🛑 Stopping Frontend Service..."

# Stop frontend service
docker-compose stop frontend

echo "✅ Frontend service stopped!"

