#!/bin/bash
# Stop Backend Script
set -e

cd "$(dirname "$0")"

echo "🛑 Stopping Backend..."
docker-compose stop ollama backend postgres

echo "✅ Backend stopped!"
