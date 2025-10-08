#!/bin/bash

# Script to initialize the database with all tables and sample data

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     INITIALIZING DATABASE WITH TEMPLATE SUPPORT   ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Activate virtual environment if it exists
if [ -d "./venv" ]; then
    source ./venv/bin/activate
elif [ -d "./.venv" ]; then
    source ./.venv/bin/activate
fi

# Run the database initialization scripts
echo -e "${YELLOW}Initializing base database schema...${NC}"
python ./scripts/init_db.py

# Update schema with template models
echo -e "${YELLOW}Adding consultation template tables...${NC}"
python ./scripts/update_schema.py

# Initialize sample data
echo -e "${YELLOW}Adding sample consultations...${NC}"
python ./scripts/init_consultations.py

# Initialize sample templates
echo -e "${YELLOW}Adding sample consultation templates...${NC}"
python ./scripts/init_templates.py

# Initialize healthcare templates
echo -e "${YELLOW}Adding healthcare templates...${NC}"
python ./scripts/init_healthcare_templates.py

echo -e "${GREEN}Database initialization complete!${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     DATABASE READY WITH TEMPLATE SUPPORT         ${NC}"
echo -e "${BLUE}==================================================${NC}"