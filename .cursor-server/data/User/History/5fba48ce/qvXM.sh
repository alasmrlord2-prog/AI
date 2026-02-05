#!/bin/bash
# Start All Services (Backend + Frontend)

set -e

cd "$(dirname "$0")"

echo "🚀 Starting All Services..."

# Clean up old containers first
./clean-containers.sh

echo ""
echo "---"

# Start backend first
./backend-start.sh

echo ""
echo "---"

# Then start frontend
./frontend-start.sh

echo ""
echo "✅ All services started!"
echo ""
echo "🔗 Access URLs:"
echo "   - Dashboard: http://ai-agent.bankid-sy.com (port 3000)"
echo "   - CRM: http://crm.bankid-sy.com/crm/login (port 3001)"
echo "   - AAA: http://aaa.bankid-sy.com/aaa/login (port 3002)"
echo "   - Backend API: http://localhost:8000/docs"

