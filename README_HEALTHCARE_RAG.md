# Chakra - Healthcare SLA Management with RAG

Chakra is a Service Level Agreement (SLA) management platform enhanced with Retrieval Augmented Generation (RAG) technology, specifically tailored for healthcare organizations.

## Features

- **SLA Creation & Management**: Create, view, and manage Service Level Agreements through guided consultations
- **RAG-Enhanced Recommendations**: Get intelligent recommendations based on healthcare regulations and best practices
- **Healthcare Knowledge Base**: Access to specialized healthcare requirements like HIPAA compliance
- **Document Generation**: Automatically generate complete, compliant SLA documents
- **Source Citations**: View references to specific healthcare regulations and standards

## Setup & Installation

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- npm or yarn
- Git

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/tamraj-93/chakra.git
   cd chakra
   ```

2. Setup backend:
   ```
   cd backend
   pip install -r requirements.txt
   python -m scripts.init_db
   ```

3. Setup frontend:
   ```
   cd ../frontend
   npm install
   ```

4. Start the services:
   ```
   # Start backend (from root directory)
   ./start_backend.sh

   # Start frontend (from root directory)
   ./restart_frontend.sh
   ```

## Testing the Healthcare RAG Integration

Follow these steps to test the complete end-to-end flow of the healthcare RAG integration:

### 1. Setup Knowledge Base

1. Login to the application
2. Navigate to "Knowledge Base" from the navbar
3. Click "Upload Document"
4. Upload the healthcare document from `/docs/demo docs/healthcare_security requirements.md`
5. In the upload form, you'll see a "Document Tags" field or dropdown - select or type "healthcare" in this field. This tags the document as healthcare-related in the knowledge base so the RAG system can properly categorize it. If you don't see a specific tagging option, look for:
   - A "Category" dropdown (select "Healthcare" or "Medical")
   - A "Tags" text field (type "healthcare, HIPAA")
   - Industry/Domain selection (choose "Healthcare")
6. Click "Process Document" to add it to the RAG system

### 2. Start Healthcare SLA Consultation

1. Navigate to "Templates" from the navbar
2. Select the "Healthcare EHR Hosting SLA" template
3. Click "Start Consultation"
4. Complete the consultation by asking these specific questions to test the RAG system:
   - When asked about the type of healthcare service, mention "EHR Hosting"
   - For security requirements, ask "What HIPAA security controls should I include?"
   - After receiving the HIPAA security controls answer, continue with these follow-up questions:
     
     **Technical Questions**:
     - "What encryption standards should I use for Protected Health Information (PHI)?"
     - "How often should security risk assessments be performed under HIPAA?"
     - "What are the requirements for audit logging in healthcare systems?"
     
     **Compliance Questions**:
     - "What should be included in a HIPAA-compliant Business Associate Agreement?"
     - "How should we handle patient data breaches under HIPAA?"
     - "What are the retention requirements for healthcare records?"
     
     **SLA-Specific Questions**:
     - "What uptime guarantees should be included for an EHR system?"
     - "What response times are appropriate for healthcare system incidents?"
     - "How should we define severity levels for healthcare system issues?"
     
   - Note how the system provides healthcare-specific answers with source citations for each question
   - Look for references to specific HIPAA sections, healthcare standards, or other authoritative sources

### 3. Complete the Consultation

1. Continue asking all recommended questions listed in the documentation
2. The "Complete Consultation" button is always visible at the bottom right of the chat interface for easy demo access
3. Click the "Complete Consultation" button when you feel you've gathered enough information
4. Confirm when prompted "Are you ready to complete this consultation?"
5. You'll see a summary of all collected information
6. Click "Export Results"
   - An alert will appear confirming "SLA document has been generated! Redirecting to My SLAs page."
6. You'll be automatically redirected to the "My SLAs" page
   - A green success banner will appear at the top of the page: "Success! Your SLA document has been generated successfully."
   - The success message will automatically dismiss after 10 seconds, or you can close it manually
   - The newly generated SLA will be at the top of the list with a "Draft" status
   - This confirms that your consultation has been completed and converted to an SLA document

### 4. View and Manage Generated SLAs

1. On the "My SLAs" page, you'll see your newly generated SLA
2. Click "View" to see the complete document:
   - If the document appears blank, we've implemented a fix that will now show an error message
   - The error message will direct you to use the "Export as PDF" button
   - **Alternative Method**: Use the "Export" button directly from the My SLAs list to download the SLA as PDF
3. Test the filter functionality (filter by "Healthcare" type)
4. Use the status dropdown to change the document status (Draft → Review → Approved → Active)
5. **Note**: We've made improvements to ensure at least sample content is visible for each SLA document

### 5. Verify RAG Integration Features

During this flow, look for these specific RAG features:

- **Healthcare Mode Indicator**: Green banner at the top of the consultation showing "Healthcare Knowledge Enhanced"
- **Source Citations**: Look for "Healthcare References" section below AI responses
- **HIPAA Badge**: A small "HIPAA" badge next to the assistant's name
- **Healthcare-Specific Content**: Responses should include specific references to HIPAA requirements and healthcare standards

### 6. Evaluating the RAG System Performance

To properly evaluate how well the RAG system works, assess these aspects:

1. **Retrieval Relevance**: Are the citations relevant to the question being asked?
   - Good: Citations about encryption standards when asking about PHI encryption
   - Poor: Citations about general IT practices not specific to healthcare

### 7. Hackathon Demo Tips

For a successful hackathon demonstration, follow these recommendations:

1. **Prepare Specific Examples**: 
   - Have 3-4 healthcare-specific questions ready to demonstrate
   - Choose questions that highlight different aspects of healthcare compliance

2. **Highlight Key Features**:
   - Point out the "Healthcare Knowledge Enhanced" banner when it appears
   - Show how source citations provide evidence for the AI responses
   - Point out the "Complete Consultation" button that is always visible for easy demo access

3. **Explain the End-to-End Flow**:
   - Upload document → Start consultation → Ask questions → Complete consultation → Export SLA
   - Emphasize how the RAG system enhances the quality of healthcare-specific responses

4. **Fallback Options**:
   - If the system is slow, mention that you've implemented a lightweight option
   - If citations don't appear for a specific question, try an alternative question from your prepared list

2. **Answer Accuracy**: Are the answers factually correct according to healthcare regulations?
   - Test by comparing responses to information from official HHS/HIPAA documentation
   - The system should correctly reference specific HIPAA sections (e.g., Security Rule § 164.312)

3. **Context Integration**: Does the system incorporate knowledge from your uploaded documents?
   - Look for citations that specifically reference your uploaded healthcare document
   - If you uploaded document mentions "quarterly assessments," this should appear in responses

4. **Consultation Depth**: The system should allow approximately 10-15 turns of conversation before completing
   - This is sufficient to cover the essential aspects of a healthcare SLA
   - The conversation should naturally progress through technical, compliance, and operational aspects

5. **Grounding vs. Hallucination**: Evaluate if responses are grounded in the knowledge base
   - Good: "According to the uploaded document on healthcare security requirements..."
   - Poor: Making specific claims without citation or source reference

## Development

To reset the database:
```
cd backend
python -m scripts.init_db --reset
```

## Advanced Testing

To test the system's performance with different memory constraints:

- Use lightweight mode (reduced resource usage):
  ```
  ./start_chakra.sh --lightweight
  ```

- Use minimal mode (for very limited resources):
  ```
  ./start_chakra.sh --minimal
  ```

## Starting and Stopping the System

### Starting the System
To start the complete system (backend, frontend, and LLM services):
```
./start_chakra.sh
```

### Stopping the System
When you need to stop the system, it's important to properly shut down all components:

1. Use the dedicated stop script which handles all components (frontend, backend, and LLM processes):
```
./stop_chakra.sh
```

This script will:
- Stop the frontend Angular server
- Stop the backend FastAPI server
- Find and terminate any LLM-related processes (Ollama, sentence-transformers, etc.)
- Verify all processes have been properly terminated

If any processes remain after the automatic shutdown, the script will give you the option to force kill them.

### Restarting After Changes
If you've made changes to the code:

1. Stop all services using the stop script:
```
./stop_chakra.sh
```

2. Clear any temporary files and Python cache:
```
rm -rf backend/__pycache__
rm -rf backend/app/__pycache__
```

3. Restart the system:
```
./start_chakra.sh
```

For a quick restart of both frontend and backend without restarting LLM processes:
```
./restart_services.sh
```

## Troubleshooting

### System Performance Issues

If you experience system hanging during initialization:
1. Check system memory using `free -m`
2. If available memory is less than 2GB, use lightweight mode
3. If errors persist, check logs in `server.log`
4. Make sure no old LLM processes are still running from previous sessions

### RAG-Specific Issues

If the RAG system isn't working correctly:

1. **No Citations Appearing**:
   - Check if documents were properly uploaded with the "healthcare" tag
   - Verify document processing completed successfully in the backend logs
   - Try asking more specific healthcare-related questions

2. **Irrelevant Citations**:
   - The query might be too generic; make questions more specific to healthcare
   - Try rephrasing with domain-specific terminology (e.g., "PHI" instead of "data")
   - Check if your uploaded document covers the topic you're asking about

3. **Generic (Non-Healthcare) Responses**:
   - Ensure the consultation was started from a healthcare-specific template
   - Check if the "Healthcare Knowledge Enhanced" banner is visible
   - If missing, restart the consultation and ensure proper template selection

4. **Citation Links Not Working**:
   - This is expected in the demo version - citation links are placeholders
   - In a production environment, these would link to specific document sections
   - The content of the citations should still be relevant even if links are inactive

## License

This project is proprietary and confidential.