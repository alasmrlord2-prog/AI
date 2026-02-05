#!/bin/bash
# Stop Frontend Script
set -e

echo "🛑 Stopping Frontend..."
docker-compose stop frontend

echo "✅ Frontend stopped!"
