#!/usr/bin/env python
"""
RAG System Initialization Tool

This script initializes the RAG system by:
1. Loading SLA documents from the examples directory
2. Processing them into chunks
3. Creating embeddings
4. Storing them in the vector database
"""

import os
import sys
import logging
import json
from pathlib import Path

# Add the parent directory to the path so we can import our app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vector_store import get_vector_store
from app.services.document_processor import get_document_processor
from app.core.config import LLM_PROVIDER
from app.services.llm_provider import LLMProvider
from app.services.openai_provider import OpenAIProvider
from app.services.ollama_provider import OllamaProvider

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def get_llm_provider() -> LLMProvider:
    """Get the configured LLM provider."""
    provider_name = LLM_PROVIDER.lower() if LLM_PROVIDER else "openai"
    
    if provider_name == "ollama":
        from app.core.config import OLLAMA_API_URL, OLLAMA_MODEL
        return OllamaProvider(
            api_url=OLLAMA_API_URL,
            model=OLLAMA_MODEL
        )
    else:
        from app.core.config import OPENAI_API_KEY
        return OpenAIProvider(api_key=OPENAI_API_KEY)

def initialize_rag_system():
    """Initialize the RAG system with documents."""
    logger.info("Initializing RAG system")
    
    # Get document processor
    document_processor = get_document_processor()
    
    # Get examples directory
    sla_examples_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "sla_examples"
    )
    
    if not os.path.exists(sla_examples_dir):
        logger.error(f"Examples directory not found: {sla_examples_dir}")
        return False
    
    # Check if directory is empty
    files = [f for f in os.listdir(sla_examples_dir) if os.path.isfile(os.path.join(sla_examples_dir, f))]
    
    if not files:
        logger.warning(f"No files found in {sla_examples_dir}")
        return False
        
    logger.info(f"Found {len(files)} files in {sla_examples_dir}")
    
    # Load documents
    documents = document_processor.load_directory(sla_examples_dir)
    
    if not documents:
        logger.error("Failed to load any documents")
        return False
    
    logger.info(f"Loaded {len(documents)} documents")
    
    # Get vector store
    vector_store = get_vector_store()
    
    # Check if vector store already has documents
    count = vector_store.get_document_count()
    
    if count > 0:
        logger.warning(f"Vector store already contains {count} documents. Clearing...")
        vector_store.clear()
    
    # Add documents to vector store
    doc_dicts = []
    metadatas = []
    
    for doc in documents:
        doc_dicts.append({"content": doc["content"]})
        metadatas.append(doc.get("metadata", {}))
    
    doc_ids = vector_store.add_documents(doc_dicts, metadatas)
    
    logger.info(f"Added {len(doc_ids)} documents to the vector store")
    
    # Test search
    test_query = "What are the standard response time SLAs for cloud databases?"
    results = vector_store.search(test_query, top_k=2)
    
    logger.info(f"Test search for '{test_query}' returned {len(results)} results")
    
    if results:
        for i, result in enumerate(results):
            logger.info(f"Result {i+1} (score: {result['score']:.4f}):")
            logger.info(f"  Content: {result['content'][:100]}...")
    
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("RAG System Initialization")
    print("=" * 80)
    
    result = initialize_rag_system()
    
    if result:
        print("\n✅ RAG system successfully initialized!")
    else:
        print("\n❌ Failed to initialize RAG system. Check logs for details.")