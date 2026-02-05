#!/bin/bash
# Script to run database migrations

set -e

echo "🔄 Running database migrations..."

# Load environment variables
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Set DATABASE_URL if not set
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="postgresql://aiagent:aiagent123@postgres:5432/ai_agent_db"
fi

echo "📊 Database URL: ${DATABASE_URL:0:50}..."

# Run migrations
cd /home/ai/ai-agent/backend || cd /app
python3 -m alembic upgrade head

echo "✅ Migrations completed successfully!"

