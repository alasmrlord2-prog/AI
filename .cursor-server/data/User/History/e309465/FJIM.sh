#!/bin/bash
# Stop Backend Script
set -e

echo "🛑 Stopping Backend..."
docker-compose stop backend

echo "✅ Backend stopped!"
