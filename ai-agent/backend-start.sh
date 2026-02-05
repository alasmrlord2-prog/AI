#!/bin/bash
# Start Backend Services (PostgreSQL, Redis, Ollama, Backend API)

set -e

cd "$(dirname "$0")"

echo "🚀 Starting Backend Services..."

# Clean up old containers
echo "🧹 Cleaning up old containers..."
docker rm -f ai-backend ai-agent-postgres ai-agent-redis ai-agent-ollama 2>/dev/null || true

# Free up ports
echo "🔌 Freeing up ports..."
for port in 8000 5432 6379 11434; do
    PIDS=$(lsof -ti:${port} 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null || true
    fi
done
sleep 2

# Start infrastructure services first
echo "📦 Starting infrastructure services (PostgreSQL, Redis)..."
docker compose up -d postgres redis

echo "⏳ Waiting for PostgreSQL and Redis to be ready..."
sleep 5

# Check PostgreSQL
for i in {1..15}; do
    if docker compose exec -T postgres pg_isready -U aiagent > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    sleep 2
done

# Check Redis
for i in {1..10}; do
    if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is ready"
        break
    fi
    sleep 1
done

# Run migrations
echo "🔄 Running database migrations..."
docker compose exec -T backend bash -c "cd /app && export DATABASE_URL='postgresql://aiagent:aiagent123@postgres:5432/ai_agent_db' && python3 -m alembic upgrade head" 2>/dev/null || echo "⚠️  Migrations skipped or already applied"

# Start Ollama and Backend
echo "🚀 Starting Ollama and Backend API..."
docker compose up -d ollama backend

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check backend health
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running!"
        echo "   API: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend started but not responding yet."
        echo "   Check logs: docker compose logs backend"
    else
        sleep 2
    fi
done

echo ""
echo "📊 Backend Services Status:"
docker compose ps postgres redis backend ollama

echo ""
echo "📝 View logs: docker compose logs -f backend"
