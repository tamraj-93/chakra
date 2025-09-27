#!/bin/bash

# Show usage of the app and the various scripts

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}             CHAKRA SLM ASSISTANT               ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if user specified help for a particular component
if [ "$1" == "backend" ]; then
    echo -e "${YELLOW}BACKEND SETUP AND USAGE:${NC}"
    echo ""
    echo -e "${GREEN}Setup the Backend:${NC}"
    echo -e "  ./setup.sh            - Setup the entire application"
    echo -e "  ./setup_backend.sh    - Setup only the backend"
    echo ""
    echo -e "${GREEN}Initialize the Database:${NC}"
    echo -e "  ./init_db.sh          - Initialize the database with schema"
    echo -e "  ./verify_db.sh        - Verify database setup and tables"
    echo ""
    echo -e "${GREEN}Start the Backend:${NC}"
    echo -e "  ./start_chakra.sh     - Start the backend server"
    echo ""
    echo -e "${GREEN}Test the Backend:${NC}"
    echo -e "  ./test_api.sh         - Test general API endpoints"
    echo -e "  ./test_auth.sh        - Test authentication endpoints"
    echo -e "  ./test_consultation.sh- Test consultation endpoints"
    echo -e "  ./test_template_generator.sh - Test template generator functionality"
    echo ""
    echo -e "${GREEN}Data Management:${NC}"
    echo -e "  ./add_sla_example.sh  - Add example SLA templates to database"
    echo ""
    exit 0
elif [ "$1" == "frontend" ]; then
    echo -e "${YELLOW}FRONTEND SETUP AND USAGE:${NC}"
    echo ""
    echo -e "${GREEN}Setup the Frontend:${NC}"
    echo -e "  ./setup.sh            - Setup the entire application"
    echo -e "  ./setup_frontend.sh   - Setup only the frontend"
    echo ""
    echo -e "${GREEN}Start the Frontend:${NC}"
    echo -e "  cd frontend"
    echo -e "  npm start             - Start the Angular development server"
    echo ""
    echo -e "${GREEN}Build for Production:${NC}"
    echo -e "  cd frontend"
    echo -e "  npm run build         - Build the frontend for production"
    echo ""
    exit 0
elif [ "$1" == "examples" ]; then
    echo -e "${YELLOW}SLA EXAMPLES:${NC}"
    echo ""
    echo -e "${GREEN}Available Examples:${NC}"
    echo -e "  - Healthcare Cloud SLA (examples/healthcare_cloud_sla_example.md)"
    echo ""
    echo -e "${GREEN}View Examples:${NC}"
    echo -e "  ./add_sla_example.sh  - Add example SLA templates to database"
    echo -e "  Open sla_viewer.html  - View SLA examples in browser"
    echo ""
    exit 0
fi

# Display main help menu
echo -e "${YELLOW}AVAILABLE COMMANDS:${NC}"
echo ""
echo -e "${GREEN}Setup:${NC}"
echo -e "  ./setup.sh            - Setup the entire application"
echo -e "  ./setup_backend.sh    - Setup only the backend"
echo -e "  ./setup_frontend.sh   - Setup only the frontend"
echo ""
echo -e "${GREEN}Database:${NC}"
echo -e "  ./init_db.sh          - Initialize the database with schema"
echo -e "  ./verify_db.sh        - Verify database setup and tables"
echo -e "  ./add_sla_example.sh  - Add example SLA templates to database"
echo ""
echo -e "${GREEN}Run:${NC}"
echo -e "  ./start_chakra.sh     - Start the backend server"
echo -e "  cd frontend && npm start - Start the frontend development server"
echo ""
echo -e "${GREEN}Testing:${NC}"
echo -e "  ./test_api.sh         - Test general API endpoints"
echo -e "  ./test_auth.sh        - Test authentication endpoints"
echo -e "  ./test_consultation.sh- Test consultation endpoints"
echo -e "  ./test_chat_styles.sh - Test chat UI styling"
echo -e "  ./test_template_generator.sh - Test SLA template generator functionality"
echo ""
echo -e "${GREEN}Debug:${NC}"
echo -e "  ./debug_chat.sh       - Debug chat functionality"
echo ""
echo -e "${GREEN}For more details on a specific component:${NC}"
echo -e "  ./help.sh backend     - Backend-specific commands"
echo -e "  ./help.sh frontend    - Frontend-specific commands"
echo -e "  ./help.sh examples    - SLA examples information"
echo ""
echo -e "${YELLOW}GETTING STARTED:${NC}"
echo -e "1. Run ./setup.sh to install dependencies"
echo -e "2. Run ./init_db.sh to setup the database"
echo -e "3. Run ./add_sla_example.sh to add example SLA templates"
echo -e "4. Run ./start_chakra.sh to start the backend"
echo -e "5. In another terminal, run: cd frontend && npm start"
echo ""
echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}          © $(date +%Y) Chakra SLM Assistant         ${NC}"
echo -e "${BLUE}=================================================${NC}"