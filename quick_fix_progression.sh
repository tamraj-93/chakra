#!/bin/bash
# Quick Stage Progression Fix for Hackathon Demo
# Usage: ./quick_fix_progression.sh SESSION_ID
# Example: ./quick_fix_progression.sh 123

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for session ID
if [ -z "$1" ]; then
    echo -e "${YELLOW}No session ID provided, using test ID 12345${NC}"
    SESSION_ID=12345
else
    SESSION_ID=$1
fi
# For testing purposes in a development environment:
if [ "$SESSION_ID" = "test" ]; then
    echo -e "${GREEN}Test mode: Simulating successful stage progression${NC}"
    echo '{"success": true, "current_stage_index": 2, "progress_percentage": 50}' > /tmp/stage_progression_response.json
    cat /tmp/stage_progression_response.json
    exit 0
fi

API_URL="http://localhost:8000/api/consultation/sessions/$SESSION_ID/force-next-stage"

# For testing purposes, we'll use a valid token
echo -e "${YELLOW}Using valid authentication token...${NC}"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTc1OTMxNDU0Mn0.DaWSwX1HWgCLT4fMdLmNUNw4wU8oj3Y0dS6Pskm_STY"

echo -e "${YELLOW}Forcing progression to next stage for session $SESSION_ID...${NC}"

# Make the API call
response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{}" \
    "$API_URL")

# Check if successful
if [[ $response == *"current_stage_index"* || $response == *"success"* ]]; then
    # Try to extract stage index
    new_stage=$(echo $response | grep -o '"current_stage_index":[0-9]*' | cut -d':' -f2)
    if [ -z "$new_stage" ]; then
        new_stage="next"
    fi
    
    # Try to extract progress percentage
    progress=$(echo $response | grep -o '"progress_percentage":[0-9]*' | cut -d':' -f2)
    if [ -z "$progress" ]; then
        progress="updated"
    fi
    
    echo -e "${GREEN}Success! Advanced to stage $new_stage with $progress% progress.${NC}"
else
    echo -e "${RED}Error: Failed to progress stage.${NC}"
    echo "Response: $response"
    exit 1
fi