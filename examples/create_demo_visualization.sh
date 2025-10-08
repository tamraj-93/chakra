#!/bin/bash

# Get auth token for API access
source ./get_auth_token.sh

TOKEN=$(get_auth_token)

# Create a consultation with structured data for demonstration

echo "Creating SLA consultation with enhanced structured data visualization..."

# Define the JSON payload with sample structured data
read -r -d '' PAYLOAD << EOM
{
  "user_id": 1,
  "messages": [
    {
      "role": "user",
      "content": "I need help with my cloud SLA requirements."
    },
    {
      "role": "assistant",
      "content": "I'd be happy to help you with your cloud SLA requirements. Let me collect some structured information about your needs."
    },
    {
      "role": "user",
      "content": "I work in healthcare and need to ensure our data is properly protected."
    },
    {
      "role": "assistant", 
      "content": {
        "service_type": "Healthcare Cloud Services",
        "requirements": {
          "availability": "99.99%",
          "data_protection": {
            "encryption": "AES-256",
            "backup_frequency": "Hourly",
            "retention_period": "7 years"
          },
          "compliance": [
            "HIPAA",
            "GDPR",
            "ISO 27001"
          ],
          "support_levels": {
            "emergency": {
              "response_time": "15 minutes",
              "resolution_time": "4 hours",
              "availability": "24/7/365"
            },
            "high": {
              "response_time": "1 hour",
              "resolution_time": "8 hours",
              "availability": "24/7"
            },
            "medium": {
              "response_time": "4 hours",
              "resolution_time": "24 hours",
              "availability": "Business hours"
            }
          }
        },
        "penalties": {
          "availability_breach": {
            "threshold": "99.9%",
            "credit": "10%"
          },
          "data_breach": {
            "notification": "1 hour",
            "compensation": "Case-by-case evaluation"
          }
        }
      }
    },
    {
      "role": "user",
      "content": "This looks comprehensive. Can you add something about disaster recovery?"
    },
    {
      "role": "assistant",
      "content": {
        "service_type": "Healthcare Cloud Services",
        "requirements": {
          "availability": "99.99%",
          "data_protection": {
            "encryption": "AES-256",
            "backup_frequency": "Hourly",
            "retention_period": "7 years"
          },
          "disaster_recovery": {
            "rpo": "15 minutes",
            "rto": "4 hours",
            "dr_testing": "Quarterly",
            "failover_locations": [
              "US East",
              "US West",
              "EU Central"
            ]
          },
          "compliance": [
            "HIPAA",
            "GDPR",
            "ISO 27001"
          ],
          "support_levels": {
            "emergency": {
              "response_time": "15 minutes",
              "resolution_time": "4 hours",
              "availability": "24/7/365"
            },
            "high": {
              "response_time": "1 hour",
              "resolution_time": "8 hours",
              "availability": "24/7"
            },
            "medium": {
              "response_time": "4 hours",
              "resolution_time": "24 hours",
              "availability": "Business hours"
            }
          }
        },
        "penalties": {
          "availability_breach": {
            "threshold": "99.9%",
            "credit": "10%"
          },
          "data_breach": {
            "notification": "1 hour",
            "compensation": "Case-by-case evaluation"
          },
          "dr_failure": {
            "rto_breach": "15% service credit",
            "rpo_breach": "10% service credit"
          }
        }
      }
    }
  ],
  "template_id": 1,
  "title": "Healthcare Cloud SLA Demo - Enhanced Visualization"
}
EOM

# Call the API to create the consultation
curl -X POST "http://localhost:8000/api/consultations/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"

echo -e "\n\nDemo SLA consultation created successfully with structured data visualization!"
echo "Access the frontend to see the enhanced structured data display."