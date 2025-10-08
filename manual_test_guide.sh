#!/bin/bash

# Manual test script for template-based consultations
# This script provides individual commands to test each step of the process

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL for API
BASE_URL="http://localhost:8000"

# Output directory for response files
mkdir -p test_results

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE} MANUAL TESTING GUIDE FOR TEMPLATE CONSULTATIONS ${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "${YELLOW}Run these commands one by one to test the template flow:${NC}\n"

echo -e "${GREEN}1. Check if server is running:${NC}"
echo -e "   curl -s $BASE_URL/health | tee test_results/health.json\n"

echo -e "${GREEN}2. Create a user or login:${NC}"
echo -e "   curl -s -X POST $BASE_URL/auth/login -H \"Content-Type: application/json\" \\
   -d '{\"email\": \"user@example.com\", \"password\": \"password\"}' | tee test_results/login.json"
echo -e "\n   # If login fails, create a new user:"
echo -e "   curl -s -X POST $BASE_URL/auth/signup -H \"Content-Type: application/json\" \\
   -d '{\"email\": \"test@example.com\", \"password\": \"password123\"}' | tee test_results/signup.json\n"

echo -e "${GREEN}3. Store your token:${NC}"
echo -e "   TOKEN=\"your_token_from_login_response\"\n"

echo -e "${GREEN}4. Create a template:${NC}"
echo -e "   curl -s -X POST $BASE_URL/api/templates \\
   -H \"Authorization: Bearer \$TOKEN\" \\
   -H \"Content-Type: application/json\" \\
   -d @test_template.json | tee test_results/template_create.json\n"

echo -e "${GREEN}5. Store the template ID:${NC}"
echo -e "   TEMPLATE_ID=\"template_id_from_response\"\n"

echo -e "${GREEN}6. List available templates:${NC}"
echo -e "   curl -s -X GET $BASE_URL/api/templates \\
   -H \"Authorization: Bearer \$TOKEN\" | tee test_results/templates_list.json\n"

echo -e "${GREEN}7. Start a consultation with the template:${NC}"
echo -e "   curl -s -X POST \"$BASE_URL/consultation/chat?template_id=\$TEMPLATE_ID\" \\
   -H \"Authorization: Bearer \$TOKEN\" \\
   -H \"Content-Type: application/json\" \\
   -d '{\"content\": \"Hello, I need help creating an SLA\", \"role\": \"user\"}' | tee test_results/start_consultation.json\n"

echo -e "${GREEN}8. Store the session ID:${NC}"
echo -e "   SESSION_ID=\"session_id_from_response\"\n"

echo -e "${GREEN}9. Send a message to progress to the next stage:${NC}"
echo -e "   curl -s -X POST \"$BASE_URL/consultation/chat?session_id=\$SESSION_ID\" \\
   -H \"Authorization: Bearer \$TOKEN\" \\
   -H \"Content-Type: application/json\" \\
   -d '{\"content\": \"We need SLAs for our web application, database service, and API gateway.\", \"role\": \"user\"}' | tee test_results/stage1_response.json\n"

echo -e "${GREEN}10. Send another message for the next stage:${NC}"
echo -e "   curl -s -X POST \"$BASE_URL/consultation/chat?session_id=\$SESSION_ID\" \\
   -H \"Authorization: Bearer \$TOKEN\" \\
   -H \"Content-Type: application/json\" \\
   -d '{\"content\": \"For web app: 99.9% uptime, <2s response time. For DB: 99.99% availability.\", \"role\": \"user\"}' | tee test_results/stage2_response.json\n"

echo -e "${GREEN}11. Complete the final stages:${NC}"
echo -e "   curl -s -X POST \"$BASE_URL/consultation/chat?session_id=\$SESSION_ID\" \\
   -H \"Authorization: Bearer \$TOKEN\" \\
   -H \"Content-Type: application/json\" \\
   -d '{\"content\": \"We need three support tiers with escalation path Tier 1 → Tier 2 → Tier 3.\", \"role\": \"user\"}' | tee test_results/stage3_response.json\n"

echo -e "${GREEN}12. Get the session details to verify completion:${NC}"
echo -e "   curl -s -X GET \"$BASE_URL/consultation/sessions/\$SESSION_ID\" \\
   -H \"Authorization: Bearer \$TOKEN\" | tee test_results/session_details.json\n"

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE} EXPECTED OUTCOMES ${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "1. Server health check should return {\"status\": \"healthy\"}"
echo -e "2. Login/signup should return a valid access token"
echo -e "3. Template creation should return a template ID"
echo -e "4. Starting a consultation should include template_progress information"
echo -e "5. Each message response should advance the template stage"
echo -e "6. Final stage should mark the consultation as completed"
echo -e "7. Session details should show completed status"
echo -e "${BLUE}==================================================${NC}"