#!/bin/bash
# Stop Frontend Services (Docker)

set -e

cd "$(dirname "$0")"

echo "🛑 Stopping Frontend Services..."

# Stop all frontend services
docker-compose stop frontend-ai-agent frontend-crm frontend-aaa

echo "✅ Frontend services stopped!"

