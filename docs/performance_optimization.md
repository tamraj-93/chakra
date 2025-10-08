# Chakra Performance Optimization Guide

This document outlines the performance optimizations made to the Chakra application's startup scripts and server configuration to improve response times. These optimizations have been integrated into the default startup scripts.

## Key Optimizations Implemented

### 1. Uvicorn Server Configuration

The default uvicorn configuration was modified to use multiple worker processes for better performance:

- **Worker Configuration**: Using the Gunicorn-recommended formula `(2 x NUM_CORES) + 1` to determine the optimal number of worker processes.
- **Concurrency Limits**: Added `--limit-concurrency 50` to prevent server overload.
- **Keep-Alive Timeouts**: Increased the keep-alive timeout to 120 seconds with `--timeout-keep-alive 120`.
- **Production vs Development Mode**: Added a `--production` flag to switch between development mode (with auto-reload) and production mode (with workers).

### 2. Ollama Model Pre-warming

One of the main causes of slow initial response times was the cold-start problem with the Ollama model. The following optimizations address this:

- **Model Pre-warming**: Scripts now send a test prompt to the Ollama API during startup to ensure the model is loaded.
- **Multiple Pre-warming Requests**: The `warm_up_ollama.sh` script sends multiple diverse prompts to properly initialize the model.
- **Automatic Ollama Detection**: Scripts now check if Ollama is running and warn if it's not available.

### 3. Environment Setup Improvements

- **Virtual Environment Handling**: More robust detection and creation of virtual environments.
- **Dependency Management**: More efficient package installation.

## Scripts Updated

1. **start_backend.sh**: Now includes all performance optimizations.
2. **start_chakra.sh**: Now includes optimized settings for both backend and frontend.
3. **warm_up_ollama.sh**: Standalone script to pre-warm the Ollama model for faster initial responses.

> Note: The original scripts have been backed up to the `backup_scripts` directory.

## Usage Instructions

### For Production Use

Run the application with optimized settings for production:

```bash
./start_chakra.sh --production
```

This will:
- Start the backend with multiple worker processes
- Disable auto-reload for better performance
- Set production build settings for Angular frontend
- Pre-warm the Ollama model

### For Development Use

Run with development-friendly settings:

```bash
./start_chakra.sh
```

This will:
- Start the backend with auto-reload enabled
- Start Angular in development mode
- Still pre-warm the Ollama model

### Pre-warming the Model Separately

If you want to pre-warm the model before starting the application:

```bash
./warm_up_ollama.sh
```

## Configuration Options

The following environment variables can be set in your `.env` file:

```
# LLM Provider
LLM_PROVIDER=ollama
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Performance settings
UVICORN_WORKERS=4  # Optional: Override the auto-calculated number of workers
```

## Performance Tuning Tips

1. **CPU Resources**: If your server has many CPU cores, adjust the worker count appropriately.
2. **Model Selection**: Smaller Ollama models may respond faster. Consider using a smaller model if speed is critical.
3. **Memory Usage**: Monitor memory usage when running with multiple workers. Each worker will load the Python interpreter.
4. **Database Connections**: SQLite works well with low concurrency, but for high traffic, consider PostgreSQL.

## Troubleshooting

### Slow Initial Responses

If the first response after startup is still slow:
1. Make sure Ollama is running before starting the application
2. Run `./warm_up_ollama.sh` multiple times 
3. Check if you're using a very large model that takes time to load

### Server Errors Under Load

If you see server errors under heavy load:
1. Reduce the number of workers or concurrency limit
2. Check system resources (CPU, memory)
3. Look for bottlenecks in database or external service calls