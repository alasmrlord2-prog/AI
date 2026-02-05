#!/bin/bash
# Stop Backend Services (Docker)

set -e

cd "$(dirname "$0")"

echo "🛑 Stopping Backend Services..."

# Stop backend, postgres, and ollama
docker compose stop backend postgres ollama

echo "✅ Backend services stopped!"

