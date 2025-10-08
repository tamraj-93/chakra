#!/bin/bash

# Color codes for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo -e "${BLUE}${BOLD}            CHAKRA DEPENDENCY INSTALLER                           ${NC}"
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

# Step 2: Install pip if needed
echo -e "${BLUE}Step 2: Checking for pip...${NC}"

if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${YELLOW}Pip not found. Installing pip...${NC}"
    
    # Install pip using get-pip.py
    echo -e "${BLUE}Downloading get-pip.py...${NC}"
    if command -v curl &> /dev/null; then
        curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    elif command -v wget &> /dev/null; then
        wget -q https://bootstrap.pypa.io/get-pip.py
    else
        echo -e "${RED}Error: Neither curl nor wget is available. Please install pip manually:${NC}"
        echo "sudo apt install python3-pip  # For Debian/Ubuntu"
        exit 1
    fi
    
    if [ -f get-pip.py ]; then
        echo -e "${BLUE}Installing pip...${NC}"
        $PYTHON_CMD get-pip.py --user
        rm get-pip.py
        
        # Add pip to PATH if necessary
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
            export PATH="$HOME/.local/bin:$PATH"
            echo -e "${GREEN}Added ~/.local/bin to PATH${NC}"
        fi
    else
        echo -e "${RED}Failed to download get-pip.py${NC}"
        echo -e "${YELLOW}Trying alternative method...${NC}"
        
        # Try system package manager
        if command -v apt &> /dev/null; then
            echo -e "${BLUE}Installing python3-pip using apt...${NC}"
            sudo apt update && sudo apt install -y python3-pip
        elif command -v yum &> /dev/null; then
            echo -e "${BLUE}Installing python3-pip using yum...${NC}"
            sudo yum install -y python3-pip
        else
            echo -e "${RED}Could not install pip. Please install manually:${NC}"
            echo "sudo apt install python3-pip  # For Debian/Ubuntu"
            exit 1
        fi
    fi
else
    echo -e "${GREEN}Pip is already installed: $($PYTHON_CMD -m pip --version)${NC}"
fi

# Determine pip command now that we've ensured pip is installed
if command -v pip &> /dev/null; then
    PIP_CMD="pip"
elif command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
else
    PIP_CMD="$PYTHON_CMD -m pip"
fi

echo -e "${GREEN}Using pip command: $PIP_CMD${NC}"

# Step 3: Install required packages
echo -e "${BLUE}Step 3: Installing required packages...${NC}"
echo -e "This may take a few minutes..."

# Try installing the required packages with the --user flag
# to avoid permission issues
packages=("chromadb" "sentence-transformers" "langchain" "unstructured")
for package in "${packages[@]}"; do
    echo -e "${BLUE}Installing ${package}...${NC}"
    $PIP_CMD install --user $package
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install ${package}. Please try manually:${NC}"
        echo "$PIP_CMD install --user ${package}"
        echo -e "${YELLOW}Continuing with installation...${NC}"
    else
        echo -e "${GREEN}Successfully installed ${package}${NC}"
    fi
done

echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo -e "${GREEN}${BOLD}Installation completed!${NC}"
echo -e "${BLUE}${BOLD}==================================================================${NC}"
echo -e "${YELLOW}NOTE: If you installed pip with --user, you may need to restart your terminal${NC}"
echo -e "${YELLOW}or run 'source ~/.bashrc' or 'source ~/.zshrc' for changes to take effect.${NC}"
echo
echo -e "${BLUE}To test your RAG system, run:${NC}"
echo -e "./run_healthcare_rag_test.sh"
echo -e "${BLUE}==================================================================${NC}"