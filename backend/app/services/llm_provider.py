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