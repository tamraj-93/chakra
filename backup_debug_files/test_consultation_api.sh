#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     CONSULTATION API TEST                      ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if the backend server is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}Error: Backend server is not running at http://localhost:8000${NC}"
    echo -e "${YELLOW}Please start the backend server first.${NC}"
    exit 1
fi

# Test credentials
TEST_EMAIL="admin@example.com"
TEST_PASSWORD="password"

# Login and get token
echo -e "${YELLOW}Authenticating with test credentials...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

# Check if login failed
if [[ "$RESPONSE" == *"detail"* && "$RESPONSE" == *"Invalid"* ]]; then
    echo -e "${RED}✗ Authentication failed${NC}"
    echo "$RESPONSE"
    exit 1
fi

# Extract token
TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\([^"]*\)"/\1/')

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Failed to extract token${NC}"
    echo "$RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Authentication successful${NC}"

# Test the consultation chat endpoint
echo -e "\n${YELLOW}Testing consultation chat endpoint with verbose output...${NC}"

echo -e "${BLUE}Request details:${NC}"
echo "URL: http://localhost:8000/api/consultation/chat"
echo "Headers: Authorization: Bearer [TOKEN], Content-Type: application/json"
echo "Payload: {\"content\":\"What is an SLA?\",\"role\":\"user\"}"

echo -e "\n${YELLOW}Response:${NC}"
curl -v -X POST http://localhost:8000/api/consultation/chat \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"content\":\"What is an SLA?\",\"role\":\"user\"}"

echo -e "\n\n${BLUE}=================================================${NC}"
echo -e "${BLUE}     TEST COMPLETE                               ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "Check the output above to see if there are any errors in the API call."
echo -e "Look for a 200 OK response and check the content of the response for proper functioning."
echo -e "${BLUE}=================================================${NC}"