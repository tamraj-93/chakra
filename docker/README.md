# Chakra - Docker Deployment Guide for Windows# Chakra Docker Setup for Windows



This guide provides step-by-step instructions for deploying the Chakra application on Windows using Docker.This directory contains Docker configuration files to run the Chakra application on Windows Docker environments.



## Prerequisites## Prerequisites



1. **Docker Desktop for Windows**- [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) installed and configured

   - Download and install from [Docker's official website](https://www.docker.com/products/docker-desktop)- WSL 2 backend enabled (recommended for better performance)

   - Ensure it's properly configured with WSL 2 backend- Git for Windows (with Git Bash or similar terminal)

   - Allocate sufficient resources in Docker Desktop settings (recommended: 4+ GB RAM, 2+ CPUs)

## File Structure

2. **Git** (optional)

   - If you want to clone the repository instead of downloading it- `docker/backend/Dockerfile`: Backend Docker image configuration

   - Download from [git-scm.com](https://git-scm.com/download/win)- `docker/backend/entrypoint.sh`: Backend container startup script

- `docker/frontend/Dockerfile`: Frontend Docker image configuration

## Deployment Options- `docker/frontend/nginx.conf`: Nginx configuration for the frontend

- `docker-compose.yml`: Main Docker Compose configuration (with GPU support)

You have two deployment options based on your system capabilities:- `docker-compose.demo.yml`: Demo Docker Compose configuration (without GPU requirements)



1. **Full Deployment**: Includes all features including the Ollama LLM service## Getting Started

   - Requires 8+ GB RAM and 4+ GB disk space

   - Best for powerful Windows systems1. Clone the repository to your local Windows machine

2. Open a command prompt or PowerShell window in the project directory

2. **Demo Mode**: Runs with mock services where computationally intensive components are replaced with lightweight alternatives3. Run one of the following commands:

   - Requires minimal resources

   - Great for testing, demos, or less powerful systems### Full Mode (with GPU if available)

```

## Quick Start Guidedocker-compose up --build

```

### Option 1: Full Deployment

### Demo Mode (no GPU required)

1. Open a Command Prompt or PowerShell window```

docker-compose -f docker-compose.demo.yml up --build

2. Clone or navigate to the Chakra project folder:```

   ```

   cd path\to\chakra## Accessing the Application

   ```

- Frontend: http://localhost:4200

3. Start the Docker containers:- Backend API: http://localhost:8000

   ```- API Documentation: http://localhost:8000/docs

   docker-compose up -d

   ```## Troubleshooting Windows-Specific Issues



4. Access the application:### Volume Mounting Issues

   - Open your browser and go to `http://localhost`

   - The backend API is accessible at `http://localhost:8000`If you encounter issues with volume mounting on Windows, try:

- Using named volumes instead of bind mounts

### Option 2: Demo Mode (Recommended for most Windows users)- Using forward slashes in paths

- Setting the correct file permissions

1. Open a Command Prompt or PowerShell window

### Line Ending Issues

2. Clone or navigate to the Chakra project folder:

   ```If you encounter line ending issues (CR/LF vs LF), try:

   cd path\to\chakra- Configure Git to use LF line endings with: `git config --global core.autocrlf input`

   ```- Check your `.gitattributes` file to ensure proper line ending handling



3. Start the Docker containers in demo mode:### Docker Performance Issues

   ```

   docker-compose -f docker-compose.demo.yml up -dFor better performance on Windows:

   ```- Ensure WSL 2 backend is enabled in Docker Desktop

- Allocate sufficient memory to Docker Desktop (at least 4GB recommended)

4. Access the application:- If using bind mounts, store your project in the WSL filesystem

   - Open your browser and go to `http://localhost`

   - The backend API is accessible at `http://localhost:8000`## Demo Mode



## Detailed Setup InstructionsThe application includes a demo mode that:

- Bypasses dependency issues with huggingface_hub and sentence_transformers

### 1. Install Docker Desktop for Windows- Uses mock implementations for problematic components

- Provides basic functionality without requiring specialized hardware

1. Download Docker Desktop from [Docker's official website](https://www.docker.com/products/docker-desktop)

2. Follow the installation instructionsTo enable demo mode:

3. Ensure WSL 2 is enabled during installation- Set the `DEMO_MODE=true` environment variable

4. Start Docker Desktop and wait for it to fully initialize- Use the demo Docker Compose configuration: `docker-compose -f docker-compose.demo.yml up --build`

5. Open Docker Desktop settings:

   - Set memory to at least 4GB## Resetting the Environment

   - Set CPUs to at least 2

   - Apply & RestartTo completely reset your Docker environment:

```

### 2. Get the Chakra Applicationdocker-compose down -v

```

**Option A**: Clone the repository (if you have Git installed)This will stop all containers and remove all volumes.
```
git clone https://github.com/yourusername/chakra.git
cd chakra
```

**Option B**: Download and extract the ZIP file
1. Download the ZIP file from the repository
2. Extract it to a folder of your choice
3. Open Command Prompt or PowerShell and navigate to the folder

### 3. Start the Application

#### Full Deployment
```
docker-compose up -d
```

This will:
- Build the backend and frontend Docker images
- Set up the Ollama LLM service
- Create necessary networks and volumes
- Start all services

#### Demo Mode (Recommended for most Windows users)
```
docker-compose -f docker-compose.demo.yml up -d
```

This will:
- Start the application in lightweight demo mode
- Use mock implementations for resource-intensive components
- Run faster and with lower resource requirements

### 4. Monitoring & Management

- **View logs**:
  ```
  docker-compose logs -f
  ```

- **Stop the application**:
  ```
  docker-compose down
  ```

- **Restart the application**:
  ```
  docker-compose restart
  ```

- **Rebuild and restart** (after code changes):
  ```
  docker-compose up -d --build
  ```

## Troubleshooting

### Common Issues

1. **Docker Desktop fails to start**
   - Ensure Virtualization is enabled in BIOS
   - Verify WSL 2 is properly installed (`wsl --status`)
   - Restart your computer and try again

2. **Container fails to start**
   - Check Docker Desktop dashboard for error messages
   - View container logs: `docker-compose logs backend`
   - Ensure ports 80 and 8000 are not already in use

3. **Application is slow or unresponsive**
   - Try using demo mode instead: `docker-compose -f docker-compose.demo.yml up -d`
   - Increase Docker Desktop resource allocation
   - Check Windows Task Manager for resource bottlenecks

4. **Frontend can't connect to backend**
   - Ensure all containers are running (`docker ps`)
   - Check backend logs for errors (`docker-compose logs backend`)
   - Verify the network configuration in Docker Desktop

### Demo Mode Features & Limitations

In demo mode:

- **LLM Functions**: Uses mock responses instead of real LLM
- **RAG Service**: Uses simple text matching instead of vector embeddings
- **PDF Generation**: Creates basic PDFs with limited formatting
- **Recommendations**: Uses predefined templates instead of dynamic generation

### File Paths in Windows Docker

The Docker setup uses named volumes instead of bind mounts for better Windows compatibility. Your data is persisted in Docker volumes rather than direct file system mounts to avoid path issues between Windows and Linux containers.

## Updating the Application

To update to the latest version:

1. Pull the latest changes:
   ```
   git pull
   ```
   
2. Rebuild and restart:
   ```
   docker-compose down
   docker-compose up -d --build
   ```

## Customization

### Environment Variables

You can customize the application behavior by modifying the environment variables in the `docker-compose.yml` file:

- `DEMO_MODE`: Set to "true" to enable demo mode
- `CHAKRA_LIGHTWEIGHT_MODE`: Set to "true" for reduced resource usage
- `LLM_PROVIDER`: Choose between "ollama" and "openai"
- `OLLAMA_MODEL`: Change the Ollama model (default: "mistral")

## Need Help?

If you encounter any issues not covered in this guide, please:

1. Check the GitHub repository issues section
2. Contact the development team at support@example.com