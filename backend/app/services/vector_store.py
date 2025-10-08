"""
Vector Database Service for RAG Implementation

This module provides functionality for:
- Creating and managing a vector database
- Storing and retrieving document embeddings
- Performing similarity searches for relevant content
"""

import os
import logging
import tempfile
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# Set up logging
logger = logging.getLogger(__name__)

# Configuration constants
COLLECTION_NAME = "sla_knowledge_base"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
PERSIST_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "vector_db")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class VectorStore:
    """
    A service for storing and retrieving document embeddings for RAG.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern for VectorStore."""
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the vector store if it hasn't been initialized yet."""
        if self._initialized:
            return
            
        logger.info(f"Initializing vector store at {PERSIST_DIRECTORY}")
        
        # Ensure the persist directory exists
        os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
        
        # Create ChromaDB client
        self.client = chromadb.PersistentClient(
            path=PERSIST_DIRECTORY,
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False
            )
        )
        
        # Initialize the embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        
        # Get or create the collection
        try:
            self.collection = self.client.get_collection(name=COLLECTION_NAME)
            logger.info(f"Using existing collection: {COLLECTION_NAME}")
        except ValueError:
            self.collection = self.client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=self._get_embeddings
            )
            logger.info(f"Created new collection: {COLLECTION_NAME}")
        
        # Create text splitter for document chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self._initialized = True
        
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        logger.debug(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    def add_documents(self, documents: List[Dict[str, Any]], metadata: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries with 'content' field
            metadata: Optional list of metadata dictionaries for each document
            
        Returns:
            List of document IDs
        """
        if not documents:
            logger.warning("No documents provided to add_documents")
            return []
        
        if metadata is None:
            metadata = [{} for _ in documents]
            
        # Extract content from documents
        texts = [doc.get("content", "") for doc in documents]
        
        # Split documents into chunks
        chunks = []
        chunk_metadatas = []
        doc_ids = []
        
        for i, (text, meta) in enumerate(zip(texts, metadata)):
            doc_chunks = self.text_splitter.split_text(text)
            
            # Create metadata for each chunk that links back to the source document
            doc_id = meta.get("id", f"doc_{i}")
            chunk_meta = [
                {
                    **meta,
                    "chunk_id": f"{doc_id}_chunk_{j}",
                    "document_id": doc_id
                }
                for j in range(len(doc_chunks))
            ]
            
            chunks.extend(doc_chunks)
            chunk_metadatas.extend(chunk_meta)
            doc_ids.append(doc_id)
            
        # Add chunks to the collection
        ids = [meta["chunk_id"] for meta in chunk_metadatas]
        
        logger.info(f"Adding {len(chunks)} chunks to vector store")
        self.collection.add(
            documents=chunks,
            metadatas=chunk_metadatas,
            ids=ids
        )
        
        return doc_ids
        
    def search(self, query: str, top_k: int = 5, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            filter_criteria: Optional metadata filter for search
            
        Returns:
            List of document dictionaries with content and metadata
        """
        logger.info(f"Searching for: {query}")
        
        # Query the collection
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filter_criteria
        )
        
        # Format the results
        formatted_results = []
        
        if results and 'documents' in results and len(results['documents']) > 0:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted_results.append({
                    "content": doc,
                    "metadata": metadata,
                    "score": 1.0 - distance  # Convert distance to similarity score
                })
                
        return formatted_results
    
    def clear(self) -> None:
        """Clear all documents from the collection."""
        logger.warning("Clearing all documents from the vector store")
        self.collection.delete(delete_all=True)
        
    def get_document_count(self) -> int:
        """
        Get the number of documents in the collection.
        
        Returns:
            Number of documents
        """
        return self.collection.count()
        
def get_vector_store() -> VectorStore:
    """
    Get the vector store singleton instance.
    
    Returns:
        VectorStore instance
    """
    return VectorStore()