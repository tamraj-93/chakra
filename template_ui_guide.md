# Template-Based Consultation UI Guide

This guide explains how template-based consultations are presented in the Chakra UI and how users interact with them.

## Overview

The template-based consultation feature provides a guided conversation experience where:
- Users are led through predefined stages in a specific order
- Each stage focuses on gathering specific information
- The AI assistant guides the user through each step
- Progress is tracked and displayed to the user

## User Interface Components

### 1. Chat Interface

The primary interaction point is the **Chat Box** component (`chat-box.component.ts`). Here's what to look for:

![Chat Interface](https://placeholder-for-chat-interface.png)

- **Chat Messages**: Displays the conversation between the user and the AI assistant
- **Progress Indicator**: Shows which stage of the template is currently active
- **Input Box**: Where users type their responses to the assistant's questions
- **Send Button**: Submits the user's message and advances to the next stage when appropriate

### 2. Template Selection

Before starting a guided consultation, users select a template from available options:

![Template Selection](https://placeholder-for-template-selection.png)

- **Template Cards**: Display available templates with title, description, and domain
- **Start Button**: Begins a consultation using the selected template
- **Preview Option**: Allows viewing the template structure before starting

### 3. Stage Progression UI

As users progress through the template stages, they see:

![Stage Progression](https://placeholder-for-stage-progression.png)

- **Stage Name**: Shows the current stage (e.g., "Service Identification")
- **Progress Bar**: Visual indicator of overall completion percentage
- **Stage Description**: Brief explanation of the current stage's purpose
- **AI Prompts**: Template-specific questions from the AI assistant

### 4. Session Status

The UI provides feedback on session status:

![Session Status](https://placeholder-for-session-status.png)

- **Completed Stages**: Visual checkmarks next to completed stages
- **Current Stage**: Highlighted to show active focus
- **Upcoming Stages**: Shown but disabled until reached

## User Interaction Flow

### Step 1: Template Selection
1. User navigates to the "Templates" section
2. Browses available consultation templates
3. Selects a template that matches their needs
4. Clicks "Start Consultation" to begin

### Step 2: Stage 1 - Initial Information
1. AI assistant introduces the first stage (e.g., "Service Identification")
2. Asks specific questions defined in the template
3. User responds with relevant information
4. System stores responses as outputs for this stage

### Step 3: Stage Progression
1. After user provides information for Stage 1
2. AI processes the response and stores outputs
3. **Automatic Progression**: UI updates to show next stage
4. Progress indicator advances
5. AI introduces the next stage with template-specific prompts

### Step 4: Completion
1. After completing the final stage
2. System marks the consultation as completed
3. AI provides a summary of all gathered information
4. User can view the complete record and generated outputs

## Backend Interaction

While not visible to users, the following happens behind the scenes:

1. Template ID is attached to the consultation session
2. Current stage index is tracked in session_state
3. User responses are stored as outputs for each stage
4. Template progression is managed automatically
5. Stage-specific prompts guide the AI responses

## Example User Journey

**Example: SLA Requirements Gathering**

1. User selects "SLA Requirements Gathering" template
2. AI introduces itself and explains the consultation process
3. **Stage 1 (Service Identification)**:
   - AI: "Let's start by identifying the services that will be covered by the SLA. What IT or business services do you need to define service levels for?"
   - User: "We need SLAs for our web application, database service, and API gateway."
   - UI updates to show Stage 1 complete
4. **Stage 2 (Performance Metrics)**:
   - AI: "Now, let's define the key performance metrics for each service..."
   - User provides metrics information
   - Progress bar updates to ~50%
5. **Stage 3 (Support Levels)**:
   - AI asks about support tiers and escalation procedures
   - User provides support tier information
   - Progress bar updates to ~75%
6. **Stage 4 (SLA Summary)**:
   - AI summarizes all gathered information
   - Progress bar shows 100% complete
   - User receives comprehensive SLA requirements document

## Testing the UI Flow

To test the template-based consultation UI:

1. Start the frontend application
2. Log in with test credentials
3. Navigate to Templates section
4. Select a template and begin consultation
5. Observe how the UI guides you through each stage
6. Check that progress indicators update correctly
7. Verify that responses are stored between stages
8. Confirm that the final summary includes all provided information

## Debugging UI Issues

If the UI does not progress through stages properly:

1. Check browser console for errors
2. Verify template_progress data in network responses
3. Ensure session_state is being updated correctly
4. Check that stage_id values match expected progression