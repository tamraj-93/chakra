"""
OpenAI provider implementation for the LLM provider interface.
"""
import openai
import logging
from typing import List, Dict, Any, Optional

from .llm_provider import LLMProvider
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

# Set up logging
logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation using the OpenAI API."""
    
    def __init__(self):
        """Initialize the OpenAI provider with API key from config."""
        openai.api_key = OPENAI_API_KEY
        self.model = OPENAI_MODEL or "gpt-4"
    
    async def generate_response(self, 
                              messages: List[Dict[str, str]], 
                              max_tokens: Optional[int] = None,
                              temperature: Optional[float] = 0.7) -> str:
        """
        Generate a response using the OpenAI API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            max_tokens: Maximum number of tokens to generate
            temperature: Randomness of the generation (0.0-1.0)
            
        Returns:
            Generated text response as a string
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 800
            )
            return response.choices[0].message.content
        except Exception as e:
            # Log the error and return a friendly message
            logger.error(f"OpenAI error: {str(e)}")
            return "I'm having trouble connecting to my knowledge source. Please try again later."