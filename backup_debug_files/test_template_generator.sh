#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     CHAKRA SLA TEMPLATE GENERATOR TEST          ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}Error: Backend server is not running.${NC}"
    echo -e "${YELLOW}Please start the backend server first using:${NC}"
    echo -e "  ./start_chakra.sh"
    exit 1
fi

# Create temp directory for test
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Run a simple backend health check
echo -e "${YELLOW}Testing Backend Health...${NC}"
BACKEND_HEALTH=$(curl -s http://localhost:8000/health)
if [[ $BACKEND_HEALTH == *"\"status\":\"healthy\""* ]]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    echo "$BACKEND_HEALTH"
    exit 1
fi

# Test authentication
echo -e "\n${YELLOW}Testing Authentication...${NC}"

# Create a test user
echo -e "Creating test user..."
USER_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email": "template@test.com", "password": "Password123!"}')

# Check if registration was successful or user already exists
if [[ $USER_RESULT == *"\"email\":\"template@test.com\""* || $USER_RESULT == *"Email already registered"* ]]; then
    echo -e "${GREEN}✓ User registration successful or user already exists${NC}"
else
    echo -e "${RED}✗ User registration failed${NC}"
    echo "$USER_RESULT"
    exit 1
fi

# Login with test user
echo -e "Logging in as test user..."
LOGIN_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "template@test.com", "password": "Password123!"}')

# Extract token
ACCESS_TOKEN=$(echo "$LOGIN_RESULT" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -n "$ACCESS_TOKEN" ]; then
    echo -e "${GREEN}✓ Login successful${NC}"
    echo "$ACCESS_TOKEN" > "$TEMP_DIR/token.txt"
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "$LOGIN_RESULT"
    exit 1
fi

# Test listing templates
echo -e "\n${YELLOW}Testing Template Listing...${NC}"
TEMPLATES_RESULT=$(curl -s -X GET http://localhost:8000/api/templates/ \
    -H "Authorization: Bearer $(cat "$TEMP_DIR/token.txt")")

if [[ $TEMPLATES_RESULT == *"["* ]]; then
    echo -e "${GREEN}✓ Templates listing successful${NC}"
    TEMPLATE_COUNT=$(echo "$TEMPLATES_RESULT" | grep -o '"id"' | wc -l)
    echo -e "${BLUE}Found $TEMPLATE_COUNT templates${NC}"
else
    echo -e "${YELLOW}! No templates found or endpoint not available${NC}"
    echo "$TEMPLATES_RESULT"
fi

# Test creating a template
echo -e "\n${YELLOW}Testing Template Creation...${NC}"

# Create test template JSON
cat > "$TEMP_DIR/template.json" << EOF
{
  "service_name": "Test Healthcare App",
  "service_type": "web_application",
  "description": "A test healthcare application with HIPAA compliance",
  "metrics": ["availability", "response_time", "error_rate"]
}
EOF

TEMPLATE_RESULT=$(curl -s -X POST http://localhost:8000/api/templates/ \
    -H "Authorization: Bearer $(cat "$TEMP_DIR/token.txt")" \
    -H "Content-Type: application/json" \
    -d @"$TEMP_DIR/template.json")

TEMPLATE_ID=$(echo "$TEMPLATE_RESULT" | grep -o '"id":[0-9]*' | head -1 | sed 's/"id"://')

if [ -n "$TEMPLATE_ID" ]; then
    echo -e "${GREEN}✓ Template creation successful (ID: $TEMPLATE_ID)${NC}"
    echo "$TEMPLATE_ID" > "$TEMP_DIR/template_id.txt"
else
    echo -e "${YELLOW}! Template creation endpoint not implemented or failed${NC}"
    echo "$TEMPLATE_RESULT"
fi

# Test generating a template
echo -e "\n${YELLOW}Testing Template Generation...${NC}"

# Create test template generation JSON
cat > "$TEMP_DIR/generate.json" << EOF
{
  "service_name": "Healthcare Cloud Platform",
  "service_type": "cloud_service",
  "description": "HIPAA-compliant healthcare cloud service for patient data and EHR",
  "metrics": ["availability", "response_time", "throughput", "error_rate"]
}
EOF

GENERATE_RESULT=$(curl -s -X POST http://localhost:8000/api/templates/generate \
    -H "Authorization: Bearer $(cat "$TEMP_DIR/token.txt")" \
    -H "Content-Type: application/json" \
    -d @"$TEMP_DIR/generate.json")

if [[ $GENERATE_RESULT == *"template_url"* ]]; then
    echo -e "${GREEN}✓ Template generation successful${NC}"
    TEMPLATE_URL=$(echo "$GENERATE_RESULT" | grep -o '"template_url":"[^"]*' | sed 's/"template_url":"//')
    echo -e "${BLUE}Template URL: $TEMPLATE_URL${NC}"
else
    echo -e "${YELLOW}! Template generation endpoint not implemented or failed${NC}"
    echo "$GENERATE_RESULT"
fi

# Instructions for using the template in frontend
echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN}         TEMPLATE TESTS COMPLETED                 ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo -e "To view the template generator in the frontend:"
echo -e "1. Make sure the frontend is running (cd frontend && npm start)"
echo -e "2. Navigate to http://localhost:4200/template-generator"
echo -e "3. Click on 'Load Sample' to prefill the form with healthcare SLA data"
echo -e "4. Submit the form to generate a customized SLA template"
echo -e ""
echo -e "If you're not seeing sample data, check that:"
echo -e "- The backend is running (./start_chakra.sh)"
echo -e "- Example SLA templates are loaded (./add_sla_example.sh)"
echo -e "- API endpoints are properly implemented"
echo -e ""