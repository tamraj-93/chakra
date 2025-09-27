#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     OLLAMA NETWORK CONNECTIVITY TEST            ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Test if Ollama is running
echo -e "${YELLOW}Testing if Ollama server is running...${NC}"
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${RED}✗ Ollama server is not running${NC}"
    echo -e "${YELLOW}Starting Ollama server...${NC}"
    ollama serve &
    sleep 5
else
    echo -e "${GREEN}✓ Ollama server is running${NC}"
fi

# Get the IP address where Ollama is listening
echo -e "\n${YELLOW}Checking Ollama network binding...${NC}"
OLLAMA_PORTS=$(netstat -tlnp 2>/dev/null | grep ollama)
if [ -z "$OLLAMA_PORTS" ]; then
    echo -e "${YELLOW}Could not find Ollama network binding using netstat${NC}"
    OLLAMA_PORTS=$(ss -tlnp 2>/dev/null | grep ollama)
    if [ -z "$OLLAMA_PORTS" ]; then
        echo -e "${RED}✗ Could not determine Ollama network binding${NC}"
    else
        echo "$OLLAMA_PORTS"
    fi
else
    echo "$OLLAMA_PORTS"
fi

# Test connection to Ollama API
echo -e "\n${YELLOW}Testing connection to Ollama API...${NC}"
echo "Attempting to connect to http://localhost:11434"
CURL_RESULT=$(curl -s --connect-timeout 5 http://localhost:11434)
CURL_STATUS=$?

if [ $CURL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully connected to Ollama API${NC}"
else
    echo -e "${RED}✗ Failed to connect to Ollama API (curl status: $CURL_STATUS)${NC}"
    echo -e "${YELLOW}Trying verbose output to diagnose connection issues:${NC}"
    curl -v http://localhost:11434
fi

# Check if we can send a simple API request
echo -e "\n${YELLOW}Testing Ollama API functionality...${NC}"
MODEL_RESULT=$(curl -s --connect-timeout 5 http://localhost:11434/api/tags)
if echo "$MODEL_RESULT" | grep -q "models"; then
    echo -e "${GREEN}✓ Ollama API is responding correctly${NC}"
    echo "Available models:"
    echo "$MODEL_RESULT" | grep -o '"name":"[^"]*' | sed 's/"name":"/- /'
else
    echo -e "${RED}✗ Ollama API is not returning proper model information${NC}"
    echo "API response:"
    echo "$MODEL_RESULT"
fi

echo -e "\n${BLUE}=================================================${NC}"
echo -e "${BLUE}     NETWORK TEST COMPLETE                       ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "If you're having connection issues between your backend and Ollama:"
echo -e "1. Check that Ollama is listening on all interfaces or the correct one"
echo -e "   - Edit /etc/systemd/system/ollama.service to add:"
echo -e "     Environment=\"OLLAMA_HOST=0.0.0.0\""
echo -e "   - Then restart: systemctl restart ollama"
echo -e "2. Check for firewall rules blocking connections to port 11434"
echo -e "3. Ensure your OLLAMA_API_URL in .env points to the right address"
echo -e "${BLUE}=================================================${NC}"