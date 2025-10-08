# Chakra Knowledge Capture System - Hackathon Demo

This repository contains the implementation of the Chakra Knowledge Capture System, which demonstrates how to turn successful AI consultations into reusable templates.

## Key Features

- **Structured Data Visualization**: Format complex information into readable components
- **Automated Template Extraction**: Use AI to identify stages, prompts, and expected outputs
- **Interactive Template Editor**: Review and customize extracted templates
- **Knowledge Repository**: Build a library of templates capturing expertise

## Setup Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/tamraj-93/chakra.git
   cd chakra
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd ..
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Start the services:
   ```bash
   ./restart_services.sh
   ```

## Running the Demo

### Option 1: Using the Demo Script

1. Run the knowledge capture demo script:
   ```bash
   ./examples/create_knowledge_capture_demo.sh
   ```

2. Open the frontend in your browser:
   ```
   http://localhost:4200
   ```

3. Follow the steps displayed after the script completes.

### Option 2: Manual Testing

1. Access the frontend at http://localhost:4200
2. Log in with the demo credentials (username: `demo`, password: `demo`)
3. Navigate to Templates and start a consultation using the "Infrastructure SLA" template
4. Complete the consultation following the prompts
5. Once completed, click the "Create Template from Consultation" button
6. Review and edit the extracted template
7. Save the template
8. Start a new consultation using your newly created template

## Demo Flow

1. **Run a structured consultation** to gather and format SLA requirements
2. **Click "Create Template"** to extract consultation patterns
3. **Review and customize** the generated template structure
4. **Save the template** to make it available in the template library
5. **Start new consultations** using the newly created template

## Testing End-to-End Flow

To test the complete knowledge capture flow:

1. Run `./restart_services.sh` to ensure both backend and frontend are running
2. Run `./examples/create_knowledge_capture_demo.sh` to create a sample consultation
3. Open the frontend and log in
4. Navigate to the consultation list and open the newly created consultation
5. Click "Create Template from Consultation" and follow the process
6. Verify the new template appears in the template library
7. Start a new consultation using the template you just created
8. Confirm that the new consultation follows the structure of your template

## Presentation Materials

- View the demo presentation slide by opening `examples/hackathon_presentation.html` in your browser
- Use the presentation as a guide for demonstrating the system during the hackathon