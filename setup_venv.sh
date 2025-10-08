#!/bin/bash

# Color codes for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo -e "${BLUE}${BOLD}            CHAKRA VIRTUAL ENVIRONMENT SETUP                      ${NC}"
echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo

# Ensure we're working from the project root
PROJECT_ROOT="/home/nilabh/Projects/chakra"
cd "$PROJECT_ROOT" || {
    echo -e "${RED}Error: Could not change to project directory: $PROJECT_ROOT${NC}"
    exit 1
}

echo -e "${GREEN}Working directory: $(pwd)${NC}"

# Step 1: Check Python installation
echo -e "${BLUE}Step 1: Checking Python installation...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}Found Python 3: $(python3 --version)${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}Found Python: $(python --version)${NC}"
else
    echo -e "${RED}Error: Python not found. Please install Python 3.${NC}"
    exit 1
fi

# Make sure python3-full and python3-venv are installed
echo -e "${BLUE}Step 2: Ensuring python3-full and venv are installed...${NC}"
if command -v apt &> /dev/null; then
    echo -e "${BLUE}Using apt to install python3-full and python3-venv...${NC}"
    sudo apt update
    sudo apt install -y python3-full python3-venv
else
    echo -e "${YELLOW}Warning: Could not automatically install python3-full and python3-venv.${NC}"
    echo -e "${YELLOW}If virtual environment creation fails, please install them manually:${NC}"
    echo -e "${YELLOW}sudo apt install python3-full python3-venv${NC}"
fi

# Step 3: Create a virtual environment
echo -e "${BLUE}Step 3: Creating virtual environment...${NC}"
VENV_DIR="$PROJECT_ROOT/venv"

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Do you want to recreate it? (y/N):${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${BLUE}Removing existing virtual environment...${NC}"
        rm -rf "$VENV_DIR"
    else
        echo -e "${GREEN}Using existing virtual environment.${NC}"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Creating new virtual environment...${NC}"
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Please install python3-venv:${NC}"
        echo -e "${RED}sudo apt install python3-venv${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created at: $VENV_DIR${NC}"
fi

# Step 4: Activate the virtual environment
echo -e "${BLUE}Step 4: Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
fi
echo -e "${GREEN}Virtual environment activated.${NC}"

# Step 5: Install required packages
echo -e "${BLUE}Step 5: Installing required packages...${NC}"
echo -e "This may take a few minutes..."

pip install --upgrade pip
echo -e "${GREEN}Pip upgraded to: $(pip --version)${NC}"

# Install packages
packages=("chromadb" "sentence-transformers" "langchain" "unstructured")
for package in "${packages[@]}"; do
    echo -e "${BLUE}Installing ${package}...${NC}"
    pip install ${package}
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install ${package}.${NC}"
        exit 1
    else
        echo -e "${GREEN}Successfully installed ${package}${NC}"
    fi
done

# Create a convenience script to activate the environment
echo -e "${BLUE}Creating convenience scripts...${NC}"

# Script to activate the environment
cat > "$PROJECT_ROOT/activate_env.sh" << EOL
#!/bin/bash
source "$VENV_DIR/bin/activate"
echo "Virtual environment activated. Run 'deactivate' to exit."
EOL
chmod +x "$PROJECT_ROOT/activate_env.sh"

# Script to run tests with the virtual environment
cat > "$PROJECT_ROOT/run_healthcare_rag_test_venv.sh" << EOL
#!/bin/bash
# Activate virtual environment and run tests
source "$VENV_DIR/bin/activate"
export PYTHONPATH=\$PYTHONPATH:$PROJECT_ROOT

# Run the original test script
$PROJECT_ROOT/run_healthcare_rag_test.sh

# Deactivate when done
deactivate
EOL
chmod +x "$PROJECT_ROOT/run_healthcare_rag_test_venv.sh"

echo -e "${GREEN}${BOLD}Setup completed!${NC}"
echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo -e "${YELLOW}To activate the virtual environment manually:${NC}"
echo -e "source $VENV_DIR/bin/activate"
echo -e "${YELLOW}Or use the convenience script:${NC}"
echo -e "./activate_env.sh"
echo
echo -e "${YELLOW}To run tests with the virtual environment:${NC}"
echo -e "./run_healthcare_rag_test_venv.sh"
echo -e "${BLUE}${BOLD}==================================================================${NC}"

# Keep the environment active at the end
echo -e "${GREEN}Virtual environment is now active and ready to use.${NC}"