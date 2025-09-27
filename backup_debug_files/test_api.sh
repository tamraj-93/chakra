#!/bin/bash

# Script to test API connectivity for the Chakra application

# Set colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}====================================${NC}"
echo -e "${YELLOW}   CHAKRA API CONNECTIVITY TEST     ${NC}"
echo -e "${YELLOW}====================================${NC}"

# Base URL for the backend
API_URL="http://localhost:8000"

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: curl is not installed. Please install curl to run this test.${NC}"
    exit 1
fi

# Test API health endpoint
echo -e "\n${YELLOW}Testing API health...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)
if [ "$HEALTH_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ API is up and running! (Status: $HEALTH_RESPONSE)${NC}"
else
    echo -e "${RED}✗ API is not responding properly. (Status: $HEALTH_RESPONSE)${NC}"
    echo -e "${RED}  Make sure the backend server is running on port 8000.${NC}"
fi

# Test API docs endpoint
echo -e "\n${YELLOW}Testing API documentation...${NC}"
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/docs)
if [ "$DOCS_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ API documentation is accessible! (Status: $DOCS_RESPONSE)${NC}"
else
    echo -e "${RED}✗ API documentation is not accessible. (Status: $DOCS_RESPONSE)${NC}"
fi

# Test login endpoint with test credentials
echo -e "\n${YELLOW}Testing login functionality...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"email": "user@example.com", "password": "password"}' \
    $API_URL/auth/login)

if echo $LOGIN_RESPONSE | grep -q "access_token"; then
    echo -e "${GREEN}✓ Login successful! Authentication is working.${NC}"
    # Extract token for further testing
    TOKEN=$(echo $LOGIN_RESPONSE | sed -E 's/.*"access_token":"([^"]+)".*/\1/')
    
    # Test protected endpoint with token
    echo -e "\n${YELLOW}Testing protected endpoint with token...${NC}"
    PROTECTED_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        $API_URL/consultations/)
    
    if [ "$PROTECTED_RESPONSE" == "200" ] || [ "$PROTECTED_RESPONSE" == "404" ]; then
        echo -e "${GREEN}✓ Protected endpoint access successful! (Status: $PROTECTED_RESPONSE)${NC}"
    else
        echo -e "${RED}✗ Protected endpoint access failed. (Status: $PROTECTED_RESPONSE)${NC}"
    fi
else
    echo -e "${RED}✗ Login failed. Authentication system may not be working properly.${NC}"
    echo "Response: $LOGIN_RESPONSE"
fi

echo -e "\n${YELLOW}====================================${NC}"
echo -e "${YELLOW}           TEST COMPLETE            ${NC}"
echo -e "${YELLOW}====================================${NC}"