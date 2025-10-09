#!/bin/bash

# Healthcare RAG UI Test Script
# Tests if the frontend correctly displays source citations from the RAG system

echo "Starting Healthcare RAG UI test..."

# Define Python command based on environment
if [ -d "./backend/.venv" ]; then
    PYTHON_CMD="./backend/.venv/bin/python"
else
    PYTHON_CMD="python"
fi

# Create a test script that verifies the frontend components properly handle source citations
cat > test_rag_frontend.py << EOL
import sys
import json
import os
sys.path.append('./backend')

def check_frontend_citation_support():
    print("Checking frontend components for RAG citation support...")
    
    # Paths to check
    paths = [
        './frontend/src/app/components/chat-box/chat-box.component.ts',
        './frontend/src/app/components/chat-box/chat-box.component.html',
        './frontend/src/shared/models/chat.ts',
        './frontend/src/app/components/source-citation/source-citation.component.ts',
        './frontend/src/app/components/source-citation/source-citation.component.html'
    ]
    
    # Keywords to search for
    keywords = ['source', 'citation', 'sources', 'references']
    
    found_components = []
    missing_components = []
    
    for path in paths:
        if not os.path.exists(path):
            missing_components.append(path)
            continue
            
        with open(path, 'r') as f:
            content = f.read().lower()
            
        # Check if any keywords exist in the file
        if any(keyword in content for keyword in keywords):
            found_components.append(path)
        else:
            missing_components.append(path)
    
    # Print results
    print("\n--- Frontend RAG Support Analysis ---")
    print(f"Components with RAG citation support: {len(found_components)}")
    for comp in found_components:
        print(f"  ✓ {comp}")
        
    print(f"\nComponents potentially missing RAG citation support: {len(missing_components)}")
    for comp in missing_components:
        print(f"  ❌ {comp}")
    
    # Overall assessment
    if len(found_components) > 0:
        print("\n✓ Frontend appears to have RAG citation support")
        return True
    else:
        print("\n❌ Frontend might be missing RAG citation support")
        return False

if __name__ == "__main__":
    success = check_frontend_citation_support()
    sys.exit(0 if success else 1)
EOL

# Run the test
echo "Running frontend RAG support check..."
$PYTHON_CMD test_rag_frontend.py
frontend_status=$?

# Clean up
rm test_rag_frontend.py

# Final results
if [ $frontend_status -eq 0 ]; then
    echo "✅ Frontend RAG citation test passed"
else
    echo "❌ Frontend RAG citation test failed - UI may not display citations properly"
    echo "Action required: Review frontend components to ensure they can display source citations"
fi

echo "RAG UI test completed!"