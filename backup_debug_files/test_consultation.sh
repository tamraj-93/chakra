#!/bin/bash

# Script to test the consultation chat API specifically

# Set colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}====================================${NC}"
echo -e "${YELLOW}   CHAKRA CONSULTATION CHAT TEST    ${NC}"
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
if [ "$HEALTH_RESPONSE" != "200" ]; then
    echo -e "${RED}✗ API is not responding properly. (Status: $HEALTH_RESPONSE)${NC}"
    echo -e "${RED}  Make sure the backend server is running on port 8000.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ API is up and running! (Status: $HEALTH_RESPONSE)${NC}"
fi

# Test login endpoint with test credentials
echo -e "\n${YELLOW}Testing login with admin credentials...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@example.com", "password": "password"}' \
    $API_URL/auth/login)

if echo $LOGIN_RESPONSE | grep -q "access_token"; then
    echo -e "${GREEN}✓ Login successful! Authentication is working.${NC}"
    # Extract token for further testing
    TOKEN=$(echo $LOGIN_RESPONSE | sed -E 's/.*"access_token":"([^"]+)".*/\1/')
    
    # Test the consultation chat endpoint specifically
    echo -e "\n${YELLOW}Testing consultation chat endpoint...${NC}"
    echo -e "${YELLOW}Sending message: 'I need help creating an SLA for our cloud service'${NC}"
    
    CHAT_RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{"content":"I need help creating an SLA for our cloud service","role":"user"}' \
        $API_URL/consultation/chat)
    
    echo -e "\n${YELLOW}API Response:${NC}"
    echo $CHAT_RESPONSE | python3 -m json.tool || echo $CHAT_RESPONSE
    
    if echo $CHAT_RESPONSE | grep -q "message"; then
        echo -e "\n${GREEN}✓ Consultation chat endpoint is working!${NC}"
        
        # Extract the session_id if present
        if echo $CHAT_RESPONSE | grep -q "session_id"; then
            SESSION_ID=$(echo $CHAT_RESPONSE | sed -E 's/.*"session_id":([0-9]+).*/\1/')
            echo -e "${GREEN}✓ Session ID: $SESSION_ID${NC}"
            
            # Send another message to the same session
            echo -e "\n${YELLOW}Sending follow-up message to the same session...${NC}"
            FOLLOWUP_RESPONSE=$(curl -s -X POST \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $TOKEN" \
                -d '{"content":"What metrics should I include?","role":"user"}' \
                $API_URL/consultation/chat?session_id=$SESSION_ID)
                
            echo -e "\n${YELLOW}Follow-up Response:${NC}"
            echo $FOLLOWUP_RESPONSE | python3 -m json.tool || echo $FOLLOWUP_RESPONSE
        fi
    else
        echo -e "\n${RED}✗ Consultation chat endpoint is not responding as expected.${NC}"
    fi
else
    echo -e "${RED}✗ Login failed. Authentication system may not be working properly.${NC}"
    echo "Response: $LOGIN_RESPONSE"
fi

echo -e "\n${YELLOW}====================================${NC}"
echo -e "${YELLOW}           TEST COMPLETE            ${NC}"
echo -e "${YELLOW}====================================${NC}"