#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is not installed. Please install it first:${NC}"
    echo -e "${YELLOW}sudo apt-get install jq${NC} or ${YELLOW}brew install jq${NC}"
    exit 1
fi

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     TEST OLLAMA SLA RESPONSE                    ${NC}"
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

# Create a test system prompt and user question about SLAs
SYS_PROMPT="You are an AI assistant specializing in Service Level Management (SLM). You help users create and optimize Service Level Agreements (SLAs). Ask clarifying questions to understand their needs and provide tailored advice."
USER_PROMPT="What are the key components that should be included in an SLA for a cloud service?"

# Format the prompt correctly for Ollama (for mistral model)
SYS_PROMPT_ESCAPED=$(echo "$SYS_PROMPT" | tr '\n' ' ')
USER_PROMPT_ESCAPED=$(echo "$USER_PROMPT" | tr '\n' ' ')
FORMATTED_PROMPT="<s>[INST] ${SYS_PROMPT_ESCAPED} ${USER_PROMPT_ESCAPED} [/INST]"

echo -e "${BLUE}Sending request to Ollama API...${NC}"
echo -e "${YELLOW}System prompt:${NC} $SYS_PROMPT"
echo -e "${YELLOW}User prompt:${NC} $USER_PROMPT"
echo

# Send the request to Ollama
RESPONSE=$(curl -s -X POST "$OLLAMA_API_URL/api/generate" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"$OLLAMA_MODEL\",
        \"prompt\": \"$FORMATTED_PROMPT\",
        \"stream\": false,
        \"options\": {
            \"temperature\": 0.7
        }
    }")

# Check if we got a valid JSON response
if echo "$RESPONSE" | grep -q "response"; then
    # Extract and print the response using grep instead of jq
    RESPONSE_TEXT=$(echo "$RESPONSE" | grep -o '"response":"[^"]*"' | sed 's/"response":"//;s/"$//')
    echo -e "${BLUE}Response from Ollama:${NC}"
    echo -e "${GREEN}$RESPONSE_TEXT${NC}"
    echo
    echo -e "${GREEN}✓ Ollama SLA response test succeeded${NC}"
else
    echo -e "${RED}Error: Invalid response from Ollama API${NC}"
    echo -e "Raw response: $RESPONSE"
    echo -e "${RED}✗ Ollama SLA response test failed${NC}"
fi

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     TEST COMPLETE                               ${NC}"
echo -e "${BLUE}==================================================${NC}"