#!/bin/bash
# Run this script to create database tables

docker compose exec -T backend python3 -c "from app.core.database import Base, engine; from app.identity.models import *; from app.subscription.models import *; from app.audit.models import *; from app.access.models import *; from app.policy.models import *; Base.metadata.create_all(engine); print('✅ All tables created successfully')"

