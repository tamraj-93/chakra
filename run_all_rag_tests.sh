#!/bin/bash

# RAG System Complete Test Suite
# Runs all RAG tests in sequence to verify functionality and performance

echo "===========================================" 
echo "  Healthcare RAG System Complete Test"
echo "===========================================" 

# Step 1: Performance Test
echo -e "\n\n--- Step 1: Testing RAG Performance ---"
./test_rag_performance.sh
if [ $? -ne 0 ]; then
    echo "❌ RAG Performance test failed!"
    exit 1
fi
echo "✓ RAG Performance test passed"

# Step 2: End-to-End Test
echo -e "\n\n--- Step 2: Running End-to-End RAG Test ---"
./test_rag_e2e.sh
if [ $? -ne 0 ]; then
    echo "❌ End-to-End RAG test failed!"
    exit 1
fi
echo "✓ End-to-End RAG test passed"

# Step 3: Frontend Support Test
echo -e "\n\n--- Step 3: Testing Frontend RAG Support ---"
./test_rag_frontend.sh
if [ $? -ne 0 ]; then
    echo "❌ Frontend RAG support test failed!"
    exit 1
fi
echo "✓ Frontend RAG support test passed"

# Final Summary
echo -e "\n\n===========================================" 
echo "  All RAG Tests Completed Successfully!"
echo "===========================================" 
echo "The RAG system is functioning correctly:"
echo "✓ Performance optimization is working"
echo "✓ Healthcare document retrieval is working"
echo "✓ Source citations are supported in the UI"
echo "✓ Lightweight mode is enabled to prevent hanging"

echo -e "\nTo start the system with all optimizations:"
echo "./start_chakra.sh"
echo -e "\nRefer to docs/healthcare_rag.md for more information."