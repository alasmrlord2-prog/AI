#!/bin/bash
# Stop Backend Script
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🛑 Stopping Backend..."

# Try with docker-compose first, fallback to docker compose
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" stop ollama backend postgres
else
    docker compose -f "$PROJECT_ROOT/docker-compose.yml" stop ollama backend postgres
fi

echo "✅ Backend stopped!"
