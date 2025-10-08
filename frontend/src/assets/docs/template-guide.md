# Template-Based Consultation Implementation Guide

## Overview
This document guides you through testing and using the template-based consultation feature that has been implemented in the Chakra application.

## Prerequisites
1. Backend server running with template API endpoints
2. Angular frontend application properly configured
3. User authentication in place

## Test Flow

### 1. Start Backend & Frontend
```bash
# Start the backend server
./start_backend.sh

# In another terminal, start the frontend
cd frontend
npm start
```

### 2. Access the Debug Tools
The debug tools provide a convenient way to test templates without navigating through the regular user flow:

1. Open your browser to `http://localhost:4200`
2. Log in with your credentials
3. Click on the "Debug" link in the navbar (you should see it since we enabled the `isDeveloper` flag)
4. You'll be taken to the `/dev/debug` page with tools for testing

### 3. Testing Template API
From the Debug Tools page:

1. Click "Test Templates API" to verify that the backend is correctly returning template data
2. You should see a JSON response with available templates
3. If the API test fails, check your backend server and API endpoints

### 4. Testing Template Consultation
From the Debug Tools page:

1. The page should display a list of available templates
2. Click "Test Template" on any template to start a template-based consultation
3. This will navigate you to `/template-consultation/{id}` with the template loaded
4. You should see:
   - The template name and description
   - A progress bar showing template stages
   - The chat interface for the current stage

### 5. Alternatively, Use the Templates Page
You can also use the standard user flow:

1. Click on "Templates" in the navbar
2. Select a template from the list
3. Follow the same steps as above

## Template Progress Component
The `<app-template-stage-progress>` component visualizes:

- All stages in the current template
- The current active stage
- Progress through the stages
- Optional descriptions for each stage

## Troubleshooting

### If templates don't appear:
- Check the browser console for errors
- Verify API endpoints at `/api/consultation_templates/templates` (not `/api/templates` or `/api/consultation/templates`)
- Ensure the Template service is correctly configured with the proper endpoint

### If stage progress doesn't display:
- Verify the `TemplateStageProgressComponent` is registered in app.module.ts
- Check that the template includes properly structured stages
- Look for console errors related to missing properties

### If navigation between stages fails:
- Check the consultation service's implementation of stage transitions
- Verify the API endpoints for stage completion
- Look for console errors on stage transition calls

## Developer Features
For developers, additional tools are available:

- The `/dev/debug` page shows all templates and provides direct access to them
- API testing buttons help verify backend connectivity
- Template progress can be shown/hidden with the sidebar toggle

## Next Steps
Consider implementing:

1. Saving partial progress in template consultations
2. Export functionality for completed consultations
3. Enhanced visualizations for stage transitions