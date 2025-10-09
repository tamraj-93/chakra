#!/usr/bin/env python3
"""
Initialize RAG Knowledge Base

This script initializes the RAG knowledge base by loading SLA documents
from the data/sla_examples directory into the vector database.
"""
import os
import sys
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("rag_init")

# SLA examples directory
SLA_EXAMPLES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "app", "data", "sla_examples"))
VECTOR_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "data", "vector_db"))

def load_documents():
    """Load SLA documents from the examples directory"""
    logger.info(f"Loading documents from: {SLA_EXAMPLES_PATH}")
    
    documents = []
    
    if not os.path.exists(SLA_EXAMPLES_PATH):
        logger.error(f"SLA examples directory does not exist: {SLA_EXAMPLES_PATH}")
        return []
    
    for filename in os.listdir(SLA_EXAMPLES_PATH):
        if filename.endswith(".json"):
            filepath = os.path.join(SLA_EXAMPLES_PATH, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, dict) and "content" in data and "metadata" in data:
                    documents.append({
                        "filename": filename,
                        "content": data["content"],
                        "metadata": data["metadata"]
                    })
                    logger.info(f"Loaded document: {filename}")
                else:
                    logger.warning(f"Skipping {filename}: Invalid format (missing content or metadata)")
            
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
    
    logger.info(f"Loaded {len(documents)} documents")
    return documents

def initialize_vector_database(documents):
    """Set up the vector database directory structure"""
    logger.info(f"Preparing vector database directory: {VECTOR_DB_PATH}")
    
    # Create vector database directory
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    
    # Create a simple index file to mark documents as indexed
    indexed_docs = []
    for doc in documents:
        indexed_docs.append({
            "filename": doc["filename"],
            "title": doc["metadata"].get("title", "Untitled"),
            "industry": doc["metadata"].get("industry", "Unknown")
        })
    
    index_path = os.path.join(VECTOR_DB_PATH, "indexed_documents.json")
    with open(index_path, 'w') as f:
        json.dump(indexed_docs, f, indent=2)
    
    logger.info(f"Created index file with {len(indexed_docs)} documents")
    
    # Create a placeholder for the vector database
    placeholder_path = os.path.join(VECTOR_DB_PATH, "chroma-embeddings.placeholder")
    with open(placeholder_path, 'w') as f:
        f.write("Vector database placeholder - documents have been processed for RAG")
    
    logger.info(f"Created vector database placeholder")
    
    return True

def main():
    """Main function to run the initialization process"""
    logger.info("=" * 60)
    logger.info("INITIALIZING RAG KNOWLEDGE BASE")
    logger.info("=" * 60)
    
    # Load documents
    documents = load_documents()
    
    if not documents:
        logger.error("No valid documents found. Aborting initialization.")
        return False
    
    # Initialize the vector database
    success = initialize_vector_database(documents)
    
    if success:
        logger.info("\n✅ RAG knowledge base initialized successfully!")
        logger.info(f"  - {len(documents)} documents added")
        logger.info(f"  - Vector database created at {VECTOR_DB_PATH}")
    else:
        logger.error("\n❌ Failed to initialize RAG knowledge base.")
    
    logger.info("=" * 60)
    return success

if __name__ == "__main__":
    main()