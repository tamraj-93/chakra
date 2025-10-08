#!/bin/bash
# Test script for template-based consultations

echo "Testing template-based consultations..."

# Set the API base URL
API_URL="http://localhost:8000"

# Get authentication token
echo "Getting auth token..."
TOKEN=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password123"}' \
  | jq -r '.access_token')

if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
  echo "❌ Failed to get auth token. Make sure the server is running and a user exists."
  exit 1
fi

echo "✅ Got auth token"

# Create a test template
echo "Creating test consultation template..."
TEMPLATE_RESPONSE=$(curl -s -X POST "${API_URL}/api/templates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Template",
    "description": "A test template for consultations",
    "domain": "healthcare",
    "version": "1.0",
    "tags": ["test", "healthcare"],
    "initial_system_prompt": "You are a healthcare consultant helping with SLA creation.",
    "stages": [
      {
        "name": "Introduction",
        "description": "Introduce the consultation process",
        "stage_type": "information_gathering",
        "prompt_template": "Welcome to the healthcare SLA consultation. I will guide you through creating an SLA for healthcare services.",
        "system_instructions": "Ask the user about their healthcare organization and needs.",
        "expected_outputs": [
          {
            "name": "organization_type",
            "description": "Type of healthcare organization",
            "data_type": "text",
            "required": true
          },
          {
            "name": "primary_concern",
            "description": "Primary concern for the SLA",
            "data_type": "text",
            "required": true
          }
        ]
      },
      {
        "name": "Requirements",
        "description": "Gather specific requirements",
        "stage_type": "information_gathering",
        "prompt_template": "Now let's discuss your specific requirements for the healthcare SLA.",
        "system_instructions": "Collect detailed information about uptime, response times, and compliance needs.",
        "expected_outputs": [
          {
            "name": "uptime_requirement",
            "description": "Required uptime percentage",
            "data_type": "text",
            "required": true
          },
          {
            "name": "response_time",
            "description": "Required response time",
            "data_type": "text",
            "required": true
          }
        ]
      },
      {
        "name": "Summary",
        "description": "Summarize the consultation",
        "stage_type": "summary",
        "prompt_template": "Let me summarize what we've discussed about your healthcare SLA needs.",
        "system_instructions": "Provide a comprehensive summary of all the information gathered and suggest next steps.",
        "expected_outputs": [
          {
            "name": "summary",
            "description": "Consultation summary",
            "data_type": "text",
            "required": true
          },
          {
            "name": "recommendations",
            "description": "Key recommendations",
            "data_type": "text",
            "required": true
          }
        ]
      }
    ]
  }')

TEMPLATE_ID=$(echo $TEMPLATE_RESPONSE | jq -r '.id')

if [[ -z "$TEMPLATE_ID" || "$TEMPLATE_ID" == "null" ]]; then
  echo "❌ Failed to create template"
  echo "Response: $TEMPLATE_RESPONSE"
  exit 1
fi

echo "✅ Created template with ID: $TEMPLATE_ID"

# Start a consultation session with the template
echo "Starting consultation session with template..."
CHAT_RESPONSE=$(curl -s -X POST "${API_URL}/consultation/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"Hello, I need help with my healthcare SLA.\",
    \"role\": \"user\",
    \"template_id\": \"$TEMPLATE_ID\"
  }")

SESSION_ID=$(echo $CHAT_RESPONSE | jq -r '.session_id')

if [[ -z "$SESSION_ID" || "$SESSION_ID" == "null" ]]; then
  echo "❌ Failed to start consultation session"
  echo "Response: $CHAT_RESPONSE"
  exit 1
fi

echo "✅ Started consultation session with ID: $SESSION_ID"
echo "AI Response: $(echo $CHAT_RESPONSE | jq -r '.message')"

# Continue the conversation to progress through stages
echo "Continuing to next stage..."
NEXT_RESPONSE=$(curl -s -X POST "${API_URL}/consultation/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"I'm from a large hospital network. We need an SLA for our patient record system.\",
    \"role\": \"user\",
    \"session_id\": $SESSION_ID
  }")

echo "✅ Progress to next stage response: $(echo $NEXT_RESPONSE | jq -r '.message')"

# Check if we have template progress information
PROGRESS=$(echo $NEXT_RESPONSE | jq -r '.template_progress // empty')
if [[ ! -z "$PROGRESS" ]]; then
  echo "Template progress info: $PROGRESS"
  COMPLETED_STAGE=$(echo $PROGRESS | jq -r '.completed_stage')
  NEXT_STAGE=$(echo $PROGRESS | jq -r '.next_stage.name')
  PERCENTAGE=$(echo $PROGRESS | jq -r '.progress_percentage')
  echo "✅ Completed stage: $COMPLETED_STAGE"
  echo "✅ Next stage: $NEXT_STAGE"
  echo "✅ Progress percentage: $PERCENTAGE%"
else
  echo "❌ No template progress information received"
fi

echo "Test completed!"