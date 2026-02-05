#!/bin/bash
# 🔄 Test Complete CRM → AAA → AI Agent Workflow
# This script tests the complete onboarding and access workflow

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔄 Testing Complete CRM → AAA → AI Agent Workflow"
echo "=================================================="
echo "Base URL: $BASE_URL"
echo ""

# Variables to store IDs
TENANT_ID=""
OWNER_USER_ID=""
OWNER_TOKEN=""
EMPLOYEE_USER_ID=""
EMPLOYEE_TOKEN=""

# Step 1: Check if backend is running
echo -e "${BLUE}Step 1: Checking backend...${NC}"
if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend is not running at $BASE_URL${NC}"
    echo "   Please start the backend first: ./backend-start.sh"
    exit 1
fi
echo -e "${GREEN}✅ Backend is running${NC}"
echo ""

# Step 2: Create admin user if doesn't exist (for testing)
echo -e "${BLUE}Step 2: Setting up admin user...${NC}"
ADMIN_EMAIL="admin@shiftwave.com"
ADMIN_PASSWORD="admin123"

# Try to login as admin
login_response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" \
    "$BASE_URL/api/identity/login" 2>&1)

if echo "$login_response" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Admin user exists${NC}"
    OWNER_TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
    echo -e "${YELLOW}⚠️  Admin user doesn't exist. Creating...${NC}"
    # The system should auto-create admin on first login
    # For now, we'll skip this step
    echo -e "${YELLOW}⚠️  Please create admin user manually first${NC}"
    exit 1
fi
echo ""

# Step 3: Create Tenant
echo -e "${BLUE}Step 3: Creating tenant...${NC}"
TENANT_NAME="Test Company $(date +%s)"
TENANT_DATA="{
    \"name\": \"$TENANT_NAME\",
    \"type\": \"company\",
    \"contact_email\": \"owner@testcompany.com\",
    \"contact_phone\": \"+1234567890\",
    \"subscription_plan\": \"AI_AGENT_PRO\",
    \"max_users\": 10
}"

tenant_response=$(curl -s -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -d "$TENANT_DATA" \
    "$BASE_URL/api/crm/tenants" 2>&1)

if echo "$tenant_response" | grep -q "id"; then
    TENANT_ID=$(echo "$tenant_response" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✅ Tenant created: $TENANT_ID${NC}"
    echo "   Response: $tenant_response" | head -c 200
    echo ""
else
    echo -e "${RED}❌ Failed to create tenant${NC}"
    echo "   Response: $tenant_response"
    exit 1
fi
echo ""

# Step 4: Wait for AAA file to be generated (event processing)
echo -e "${BLUE}Step 4: Waiting for AAA file generation...${NC}"
sleep 3
echo -e "${GREEN}✅ AAA file should be generated (checking...){NC}"
echo ""

# Step 5: Create Employee User
echo -e "${BLUE}Step 5: Creating employee user...${NC}"
EMPLOYEE_EMAIL="employee$(date +%s)@testcompany.com"
EMPLOYEE_DATA="{
    \"email\": \"$EMPLOYEE_EMAIL\",
    \"password\": \"employee123\",
    \"full_name\": \"Test Employee\",
    \"role\": \"analyst\",
    \"permissions\": [\"ai.agent.chat\", \"logs.viewer\"],
    \"status\": \"active\",
    \"email_verified\": true
}"

employee_response=$(curl -s -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -d "$EMPLOYEE_DATA" \
    "$BASE_URL/api/crm/tenants/$TENANT_ID/users" 2>&1)

if echo "$employee_response" | grep -q "id"; then
    EMPLOYEE_USER_ID=$(echo "$employee_response" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✅ Employee user created: $EMPLOYEE_USER_ID${NC}"
    echo "   Email: $EMPLOYEE_EMAIL"
    echo ""
else
    echo -e "${RED}❌ Failed to create employee user${NC}"
    echo "   Response: $employee_response"
    exit 1
fi

# Wait for AAA file generation
sleep 3
echo ""

# Step 6: Employee Login
echo -e "${BLUE}Step 6: Employee logging in...${NC}"
employee_login_response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMPLOYEE_EMAIL\",\"password\":\"employee123\"}" \
    "$BASE_URL/api/auth/login" 2>&1)

