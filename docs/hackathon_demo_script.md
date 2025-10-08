# Chakra SLA Template System: Hackathon Demo Script

## Introduction

Welcome to our demonstration of Chakra, a specialized AI assistant for creating and managing Service Level Agreements (SLAs). Today, we'll show you how Chakra revolutionizes the SLA creation process by capturing expert knowledge and transforming it into reusable templates.

## Demo Setup

Before the demo, make sure to set up the environment:

1. Start the backend server: `./start_backend.sh`
2. Start the frontend application: `./start_chakra.sh`
3. Create the demo examples: `./setup_hackathon_demo.sh`

## Demo Flow

### 1. The SLA Consultation Problem (2 minutes)

**Context Setting:**
- SLAs are complex documents requiring specialized knowledge
- Traditional consulting is time-consuming and expensive
- Organizations struggle to maintain consistency across SLAs

**Our Solution:**
- AI-guided consultations for SLA creation
- Knowledge capture and template generation
- Reusable frameworks for consistent SLAs
- Enhanced visualization of structured data

### 2. Enhanced Visualization Demo (4 minutes)

**Step 1: Healthcare SLA Example**
- Navigate to the consultation list
- Open the "Healthcare Cloud SLA Demo - Enhanced Visualization" consultation
- Point out the enhanced structured data visualization:
  - Hierarchical display of complex JSON data
  - Color-coded data types (strings, numbers, booleans)
  - Clear visual separation between properties
  - Improved readability for nested objects

**Step 2: Infrastructure SLA Example**
- Navigate back to the consultation list
- Open the "Infrastructure SLA Demo - Advanced Visualization" consultation
- Highlight the array visualization improvements:
  - Numbered list format for array items
  - Clear property names and values
  - Visual hierarchy for nested objects

**Step 3: Review structured outputs**
- Show how Chakra organizes the collected information
- Highlight how the enhanced visualization improves understanding
- Demonstrate the consultation summary with structured data

### 3. Knowledge Capture: Converting to a Template (3 minutes)

**Step 1: Access the SLA Template Generator**
- Navigate to "SLA to Template" feature
- Select our completed consultation from the list

**Step 2: Template Creation Process**
- Name the template "Healthcare Cloud SLA Template"
- Add appropriate description and tags
- Demonstrate how LLM analyzes the conversation structure

**Step 3: Review Generated Template**
- Show the identified stages and flow
- Highlight how the system extracted structured fields
- Explain how domain knowledge was preserved

### 4. Template Reuse: Scaling Knowledge (3 minutes)

**Step 1: Access the Templates Library**
- Navigate to the Templates section
- Find our newly created Healthcare Cloud SLA Template

**Step 2: Start a New Guided Consultation**
- Launch a new consultation using the template
- Demonstrate the guided, stage-based approach
- Show how the template enforces consistency

**Step 3: Complete a New SLA Rapidly**
- Complete the template stages efficiently
- Show how it reduces time-to-completion
- Generate a final SLA document

### 5. Business Impact & Future Directions (2 minutes)

**Value Proposition:**
- Knowledge preservation: Expert insights captured in templates
- Consistency: Standardized approach across the organization
- Efficiency: 70% reduction in SLA creation time
- Quality: Higher compliance with industry standards
- Enhanced user experience: Improved visualization of complex data

**Next Steps:**
- Template refinement through usage analytics
- Industry-specific template libraries
- Integration with contract management systems
- Additional visualization patterns for different data types

## Technical Demonstration Points

Throughout the demo, highlight these key technical aspects:

1. **Enhanced Data Visualization**
   - Structured JSON data formatting
   - Visual hierarchy for nested objects
   - Color-coding of different data types
   - Responsive layout for complex information

2. **Structured Data Collection**
   - Stage-based information gathering
   - Field validation and type enforcement
   - Progress tracking and visualization
   - Improved presentation of collected data

3. **LLM-Assisted Template Generation**
   - Conversation analysis and stage identification
   - System prompt generation
   - Expected output extraction
   - Structured data extraction and formatting

4. **Template Execution System**
   - State management across consultation stages
   - Dynamic UI component rendering
   - Validation and progress tracking
   - Enhanced display of structured outputs

5. **Knowledge Management**
   - Template versioning and sharing
   - Domain-specific categorization
   - Structured data preservation

## Technical Implementation Details

For engineers and technical evaluators, be prepared to discuss these implementation aspects:

### Enhanced Visualization Component

1. **JSON Processing Logic**
   - Recursive rendering of nested objects and arrays
   - Type detection and appropriate styling
   - Collapsible sections for large data structures

2. **CSS Styling Enhancements**
   - Color-coded data types for clarity
   - Consistent visual hierarchy
   - Responsive layout for different screen sizes

3. **Angular Integration**
   - Custom pipe for structured data formatting
   - Safe HTML rendering with sanitization
   - DOM manipulation for complex data structures

### Demonstration Examples

Our demo includes two example consultations that showcase different aspects of structured data visualization:

1. **Healthcare Cloud SLA Example**
   - Demonstrates nested objects visualization
   - Shows complex compliance requirements
   - Displays hierarchical support levels

2. **Infrastructure SLA Example**
   - Shows array-based data visualization
   - Demonstrates performance metrics presentation
   - Illustrates service credit structures

### Running the Demo

To set up the demo environment:
```bash
# Start the backend server
./start_backend.sh

# Start the frontend application
./start_chakra.sh

# Create the demo examples with enhanced visualization
./setup_hackathon_demo.sh
```
   - Public vs. private template libraries

## Q&A Preparation

Anticipate these questions:

1. How does the system handle edge cases in SLA requirements?
2. Can templates be customized for specific industries?
3. How much human oversight is needed in the template generation?
4. What's the accuracy of the LLM in extracting structured data?
5. How does this compare to existing SLA generation tools?