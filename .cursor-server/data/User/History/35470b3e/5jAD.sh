#!/bin/bash

# ============================================
# AI Agent - Fix Issues Script
# ============================================
# This script fixes common issues:
# 1. Removes orphan containers
# 2. Rebuilds services
# 3. Fixes docker-compose issues
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🔧 Fixing Issues..."
echo "========================================"
echo ""

cd "$PROJECT_DIR" || {
    echo "❌ Error: Cannot access project directory: $PROJECT_DIR"
    exit 1
}

# Step 1: Stop all containers
echo "⏹️  Step 1: Stopping all containers..."
docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true

# Step 2: Remove orphan containers manually
echo ""
echo "🧹 Step 2: Removing orphan containers..."
docker ps -a | grep -E "agent-core|alertmanager" | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true

# Step 3: Remove old postgres container if exists
echo ""
echo "🧹 Step 3: Cleaning up old postgres container..."
docker ps -a | grep "3d28ce0e23e1_ai-agent-postgres" | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true

# Step 4: Rebuild images
echo ""
echo "🔨 Step 4: Rebuilding images..."
docker-compose -f "$COMPOSE_FILE" build --no-cache backend frontend 2>&1 | tail -20

echo ""
echo "✅ Fix complete!"
echo "========================================"
echo ""
echo "💡 Now you can run:"
echo "   ./start_backend.sh"
echo "   ./start_frontend.sh"
echo "   ./start_nginx.sh"
echo ""

