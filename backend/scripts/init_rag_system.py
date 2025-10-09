#!/usr/bin/env python
"""
RAG System Initialization Tool (Fixed Version)

This script initializes the RAG system by:
1. Loading SLA documents from the examples directory
2. Processing them into chunks
3. Creating embeddings
4. Storing them in the vector database

This version is modified to handle the specific JSON format used in the project.
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path so we can import our app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vector_store import get_vector_store
from app.services.llm_provider import LLMProvider
from app.services.openai_provider import OpenAIProvider
from app.services.ollama_provider import OllamaProvider
from app.core.config import LLM_PROVIDER, OLLAMA_API_URL, OLLAMA_MODEL

# Constants
COLLECTION_NAME = "sla_knowledge_base"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_DOCS_TO_PROCESS = 100
BATCH_SIZE = 3  # Process documents in smaller batches to reduce memory usage

# Memory management constants
MEMORY_CHECK_INTERVAL = 2  # Check memory more frequently
MAX_MEMORY_PERCENT = 75  # Lower threshold to prevent OOM errors

# Lightweight mode settings (overridden when lightweight=True)
LIGHTWEIGHT_BATCH_SIZE = 2
LIGHTWEIGHT_MAX_DOCS = 50
LIGHTWEIGHT_CHUNK_SIZE = 300
LIGHTWEIGHT_MEMORY_PERCENT = 60

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
        return OllamaProvider(
            api_url=OLLAMA_API_URL,
            model=OLLAMA_MODEL
        )
    else:
        from app.core.config import OPENAI_API_KEY
        return OpenAIProvider(api_key=OPENAI_API_KEY)

def load_sla_examples(directory_path: str) -> List[Dict[str, Any]]:
    """Load SLA examples from the given directory."""
    documents = []
    
    try:
        if not os.path.exists(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return documents
        
        # Get all JSON files in the directory
        json_files = [f for f in os.listdir(directory_path) 
                    if f.endswith('.json') and os.path.isfile(os.path.join(directory_path, f))]
        
        logger.info(f"Found {len(json_files)} JSON files in {directory_path}")
        
        # Process each file
        for filename in json_files:
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Check if it has the expected format
                    if 'content' in data and 'metadata' in data:
                        # Add source information to metadata
                        data['metadata']['source'] = filename
                        documents.append(data)
                        logger.info(f"Loaded document: {filename}")
                    else:
                        logger.warning(f"Skipping file with invalid format: {filename}")
            
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error loading documents: {str(e)}")
    
    return documents

def create_text_chunks(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into chunks for better processing."""
    if not text:
        return []
        
    chunks = []
    current_pos = 0
    text_length = len(text)
    
    while current_pos < text_length:
        # Get chunk with specified size
        chunk_end = min(current_pos + chunk_size, text_length)
        
        # If not at the end and not at a line break, find the last line break
        if chunk_end < text_length and text[chunk_end] not in ['\n', '.', '!', '?']:
            # Try to end at a natural break
            last_break = max(
                text.rfind('\n', current_pos, chunk_end),
                text.rfind('. ', current_pos, chunk_end),
                text.rfind('! ', current_pos, chunk_end),
                text.rfind('? ', current_pos, chunk_end)
            )
            
            if last_break > current_pos:
                chunk_end = last_break + 1
        
        # Get the chunk text
        chunk_text = text[current_pos:chunk_end].strip()
        
        if chunk_text:
            chunks.append(chunk_text)
        
        # Move position with overlap
        current_pos = chunk_end - chunk_overlap
    
    return chunks

