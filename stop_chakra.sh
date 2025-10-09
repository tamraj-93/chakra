#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}     Shutting Down Chakra System    ${NC}"
echo -e "${BLUE}=====================================${NC}"

# Stop backend service
echo -e "\n${YELLOW}Stopping backend services...${NC}"
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    pkill -f "uvicorn app.main:app"
    echo -e "${GREEN}✓ Backend service stopped${NC}"
else
    echo -e "${YELLOW}No running backend service found${NC}"
fi

# Stop frontend service
echo -e "\n${YELLOW}Stopping frontend services...${NC}"
if pgrep -f "ng serve" > /dev/null; then
    pkill -f "ng serve"
    echo -e "${GREEN}✓ Frontend service stopped${NC}"
else
    echo -e "${YELLOW}No running frontend service found${NC}"
fi

# Stop LLM processes
echo -e "\n${YELLOW}Stopping LLM and related processes...${NC}"

# Find and kill Ollama processes
if pgrep -f "ollama" > /dev/null; then
    echo -e "${YELLOW}Found Ollama processes:${NC}"
    ps aux | grep -i "ollama" | grep -v grep
    pkill -f "ollama"
    echo -e "${GREEN}✓ Ollama processes stopped${NC}"
else
    echo -e "${YELLOW}No Ollama processes found${NC}"
fi

# Find and kill sentence-transformers processes
if pgrep -f "sentence-transformers" > /dev/null; then
    echo -e "${YELLOW}Found sentence-transformers processes:${NC}"
    ps aux | grep -i "sentence-transformers" | grep -v grep
    pkill -f "sentence-transformers"
    echo -e "${GREEN}✓ Sentence-transformers processes stopped${NC}"
else
    echo -e "${YELLOW}No sentence-transformers processes found${NC}"
fi

# Find and kill Python processes related to RAG
if pgrep -f "python.*rag" > /dev/null; then
    echo -e "${YELLOW}Found RAG-related Python processes:${NC}"
    ps aux | grep -i "python.*rag" | grep -v grep
    pkill -f "python.*rag"
    echo -e "${GREEN}✓ RAG-related Python processes stopped${NC}"
else
    echo -e "${YELLOW}No RAG-related Python processes found${NC}"
fi

echo -e "\n${YELLOW}Verifying all processes are stopped...${NC}"
# Check for any remaining Python processes related to the project
REMAINING=$(ps aux | grep -i "python.*chakra\|ollama\|sentence-transformers" | grep -v grep | wc -l)

if [ $REMAINING -gt 0 ]; then
    echo -e "${YELLOW}Found $REMAINING remaining processes:${NC}"
    ps aux | grep -i "python.*chakra\|ollama\|sentence-transformers" | grep -v grep
    
    echo -e "\n${YELLOW}Do you want to force kill these processes? (y/n)${NC}"
    read -p "" -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Get PIDs and kill them
        PIDS=$(ps aux | grep -i "python.*chakra\|ollama\|sentence-transformers" | grep -v grep | awk '{print $2}')
        for PID in $PIDS; do
            kill -9 $PID
            echo -e "${GREEN}Killed process $PID${NC}"
        done
    fi
else
    echo -e "${GREEN}✓ No remaining processes found${NC}"
fi

echo -e "\n${BLUE}=====================================${NC}"
echo -e "${GREEN}System shutdown complete!${NC}"
echo -e "${BLUE}=====================================${NC}"