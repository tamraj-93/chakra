#!/bin/bash

# Test Healthcare RAG functionality for Chakra
# This script initializes the RAG system and tests healthcare-specific queries

# Color codes for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo -e "${BLUE}${BOLD}            CHAKRA HEALTHCARE RAG TESTING SCRIPT                  ${NC}"
echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo

# Make sure we're in the project directory
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR" || exit 1

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}Error: Cannot find backend or frontend directories${NC}"
    echo "Current directory: $(pwd)"
    echo "Directory contents:"
    ls -la
    exit 1
fi

# Print working directory for confirmation
echo -e "${GREEN}Working directory: $(pwd)${NC}"

# Make sure Python environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: No Python virtual environment detected${NC}"
    echo "It's recommended to activate your virtual environment before running this script"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for required Python packages
echo -e "${BLUE}Checking required packages...${NC}"
REQUIRED_PACKAGES=("chromadb" "sentence_transformers" "langchain" "unstructured")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    # Try to import the package
    if ! python -c "import $package" &> /dev/null; then
        # Special case for sentence_transformers (import name differs from package name)
        if [ "$package" == "sentence_transformers" ]; then
            if ! pip list | grep -i "sentence-transformers" &> /dev/null; then
                MISSING_PACKAGES+=("sentence-transformers")
            fi
        else
            MISSING_PACKAGES+=("$package")
        fi
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}Missing required packages: ${MISSING_PACKAGES[*]}${NC}"
    echo "Installing missing packages..."
    pip install ${MISSING_PACKAGES[@]}
fi

echo -e "${GREEN}All required packages are installed${NC}"
echo

# Step 1: Initialize RAG system
echo -e "${BLUE}${BOLD}Step 1: Initializing RAG system${NC}"
echo -e "${BLUE}==================================================================${NC}"
echo "This will load all SLA examples into the vector database"
echo

# Check if the script exists
if [ ! -f "backend/scripts/initialize_rag.py" ]; then
    echo -e "${RED}Error: Cannot find initialize_rag.py script${NC}"
    echo "Expected path: backend/scripts/initialize_rag.py"
    echo "Current directory: $(pwd)"
    find backend/scripts -type f -name "*.py" | sort
    exit 1
fi

# Run the initialization script
python backend/scripts/initialize_rag.py

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to initialize RAG system${NC}"
    exit 1
fi

echo
echo -e "${GREEN}${BOLD}RAG system successfully initialized!${NC}"
echo

# Step 2: Run healthcare-specific RAG tests
echo -e "${BLUE}${BOLD}Step 2: Running healthcare-specific RAG tests${NC}"
echo -e "${BLUE}==================================================================${NC}"
echo "Testing RAG system with healthcare queries"
echo

# Check if the script exists
if [ ! -f "backend/scripts/test_healthcare_rag.py" ]; then
    echo -e "${RED}Error: Cannot find test_healthcare_rag.py script${NC}"
    echo "Expected path: backend/scripts/test_healthcare_rag.py"
    echo "Current directory: $(pwd)"
    find backend/scripts -type f -name "*.py" | sort
    exit 1
fi

# Run the test script
python backend/scripts/test_healthcare_rag.py

if [ $? -ne 0 ]; then
    echo -e "${RED}Healthcare RAG tests failed${NC}"
    exit 1
fi

echo
echo -e "${GREEN}${BOLD}All tests completed!${NC}"
echo -e "${BLUE}==================================================================${NC}"
echo
echo -e "To review test results, check the JSON files in the backend/tests/results directory"
echo