#!/usr/bin/env python3
"""
Simple RAG Test

A simplified test script for the RAG system that uses minimal imports
and directly tests the retrieval capabilities.
"""

import os
import sys
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("simple_rag_test")

# Directory paths
script_dir = os.path.dirname(os.path.abspath(__file__))
examples_path = os.path.join(script_dir, "examples")
vector_db_path = os.path.join(script_dir, "backend", "data", "vector_db")

# Test questions
HEALTHCARE_TEST_QUESTIONS = [
    "What are the key HIPAA requirements for a healthcare SLA?",
    "What uptime should be guaranteed for critical healthcare systems?",
    "How should patient data be protected according to healthcare regulations?"
]

def main():
    """Main function to test RAG capabilities"""
    logger.info("=" * 60)
    logger.info("SIMPLE RAG TEST")
    logger.info("=" * 60)
    
    # Check if vector database exists
    if not os.path.exists(vector_db_path):
        logger.error(f"Vector database not found at: {vector_db_path}")
        logger.info("Make sure to run initialize_rag.py first")
        return
    
    # Load index file to see what documents have been indexed
    index_path = os.path.join(vector_db_path, "indexed_documents.json")
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r') as f:
                indexed_docs = json.load(f)
            logger.info(f"Found {len(indexed_docs)} indexed documents:")
            for doc in indexed_docs:
                logger.info(f"  - {doc.get('title', 'Untitled')} ({doc.get('filename', 'unknown')})")
        except Exception as e:
            logger.error(f"Error loading index file: {str(e)}")
    else:
        logger.warning(f"No index file found at: {index_path}")
    
    # Check example files directly
    if os.path.exists(examples_path):
        healthcare_files = [f for f in os.listdir(examples_path) if "healthcare" in f.lower()]
        logger.info(f"\nFound {len(healthcare_files)} healthcare example files:")
        for filename in healthcare_files:
            logger.info(f"  - {filename}")
            
            # If it's a markdown file, print the first few lines
            if filename.endswith('.md'):
                try:
                    filepath = os.path.join(examples_path, filename)
                    with open(filepath, 'r') as f:
                        content = f.read(500)  # Read first 500 chars
                    logger.info(f"    Preview: {content[:100]}...")
                except Exception as e:
                    logger.error(f"Error reading {filename}: {str(e)}")
    else:
        logger.warning(f"Examples directory not found at: {examples_path}")
    
    logger.info("\nTest questions that would be asked:")
    for i, question in enumerate(HEALTHCARE_TEST_QUESTIONS):
        logger.info(f"  {i+1}. {question}")
    
    logger.info("\nTo fully test with LLM responses, use test_healthcare_rag.py")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()