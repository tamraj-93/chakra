FROM python:3.10-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy backend requirements
COPY ./backend/requirements.txt /app/requirements.txt
COPY ./docker/backend/resolve_dependencies.py /app/resolve_dependencies.py

# Install Python dependencies
# First install specific versions to resolve dependency conflicts
RUN pip install --no-cache-dir \
    pydantic==2.4.2 \
    starlette==0.27.0 \
    ecdsa \
    pyasn1 \
    rsa \
    click \
    "httpcore>=0.18.0,<0.19.0" \
    httpx==0.25.0 \
    overrides>=7.3.1

# Install basic packages first (without problematic dependencies)
RUN grep -v "sentence-transformers\|huggingface\|langchain\|transformers" requirements.txt > /app/base_requirements.txt || true
RUN pip install --no-cache-dir -r /app/base_requirements.txt

# Install compatible versions of problematic packages
RUN python /app/resolve_dependencies.py

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy backend code
COPY ./backend /app/backend

# Copy Docker-specific files
COPY docker/backend/vector_store_updated.py /app/backend/app/services/vector_store.py
COPY docker/backend/document_processor_compat.py /app/backend/app/services/document_processor.py
COPY docker/backend/demo_mode.py /app/demo_mode.py

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEMO_MODE=false

# Entrypoint script
COPY ./docker/backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create directories and set permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
ENTRYPOINT ["/app/entrypoint.sh"]