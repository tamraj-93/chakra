#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     CHAKRA INTEGRATION QUICK TEST              ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${RED}Error: Backend server is not running.${NC}"
    echo -e "${YELLOW}Please start the backend server first using:${NC}"
    echo -e "  ./start_chakra.sh"
    exit 1
fi

# Create temp directory for test
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Run a simple backend health check
echo -e "${YELLOW}Testing Backend Health...${NC}"
BACKEND_HEALTH=$(curl -s http://localhost:8000/api/health)
if [[ $BACKEND_HEALTH == *"\"status\":\"ok\""* ]]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    echo "$BACKEND_HEALTH"
    exit 1
fi

# Test authentication
echo -e "\n${YELLOW}Testing Authentication...${NC}"

# Create a test user
echo -e "Creating test user..."
USER_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username": "integrationtest", "email": "integration@test.com", "password": "Password123!"}')

# Check if registration was successful or user already exists
if [[ $USER_RESULT == *"\"username\":\"integrationtest\""* || $USER_RESULT == *"username already registered"* ]]; then
    echo -e "${GREEN}✓ User registration successful or user already exists${NC}"
else
    echo -e "${RED}✗ User registration failed${NC}"
    echo "$USER_RESULT"
    exit 1
fi

# Login with test user
echo -e "Logging in as test user..."
LOGIN_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "integrationtest", "password": "Password123!"}')

# Extract token
ACCESS_TOKEN=$(echo "$LOGIN_RESULT" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -n "$ACCESS_TOKEN" ]; then
    echo -e "${GREEN}✓ Login successful${NC}"
    echo "$ACCESS_TOKEN" > "$TEMP_DIR/token.txt"
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "$LOGIN_RESULT"
    exit 1
fi

# Test accessing a protected endpoint
echo -e "\n${YELLOW}Testing Protected Endpoint Access...${NC}"
USER_PROFILE=$(curl -s -X GET http://localhost:8000/api/users/me \
    -H "Authorization: Bearer $(cat "$TEMP_DIR/token.txt")")

if [[ $USER_PROFILE == *"\"username\":\"integrationtest\""* ]]; then
    echo -e "${GREEN}✓ Protected endpoint access successful${NC}"
else
    echo -e "${RED}✗ Protected endpoint access failed${NC}"
    echo "$USER_PROFILE"
    exit 1
fi

# Test consultation creation
echo -e "\n${YELLOW}Testing Consultation Creation...${NC}"
CONSULTATION_RESULT=$(curl -s -X POST http://localhost:8000/api/consultations/ \
    -H "Authorization: Bearer $(cat "$TEMP_DIR/token.txt")" \
    -H "Content-Type: application/json" \
    -d '{"title": "Integration Test Consultation", "description": "This is a test consultation"}')

CONSULTATION_ID=$(echo "$CONSULTATION_RESULT" | grep -o '"id":[0-9]*' | head -1 | sed 's/"id"://')

if [ -n "$CONSULTATION_ID" ]; then
    echo -e "${GREEN}✓ Consultation creation successful (ID: $CONSULTATION_ID)${NC}"
    echo "$CONSULTATION_ID" > "$TEMP_DIR/consultation_id.txt"
else
    echo -e "${RED}✗ Consultation creation failed${NC}"
    echo "$CONSULTATION_RESULT"
    exit 1
fi

# Test sending a message
echo -e "\n${YELLOW}Testing Message Sending...${NC}"
MESSAGE_RESULT=$(curl -s -X POST "http://localhost:8000/api/consultations/$(cat "$TEMP_DIR/consultation_id.txt")/messages" \
    -H "Authorization: Bearer $(cat "$TEMP_DIR/token.txt")" \
    -H "Content-Type: application/json" \
    -d '{"content": "Hello, I need a test SLA for my integration test"}')

if [[ $MESSAGE_RESULT == *"\"content\":"* ]]; then
    echo -e "${GREEN}✓ Message sending successful${NC}"
else
    echo -e "${RED}✗ Message sending failed${NC}"
    echo "$MESSAGE_RESULT"
    exit 1
fi

# Test getting messages
echo -e "\n${YELLOW}Testing Message Retrieval...${NC}"
MESSAGES_RESULT=$(curl -s -X GET "http://localhost:8000/api/consultations/$(cat "$TEMP_DIR/consultation_id.txt")/messages" \
    -H "Authorization: Bearer $(cat "$TEMP_DIR/token.txt")")

if [[ $MESSAGES_RESULT == *"\"content\":"* ]]; then
    echo -e "${GREEN}✓ Message retrieval successful${NC}"
else
    echo -e "${RED}✗ Message retrieval failed${NC}"
    echo "$MESSAGES_RESULT"
    exit 1
fi

# Cleanup - Delete the test consultation
echo -e "\n${YELLOW}Cleaning up test data...${NC}"
DELETE_RESULT=$(curl -s -X DELETE "http://localhost:8000/api/consultations/$(cat "$TEMP_DIR/consultation_id.txt")" \
    -H "Authorization: Bearer $(cat "$TEMP_DIR/token.txt")")

if [[ $DELETE_RESULT == *"true"* ]]; then
    echo -e "${GREEN}✓ Test consultation deleted successfully${NC}"
else
    echo -e "${YELLOW}! Could not delete test consultation, it may require manual cleanup${NC}"
fi

echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN}         INTEGRATION TEST COMPLETED SUCCESSFULLY    ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo -e "The test verified:"
echo -e "  - Backend health and connectivity"
echo -e "  - User registration and authentication"
echo -e "  - Protected API access"
echo -e "  - Consultation creation and management"
echo -e "  - Message sending and retrieval"
echo ""