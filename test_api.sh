#!/bin/bash

# Comprehensive API testing script
# Tests the running API using curl

API_URL="${API_URL:-http://localhost:8000}"
echo "?? Testing PayQI API at $API_URL"
echo "=================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    echo -e "\n${YELLOW}Testing: $name${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint" -H "Authorization: Bearer $TOKEN" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "$data" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}? PASS${NC} - Status: $http_code"
        echo "Response: $body" | head -c 200
        ((PASSED++))
        return 0
    else
        echo -e "${RED}? FAIL${NC} - Expected: $expected_status, Got: $http_code"
        echo "Response: $body"
        ((FAILED++))
        return 1
    fi
}

# Health check
echo -e "\n${YELLOW}1. Health Check${NC}"
health=$(curl -s "$API_URL/health")
if echo "$health" | grep -q "ok"; then
    echo -e "${GREEN}? API is running${NC}"
    ((PASSED++))
else
    echo -e "${RED}? API health check failed${NC}"
    echo "Response: $health"
    ((FAILED++))
    exit 1
fi

# Register a test merchant
echo -e "\n${YELLOW}2. Register Merchant${NC}"
register_data='{"email":"test'$(date +%s)'@example.com","password":"testpass123"}'
register_response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/register" \
    -H "Content-Type: application/json" \
    -d "$register_data")

http_code=$(echo "$register_response" | tail -n1)
body=$(echo "$register_response" | sed '$d')

if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}? Registration successful${NC}"
    EMAIL=$(echo "$body" | grep -o '"email":"[^"]*' | cut -d'"' -f4)
    ((PASSED++))
else
    echo -e "${RED}? Registration failed${NC}"
    echo "Response: $body"
    ((FAILED++))
    exit 1
fi

# Login
echo -e "\n${YELLOW}3. Login${NC}"
login_data='{"email":"'$EMAIL'","password":"testpass123"}'
login_response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/login" \
    -H "Content-Type: application/json" \
    -d "$login_data")

http_code=$(echo "$login_response" | tail -n1)
body=$(echo "$login_response" | sed '$d')

if [ "$http_code" = "200" ]; then
    TOKEN=$(echo "$body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}? Login successful${NC}"
    echo "Token: ${TOKEN:0:20}..."
    ((PASSED++))
else
    echo -e "${RED}? Login failed${NC}"
    echo "Response: $body"
    ((FAILED++))
    exit 1
fi

# Test authenticated endpoints
test_endpoint "Get Current Merchant" "GET" "/api/me" "" "200"
test_endpoint "Create XRP Payment" "POST" "/api/payments" '{"amount":10.00,"currency":"XRP"}' "201"

# Get payment ID from previous response
if [ -n "$body" ]; then
    PAYMENT_ID=$(echo "$body" | grep -o '"payment_id":[0-9]*' | cut -d':' -f2)
    if [ -n "$PAYMENT_ID" ]; then
        test_endpoint "Get Payment" "GET" "/api/payments/$PAYMENT_ID" "" "200"
    fi
fi

test_endpoint "Get Transactions" "GET" "/api/transactions" "" "200"

# Test error cases
echo -e "\n${YELLOW}Testing Error Cases${NC}"
test_endpoint "Get Payment (Unauthorized)" "GET" "/api/payments/1" "" "401" || TOKEN=""
test_endpoint "Create Payment (Unauthorized)" "POST" "/api/payments" '{"amount":10,"currency":"XRP"}' "401"

# Summary
echo -e "\n=================================="
echo -e "${YELLOW}Test Summary${NC}"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "=================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}? All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}? Some tests failed${NC}"
    exit 1
fi
