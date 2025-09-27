#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     TESTING OLLAMA RESPONSE FORMAT               ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Get the Ollama API URL from .env file
if [ -f "./backend/.env" ]; then
    OLLAMA_API_URL=$(grep "OLLAMA_API_URL" ./backend/.env | cut -d '=' -f2)
    OLLAMA_MODEL=$(grep "OLLAMA_MODEL" ./backend/.env | cut -d '=' -f2)
else
    OLLAMA_API_URL="http://localhost:11434"
    OLLAMA_MODEL="mistral"
fi

echo -e "Testing with API URL: ${YELLOW}$OLLAMA_API_URL${NC}"
echo -e "Testing with Model: ${YELLOW}$OLLAMA_MODEL${NC}"
echo

# Create a simple test prompt
echo -e "${BLUE}Sending test request to Ollama API...${NC}"
TEST_PROMPT="What are the key components of a Service Level Agreement?"

# Send the request to Ollama
echo -e "Prompt: \"${YELLOW}$TEST_PROMPT${NC}\""
echo
echo -e "${BLUE}Response:${NC}"
RESPONSE=$(curl -s -X POST "$OLLAMA_API_URL/api/generate" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"$OLLAMA_MODEL\",
        \"prompt\": \"$TEST_PROMPT\",
        \"stream\": false,
        \"options\": {
            \"temperature\": 0.7
        }
    }")

# Check if we got a valid JSON response
if echo "$RESPONSE" | jq -e . >/dev/null 2>&1; then
    # Extract and print the response
    RESPONSE_TEXT=$(echo "$RESPONSE" | jq -r '.response')
    echo -e "${GREEN}$RESPONSE_TEXT${NC}"
    echo
    echo -e "${GREEN}✓ Ollama response format is valid${NC}"
else
    echo -e "${RED}Error: Invalid response from Ollama API${NC}"
    echo -e "Raw response: $RESPONSE"
    echo -e "${RED}✗ Ollama response format test failed${NC}"
fi

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     TEST COMPLETE                               ${NC}"
echo -e "${BLUE}==================================================${NC}"