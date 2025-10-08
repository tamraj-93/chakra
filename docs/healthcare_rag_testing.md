# Healthcare RAG Testing Guide

This guide explains how to test the Retrieval-Augmented Generation (RAG) functionality with healthcare domain knowledge in the Chakra system.

## Prerequisites

- Python 3.9+ (either as `python` or `python3`)
- Pip (either as `pip` or `pip3`)
- Required Python packages:
  - chromadb
  - sentence-transformers 
  - langchain
  - unstructured
  - For visualization: matplotlib, numpy

> Note: The test script will attempt to install missing packages automatically.

## Testing via UI

You can test the healthcare RAG functionality through the Chakra web interface. This allows you to see how the system uses healthcare SLA knowledge to generate better recommendations.

### Step 1: Start the Chakra System

```bash
./start_chakra.sh
```

This script will:
- Set up the Python environment
- Install all dependencies from requirements.txt (including RAG dependencies)
- Start both backend and frontend servers

### Step 2: Upload Healthcare SLA Documents

1. Open your browser and navigate to http://localhost:4200
2. Login with your credentials
3. Navigate to the Knowledge Base section (click "Knowledge Base" in the navigation menu)
4. Upload healthcare-specific SLA documents:
   - Click "Select files" in the Upload Documents section
   - Select healthcare SLA documents from the `/examples` directory:
     - `healthcare_data_security_sla.md` - Contains healthcare data security requirements
     - `healthcare_telemedicine_sla.md` - Contains telemedicine platform requirements
   - Click "Upload Documents"
   - Wait for the documents to be processed (status will change to "processed")

### Step 3: Test RAG-Enhanced Consultations

1. Navigate to "New Consultation" in the main menu
2. Start a consultation focused on healthcare SLAs:
   - Select "Healthcare" as the industry
   - Describe a healthcare-specific scenario (e.g., "I need an SLA for a patient data management system")
   - Include specific requirements that should match your uploaded documents

3. Observe how the system uses the healthcare knowledge base:
   - The system should incorporate relevant information from your uploaded healthcare SLA documents
   - Recommendations should be tailored to healthcare industry standards
   - Generated SLAs should reference appropriate security, compliance, and performance metrics for healthcare

### Step 4: Compare With and Without RAG

To see the difference RAG makes:

1. Delete your uploaded healthcare documents from the Knowledge Base
2. Start a new consultation with the same healthcare scenario
3. Compare the results:
   - Without RAG: Generic SLA recommendations
   - With RAG: Healthcare-specific recommendations with industry-appropriate terms and metrics

## Running the Healthcare RAG Test

1. **Update your environment with the RAG dependencies**:
   ```bash
   ./update_rag_dependencies.sh
   ```
   This will add the necessary RAG packages to your existing Chakra environment.

2. **Run the full test suite**:
   ```bash
   ./run_healthcare_rag_test.sh
   ```
   This script will:
   - Automatically detect your Python installation (`python` or `python3`)
   - Install required dependencies
   - Initialize the RAG system with the latest SLA documents
   - Run a series of healthcare-specific queries
   - Generate a test report with scores

   > Note: If you encounter issues with the script, you can also run each step manually:
   > ```bash
   > # Determine which Python command to use
   > PYTHON_CMD="python3"  # or "python" depending on your system
   > 
   > # Initialize RAG system
   > $PYTHON_CMD backend/scripts/initialize_rag.py
   > 
   > # Run healthcare tests
   > $PYTHON_CMD backend/scripts/test_healthcare_rag.py
   > ```

2. **Visualize the results**:
   ```bash
   python visualize_healthcare_rag_results.py
   ```
   This will:
   - Generate charts showing keyword coverage across queries
   - Create a summary pie chart
   - Display detailed test results

## Test Cases Covered

The healthcare RAG test evaluates the system's knowledge of:

1. **Healthcare Application SLAs**
   - Uptime requirements
   - Response time standards
   - Performance metrics

2. **Regulatory Compliance**
   - HIPAA requirements
   - Patient data protection
   - Breach notification protocols

3. **Data Security**
   - Encryption standards
   - Access controls
   - Audit logging

4. **Telemedicine-Specific Requirements**
   - Video quality standards
   - Clinical workflow continuity
   - Medical device integration

5. **Disaster Recovery**
   - Recovery time objectives (RTO)
   - Recovery point objectives (RPO)
   - Backup requirements

## Adding More Healthcare SLA Documents

To enhance the RAG system with additional healthcare domain knowledge:

1. Add new healthcare SLA documents to:
   ```
   backend/app/data/sla_examples/       # For JSON format files
   # or
   /home/nilabh/Projects/chakra/examples/  # For MD files to upload through UI
   ```

2. Format the files with:
   - `content`: The full text of the SLA document
   - `metadata`: Object with industry, service type, title, etc.

3. Re-run the initialization script:
   ```bash
   python backend/scripts/initialize_rag.py
   ```

## Interpreting Results

- **Pass**: 80%+ of expected keywords found
- **Partial**: 50-79% of expected keywords found  
- **Fail**: <50% of expected keywords found

The overall score represents how well the RAG system incorporates healthcare domain knowledge into its responses.

## Troubleshooting

- **Empty vector store**: Run the initialization script first
- **Low scores**: Add more domain-specific documents
- **Visualization errors**: Install matplotlib and numpy