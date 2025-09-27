#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     DIRECT OLLAMA API TEST                     ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Test Ollama API directly with curl
echo -e "${YELLOW}Testing direct API call to Ollama...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{
      "model": "mistral",
      "prompt": "What is an SLA and why is it important for businesses?",
      "stream": false
    }')

if [ -z "$RESPONSE" ]; then
    echo -e "${RED}✗ No response received${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Received response from Ollama API${NC}"
    echo -e "\n${BLUE}Response:${NC}"
    echo "$RESPONSE" | grep -o '"response":"[^"]*' | sed 's/"response":"//'
fi

echo -e "\n${BLUE}=================================================${NC}"
echo -e "${BLUE}     TEST COMPLETE                               ${NC}"
echo -e "${BLUE}=================================================${NC}"