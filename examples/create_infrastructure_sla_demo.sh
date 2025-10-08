#!/bin/bash

# Get auth token for API access
source ./get_auth_token.sh

TOKEN=$(get_auth_token)

# Create a consultation with structured data for demonstration

echo "Creating infrastructure SLA consultation with enhanced structured data visualization..."

# Visual stage transition
echo "Initializing..."
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
    }
  ],
  "template_id": 2,
  "title": "Infrastructure SLA Demo - Advanced Visualization"
}
EOM

# Visual stage transition
echo "Preparing to send API request..."
sleep 1

# Call the API to create the consultation
curl -X POST "http://localhost:8000/api/consultations/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"

# Visual progress bar
echo -e "\nCreating consultation"
for i in {1..5}; do
  echo -n "."
  sleep 1
done
echo " Done!"

# Final summary message
echo -e "\n\nDemo infrastructure SLA consultation created successfully with structured data visualization!"
echo "Access the frontend to see the enhanced structured data display."
echo "Consultation Details:"
echo "---------------------"
echo "Title: Infrastructure SLA Demo - Advanced Visualization"
echo "Template ID: 2"
echo "User ID: 1"
echo "Messages: $(echo $PAYLOAD | jq '.messages')"
echo "Structured Data: $(echo $PAYLOAD | jq '.messages[-1].content')"
echo "---------------------"