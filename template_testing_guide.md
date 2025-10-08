# Template-Based Consultation Testing Guide

This guide provides step-by-step instructions for testing the template-based consultation features in the Chakra application.

## Prerequisites

1. Make sure both backend and frontend services are properly configured
2. The database should have at least one consultation template defined
3. User authentication is set up (if required by your app)

## Backend Setup Verification

Before testing the frontend, verify that the backend APIs are properly set up:

1. Start the backend server:
   ```bash
   cd /home/nilabh/Projects/chakra/backend
   python -m app.main
   ```

2. Test the template API endpoints:
   ```bash
   # Get all consultation templates
   curl -X GET http://localhost:8000/api/consultation/templates

   # Get a specific template (replace {id} with an actual template ID)
   curl -X GET http://localhost:8000/api/consultation/templates/{id}
   ```

3. Ensure the response includes templates with stages and other required properties

## Frontend Testing

### Step 1: Start the Frontend Application

```bash
cd /home/nilabh/Projects/chakra/frontend
npm start
```

### Step 2: Navigate to the Templates Page

1. Open your browser and go to `http://localhost:4200` (or your configured port)
2. Log in to the application (if authentication is required)
3. Navigate to the Templates section, which should be available in the main navigation

### Step 3: Browse Templates

1. Verify that the templates are displayed in a grid format
2. Check that template details like name, description, domain, and stages count are visible
3. Try the filtering functionality:
   - Search for a specific template by name
   - Filter templates by domain

### Step 4: Start a Template Consultation

1. Select a template and click "Start Consultation"
2. Verify that the consultation starts and you're redirected to the consultation view
3. Check that the initial welcome message is displayed

### Step 5: Test the Consultation Flow

1. Verify the Template Progress Display:
   - Progress bar shows the current position in the consultation
   - Current stage name is clearly displayed
   - Stage count (e.g., "Stage 1 of 5") is visible

2. Progress Through Stages:
   - Respond to the prompts for the first stage
   - Verify that after your response, the assistant replies and the progress advances
   - Check that stage transitions are clearly marked in the chat

3. Test Structured Input (if applicable):
   - When a stage requires structured input, check that the form appears
   - Try submitting the form with missing required fields (should show validation errors)
   - Fill in all required fields and submit
   - Verify that the submission is processed and the consultation advances

4. Toggle the Progress Sidebar:
   - Click the "Hide Progress" button to hide the sidebar
   - Click "Show Progress" to bring it back
   - Check that the progress indicator updates correctly as you advance

### Step 6: Test Completion

1. Progress through all stages of the consultation
2. Verify that the final summary is displayed
3. Check that the consultation is properly marked as completed
4. Try exporting the results (if implemented)

## Testing Mobile Responsiveness

1. Use browser developer tools to simulate mobile devices (e.g., iPhone, Android)
2. Check that the layout adapts appropriately:
   - Template cards stack vertically
   - Progress sidebar is hidden by default
   - Input forms are usable on small screens
   - Chat messages are readable and properly formatted

## Common Issues and Troubleshooting

### Backend Issues

- If templates aren't loading, check the network request in the browser console for errors
- Verify the backend logs for any exceptions or errors
- Check that your database contains valid template data

### Frontend Issues

- If components aren't displaying properly, check the browser console for errors
- Verify that all required modules are imported in the Angular module
- For routing issues, check that all routes are properly configured

## Test Data Generation

If you need to create test templates, use the following curl command:

```bash
curl -X POST http://localhost:8000/api/consultation/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test SLA Template",
    "description": "A template for gathering SLA requirements",
    "domain": "IT Services",
    "version": "1.0",
    "tags": ["SLA", "Requirements", "IT"],
    "initial_system_prompt": "You are an SLA requirements assistant. Help the user define their service level agreement requirements.",
    "stages": [
      {
        "name": "Service Definition",
        "description": "Define the service scope and objectives",
        "stage_type": "information_gathering",
        "prompt_template": "Let's start by defining what service this SLA will cover. Please describe the service in detail, including its purpose and scope.",
        "expected_outputs": [
          {
            "name": "service_description",
            "description": "Detailed description of the service",
            "data_type": "text",
            "required": true
          }
        ]
      },
      {
        "name": "Performance Metrics",
        "description": "Define the key metrics for measuring service performance",
        "stage_type": "structured_input",
        "prompt_template": "Now, let's define the key performance metrics for this service.",
        "expected_outputs": [
          {
            "name": "availability",
            "description": "Service availability target (e.g., 99.9%)",
            "data_type": "number",
            "required": true
          },
          {
            "name": "response_time",
            "description": "Maximum response time for incidents",
            "data_type": "text",
            "required": true
          }
        ],
        "ui_components": {
          "structured_input": {
            "prompt": "Please provide the following performance metrics:",
            "fields": [
              {
                "id": "availability",
                "label": "Service Availability Target",
                "type": "select",
                "options": [
                  {"value": "99.9", "label": "99.9% (8.76 hours downtime/year)"},
                  {"value": "99.99", "label": "99.99% (52.6 minutes downtime/year)"},
                  {"value": "99.999", "label": "99.999% (5.26 minutes downtime/year)"}
                ],
                "required": true,
                "help_text": "Higher availability means less allowed downtime but typically costs more"
              },
              {
                "id": "response_time",
                "label": "Incident Response Time",
                "type": "radio",
                "options": [
                  {"value": "15min", "label": "15 minutes"},
                  {"value": "30min", "label": "30 minutes"},
                  {"value": "1hour", "label": "1 hour"},
                  {"value": "4hours", "label": "4 hours"}
                ],
                "required": true
              }
            ]
          }
        }
      },
      {
        "name": "Summary and Recommendations",
        "description": "Review collected information and provide recommendations",
        "stage_type": "summary",
        "prompt_template": "Based on the information provided, here's a summary of the SLA requirements and my recommendations.",
        "expected_outputs": [
          {
            "name": "sla_summary",
            "description": "Summary of the SLA requirements",
            "data_type": "text",
            "required": true
          }
        ]
      }
    ]
  }'
```

## Expected Results

When testing is successful, you should be able to:

1. Browse and filter available templates
2. Start a consultation based on a selected template
3. Progress through all stages of the consultation with appropriate guidance
4. See clear visual indicators of your progress
5. Submit both free-text responses and structured input
6. Receive a complete summary at the end of the consultation
7. Export or save the consultation results

If any part of this flow fails, consult the troubleshooting section or check the browser console and server logs for more detailed error information.