"""
Abstract base class for LLM providers.
This provides a common interface for different LLM implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    Implementations must override the generate_response method.
    """
    
    @abstractmethod
    async def generate_response(self, 
                               messages: List[Dict[str, str]], 
                               max_tokens: Optional[int] = None,
                               temperature: Optional[float] = 0.7) -> str:
        """
        Generate a response from the LLM given a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            max_tokens: Maximum number of tokens to generate
            temperature: Randomness of the generation (0.0-1.0)
            
        Returns:
            Generated text response as a string
        """
        pass
        
    def generate_response_sync(self, 
                              messages: List[Dict[str, str]], 
                              max_tokens: Optional[int] = None,
                              temperature: Optional[float] = None) -> str:
        """
        Synchronous version of generate_response for simple use cases.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            max_tokens: Maximum number of tokens to generate
            temperature: Randomness of the generation (0.0-1.0)
            
        Returns:
            Generated text response as a string
        """
        try:
            # Base implementation - to be overridden by provider-specific implementations
            # that use purely synchronous HTTP libraries (not asyncio)
            logger.info("Base synchronous response generation called")
            
            # This method should be overridden by child classes
            return "Synchronous response generation not implemented for this provider"
        except Exception as e:
            logger.error(f"Error in generate_response_sync: {e}")
            return f"Error generating response: {str(e)}"