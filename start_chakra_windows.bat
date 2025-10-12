@echo off
setlocal enabledelayedexpansion

echo ===========================================
echo      CHAKRA FULL SETUP FOR WINDOWS
echo ===========================================
echo.

:: Set the base directory
set "BASE_DIR=%~dp0"
set "BASE_DIR=%BASE_DIR:~0,-1%"
cd "%BASE_DIR%"

:: Function to check if a command exists
:check_command
where %~1 >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo %~2 is not installed or not in PATH
    echo Please install %~2 and try again
    exit /b 1
)
goto :eof

:: Check dependencies
echo Checking dependencies...

:: Check for Python
call :check_command python "Python 3.8+"
python --version | findstr "3." >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python 3.8+ is required. Current version is not compatible.
    exit /b 1
)

:: Check for Node.js
call :check_command node "Node.js 14+"
node --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Node.js 14+ is required
    exit /b 1
)

:: Check for Angular CLI
call :check_command ng "Angular CLI"
ng --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Angular CLI is required. Install with: npm install -g @angular/cli
    exit /b 1
)

:: Check for Git
call :check_command git "Git"

echo ✓ All dependencies verified

:: Check Docker status
echo Checking Docker status...
docker info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker is not running. Please start Docker Desktop first.
    echo Windows setup will continue with local installation instead of containers.
    set DOCKER_RUNNING=false
) else (
    echo ✓ Docker is running
    set DOCKER_RUNNING=true
)

:: Check for Ollama (which might be running in Docker or locally)
echo Checking Ollama status...
curl -s --head http://localhost:11434/api/version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Ollama service doesn't appear to be running.
    echo Will use fallback AI provider.
    set OLLAMA_RUNNING=false
) else (
    echo ✓ Ollama is running
    set OLLAMA_RUNNING=true
    
    :: Pre-warm the Ollama model
    echo Pre-warming the Ollama model (mistral)...
    curl -s -X POST http://localhost:11434/api/generate -d "{\"model\":\"mistral\",\"prompt\":\"Hello\",\"stream\":false}" >nul 2>nul
    echo ✓ Model pre-warmed
)

:: Setup Backend
echo.
echo Setting up backend...
cd "%BASE_DIR%\backend"

:: Create Python virtual environment if it doesn't exist
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

:: Initialize the database
echo Initializing database...
python -m scripts.init_db || (
    echo Database initialization encountered issues, but will continue...
)

:: Initialize healthcare templates - CRITICAL for your issue
echo Initializing healthcare templates...

:: First ensure the templates directory exists
if not exist "%BASE_DIR%\backend\data\templates" (
    mkdir "%BASE_DIR%\backend\data\templates"
)

:: Check if healthcare template exists, if not create it
if not exist "%BASE_DIR%\backend\data\templates\healthcare_ehr_hosting_sla.json" (
    echo Creating healthcare EHR template...
    
    echo {^
  "name": "Healthcare EHR Hosting SLA",^
  "description": "A template to guide healthcare providers through creating SLAs for EHR hosting services",^
  "domain": "Healthcare",^
  "version": "1.0",^
  "tags": ["healthcare", "EHR", "cloud hosting", "HIPAA", "medical data"],^
  "initial_system_prompt": "You are Chakra, an AI assistant specializing in healthcare SLAs. Your goal is to help healthcare providers create comprehensive service level agreements for Electronic Health Record (EHR) hosting services. Follow each stage carefully and guide the user through the process, ensuring HIPAA compliance and addressing healthcare-specific requirements.",^
  "stages": [^
    {^
      "name": "Service Scope Definition",^
      "description": "Define the EHR services covered by the SLA",^
      "stage_type": "information_gathering",^
      "expected_outputs": [^
        {^
          "name": "ehr_modules",^
          "description": "List of EHR modules covered by the SLA",^
          "data_type": "list",^
          "required": true^
        }^
      ]^
    }^
  ]^
} > "%BASE_DIR%\backend\data\templates\healthcare_ehr_hosting_sla.json"
)

:: Run healthcare templates initialization script
echo Running healthcare templates initialization script...
python -m scripts.init_healthcare_templates.py

:: Initialize RAG system with appropriate memory constraints
echo Checking system memory capacity...

:: Get memory info using wmic
for /f "tokens=4" %%a in ('wmic OS get FreePhysicalMemory /Value ^| find "="') do set FREE_MEM=%%a
for /f "tokens=4" %%a in ('wmic OS get TotalVisibleMemorySize /Value ^| find "="') do set TOTAL_MEM=%%a

:: Convert to GB (divide by 1048576 = 1024*1024)
set /a FREE_MEM_GB=%FREE_MEM% / 1048576
set /a TOTAL_MEM_GB=%TOTAL_MEM% / 1048576

echo System memory: %TOTAL_MEM_GB%GB total, %FREE_MEM_GB%GB free

:: Choose RAG mode based on available memory
if %FREE_MEM_GB% LSS 2 (
    echo Low memory detected, using minimal RAG mode...
    python -m scripts.init_rag_system.py --minimal
) else if %FREE_MEM_GB% LSS 4 (
    echo Limited memory detected, using lightweight RAG mode...
    python -m scripts.init_rag_system.py --lightweight
) else (
    echo Initializing RAG system for healthcare documents...
    python -m scripts.init_rag_system.py --lightweight
)

echo ✓ RAG system initialized

:: Start the backend server
echo Starting FastAPI backend on http://localhost:8000
start cmd /c "title Chakra Backend && cd "%BASE_DIR%\backend" && call .venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

:: Setup Frontend
echo.
echo Setting up frontend...
cd "%BASE_DIR%\frontend"

:: Install frontend dependencies if needed
if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
)

:: Start the Angular development server
echo Starting Angular frontend on http://localhost:4200
start cmd /c "title Chakra Frontend && cd "%BASE_DIR%\frontend" && ng serve --port 4200"

echo.
echo ===========================================
echo All services started successfully!
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:4200
echo - API Docs: http://localhost:8000/docs
echo ===========================================
echo.
echo NOTE: The backend and frontend are running in separate command windows.
echo Close those windows to stop the servers when you're done.
echo.
echo Press any key to continue...
pause > nul