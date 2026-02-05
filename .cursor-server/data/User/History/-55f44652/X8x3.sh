#!/bin/bash
# Create Database Tables - Run this manually

echo "🔧 Creating database tables..."
echo ""
echo "Run this command:"
echo ""
echo "docker compose exec backend python3 << 'PYTHON_SCRIPT'"
echo "from app.core.database import Base, engine"
echo "from app.identity.models import *"
echo "from app.subscription.models import *"
echo "from app.audit.models import *"
echo "from app.access.models import *"
echo "from app.policy.models import *"
echo ""
echo "Base.metadata.create_all(engine)"
echo "print('✅ All tables created successfully')"
echo "PYTHON_SCRIPT"
echo ""

