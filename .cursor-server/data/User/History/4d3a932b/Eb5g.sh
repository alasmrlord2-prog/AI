#!/bin/bash
# 🔍 Test All Endpoints - CRM, AAA, AI Agent
# This script tests all endpoints to ensure they're working correctly

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Testing All Endpoints"
echo "========================"
echo "Base URL: $BASE_URL"
echo ""

# Counters
PASSED=0
FAILED=0
SKIPPED=0

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    local expected_status=${5:-200}
    local token=${6:-""}
    
    local url="$BASE_URL$endpoint"
    local headers="Content-Type: application/json"
    
    if [ -n "$token" ]; then
        headers="$headers\nAuthorization: Bearer $token"
    fi
    
    echo -n "Testing: $description ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -H "Content-Type: application/json" ${token:+-H "Authorization: Bearer $token"} "$url" 2>&1)
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" ${token:+-H "Authorization: Bearer $token"} -d "$data" "$url" 2>&1)
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT -H "Content-Type: application/json" ${token:+-H "Authorization: Bearer $token"} -d "$data" "$url" 2>&1)
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE -H "Content-Type: application/json" ${token:+-H "Authorization: Bearer $token"} "$url" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (Status: $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $http_code)"
        echo "   Response: $body" | head -c 200
        echo ""
        ((FAILED++))
        return 1
    fi
}

# Check if backend is running
echo "🔍 Checking if backend is running..."
if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend is not running at $BASE_URL${NC}"
    echo "   Please start the backend first: ./backend-start.sh"
    exit 1
fi
echo -e "${GREEN}✅ Backend is running${NC}"
echo ""

# ==================== Health Check ====================
echo "📊 Health Check"
echo "---------------"
test_endpoint "GET" "/health" "Health check"
echo ""

# ==================== Authentication ====================
echo "🔐 Authentication Endpoints"
echo "---------------------------"

# Try to login (might fail if no users exist, that's OK)
echo -n "Testing: Login endpoint exists ... "
login_response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"test123"}' \
    "$BASE_URL/api/auth/login" 2>&1)
login_code=$(echo "$login_response" | tail -n1)
if [ "$login_code" = "200" ] || [ "$login_code" = "401" ] || [ "$login_code" = "422" ]; then
    echo -e "${GREEN}✅ PASS${NC} (Status: $login_code)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Status: $login_code)"
    ((FAILED++))
fi

test_endpoint "GET" "/api/auth/me" "Get current user" "" "200" ""
test_endpoint "GET" "/api/auth/roles" "Get available roles"
echo ""

# ==================== CRM Endpoints ====================
echo "📊 CRM Endpoints"
echo "----------------"

# Note: Most CRM endpoints require authentication
# We'll test that they exist (return 401/403 if not authenticated, which is expected)
test_endpoint "GET" "/api/crm/tenants" "List tenants" "" "401" ""
test_endpoint "GET" "/api/crm/tenants/00000000-0000-0000-0000-000000000000/dashboard" "Get tenant dashboard" "" "401" ""
test_endpoint "GET" "/api/crm/tenants/00000000-0000-0000-0000-000000000000/users" "Get tenant users" "" "401" ""
echo ""

# ==================== Identity/AAA Endpoints ====================
echo "🔐 Identity/AAA Endpoints"
echo "-------------------------"

test_endpoint "POST" "/api/identity/login" "Identity login" '{"email":"test@example.com","password":"test123"}' "200" ""
test_endpoint "GET" "/api/identity/users" "List users" "" "401" ""
test_endpoint "GET" "/api/identity/tenants" "List tenants" "" "401" ""
echo ""

# ==================== Access/AAA Endpoints ====================
echo "🔒 Access/AAA Endpoints"
echo "----------------------"

test_endpoint "GET" "/api/access/permissions" "Get permissions" "" "401" ""
test_endpoint "POST" "/api/access/permissions/check" "Check permission" '{"permission":"test"}' "401" ""
echo ""

# ==================== Policy Endpoints ====================
echo "📋 Policy Endpoints"
echo "-------------------"

test_endpoint "GET" "/api/policy/policies" "List policies" "" "401" ""
test_endpoint "GET" "/api/policy/policies/00000000-0000-0000-0000-000000000000" "Get policy" "" "401" ""
echo ""

# ==================== Subscription Endpoints ====================
echo "💳 Subscription Endpoints"
echo "--------------------------"

test_endpoint "GET" "/api/subscription/subscriptions" "List subscriptions" "" "401" ""
test_endpoint "GET" "/api/subscription/subscriptions/00000000-0000-0000-0000-000000000000" "Get subscription" "" "401" ""
echo ""

# ==================== AI Agent Endpoints ====================
echo "🤖 AI Agent Endpoints"
echo "---------------------"

test_endpoint "POST" "/api/agent/chat" "AI Agent chat" '{"message":"test"}' "401" ""
test_endpoint "GET" "/api/agent/capabilities" "Get agent capabilities"
test_endpoint "GET" "/api/capabilities" "Get capabilities"
echo ""

# ==================== Dashboard Endpoints ====================
echo "📊 Dashboard Endpoints"
echo "----------------------"

test_endpoint "GET" "/api/dashboard/stats" "Get dashboard stats" "" "200" ""
echo ""

# ==================== Other Service Endpoints ====================
echo "🔧 Other Service Endpoints"
echo "--------------------------"

test_endpoint "GET" "/api/logs" "Get logs" "" "401" ""
test_endpoint "GET" "/api/monitoring" "Get monitoring" "" "401" ""
test_endpoint "GET" "/api/audit/logs" "Get audit logs" "" "401" ""
echo ""

# ==================== Summary ====================
echo "========================"
echo "📊 Test Summary"
echo "========================"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo -e "${YELLOW}⏭️  Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please check the output above.${NC}"
    exit 1
fi

