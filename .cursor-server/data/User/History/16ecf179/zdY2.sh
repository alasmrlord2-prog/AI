#!/bin/bash
# Simple script to create database tables

echo "🔧 Creating database tables..."
echo ""
echo "Run this command:"
echo ""
echo "docker compose exec -T backend python3 -c \""
echo "from app.core.database import Base, engine"
echo "from app.identity.models import *"
echo "from app.subscription.models import *"
echo "from app.audit.models import *"
echo "from app.access.models import *"
echo "from app.policy.models import *"
echo "Base.metadata.create_all(engine)"
echo "print('✅ All tables created successfully')"
echo "\""
echo ""

