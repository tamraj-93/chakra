#!/bin/bash

# Script to pre-warm the Ollama model to reduce initial response times

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to the script's directory
cd "$(dirname "$0")"

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     PRE-WARMING OLLAMA MODEL                     ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Get model name from .env file or use default
MODEL_NAME="mistral"
if [ -f "./backend/.env" ]; then
    MODEL_NAME=$(grep "OLLAMA_MODEL" ./backend/.env | cut -d '=' -f2 || echo "mistral")
fi

# Get API URL from .env file or use default
API_URL="http://localhost:11434"
if [ -f "./backend/.env" ]; then
    API_URL=$(grep "OLLAMA_API_URL" ./backend/.env | cut -d '=' -f2 || echo "http://localhost:11434")
fi

echo -e "${YELLOW}Using model: ${MODEL_NAME}${NC}"
echo -e "${YELLOW}Using API URL: ${API_URL}${NC}"

# Check if Ollama is running
echo -e "${YELLOW}Checking Ollama status...${NC}"
if ! curl -s --head $API_URL/api/version > /dev/null; then
    echo -e "${RED}Error: Ollama service is not running at ${API_URL}${NC}"
    echo -e "${YELLOW}Start Ollama with 'ollama serve' in another terminal${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Ollama is running${NC}"

# Pre-warm the model with different prompts
echo -e "${YELLOW}Pre-warming the model with multiple requests...${NC}"

echo -e "${YELLOW}Request 1: Simple greeting...${NC}"
curl -s -X POST $API_URL/api/generate -d "{\"model\":\"$MODEL_NAME\",\"prompt\":\"Hello, how are you?\",\"stream\":false}" > /dev/null
echo -e "${GREEN}✓ Completed${NC}"

echo -e "${YELLOW}Request 2: SLA-related prompt...${NC}"
curl -s -X POST $API_URL/api/generate -d "{\"model\":\"$MODEL_NAME\",\"prompt\":\"What are the key components of a service level agreement?\",\"stream\":false}" > /dev/null
echo -e "${GREEN}✓ Completed${NC}"

echo -e "${YELLOW}Request 3: Technical question...${NC}"
curl -s -X POST $API_URL/api/generate -d "{\"model\":\"$MODEL_NAME\",\"prompt\":\"Explain how to optimize performance in a FastAPI application\",\"stream\":false}" > /dev/null
echo -e "${GREEN}✓ Completed${NC}"

# Final confirmation
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     OLLAMA MODEL PRE-WARMING COMPLETE            ${NC}"
echo -e "${BLUE}     The model should now respond faster!          ${NC}"
echo -e "${BLUE}==================================================${NC}"