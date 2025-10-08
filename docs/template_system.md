# Chakra Template-Based Consultation System

This document provides an overview of the template-based consultation system implemented for the Chakra application.

## 1. System Overview

The template-based consultation system provides a structured approach to conversations, allowing for more meaningful and guided interactions. The system is built on a flexible template model that can be adapted to various domains and use cases.

## 2. Components Implemented

### 2.1 Data Models

- **ConsultationTemplate**: The core template model that defines a structured conversation flow
- **ConsultationStage**: Individual stages within a template (e.g., information gathering, analysis, recommendations)
- **ExpectedOutput**: Specific pieces of information to be collected during each stage
- **Tag**: Categorization system for templates

### 2.2 API Endpoints

- **GET /api/templates**: Retrieve available templates (with filtering options)
- **GET /api/templates/{template_id}**: Get a specific template's details
- **POST /api/templates**: Create a new consultation template
- **PUT /api/templates/{template_id}**: Update an existing template
- **DELETE /api/templates/{template_id}**: Remove a template

### 2.3 Sample Templates

Three comprehensive templates have been created for demonstration:

1. **Health Symptom Assessment**: A structured health consultation that guides users through symptom assessment and provides preliminary guidance.
2. **Technical Issue Troubleshooting**: A step-by-step technical support template for diagnosing and resolving technical issues.
3. **Financial Goal Planning**: A financial advisory template that helps users clarify financial goals and develop action plans.

### 2.4 Database Integration

- Extended database models to support the template system
- Created scripts for initializing the database schema and populating sample templates
- Updated the main initialization script to include template support

### 2.5 Documentation

- Created comprehensive demo guide for showcasing the template system
- Documented the technical implementation and architecture

## 3. Next Steps for Implementation

The following components still need to be implemented to complete the system:

### 3.1 Frontend Components

- Template browser/selector interface
- Context card UI components
- Progress tracking visualizations
- Template-aware chat interface

### 3.2 Session Management

- Enhanced session handling to track progress through templates
- Storage of collected information during conversations
- Resumption of in-progress consultations

### 3.3 Integration with LLM Provider

- Template-aware prompt generation
- Structured information extraction from responses
- Stage-based conversation management

## 4. How to Use

### 4.1 Initialize the Database

```bash
./init_db.sh
```

This will set up the database with all required tables and sample templates.

### 4.2 Explore Available Templates

Use the API endpoint:
```
GET /api/templates
```

### 4.3 Start a Template-Based Consultation

Once the frontend components are implemented, users will be able to:
1. Browse available templates
2. Select a template for their consultation
3. Follow the guided conversation flow
4. Receive structured recommendations and summaries

## 5. Technical Considerations

- Templates are versioned to allow for updates and improvements
- The system supports both public templates and user-specific private templates
- Templates can be customized for different domains and use cases
- Stage-based approach allows for flexible conversation flows with conditional branching