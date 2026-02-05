# Migration Guide - Running Database Migrations

## Prerequisites

1. **Install Dependencies**
   ```bash
   cd backend
   pip3 install -r requirements.txt
   # Or specifically:
   pip3 install psycopg2-binary alembic sqlalchemy
   ```

2. **Set Environment Variables**
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env and set DATABASE_URL
   # Format: postgresql://username:password@host:port/database
   DATABASE_URL=postgresql://aiagent:aiagent123@postgres:5432/ai_agent_db
   ```

## Running Migrations

### Option 1: Using Docker (Recommended)

If you're using Docker Compose:

```bash
# Start services
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
sleep 10

# Run migrations inside backend container
docker-compose exec backend alembic upgrade head

# Or run from host (if alembic is installed)
cd backend
export $(cat ../.env | xargs)  # Load .env variables
alembic upgrade head
```

### Option 2: Direct Connection

If running migrations from host machine:

```bash
cd backend

# Load environment variables
export $(cat ../.env | xargs)

# Or set directly:
export DATABASE_URL="postgresql://aiagent:aiagent123@localhost:5432/ai_agent_db"

# Run migrations
alembic upgrade head
```

### Option 3: Using Python Script

```bash
cd backend
python3 << EOF
import os
from app.core.config import get_settings
from alembic.config import Config
from alembic import command

# Load settings
settings = get_settings()

# Configure Alembic
alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Run migrations
command.upgrade(alembic_cfg, "head")
EOF
```

## Troubleshooting

### Error: "psycopg2 not installed"

**Solution:**
```bash
pip3 install psycopg2-binary
# Or
pip3 install --user psycopg2-binary
```

### Error: "Connection refused" or "Database not found"

**Check:**
1. PostgreSQL is running: `docker-compose ps postgres`
2. Database exists: `docker-compose exec postgres psql -U aiagent -d ai_agent_db -c "SELECT 1;"`
3. Connection string is correct in `.env`

**Create database if missing:**
```bash
docker-compose exec postgres psql -U aiagent -c "CREATE DATABASE ai_agent_db;"
```

### Error: "No such revision"

**Solution:**
```bash
# Check current revision
alembic current

# If no revision, stamp to base
alembic stamp head

# Or create initial migration
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Error: "Table already exists"

**Solution:**
```bash
# Check what migrations are applied
alembic current

# If tables exist but migrations not tracked:
alembic stamp head

# Or manually mark as applied:
alembic stamp 001_add_indexes
```

## Available Migrations

1. **001_add_indexes_and_optimizations.py**
   - Adds indexes for performance
   - Indexes on: users, tenants, sessions, audit_logs, tokens

2. **002_add_sessions_table.py**
   - Creates sessions table
   - For session management and refresh tokens

## Verifying Migrations

```bash
# Check current revision
alembic current

# View migration history
alembic history

# Check database tables
docker-compose exec postgres psql -U aiagent -d ai_agent_db -c "\dt"
```

## Rolling Back

If you need to rollback:

```bash
# Rollback one revision
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 001_add_indexes

# Rollback all
alembic downgrade base
```

## Production Deployment

For production:

1. **Backup database first**
   ```bash
   docker-compose exec postgres pg_dump -U aiagent ai_agent_db > backup.sql
   ```

2. **Run migrations**
   ```bash
   alembic upgrade head
   ```

3. **Verify**
   ```bash
   alembic current
   ```

4. **Monitor logs**
   ```bash
   docker-compose logs backend | grep -i migration
   ```

