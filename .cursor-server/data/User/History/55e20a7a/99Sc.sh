#!/bin/bash
# Start Backend directly without Docker (alternative method)
set -e

cd "$(dirname "$0")"

echo "🚀 Starting Backend directly (without Docker)..."
echo "⚠️  This requires Python and dependencies to be installed"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if PostgreSQL is accessible
echo "🔍 Checking database connection..."
if python3 -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://aiagent:aiagent123@localhost:5432/ai_agent_db'
try:
    from sqlalchemy import create_engine
    engine = create_engine(os.environ['DATABASE_URL'])
    conn = engine.connect()
    conn.close()
    print('✅ Database connection OK')
except Exception as e:
    print(f'⚠️  Database connection failed: {e}')
    print('   Continuing anyway...')
" 2>/dev/null; then
    echo ""
fi

# Set environment variables
export DATABASE_URL=${DATABASE_URL:-"postgresql://aiagent:aiagent123@localhost:5432/ai_agent_db"}
export DEBUG=true
export LOG_LEVEL=INFO
export CORS_ORIGINS='["*"]'
export SECRET_KEY=${SECRET_KEY:-"your-secret-key-change-in-production"}

# Check if port is available
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use!"
    echo "   Killing existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start backend
echo "🚀 Starting Backend on port 8000..."
echo ""
echo "📝 Backend will be available at: http://localhost:8000"
echo "📝 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

