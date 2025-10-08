#!/bin/bash

# API Test Script for Chakra
# This script tests all the API endpoints to verify they're working correctly

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# API base URL
API_BASE_URL="http://localhost:8000"
AUTH_TOKEN=""

echo -e "${BLUE}=== Chakra API Test Script ===${NC}"
echo "This script will test all the API endpoints to verify they're working correctly."
echo ""

# Function to show test result
test_result() {
  local status_code=$1
  local expected_code=$2
  local endpoint=$3
  
  if [ "$status_code" -eq "$expected_code" ]; then
    echo -e "${GREEN}✓ $endpoint - Status: $status_code (OK)${NC}"
    return 0
  else
    echo -e "${RED}✗ $endpoint - Status: $status_code (Expected: $expected_code)${NC}"
    return 1
  fi
}

# Test 1: Health Check
echo -e "\n${YELLOW}Testing Health Check:${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" $API_BASE_URL/health)
test_result $response 200 "GET /health"

# Test 2: Login to get auth token
echo -e "\n${YELLOW}Testing Authentication:${NC}"
echo "Enter username: "
read username
echo "Enter password: "
read -s password

login_response=$(curl -s -X POST "$API_BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$username\",\"password\":\"$password\"}")

if [[ $login_response == *"access_token"* ]]; then
  AUTH_TOKEN=$(echo $login_response | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
  echo -e "${GREEN}✓ Login successful - Auth token obtained${NC}"
else
  echo -e "${RED}✗ Login failed${NC}"
  echo "Response: $login_response"
  echo -e "${YELLOW}Continuing tests without authentication...${NC}"
fi

# Test 3: Templates API
echo -e "\n${YELLOW}Testing SLA Templates API:${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $AUTH_TOKEN" "$API_BASE_URL/api/templates")
test_result $response 200 "GET /api/templates"

# Test 4: Consultation Templates API
echo -e "\n${YELLOW}Testing Consultation Templates API:${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $AUTH_TOKEN" "$API_BASE_URL/api/consultation_templates/templates")
test_result $response 200 "GET /api/consultation_templates/templates"

# Test 5: Consultation API
echo -e "\n${YELLOW}Testing Consultation API:${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $AUTH_TOKEN" "$API_BASE_URL/api/consultation/chat")
test_result $response 405 "GET /api/consultation/chat (Expected 405 Method Not Allowed as this is a POST endpoint)"

# Test 6: Consultation Sessions API
echo -e "\n${YELLOW}Testing Consultation Sessions API:${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $AUTH_TOKEN" "$API_BASE_URL/api/consultation/sessions")
test_result $response 200 "GET /api/consultation/sessions"

# Optional: Fetch and display one full response to verify data format
echo -e "\n${YELLOW}Fetching a sample template:${NC}"
sample_response=$(curl -s -H "Authorization: Bearer $AUTH_TOKEN" "$API_BASE_URL/api/consultation_templates/templates?limit=1")
echo "$sample_response" | grep -o '"name":"[^"]*' | head -1 | sed 's/"name":"/Template name: /'

echo -e "\n${BLUE}=== Test Complete ===${NC}"
echo "Remember to use the correct endpoint path in your frontend code:"
echo -e "${GREEN}✓ Use: /api/consultation_templates/templates${NC}"
echo -e "${RED}✗ Not: /api/consultation/templates${NC}"