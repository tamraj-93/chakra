"""
RAG (Retrieval-Augmented Generation) Service

This module provides functionality for:
- Combining the vector store with AI language models
- Retrieving relevant context for user queries
- Generating responses with contextual augmentation
- Managing knowledge sources for better SLA generation
"""

import logging
import os
import json
from typing import List, Dict, Any, Optional

from app.services.vector_store import get_vector_store
from app.services.document_processor import get_document_processor
from app.services.llm_provider import LLMProvider

# Set up logging
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_NUM_RESULTS = 5
MAX_CONTEXT_LENGTH = 2000
DEFAULT_SLA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sla_examples")


class RAGService:
    """
    Service for Retrieval-Augmented Generation functionality.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the RAG service.
        
        Args:
            llm_provider: LLM provider for generating responses
        """
        self.vector_store = get_vector_store()
        self.document_processor = get_document_processor()
        self.llm_provider = llm_provider
        logger.info("Initialized RAG Service")
        
        # Check if we have documents in the vector store
        count = self.vector_store.get_document_count()
        if count == 0:
            logger.warning("Vector store is empty. Consider loading documents using initialize_knowledge_base().")
    
    def initialize_knowledge_base(self, directory: str = DEFAULT_SLA_DIR) -> int:
        """
        Initialize the knowledge base with SLA documents.
        
        Args:
            directory: Directory containing SLA documents
            
        Returns:
            Number of documents loaded
        """
        logger.info(f"Initializing knowledge base from {directory}")
        
        # Load documents
        documents = self.document_processor.load_directory(directory)
        
        if not documents:
            logger.warning(f"No documents found in {directory}")
            return 0
            
        # Extract content and metadata
        contents = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        # Add documents to the vector store
        doc_dicts = [{"content": content} for content in contents]
        self.vector_store.add_documents(doc_dicts, metadatas)
        
        logger.info(f"Initialized knowledge base with {len(documents)} documents")
        return len(documents)
    
    def get_relevant_context(self, query: str, top_k: int = DEFAULT_NUM_RESULTS, filter_criteria: Optional[Dict[str, Any]] = None) -> str:
        """
        Get relevant context from the knowledge base for a query.
        
        Args:
            query: User query
            top_k: Number of results to retrieve
            filter_criteria: Optional metadata filter
            
        Returns:
            Concatenated context from relevant documents
        """
        # Search the vector store
        results = self.vector_store.search(query, top_k, filter_criteria)
        
        if not results:
            logger.warning(f"No relevant context found for query: {query}")
            return ""
        
        # Format the results into a context string
        context_parts = []
        
        for i, result in enumerate(results):
            # Format source information
            source_info = "UNKNOWN SOURCE"
            if "metadata" in result and result["metadata"]:
                source = result["metadata"].get("source", "").split(os.path.sep)[-1]
                source_info = source if source else "UNKNOWN SOURCE"
            
            # Format the context part
            context_part = f"[Source {i+1}: {source_info}]\n{result['content']}\n"
            context_parts.append(context_part)
        
        # Join all context parts
        full_context = "\n".join(context_parts)
        
        # Truncate if too long
        if len(full_context) > MAX_CONTEXT_LENGTH:
            logger.info(f"Context too long ({len(full_context)} chars), truncating to {MAX_CONTEXT_LENGTH}")
            full_context = full_context[:MAX_CONTEXT_LENGTH] + "..."
        
        return full_context
    
    async def generate_response_with_rag(self, messages: List[Dict[str, str]], query: str) -> str:
        """
        Generate a response using RAG.
        
        Args:
            messages: List of message dictionaries
            query: Current user query
            
        Returns:
            AI-generated response with contextual augmentation
        """
        # Get relevant context
        context = self.get_relevant_context(query)
        
        if not context:
            logger.warning("No context retrieved, falling back to standard generation")
            return await self.llm_provider.generate_response(messages)
        
        # Create augmented prompt
        system_message = next((m for m in messages if m["role"] == "system"), None)
        
        if system_message:
            # Modify existing system message
            augmented_system = {
                "role": "system",
                "content": f"{system_message['content']}\n\nUse the following information to help answer the user's question:\n\n{context}"
            }
            
            # Replace the system message
            augmented_messages = [augmented_system if m["role"] == "system" else m for m in messages]
        else:
            # Create new system message
            augmented_system = {
                "role": "system",
                "content": f"You are an AI assistant specialized in SLA (Service Level Agreement) management. Use the following relevant information to help answer the user's question:\n\n{context}"
            }
            
            # Add the system message at the beginning
            augmented_messages = [augmented_system] + messages
        
        # Generate response with the augmented messages
        response = await self.llm_provider.generate_response(augmented_messages)
        
        return response
    
    def add_document_to_knowledge_base(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a new document to the knowledge base.
        
        Args:
            content: Document content
            metadata: Optional metadata
            
        Returns:
            Document ID
        """
        if metadata is None:
            metadata = {}
        
        # Save the document
        file_path = self.document_processor.save_document(content, metadata)
        
        # Add to vector store
        doc_dict = {"content": content}
        doc_ids = self.vector_store.add_documents([doc_dict], [metadata])
        
        logger.info(f"Added document to knowledge base with ID: {doc_ids[0]}")
        return doc_ids[0]

# Singleton instance
_rag_service = None

def get_rag_service(llm_provider: LLMProvider) -> RAGService:
    """
    Get the RAG service singleton.
    
    Args:
        llm_provider: LLM provider for generating responses
        
    Returns:
        RAG service instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService(llm_provider)
    return _rag_service