#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}    Chakra Knowledge Capture Demo    ${NC}"
echo -e "${BLUE}=====================================${NC}"

# Get auth token for API access
source ./get_auth_token.sh

TOKEN=$(get_auth_token)

# Create a consultation with structured data for demonstration
echo -e "\n${YELLOW}Step 1: Creating infrastructure SLA consultation${NC}"
echo -e "Creating consultation with enhanced structured data visualization..."

# Visual stage transition
echo -e "\n${BLUE}[25%]${NC} Initializing consultation..."
sleep 1

# Define the JSON payload with sample structured data
read -r -d '' PAYLOAD << EOM
{
  "user_id": 1,
  "messages": [
    {
      "role": "user",
      "content": "I need help creating an SLA for our infrastructure services."
    },
    {
      "role": "assistant",
      "content": "I can help you create an infrastructure SLA. Let me gather some information about your requirements."
    },
    {
      "role": "user",
      "content": "We run multiple data centers and need to ensure high availability."
    },
    {
      "role": "assistant", 
      "content": "Let me collect the specific SLA terms for your infrastructure services. Can you confirm the following availability targets?"
    },
    {
      "role": "user",
      "content": "We need 99.999% for critical systems, 99.99% for high priority, and 99.9% for standard services."
    },
    {
      "role": "assistant",
      "content": [
        {
          "service_level": "Critical",
          "availability": "99.999%",
          "allowed_downtime_per_year": "5.26 minutes",
          "monitoring": "Real-time",
          "notification_channels": ["SMS", "Email", "Phone", "Dashboard"]
        },
        {
          "service_level": "High Priority",
          "availability": "99.99%",
          "allowed_downtime_per_year": "52.6 minutes",
          "monitoring": "Every 1 minute",
          "notification_channels": ["Email", "Dashboard", "SMS"]
        },
        {
          "service_level": "Standard",
          "availability": "99.9%",
          "allowed_downtime_per_year": "8.76 hours",
          "monitoring": "Every 5 minutes",
          "notification_channels": ["Email", "Dashboard"]
        }
      ]
    },
    {
      "role": "user",
      "content": "That looks good. Can you also include details about performance metrics?"
    },
    {
      "role": "assistant",
      "content": {
        "performance_metrics": {
          "response_time": {
            "web_applications": "< 2 seconds",
            "api_endpoints": "< 300 ms",
            "database_queries": "< 100 ms"
          },
          "throughput": {
            "network": "10 Gbps minimum",
            "transaction_processing": "1000 TPS minimum",
            "batch_processing": "50,000 records/minute minimum"
          },
          "measurement_methodology": {
            "sampling_frequency": "Every 5 minutes",
            "measurement_points": ["Edge", "Application tier", "Database tier"],
            "reporting_period": "Hourly aggregates with daily reports"
          }
        },
        "service_credits": {
          "availability_breach": {
            "99.9% to 99.0%": "10% monthly fee",
            "99.0% to 95.0%": "25% monthly fee",
            "Below 95.0%": "50% monthly fee"
          },
          "response_time_breach": {
            "110% of target": "5% monthly fee",
            "150% of target": "10% monthly fee",
            "200% of target": "15% monthly fee"
          }
        }
      }
    },
    {
      "role": "user",
      "content": "This looks comprehensive. Can we finalize the SLA now?"
    },
    {
      "role": "assistant",
      "content": "I've completed the SLA for your infrastructure services based on your requirements. Here's a summary of what we've defined:\n\n1. **Service Levels**:\n   - Critical: 99.999% availability (5.26 minutes downtime/year)\n   - High Priority: 99.99% availability (52.6 minutes downtime/year)\n   - Standard: 99.9% availability (8.76 hours downtime/year)\n\n2. **Performance Metrics**:\n   - Response times for web, API, and database operations\n   - Throughput requirements for network and processing\n   - Measurement methodology with sampling points\n\n3. **Service Credits**:\n   - Tiered compensation structure for availability and performance breaches\n\nThe SLA is now ready for implementation across your data centers."
    },
    {
      "role": "user", 
      "content": "Perfect, thank you!"
    }
  ],
  "template_id": 2,
  "title": "Infrastructure SLA Demo - Knowledge Capture"
}
EOM

# Visual stage transition
echo -e "\n${BLUE}[50%]${NC} Preparing to send API request..."
sleep 1

# Call the API to create the consultation
echo -e "\n${YELLOW}Sending consultation data to API...${NC}"

CONSULTATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/consultations/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Extract the consultation ID from response
CONSULTATION_ID=$(echo $CONSULTATION_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

# Visual progress bar
echo -e "\n${BLUE}[75%]${NC} Creating consultation"
for i in {1..5}; do
  echo -n "."
  sleep 1
done
echo " Done!"

# Final summary message
echo -e "\n${GREEN}✓ Demo infrastructure SLA consultation created successfully!${NC}"
echo -e "${YELLOW}Consultation Details:${NC}"
echo -e "---------------------"
echo -e "ID: ${GREEN}$CONSULTATION_ID${NC}"
echo -e "Title: ${GREEN}Infrastructure SLA Demo - Knowledge Capture${NC}"
echo -e "Template ID: ${GREEN}2${NC}"
echo -e "User ID: ${GREEN}1${NC}"
echo -e "Message Count: ${GREEN}9${NC}"
echo -e "---------------------"

echo -e "\n${BLUE}[100%]${NC} Knowledge capture cycle complete!"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. Access the frontend at ${GREEN}http://localhost:4200${NC}"
echo -e "2. Navigate to the consultation (ID: ${GREEN}$CONSULTATION_ID${NC})"
echo -e "3. Click 'Create Template from Consultation' to extract reusable template"
echo -e "4. Review and edit the extracted template structure"
echo -e "5. Save the template to create a new reusable template"
echo -e "6. Use the new template to start another consultation"

echo -e "\n${BLUE}=====================================${NC}"
echo -e "${BLUE}   Knowledge Capture Demo Complete    ${NC}"
echo -e "${BLUE}=====================================${NC}"