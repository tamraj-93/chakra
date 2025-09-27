"""
Ollama provider implementation for the LLM provider interface.
"""
import httpx
import logging
from typing import List, Dict, Any, Optional

from .llm_provider import LLMProvider
from app.core.config import OLLAMA_API_URL, OLLAMA_MODEL, LLM_PROVIDER

# Set up logging
logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    """Ollama provider implementation for local LLM integration."""
    
    def __init__(self):
        """Initialize the Ollama provider with API URL from config."""
        # Ensure the API URL uses http:// protocol and remove any trailing slashes
        api_url = OLLAMA_API_URL or "http://localhost:11434"
        if not api_url.startswith("http://") and not api_url.startswith("https://"):
            api_url = f"http://{api_url}"
        self.api_url = api_url.rstrip("/")
        self.model = OLLAMA_MODEL or "mistral"
        logger.info(f"Initialized Ollama provider with URL: {self.api_url} and model: {self.model}")
    
    async def generate_response(self, 
                              messages: List[Dict[str, str]], 
                              max_tokens: Optional[int] = None,
                              temperature: Optional[float] = 0.7) -> str:
        """
        Generate a response using the local Ollama API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            max_tokens: Maximum number of tokens to generate
            temperature: Randomness of the generation (0.0-1.0)
            
        Returns:
            Generated text response as a string
        """
        try:
            # Enhanced logging for debugging
            logger.info("=" * 50)
            logger.info(f"Ollama Provider: Generating response with model: {self.model}")
            logger.info(f"Ollama API URL: {self.api_url}")
            logger.info(f"Input messages: {len(messages)} messages")
            logger.info(f"Temperature: {temperature}, Max tokens: {max_tokens or 'default'}")
            logger.info("=" * 50)
            
            # Log a sample of the input messages
            if messages:
                logger.info(f"First message role: {messages[0]['role']}")
                logger.info(f"First message content sample: {messages[0]['content'][:50]}...")
            
            # Convert OpenAI-style messages to Ollama format
            prompt = self._format_messages(messages)
            logger.info(f"Formatted prompt sample: {prompt[:150]}...")  # Log first 150 chars
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens or 800,
                    "temperature": temperature
                }
            }
            logger.debug(f"Request payload: {payload}")
            
            # Log detailed request payload for debugging
            logger.info(f"Request payload: model={payload['model']}, stream={payload['stream']}")
            logger.info(f"Options: {payload['options']}")

            # Try direct curl command for debugging
            import subprocess
            try:
                logger.info("Testing Ollama with curl command...")
                curl_cmd = f"curl -s -X POST {self.api_url}/api/generate -H 'Content-Type: application/json' -d '{{\"model\":\"{self.model}\",\"prompt\":\"Hello\",\"stream\":false}}'"
                result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)
                logger.info(f"Curl test result: {result.stdout[:100]}...")
            except Exception as curl_error:
                logger.error(f"Curl test failed: {str(curl_error)}")
            
            # Make async request to Ollama API using a more robust approach
            logger.info(f"Sending request to Ollama API at: {self.api_url}/api/generate")
            
            # First try with standard configuration
            try:
                logger.info("Attempt 1: Standard connection...")
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.api_url}/api/generate",
                        json=payload
                    )
                    
                # Check for successful response
                if response.status_code == 200:
                    result = response.json()
                    logger.info("Successfully received response from Ollama")
                    logger.info(f"Response sample: {result.get('response', '')[:100]}...")
                    return result.get("response", "No response generated")
                else:
                    logger.error(f"Ollama API error: Status {response.status_code}")
                    logger.error(f"Response text: {response.text}")
                    # Continue to second attempt instead of returning error
            
            except Exception as e:
                # Log the exception but continue to try the second approach
                logger.warning(f"First attempt failed: {str(e)}")
            
            # Second attempt with more permissive configuration
            try:
                logger.info("Attempt 2: Using relaxed HTTP client settings...")
                async with httpx.AsyncClient(
                    timeout=90.0,         # Increased timeout
                    verify=False,         # Disable SSL verification for local connections
                    http2=False,          # Disable HTTP/2 which can sometimes cause issues
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                ) as client:
                    response = await client.post(
                        f"{self.api_url}/api/generate",
                        json=payload
                    )
                
                # Check for successful response from second attempt
                if response.status_code == 200:
                    result = response.json()
                    logger.info("Successfully received response from Ollama (second attempt)")
                    logger.info(f"Response sample: {result.get('response', '')[:100]}...")
                    return result.get("response", "No response generated")
                else:
                    logger.error(f"Ollama API error (second attempt): Status {response.status_code}")
                    logger.error(f"Response text: {response.text}")
                    return f"I encountered an issue with my local knowledge system (Status: {response.status_code}). Please try again."
                    
            except Exception as e:
                logger.error(f"Both connection attempts failed: {str(e)}")
                
                # Final fallback attempt using subprocess as a last resort
                try:
                    logger.info("Final attempt: Using subprocess to call curl...")
                    curl_cmd = f"curl -s -X POST {self.api_url}/api/generate -H 'Content-Type: application/json' -d '{{\"model\":\"{self.model}\",\"prompt\":\"{prompt[:200].replace('\"', '\\\"')}\",\"stream\":false}}'"
                    result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0 and result.stdout:
                        logger.info("Successfully received response from curl fallback")
                        import json
                        curl_result = json.loads(result.stdout)
                        return curl_result.get("response", "Generated using fallback method")
                    else:
                        logger.error(f"Curl fallback failed: {result.stderr}")
                except Exception as curl_error:
                    logger.error(f"Curl fallback error: {str(curl_error)}")
                
                # If all attempts fail, return a generic error message
                return "I'm having trouble connecting to my knowledge base. Please try again later."
                
        except httpx.ConnectError as e:
            logger.error(f"Ollama connection error: {str(e)}")
            logger.error(f"Check if Ollama is running at {self.api_url}")
            return "I couldn't connect to the local AI system. Please check if Ollama is running on your machine."
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out: {str(e)}")
            logger.error(f"Consider using a smaller model than {self.model}")
            return "The request to the local AI system timed out. The model might be too large for your hardware."
        except Exception as e:
            logger.error(f"Ollama error: {str(e)}", exc_info=True)
            logger.error(f"API URL: {self.api_url}, Model: {self.model}")
            # Don't return the error message to the user
            return "I'm having trouble accessing my knowledge base. Please try again later."
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert OpenAI-style messages to Ollama prompt format.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            Formatted prompt string for Ollama
        """
        # First try to detect if this is a Llama2 based model
        is_llama_model = "llama" in self.model.lower()
        is_mistral_model = "mistral" in self.model.lower()
        
        # Extract system message if present
        system_content = ""
        user_messages = []
        assistant_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            elif msg["role"] == "user":
                user_messages.append(msg["content"])
            elif msg["role"] == "assistant":
                assistant_messages.append(msg["content"])
        
        # Format based on model type
        if is_llama_model:
            # Llama2 format
            formatted_prompt = self._format_llama2(system_content, user_messages, assistant_messages)
        elif is_mistral_model:
            # Mistral format
            formatted_prompt = self._format_mistral(system_content, user_messages, assistant_messages)
        else:
            # Generic format that works with most models
            formatted_prompt = self._format_generic(system_content, user_messages, assistant_messages)
        
        logger.debug(f"Formatted prompt for model {self.model}: {formatted_prompt[:100]}...")
        return formatted_prompt
    
    def _format_llama2(self, system_content: str, user_messages: List[str], assistant_messages: List[str]) -> str:
        """Format messages for Llama2 models"""
        formatted_messages = []
        
        # Add system message
        if system_content:
            formatted_messages.append(f"<s>[INST] <<SYS>>\n{system_content}\n<</SYS>>\n\n")
        else:
            formatted_messages.append("<s>[INST] ")
        
        # Add conversation history
        for i in range(max(len(user_messages), len(assistant_messages))):
            if i == 0 and i < len(user_messages):
                # First user message is already started above
                formatted_messages.append(f"{user_messages[i]} [/INST]")
            elif i < len(user_messages):
                formatted_messages.append(f"</s><s>[INST] {user_messages[i]} [/INST]")
                
            if i < len(assistant_messages):
                formatted_messages.append(f" {assistant_messages[i]}")
        
        # Close the last message if needed
        if len(assistant_messages) < len(user_messages):
            formatted_messages.append(" ")
        
        return "".join(formatted_messages)
    
    def _format_mistral(self, system_content: str, user_messages: List[str], assistant_messages: List[str]) -> str:
        """Format messages for Mistral models"""
        formatted_messages = []
        
        # Add system message
        if system_content:
            formatted_messages.append(f"<s>[INST] {system_content}\n\n")
        else:
            formatted_messages.append("<s>[INST] ")
        
        # Add conversation history
        for i in range(max(len(user_messages), len(assistant_messages))):
            if i == 0 and i < len(user_messages):
                # First user message continues from system
                if system_content:
                    formatted_messages.append(f"{user_messages[i]} [/INST]")
                else:
                    formatted_messages.append(f"{user_messages[i]} [/INST]")
            elif i < len(user_messages):
                formatted_messages.append(f"</s><s>[INST] {user_messages[i]} [/INST]")
                
            if i < len(assistant_messages):
                formatted_messages.append(f" {assistant_messages[i]}")
        
        # Close the last message if needed
        if len(assistant_messages) < len(user_messages):
            formatted_messages.append(" ")
        
        return "".join(formatted_messages)
    
    def _format_generic(self, system_content: str, user_messages: List[str], assistant_messages: List[str]) -> str:
        """Generic format that works with most models"""
        formatted_messages = []
        
        # Add system message if present
        if system_content:
            formatted_messages.append(f"System: {system_content}\n\n")
        
        # Interleave user and assistant messages
        for i in range(max(len(user_messages), len(assistant_messages))):
            if i < len(user_messages):
                formatted_messages.append(f"User: {user_messages[i]}\n")
            if i < len(assistant_messages):
                formatted_messages.append(f"Assistant: {assistant_messages[i]}\n")
        
        # Add final assistant prompt
        formatted_messages.append("Assistant: ")
        
        return "".join(formatted_messages)