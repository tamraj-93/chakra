# Running Full Chakra Environment on Windows

This guide explains how to run the complete Chakra environment on Windows with all features, including healthcare templates and RAG system.

## Prerequisites

Before starting, ensure you have the following installed on your Windows system:

1. **Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation
   - Verify with: `python --version`

2. **Node.js 14+ and npm**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify with: `node --version` and `npm --version`

3. **Angular CLI**
   - Install with: `npm install -g @angular/cli`
   - Verify with: `ng --version`

4. **Git**
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Verify with: `git --version`

5. **Ollama** (optional but recommended)
   - Download from [ollama.com](https://ollama.com/download)
   - After installation, run: `ollama pull mistral`

## Running the Full Environment

### Option 1: Using the Windows Setup Script (Recommended)

1. Open Command Prompt or PowerShell as Administrator
2. Navigate to your chakra project directory
3. Run the Windows setup script:
   ```
   start_chakra_windows.bat
   ```
4. Wait for all services to start (both backend and frontend)
5. Access the application at http://localhost:4200

### Option 2: Manual Setup (If script doesn't work)

#### Backend Setup
1. Open Command Prompt
2. Navigate to the backend directory:
   ```
   cd \path\to\chakra\backend
   ```
3. Create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
4. Initialize the database:
   ```
   python -m scripts.init_db
   ```
5. Initialize healthcare templates:
   ```
   python -m scripts.init_healthcare_templates
   ```
6. Initialize the RAG system:
   ```
   python -m scripts.init_rag_system --lightweight
   ```
7. Start the backend server:
   ```
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup (in a new Command Prompt window)
1. Open a new Command Prompt
2. Navigate to the frontend directory:
   ```
   cd \path\to\chakra\frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```
4. Start the frontend server:
   ```
   ng serve --port 4200
   ```

## Verifying All Components Are Working

After starting the application, check that all components are working correctly:

1. **Backend API**:
   - Open http://localhost:8000/docs in your browser
   - You should see the Swagger API documentation
   - Try the `/health` endpoint to verify the backend is running

2. **Frontend**:
   - Open http://localhost:4200 in your browser
   - Login with test credentials: `admin@example.com` / `password`
   - Navigate to the Templates section
   - You should see all template categories including Healthcare

3. **Healthcare Templates**:
   - In the Templates section, you should see a "Healthcare Templates" category
   - Click on a healthcare template to start a consultation
   - If templates are not visible, check the backend logs for errors

4. **RAG System**:
   - Upload a sample SLA document to test the RAG system
   - Ask questions about the document to verify RAG functionality

## Troubleshooting

### Healthcare Templates Not Visible

If healthcare templates are not visible after running the script:

1. Ensure the backend is running correctly by checking http://localhost:8000/docs
2. Check if templates exist in the `backend/data/templates` directory
3. Try manually creating the healthcare template:
   ```
   cd backend
   .venv\Scripts\activate
   python -m scripts.init_healthcare_templates
   ```
4. Restart the backend server after creating templates

### RAG System Issues

If the RAG system is not working properly:

1. Check if your system has sufficient memory (at least 4GB free)
2. Try running with the minimal option:
   ```
   python -m scripts.init_rag_system --minimal
   ```
3. Ensure that the LLM provider (Ollama or OpenAI) is properly configured

### Dependency Issues

If you encounter dependency issues:

1. Make sure all prerequisites are installed and in your PATH
2. Try recreating the Python virtual environment:
   ```
   rd /s /q .venv
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
3. For Node.js issues, try clearing npm cache:
   ```
   npm cache clean --force
   rd /s /q node_modules
   npm install
   ```

## Advanced Configuration

### Using with Docker

If you prefer to use Docker, the script will detect if Docker is running and provide alternative options. For a full Docker setup, use:

```
docker-compose up -d
```

However, be aware that the Docker setup may not include all features of the local setup, particularly the healthcare templates.

### Using Different LLM Providers

By default, the system uses Ollama with the Mistral model. To use a different provider:

1. Create a `.env` file in the backend directory
2. Set the appropriate environment variables:
   ```
   LLM_PROVIDER=openai  # or ollama
   OPENAI_API_KEY=your-api-key  # if using OpenAI
   OLLAMA_MODEL=llama2  # if using a different Ollama model
   ```

## Need More Help?

If you encounter issues not covered in this guide:

1. Check the logs in the backend and frontend terminal windows
2. Look for specific error messages related to your issue
3. Refer to the project documentation or README files
4. Try running the test-healthcare-templates.sh (on WSL) or fix-healthcare-templates-windows.bat scripts if healthcare templates are still not working