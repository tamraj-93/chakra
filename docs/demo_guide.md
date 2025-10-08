# Chakra Demo Guide: Template-Based Consultations

This document provides a comprehensive guide for demonstrating the Chakra application's template-based consultation features. Use this guide to showcase the capabilities of the system during your hackathon presentation.

## 1. System Overview

Chakra is an intelligent consultation assistant that provides structured guidance for complex discussions. The system offers:

- **Template-Based Consultations**: Pre-defined conversation flows for different domains
- **Context-Aware Responses**: Maintains understanding throughout the conversation
- **Structured Data Collection**: Gathers information in an organized manner
- **Action Item Generation**: Creates summaries and next steps for users

## 2. Key Features to Showcase

### 2.1 Template Selection
- Demonstrate how users can browse different consultation templates
- Show filtering by domain (healthcare, tech support, financial)
- Point out the template preview feature

### 2.2 Guided Conversation Flow
- Show how the system guides users through conversation stages
- Highlight the progress indicator showing advancement through the template
- Demonstrate how the system keeps users on track with gentle guidance

### 2.3 Context Cards
- Show how key information is extracted and displayed in context cards
- Demonstrate editing/correcting information as the conversation progresses
- Point out how this information persists throughout the conversation

### 2.4 Summary Generation
- Show the automatic generation of consultation summaries
- Demonstrate exporting/sharing options
- Point out how action items are clearly highlighted

## 3. Demo Scenarios

### 3.1 Health Consultation Demo

**Scenario**: A user experiencing persistent headaches seeks guidance

**Flow**:
1. **Template Selection**: User selects "Health Symptom Assessment" template
2. **Symptom Gathering**: System asks structured questions about symptoms
   - Duration: "2 weeks"
   - Severity: "7/10"
   - Triggers: "Worse after screen time"
3. **Medical History**: System collects relevant medical context
4. **Risk Assessment**: System evaluates if urgent care is needed
5. **Recommendations**: System provides structured guidance
   - Self-care strategies
   - When to see a doctor
   - Lifestyle adjustments
6. **Summary**: System generates a consultation summary with action items

**Key Points to Highlight**:
- The system's ability to ask relevant follow-up questions
- How medical context is maintained throughout the conversation
- The clear, actionable recommendations

### 3.2 Technical Support Demo

**Scenario**: A user experiencing computer performance issues

**Flow**:
1. **Template Selection**: User selects "Technical Issue Troubleshooting" template
2. **Problem Identification**: System gathers details about the performance issue
3. **System Information**: System collects relevant technical specifications
4. **Troubleshooting Steps**: System provides step-by-step guidance
5. **Resolution**: System confirms issue resolution or suggests next steps
6. **Summary**: System generates a technical support report

**Key Points to Highlight**:
- How the system adapts questions based on the specific technical issue
- The step-by-step troubleshooting approach
- The technical summary that could be shared with IT support

### 3.3 Financial Advisory Demo

**Scenario**: A user planning for retirement savings

**Flow**:
1. **Template Selection**: User selects "Financial Goal Planning" template
2. **Goal Identification**: System helps articulate specific retirement goals
3. **Financial Situation**: System gathers current financial status
4. **Gap Analysis**: System identifies gaps between current state and goals
5. **Action Plan**: System creates a structured financial action plan
6. **Resources**: System suggests helpful tools and professionals
7. **Summary**: System generates a financial planning summary

**Key Points to Highlight**:
- How the system helps transform vague goals into specific ones
- The gap analysis visualization
- The time-based action plan with immediate and long-term steps

## 4. Technical Implementation Details

### 4.1 Template Structure
- Templates define conversation stages and expected data collection
- Each stage has specific prompt templates and system instructions
- Stages can branch based on user responses

### 4.2 Context Management
- Information is extracted and stored in a structured session state
- Previous responses inform future questions
- Context is maintained across the entire conversation

### 4.3 Response Generation
- Specialized prompts guide the AI to provide structured responses
- System instructions ensure consistent, helpful interactions
- Expected outputs ensure all necessary information is collected

## 5. Demonstration Tips

- **Start with a clear scenario**: Begin each demo with a relatable user scenario
- **Highlight the structure**: Point out how the conversation follows a logical progression
- **Show the benefits**: Emphasize how this approach improves on unstructured chat
- **Demonstrate customization**: Show how templates can be adapted for different needs
- **End with outcomes**: Always conclude by showing the tangible outputs (summaries, action items)

## 6. Q&A Preparation

Be prepared to answer questions about:

- How templates are created and customized
- How the system handles unexpected user responses
- Data privacy and security considerations
- How the system could integrate with other tools/systems
- Future development plans and potential use cases