def get_memory_usage():
    """Get the current memory usage percentage."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_percent = process.memory_percent()
        return memory_percent
    except ImportError:
        logger.warning("psutil not installed, cannot monitor memory usage")
        return 0.0
    except Exception as e:
        logger.warning(f"Error checking memory usage: {e}")
        return 0.0

def initialize_rag_system(lightweight=False):
    """
    Initialize the RAG system with healthcare SLA documents.
    
    Args:
        lightweight: If True, use a more memory-efficient approach
    """
    logger.info("Starting RAG system initialization")
    
    # Directory paths
    app_dir = Path(__file__).resolve().parent.parent
    app_data_dir = app_dir / "app" / "data" / "sla_examples"
    backup_data_dir = app_dir / "data" / "sla_examples"
    
    # First check the app data directory
    logger.info(f"Checking for documents in {app_data_dir}")
    documents = load_sla_examples(str(app_data_dir))
    
    # If no documents found, check the backup directory
    if not documents:
        logger.info(f"No documents found, checking backup directory {backup_data_dir}")
        documents = load_sla_examples(str(backup_data_dir))
    
    # If still no documents, check examples directory
    if not documents:
        examples_dir = Path(__file__).resolve().parent.parent.parent / "examples"
        logger.info(f"No documents found, checking examples directory {examples_dir}")
        documents = load_sla_examples(str(examples_dir))
    
    if not documents:
        logger.error("No SLA documents found to process")
        return False
    
    logger.info(f"Processing {len(documents)} documents")
    
    # Get vector store
    vector_store = get_vector_store()
    
    # The vector_store already handles collection creation
    logger.info("Using vector store's built-in collection management")
    collection = vector_store.collection
    
    # Configure based on lightweight mode
    if lightweight:
        logger.info("Using lightweight settings for memory-constrained environments")
        actual_max_docs = LIGHTWEIGHT_MAX_DOCS
        actual_batch_size = LIGHTWEIGHT_BATCH_SIZE
        actual_memory_percent = LIGHTWEIGHT_MEMORY_PERCENT
        actual_chunk_size = LIGHTWEIGHT_CHUNK_SIZE
        
        # Clear Python's memory cache for additional safety
        import gc
        gc.collect()
    else:
        actual_max_docs = MAX_DOCS_TO_PROCESS
        actual_batch_size = BATCH_SIZE
        actual_memory_percent = MAX_MEMORY_PERCENT
        actual_chunk_size = CHUNK_SIZE
    
    # Process documents in batches
    documents_to_process = documents[:actual_max_docs]
    total_docs = len(documents_to_process)
    total_batches = (total_docs + actual_batch_size - 1) // actual_batch_size
    
    logger.info(f"Processing {total_docs} documents in {total_batches} batches")
    
    batch_num = 0
    for batch_start in range(0, total_docs, actual_batch_size):
        batch_num += 1
        batch_end = min(batch_start + actual_batch_size, total_docs)
        batch = documents_to_process[batch_start:batch_end]
        
        logger.info(f"Processing batch {batch_num}/{total_batches} (docs {batch_start+1}-{batch_end})")
        
        # If in lightweight mode, pause between batches to let system recover
        if lightweight and batch_num > 1:
            import time
            logger.info("Pausing to let system memory recover...")
            time.sleep(2)  # 2-second pause
        
        # Process each document in the batch
        for batch_idx, doc in enumerate(batch):
            doc_idx = batch_start + batch_idx
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            # Check memory usage periodically
            if doc_idx % MEMORY_CHECK_INTERVAL == 0:
                mem_usage = get_memory_usage()
                logger.info(f"Memory usage: {mem_usage:.1f}%")
                
                if mem_usage > actual_memory_percent:
                    logger.warning(f"Memory usage too high ({mem_usage:.1f}%), stopping processing")
                    break
            
            logger.info(f"Processing document {doc_idx+1}/{total_docs}: {metadata.get('title', 'Untitled')}")
            
            # Create chunks from document using the appropriate chunk size
            chunks = create_text_chunks(content, chunk_size=actual_chunk_size)
            
            # Force memory cleanup after chunking
            if lightweight:
                gc.collect()
            
            # Add chunks in mini-batches to reduce memory pressure
            chunk_docs = []
            chunk_metadatas = []
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = f"{doc_idx}-{i}"
                chunk_metadata['chunk_index'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                
                chunk_docs.append(chunk)
                chunk_metadatas.append(chunk_metadata)
                chunk_ids.append(f"doc{doc_idx}_chunk{i}")
                
                # Add in mini-batches of 10 chunks
                if len(chunk_docs) >= 10 or i == len(chunks) - 1:
                    try:
                        # Add to collection
                        collection.add(
                            documents=chunk_docs,
                            metadatas=chunk_metadatas,
                            ids=chunk_ids
                        )
                        
                        # Clear lists after adding
                        chunk_docs = []
                        chunk_metadatas = []
                        chunk_ids = []
                        
                        # Force garbage collection to free memory
                        if lightweight:
                            gc.collect()
                    except Exception as e:
                        logger.error(f"Error adding chunks: {str(e)}")
                        # Continue with next mini-batch
    
    # Add information about indexed documents to the vector store directory
    index_info = {
        "document_count": len(documents),
        "chunk_count": sum(len(create_text_chunks(doc.get('content', ''))) for doc in documents),
        "indexed_at": str(Path.ctime(Path.cwd())),
        "documents": [doc.get('metadata', {}) for doc in documents]
    }
    
    # Save index info to file
    vector_db_dir = app_dir / "data" / "vector_db"
    os.makedirs(vector_db_dir, exist_ok=True)
    
    with open(vector_db_dir / "indexed_documents.json", 'w') as f:
        json.dump(index_info, f, indent=2)
    
    logger.info(f"Successfully initialized RAG system with {len(documents)} documents")
    return True

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize the RAG system')
    parser.add_argument('--lightweight', action='store_true', help='Use lightweight mode for systems with limited resources')
    parser.add_argument('--minimal', action='store_true', help='Use super lightweight mode with minimal document processing')
    args = parser.parse_args()
    
    # If minimal mode is requested, override lightweight
    if args.minimal:
        args.lightweight = True
        global LIGHTWEIGHT_BATCH_SIZE, LIGHTWEIGHT_MAX_DOCS, LIGHTWEIGHT_CHUNK_SIZE, LIGHTWEIGHT_MEMORY_PERCENT
        LIGHTWEIGHT_BATCH_SIZE = 1
        LIGHTWEIGHT_MAX_DOCS = 20
        LIGHTWEIGHT_CHUNK_SIZE = 200
        LIGHTWEIGHT_MEMORY_PERCENT = 50
    
    print("=" * 80)
    print("RAG System Initialization (Optimized Version)")
    print("=" * 80)
    
    if args.minimal:
        print("Using MINIMAL mode - lowest memory usage, reduced document set")
    elif args.lightweight:
        print("Using LIGHTWEIGHT mode - reduced memory usage")
    
    # Print memory information
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"System memory: {memory.total / (1024**3):.1f} GB total, {memory.available / (1024**3):.1f} GB available ({memory.percent}% used)")
    except:
        print("Unable to retrieve system memory information")
    
    # Try to install psutil if missing
    try:
        import psutil
    except ImportError:
        print("Installing psutil for memory monitoring...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    
    success = initialize_rag_system(lightweight=args.lightweight)
    
    if success:
        print("\n✅ Successfully initialized RAG system!")
        print("You can now use check_healthcare_rag.py to test the integration")
    else:
        print("\n❌ Failed to initialize RAG system. Check logs for details.")

if __name__ == "__main__":
    main()