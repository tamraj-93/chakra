#!/bin/bash

# Healthcare RAG Test Script
# Tests the RAG system with healthcare-specific queries

# Color codes for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo -e "${BLUE}${BOLD}            CHAKRA HEALTHCARE RAG TESTING                         ${NC}"
echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo

# Ensure we're working from the project root
PROJECT_ROOT="/home/nilabh/Projects/chakra"
cd "$PROJECT_ROOT" || {
    echo -e "${RED}Error: Could not change to project directory: $PROJECT_ROOT${NC}"
    exit 1
}

echo -e "${GREEN}Working directory: $(pwd)${NC}"

# Check if required directories exist
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}Error: Required directories not found${NC}"
    echo "Current directory structure:"
    ls -la
    exit 1
fi

echo -e "${BLUE}Step 1: Setting up environment${NC}"

# Check for Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}Found Python 3: $(python3 --version)${NC}"
else
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

# Check for virtual environment and activate it
VENV_PATH=""
if [ -d "backend/.venv" ]; then
    VENV_PATH="backend/.venv"
elif [ -d "backend/venv" ]; then
    VENV_PATH="backend/venv"
fi

if [ -n "$VENV_PATH" ]; then
    echo -e "${GREEN}Found virtual environment at $VENV_PATH${NC}"
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}Virtual environment activated${NC}"
else
    echo -e "${YELLOW}No virtual environment found.${NC}"
    echo -e "${YELLOW}Using system Python - this may cause dependency issues.${NC}"
    echo -e "${YELLOW}Consider running start_chakra.sh first to set up the environment.${NC}"
    
    # Ask user if they want to continue
    echo -ne "${YELLOW}Do you want to continue anyway? (y/N): ${NC}"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${YELLOW}Exiting. Please run start_chakra.sh first.${NC}"
        exit 0
    fi
fi

# Ensure required packages are installed
echo -e "${BLUE}Checking for required packages...${NC}"
MISSING_PACKAGES=()

# Check for required packages
if ! $PYTHON_CMD -c "import chromadb" &> /dev/null; then
    MISSING_PACKAGES+=("chromadb")
fi

if ! $PYTHON_CMD -c "import sentence_transformers" &> /dev/null; then
    MISSING_PACKAGES+=("sentence-transformers")
fi

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    
    # Ask user if they want to install missing packages
    echo -ne "${YELLOW}Do you want to install missing packages? (Y/n): ${NC}"
    read -r response
    if [[ ! "$response" =~ ^([nN][oO]|[nN])$ ]]; then
        echo -e "${BLUE}Installing missing packages...${NC}"
        for package in "${MISSING_PACKAGES[@]}"; do
            echo -e "${BLUE}Installing $package...${NC}"
            pip install $package
        done
    else
        echo -e "${YELLOW}Continuing without installing packages.${NC}"
        echo -e "${YELLOW}Tests may fail due to missing dependencies.${NC}"
    fi
else
    echo -e "${GREEN}All required packages are installed.${NC}"
fi

# Set PYTHONPATH for module imports
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT
echo -e "${GREEN}PYTHONPATH set to: $PYTHONPATH${NC}"

# Create required directories
mkdir -p backend/data/test_vector_db
mkdir -p backend/tests/results

echo -e "${BLUE}Step 2: Running minimal healthcare RAG test${NC}"
echo -e "${BLUE}--------------------------------------${NC}"

# Try to run the minimal test script first
MINIMAL_TEST_SCRIPT="backend/scripts/minimal_test_healthcare_rag.py"
if [ -f "$MINIMAL_TEST_SCRIPT" ]; then
    echo -e "${BLUE}Running: $PYTHON_CMD $MINIMAL_TEST_SCRIPT${NC}"
    cd backend || exit 1
    $PYTHON_CMD scripts/minimal_test_healthcare_rag.py
    MINIMAL_TEST_RESULT=$?
    cd ..
    
    if [ $MINIMAL_TEST_RESULT -eq 0 ]; then
        echo -e "${GREEN}Minimal healthcare RAG test passed!${NC}"
    else
        echo -e "${RED}Minimal healthcare RAG test failed.${NC}"
        echo -e "${YELLOW}Please run ./install_dependencies.sh to ensure all dependencies are installed.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Minimal test script not found: $MINIMAL_TEST_SCRIPT${NC}"
    echo -e "${YELLOW}Will try the full test script instead.${NC}"
fi

echo -e "${BLUE}Step 3: Running full healthcare RAG tests${NC}"
echo -e "${BLUE}--------------------------------------${NC}"

# Verify that the test script exists
TEST_SCRIPT="backend/scripts/test_healthcare_rag.py"
if [ ! -f "$TEST_SCRIPT" ]; then
    echo -e "${RED}Error: Test script not found: $TEST_SCRIPT${NC}"
    echo "Available scripts:"
    find backend/scripts -name "*.py" | sort
    exit 1
fi

# Run healthcare tests
echo -e "${BLUE}Running: $PYTHON_CMD $TEST_SCRIPT${NC}"
cd backend || exit 1  # Change to backend directory to help with imports
$PYTHON_CMD scripts/test_healthcare_rag.py
TEST_RESULT=$?
cd .. || exit 1

if [ $TEST_RESULT -ne 0 ]; then
    echo -e "${RED}Healthcare RAG tests failed${NC}"
    echo -e "${YELLOW}Try running ./install_dependencies.sh to ensure all dependencies are installed.${NC}"
    exit 1
fi

echo -e "${GREEN}${BOLD}All tests completed successfully!${NC}"
echo -e "Results are available in the backend/tests/results directory"
echo
echo -e "${BLUE}To visualize the results, run:${NC}"
echo -e "$PYTHON_CMD visualize_healthcare_rag_results.py"
echo -e "${BLUE}==================================================================${NC}"