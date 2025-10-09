#!/usr/bin/env python
"""
Fix RAG Database and Vector Store Initialization

This script fixes the initialization of the RAG vector database.
"""

import os
import sys
import logging
import json

# Add the parent directory to the path so we can import our app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import chromadb
from chromadb.config import Settings

# Constants
COLLECTION_NAME = "sla_knowledge_base"
PERSIST_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vector_db")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_vector_store():
    """Create the collection directly to fix the initialization issue."""
    logger.info(f"Fixing vector store at {PERSIST_DIRECTORY}")
    
    # Ensure the directory exists
    os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
    
    # Create a client
    client = chromadb.PersistentClient(
        path=PERSIST_DIRECTORY,
        settings=Settings(
            allow_reset=True,
            anonymized_telemetry=False
        )
    )
    
    # Create collection if it doesn't exist
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        logger.info(f"Collection {COLLECTION_NAME} already exists")
    except Exception:
        collection = client.create_collection(name=COLLECTION_NAME)
        logger.info(f"Created collection {COLLECTION_NAME}")
    
    # Create a placeholder file to indicate initialization
    with open(os.path.join(PERSIST_DIRECTORY, "chroma-embeddings.placeholder"), "w") as f:
        f.write("Placeholder file for vector database")
    
    # Create a minimal indexed_documents.json file
    index_info = {
        "document_count": 0,
        "chunk_count": 0,
        "indexed_at": "Initialization",
        "documents": []
    }
    
    with open(os.path.join(PERSIST_DIRECTORY, "indexed_documents.json"), "w") as f:
        json.dump(index_info, f, indent=2)
    
    logger.info("Vector store initialization fixed")
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("RAG Vector Store Fix")
    print("=" * 80)
    
    success = fix_vector_store()
    
    if success:
        print("\n✅ Successfully fixed vector store!")
        print("Now you can run init_rag_system.py to initialize the RAG system")
    else:
        print("\n❌ Failed to fix vector store.")