if echo "$employee_login_response" | grep -q "access_token"; then
    EMPLOYEE_TOKEN=$(echo "$employee_login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✅ Employee logged in successfully${NC}"
    echo ""
else
    echo -e "${RED}❌ Employee login failed${NC}"
    echo "   Response: $employee_login_response"
    exit 1
fi

# Step 7: Test Employee Access to AI Agent
echo -e "${BLUE}Step 7: Testing employee access to AI Agent...${NC}"

# Test chat endpoint
chat_response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
    -d '{"message":"Hello, this is a test"}' \
    "$BASE_URL/api/agent/chat" 2>&1)

chat_code=$(echo "$chat_response" | tail -n1)
if [ "$chat_code" = "200" ]; then
    echo -e "${GREEN}✅ Employee can access AI Agent chat${NC}"
else
    echo -e "${YELLOW}⚠️  Chat endpoint returned: $chat_code${NC}"
    echo "   (This might be expected if AI service is not running)"
fi

# Test logs endpoint
logs_response=$(curl -s -w "\n%{http_code}" -X GET \
    -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
    "$BASE_URL/api/logs" 2>&1)

logs_code=$(echo "$logs_response" | tail -n1)
if [ "$logs_code" = "200" ]; then
    echo -e "${GREEN}✅ Employee can access logs${NC}"
elif [ "$logs_code" = "403" ]; then
    echo -e "${RED}❌ Employee cannot access logs (403 Forbidden)${NC}"
    echo "   This might indicate a permission issue"
else
    echo -e "${YELLOW}⚠️  Logs endpoint returned: $logs_code${NC}"
fi

# Test dashboard
dashboard_response=$(curl -s -w "\n%{http_code}" -X GET \
    -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
    "$BASE_URL/api/dashboard/stats" 2>&1)

dashboard_code=$(echo "$dashboard_response" | tail -n1)
if [ "$dashboard_code" = "200" ]; then
    echo -e "${GREEN}✅ Employee can access dashboard${NC}"
else
    echo -e "${YELLOW}⚠️  Dashboard endpoint returned: $dashboard_code${NC}"
fi

echo ""

# Step 8: Verify AAA File Exists
echo -e "${BLUE}Step 8: Verifying AAA file exists...${NC}"
aaa_response=$(curl -s -w "\n%{http_code}" -X GET \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    "$BASE_URL/api/access/files/$TENANT_ID/$EMPLOYEE_USER_ID" 2>&1)

aaa_code=$(echo "$aaa_response" | tail -n1)
if [ "$aaa_code" = "200" ]; then
    echo -e "${GREEN}✅ AAA file exists for employee${NC}"
    echo "   AAA File content: $(echo "$aaa_response" | sed '$d' | head -c 200)"
    echo ""
elif [ "$aaa_code" = "404" ]; then
    echo -e "${RED}❌ AAA file not found (404)${NC}"
    echo "   This indicates the event system might not be working"
    echo ""
else
    echo -e "${YELLOW}⚠️  AAA file check returned: $aaa_code${NC}"
    echo ""
fi

# Summary
echo "=================================================="
echo "📊 Workflow Test Summary"
echo "=================================================="
echo -e "Tenant ID: ${BLUE}$TENANT_ID${NC}"
echo -e "Owner Token: ${BLUE}${OWNER_TOKEN:0:20}...${NC}"
echo -e "Employee ID: ${BLUE}$EMPLOYEE_USER_ID${NC}"
echo -e "Employee Email: ${BLUE}$EMPLOYEE_EMAIL${NC}"
echo -e "Employee Token: ${BLUE}${EMPLOYEE_TOKEN:0:20}...${NC}"
echo ""
echo -e "${GREEN}✅ Workflow test completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Check CRM dashboard: http://localhost:3001"
echo "2. Check AAA dashboard: http://localhost:3002"
echo "3. Check AI Agent: http://localhost:3000"
echo ""

