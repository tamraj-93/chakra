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
        logger.info(f"Initializing RAG Service with {llm_provider.__class__.__name__}")
        self.vector_store = get_vector_store()
        logger.debug(f"Vector store initialized: {type(self.vector_store).__name__}")
        
        self.document_processor = get_document_processor()
        logger.debug(f"Document processor initialized: {type(self.document_processor).__name__}")
        
        self.llm_provider = llm_provider
        logger.debug(f"LLM provider initialized: {type(self.llm_provider).__name__}")
        
        # Check if we have documents in the vector store
        count = self.vector_store.get_document_count()
        logger.info(f"Vector store contains {count} documents")
        
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
    
    def get_relevant_context(self, query: str, top_k: int = DEFAULT_NUM_RESULTS, 
                            filter_criteria: Optional[Dict[str, Any]] = None, 
                            include_sources: bool = False) -> Any:
        """
        Get relevant context from the knowledge base for a query.
        
        Args:
            query: User query
            top_k: Number of results to retrieve
            filter_criteria: Optional metadata filter
            include_sources: Whether to include source information in the result
            
        Returns:
            Either a string of concatenated context or an object with context and sources
        """
        logger.info(f"Getting relevant context for query: '{query[:50]}...' (top_k={top_k})")
        if filter_criteria:
            logger.info(f"Using filter criteria: {filter_criteria}")
        
        # Search the vector store
        logger.debug(f"Searching vector store with query: '{query[:50]}...'")
        results = self.vector_store.search(query, top_k, filter_criteria)
        
        if not results:
            logger.warning(f"No relevant context found for query: '{query[:50]}...'")
            return "" if not include_sources else type('ContextWithSources', (), {'text': "", 'sources': []})()
            
        logger.info(f"Found {len(results)} relevant document(s) for query")
        for i, result in enumerate(results):
            source = "UNKNOWN"
            if "metadata" in result and result["metadata"]:
                source = result["metadata"].get("source", "UNKNOWN")
            logger.debug(f"Result {i+1}: from '{source}' ({len(result['content'])} chars)")  
        
        # Format the results into a context string
        logger.debug("Formatting search results into context string")
        context_parts = []
        sources = results.copy()  # Store original results for source citation
        
        for i, result in enumerate(results):
            # Format source information
            source_info = "UNKNOWN SOURCE"
            if "metadata" in result and result["metadata"]:
                source = result["metadata"].get("source", "").split(os.path.sep)[-1]
                source_info = source if source else "UNKNOWN SOURCE"
                logger.debug(f"Result {i+1} metadata: {json.dumps(result['metadata'])}")
            
            # Format the context part
            context_part = f"[Source {i+1}: {source_info}]\n{result['content']}\n"
            context_parts.append(context_part)
            logger.debug(f"Added context part from source '{source_info}' ({len(result['content'])} chars)")
        
        # Join all context parts
        full_context = "\n".join(context_parts)
        logger.info(f"Created context with {len(context_parts)} sources ({len(full_context)} total chars)")
        
        # Truncate if too long
        if len(full_context) > MAX_CONTEXT_LENGTH:
            logger.warning(f"Context too long ({len(full_context)} chars), truncating to {MAX_CONTEXT_LENGTH}")
            full_context = full_context[:MAX_CONTEXT_LENGTH] + "..."
        
        # If include_sources is True, return an object with both text and sources
        if include_sources:
            context_obj = type('ContextWithSources', (), {
                'text': full_context,
                'sources': sources
            })()
            return context_obj
        
        # Otherwise just return the text
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
        logger.info(f"Generating RAG-enhanced response for query: '{query[:50]}...'")
        logger.debug(f"Input messages: {len(messages)} messages, last from: {messages[-1]['role'] if messages else 'none'}")
        
        # Get relevant context
        logger.info("Retrieving relevant context from knowledge base")
        context = self.get_relevant_context(query)
        
        if not context:
            logger.warning("No context retrieved, falling back to standard generation")
            return await self.llm_provider.generate_response(messages)
        
        # Create augmented prompt
        logger.info(f"Retrieved context: {len(context)} chars, creating augmented prompt")
        system_message = next((m for m in messages if m["role"] == "system"), None)
        
        if system_message:
            # Modify existing system message
            logger.debug(f"Found existing system message, augmenting with context")
            original_system_content = system_message["content"]
            logger.debug(f"Original system content ({len(original_system_content)} chars): '{original_system_content[:100]}...'")
            
            augmented_system = {
                "role": "system",
                "content": f"{system_message['content']}\n\nUse the following information to help answer the user's question:\n\n{context}"
            }
            
            # Replace the system message
            augmented_messages = [augmented_system if m["role"] == "system" else m for m in messages]
            logger.debug(f"Modified system message with context ({len(augmented_system['content'])} chars)")
        else:
            # Create new system message
            logger.debug(f"No system message found, creating new one with context")
            augmented_system = {
                "role": "system",
                "content": f"You are an AI assistant specialized in SLA (Service Level Agreement) management. Use the following relevant information to help answer the user's question:\n\n{context}"
            }
            
            # Add the system message at the beginning
            augmented_messages = [augmented_system] + messages
            logger.debug(f"Added new system message with context ({len(augmented_system['content'])} chars)")
        
        # Generate response with the augmented messages
        logger.info(f"Calling LLM provider with RAG-augmented messages ({len(augmented_messages)} messages)")
        response = await self.llm_provider.generate_response(augmented_messages)
        logger.info(f"Received RAG-enhanced response ({len(response)} chars)")
        
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
        
        logger.info(f"Adding new document to knowledge base ({len(content)} chars)")
        logger.debug(f"Document metadata: {json.dumps(metadata)}")
        
        # Save the document
        file_path = self.document_processor.save_document(content, metadata)
        logger.debug(f"Document saved to: {file_path}")
        
        # Add to vector store
        doc_dict = {"content": content}
        logger.debug(f"Adding document to vector store")
        doc_ids = self.vector_store.add_documents([doc_dict], [metadata])
        
        logger.info(f"Successfully added document to knowledge base with ID: {doc_ids[0]}")
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
        logger.info(f"Creating new RAG service instance with {llm_provider.__class__.__name__}")
        _rag_service = RAGService(llm_provider)
    else:
        logger.debug(f"Reusing existing RAG service instance")
    return _rag_service
    

def get_healthcare_document_count() -> int:
    """
    Get the count of healthcare documents in the knowledge base.
    
    Returns:
        Count of healthcare documents (0 if none or if query fails)
    """
    try:
        from .vector_store import get_vector_store
        vector_store = get_vector_store()
        
        # Use a simple search to find healthcare documents
        healthcare_results = vector_store.search(
            query="healthcare HIPAA patient data", 
            top_k=20, 
            filter_criteria={"metadata.industry": "healthcare"}
        )
        
        logger.info(f"Found {len(healthcare_results)} healthcare documents in knowledge base")
        return len(healthcare_results)
    except Exception as e:
        logger.error(f"Error checking healthcare documents: {e}")
        return 0