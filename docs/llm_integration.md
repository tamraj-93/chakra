# Local LLM Integration Guide for Chakra SLM

This guide explains how to use the local LLM integration with Ollama in the Chakra SLM Assistant.

## Overview

Chakra SLM now supports two LLM providers:
1. **OpenAI** - Cloud-based API for production use
2. **Ollama** - Local LLM for offline development and testing

## Setup Instructions

### Prerequisites

- Linux, macOS, or Windows with WSL
- Minimum 8GB RAM (16GB recommended for larger models)
- At least 5GB of disk space for model storage

### OpenAI (Default)

1. Ensure your `.env` file has your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key
   LLM_PROVIDER=openai
   OPENAI_MODEL=gpt-4
   ```

2. Restart your backend server.

### Ollama (Local)

1. Run the Ollama setup script:
   ```bash
   ./scripts/setup_ollama.sh
   ```

   This will:
   - Install Ollama if not already installed
   - Download the Mistral model
   - Configure your `.env` file
   - Start the Ollama service

2. Restart your backend server:
   ```bash
   ./start_chakra.sh
   ```

## Testing

To test your LLM integration:

```bash
./test_llm_integration.sh
```

This will verify that your chosen LLM provider is working correctly.

## Switching Between Providers

To switch between providers:

1. Edit your `.env` file:
   ```
   # For OpenAI
   LLM_PROVIDER=openai
   
   # For Ollama
   LLM_PROVIDER=ollama
   ```

2. Restart your backend server.

## Troubleshooting

### OpenAI Issues

- Verify your API key is correct
- Check your internet connection
- Ensure you have API credits available

### Ollama Issues

- Verify Ollama is running with `ps aux | grep ollama`
- Restart Ollama with `ollama serve`
- Check Ollama models with `ollama list`
- Verify the model is downloaded with `ollama pull mistral`

If you encounter persistent issues, check the logs for more details:

```bash
tail -f logs/backend.log
```

## Advanced Configuration

You can configure additional parameters in your `.env` file:

```
# OpenAI settings
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo, etc.

# Ollama settings
OLLAMA_API_URL=http://localhost:11434  # default Ollama API URL
OLLAMA_MODEL=mistral  # or llama2, codellama, etc.
```