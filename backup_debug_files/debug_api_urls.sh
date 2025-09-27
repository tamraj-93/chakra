#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     DEBUG API URL CONFIGURATION                 ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Check environment files
echo -e "\n${YELLOW}Checking environment files:${NC}"

ENV_FILE="/home/nilabh/Projects/chakra/frontend/src/environments/environment.ts"
PROD_ENV_FILE="/home/nilabh/Projects/chakra/frontend/src/environments/environment.prod.ts"

if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}✓ Found environment.ts${NC}"
    API_URL=$(grep -o "apiUrl: '[^']*'" "$ENV_FILE" | cut -d "'" -f 2)
    echo -e "  API URL: ${BLUE}$API_URL${NC}"
else
    echo -e "${RED}✗ environment.ts not found${NC}"
fi

if [ -f "$PROD_ENV_FILE" ]; then
    echo -e "${GREEN}✓ Found environment.prod.ts${NC}"
    PROD_API_URL=$(grep -o "apiUrl: '[^']*'" "$PROD_ENV_FILE" | cut -d "'" -f 2)
    echo -e "  Production API URL: ${BLUE}$PROD_API_URL${NC}"
else
    echo -e "${RED}✗ environment.prod.ts not found${NC}"
fi

# Compare service endpoints
echo -e "\n${YELLOW}Checking service endpoint configurations:${NC}"

AUTH_SERVICE=$(grep -o "http[^']*" "/home/nilabh/Projects/chakra/frontend/src/app/services/auth.service.ts" | head -1)
CONSULTATION_SERVICE=$(grep -o "http[^']*" "/home/nilabh/Projects/chakra/frontend/src/app/services/consultation.service.ts" | head -1)

echo -e "Auth Service URL: ${BLUE}$AUTH_SERVICE${NC}"
echo -e "Consultation Service URL: ${BLUE}$CONSULTATION_SERVICE${NC}"

# Check specific API calls
echo -e "\n${YELLOW}Checking specific API endpoint formats:${NC}"
echo -e "Auth login: ${BLUE}${API_URL}/api/auth/login${NC}"
echo -e "Auth token: ${BLUE}${API_URL}/api/auth/token${NC}"
echo -e "Consultation chat: ${BLUE}${API_URL}/api/consultation/chat${NC}"

# Test API endpoints
echo -e "\n${YELLOW}Testing backend API endpoints:${NC}"

# Test auth token endpoint
echo -e "Testing auth token endpoint..."
AUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API_URL}/api/auth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@example.com&password=password")

if [ "$AUTH_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Auth token endpoint works (${AUTH_RESPONSE})${NC}"
else
    echo -e "${RED}✗ Auth token endpoint returned ${AUTH_RESPONSE}${NC}"
fi

# Get token for consultation test
TOKEN_RESP=$(curl -s -X POST "${API_URL}/api/auth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@example.com&password=password")

TOKEN=$(echo "$TOKEN_RESP" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\([^"]*\)"/\1/')

# Test consultation chat endpoint
if [ -n "$TOKEN" ]; then
    echo -e "Testing consultation chat endpoint with token..."
    CHAT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API_URL}/api/consultation/chat" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{"content":"What is an SLA?","role":"user"}')
    
    if [ "$CHAT_RESPONSE" == "200" ]; then
        echo -e "${GREEN}✓ Consultation chat endpoint works (${CHAT_RESPONSE})${NC}"
    else
        echo -e "${RED}✗ Consultation chat endpoint returned ${CHAT_RESPONSE}${NC}"
    fi
    
    # Try with debug output to see the full error
    echo -e "\nVerbose test of consultation chat endpoint:"
    curl -v -X POST "${API_URL}/api/consultation/chat" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{"content":"What is an SLA?","role":"user"}'
else
    echo -e "${RED}✗ Could not get auth token for testing consultation endpoint${NC}"
fi

echo -e "\n${BLUE}==================================================${NC}"
echo -e "${BLUE}     DEBUG COMPLETE                              ${NC}"
echo -e "${BLUE}==================================================${NC}"
