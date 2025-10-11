"""
Vector Store Compatibility Layer for Docker Windows Environment
Vector Database Service for RAG Implementation - Compatibility Version

This module provides a simplified vector store implementation that works
reliably across different environments, including Docker on Windows.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVectorStore:
    """A simplified vector store that uses JSON files for storage"""
    
    def __init__(self, collection_name: str, base_path: str = "/app/data/vector_db"):
        """Initialize the vector store
        
        Args:
            collection_name: Name of the collection to use
            base_path: Base directory for storage
        """
        self.collection_name = collection_name
        self.base_path = base_path
        self.collection_path = os.path.join(self.base_path, f"{collection_name}.json")
        self._ensure_dirs()
        self._load_or_create_collection()
    
    def _ensure_dirs(self):
        """Ensure the storage directory exists"""
        os.makedirs(self.base_path, exist_ok=True)
    
    def _load_or_create_collection(self):
        """Load the collection or create it if it doesn't exist"""
        if os.path.exists(self.collection_path):
            try:
                with open(self.collection_path, 'r') as f:
                    self.collection = json.load(f)
                logger.info(f"Loaded collection {self.collection_name} with {len(self.collection)} items")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in {self.collection_path}, creating new collection")
                self.collection = []
        else:
            logger.info(f"Creating new collection {self.collection_name}")
            self.collection = []
            self._save_collection()
    
    def _save_collection(self):
        """Save the collection to disk"""
        with open(self.collection_path, 'w') as f:
            json.dump(self.collection, f)
    
    def add_texts(self, texts: List[str], metadata: List[Dict[str, Any]] = None, 
                  embeddings: List[List[float]] = None) -> List[str]:
        """Add texts to the vector store
        
        Args:
            texts: List of text strings to add
            metadata: Optional metadata for each text
            embeddings: Optional pre-computed embeddings
            
        Returns:
            List of IDs for the added texts
        """
        if metadata is None:
            metadata = [{} for _ in texts]
        
        # Generate simple IDs based on collection size
        start_idx = len(self.collection)
        ids = [f"{self.collection_name}_{start_idx + i}" for i in range(len(texts))]
        
        # Add items to collection
        for i, (text, meta, id_) in enumerate(zip(texts, metadata, ids)):
            item = {
                "id": id_,
                "text": text,
                "metadata": meta,
            }
            if embeddings is not None and i < len(embeddings):
                item["embedding"] = embeddings[i]
            self.collection.append(item)
        
        # Save to disk
        self._save_collection()
        return ids
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar texts using basic keyword matching
        
        In a real vector store, this would use vector similarity.
        This implementation uses basic substring matching as a fallback.
        
        Args:
            query: The query text
            k: Number of results to return
            
        Returns:
            List of documents with text and metadata
        """
        # Basic implementation: look for substring matches
        query_terms = query.lower().split()
        
        results = []
        for item in self.collection:
            text = item["text"].lower()
            # Simple scoring: count how many query terms appear in the text
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                results.append((score, item))
        
        # Sort by score (descending) and take top k
        results.sort(reverse=True, key=lambda x: x[0])
        return [
            {"page_content": item["text"], "metadata": item["metadata"]} 
            for _, item in results[:k]
        ]

# Compatibility functions that mirror the langchain vector store API
def VectorStore(collection_name: str, **kwargs):
    """Factory function to create a vector store instance"""
    if os.environ.get("DEMO_MODE", "").lower() == "true":
        logger.info(f"Creating simplified vector store for collection {collection_name} (demo mode)")
        return SimpleVectorStore(collection_name)
    
    try:
        # Try to import and use Chroma if available
        import chromadb
        from langchain_community.vectorstores import Chroma
        from langchain_openai import OpenAIEmbeddings
        
        logger.info(f"Creating Chroma vector store for collection {collection_name}")
        
        # Create a client
        client = chromadb.PersistentClient(path="/app/data/chroma_db")
        
        # Get or create a collection
        try:
            collection = client.get_collection(name=collection_name)
        except Exception:
            collection = client.create_collection(name=collection_name)
        
        # Create embeddings
        embeddings = OpenAIEmbeddings()
        
        # Return a Chroma instance
        return Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embeddings,
            **kwargs
        )
    
    except ImportError:
        logger.warning("Could not import Chroma or required dependencies, falling back to simplified vector store")
        return SimpleVectorStore(collection_name)
    except Exception as e:
        logger.warning(f"Error initializing Chroma: {e}, falling back to simplified vector store")
        return SimpleVectorStore(collection_name)

# Add the missing get_vector_store function that's imported in rag_service.py
def get_vector_store(collection_name: str = "chakra_docs", **kwargs):
    """Get a vector store instance
    
    This function provides a consistent interface to get a vector store,
    abstracting away the underlying implementation.
    
    Args:
        collection_name: Name of the collection to use
        **kwargs: Additional arguments to pass to the vector store
        
    Returns:
        A vector store instance (either SimpleVectorStore or Chroma)
    """
    return VectorStore(collection_name, **kwargs)