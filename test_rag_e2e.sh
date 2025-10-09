#!/bin/bash

# End-to-end test for the healthcare RAG system
# This script tests both initialization and functionality of the RAG system

echo "Starting end-to-end RAG system test..."

# Define Python command based on environment
if [ -d "./backend/.venv" ]; then
    PYTHON_CMD="./backend/.venv/bin/python"
else
    PYTHON_CMD="python"
fi

# Step 1: Initialize the RAG system with lightweight mode
echo "Step 1: Initializing RAG system with lightweight mode..."
$PYTHON_CMD ./scripts/init_rag_system.py --lightweight
if [ $? -ne 0 ]; then
    echo "❌ RAG system initialization failed!"
    exit 1
fi
echo "✓ RAG system initialized successfully"

# Step 2: Test RAG query with healthcare-specific question
echo "Step 2: Testing RAG query functionality..."
cat > test_rag_query.py << EOL
import sys
sys.path.append('./backend')
from app.services.ai import AIService
from app.services.llm_provider import LLMProvider
from app.models.consultation import ConsultationInput
import json

def test_rag_query():
    print("Testing RAG query with healthcare-specific question...")
    
    # Initialize services
    llm_provider = LLMProvider()
    ai_service = AIService(llm_provider)
    
    # Create a test consultation with healthcare context
    consultation = ConsultationInput(
        title="Healthcare SLA Test",
        industry="Healthcare",
        company="Test Hospital",
        requirements=[
            "Need a cloud service with 99.9% uptime",
            "Must comply with HIPAA regulations",
            "Need data backup and disaster recovery"
        ],
        context="This is a test for healthcare RAG functionality"
    )
    
    # Make a query that should trigger RAG retrieval
    response = ai_service.generate_sla_recommendation(consultation)
    
    # Print the response
    print("\n--- RAG Response ---")
    print(json.dumps(response, indent=2))
    
    # Check if sources are included in the response
    if 'sources' in response and response['sources']:
        print("\n✓ RAG retrieval successful - Sources included in response")
        return True
    else:
        print("\n❌ RAG retrieval failed - No sources in response")
        return False

if __name__ == "__main__":
    success = test_rag_query()
    sys.exit(0 if success else 1)
EOL

# Run the test
echo "Running RAG query test..."
$PYTHON_CMD test_rag_query.py
if [ $? -ne 0 ]; then
    echo "❌ RAG query test failed!"
    exit 1
fi
echo "✓ RAG query test completed successfully"

# Clean up temporary files
rm test_rag_query.py

echo "All RAG tests completed successfully!"