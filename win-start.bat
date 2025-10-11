@echo off
setlocal enabledelayedexpansion

echo ================================================
echo    Windows Docker Setup for Chakra Project
echo ================================================
echo.

:: Check if Docker is running
echo Checking Docker status...
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running.
    echo Please start Docker Desktop and try again.
    exit /b 1
)

:: Check if the script directory is writable
echo Testing write permissions...
echo test > test_permissions.txt 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Current directory might not be writable.
    echo Consider running this script as administrator.
    pause
)
del test_permissions.txt >nul 2>&1

:: Check for known Windows processes that might conflict with ports
echo Checking for port conflicts...
netstat -ano | findstr ":80" > port_check.txt
netstat -ano | findstr ":8000" >> port_check.txt
if %errorlevel% equ 0 (
    echo WARNING: Ports 80 or 8000 might be in use by:
    type port_check.txt
    echo.
    echo Consider stopping IIS or other web servers, or modifying the docker-compose.demo.yml 
    echo to use different ports if you encounter "port already allocated" errors.
    echo.
    echo Proceeding anyway...
    echo.
)
del port_check.txt >nul 2>&1

:: Fix line endings in shell scripts
echo Fixing line endings in shell scripts using Git...
where git >nul 2>&1
if %errorlevel% equ 0 (
    git config core.autocrlf false
    echo Using Git to fix line endings...
    git ls-files -- "*.sh" | xargs -r git checkout --
) else (
    echo WARNING: Git not found, will use Docker to fix line endings later.
)

:: Create a fixed-path version of docker-compose-demo.yml if it doesn't exist
if not exist docker-compose.win.yml (
    echo Creating Windows-specific docker-compose file...
    copy docker-compose.demo.yml docker-compose.win.yml
)

:: Try to build the containers
echo.
echo Building Docker containers...
echo This may take several minutes on the first run...
echo.
docker-compose -f docker-compose.demo.yml build

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to build containers.
    echo.
    echo Trying with Windows-specific fixes...
    echo.
    
    :: Fix line endings using Docker
    echo Fixing line endings with Docker...
    docker run --rm -v "%cd%:/app" busybox sh -c "find /app/docker -type f -name '*.sh' -exec sed -i 's/\r$//' {} \;"
    
    :: Try building again
    echo.
    echo Trying to build again...
    docker-compose -f docker-compose.demo.yml build
    
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Container build failed after fixes.
        echo Please check the error messages above.
        echo.
        echo Try the following troubleshooting steps:
        echo 1. Ensure Docker Desktop has enough resources allocated
        echo 2. Check internet connectivity for downloading packages
        echo 3. Try running Docker Desktop as administrator
        echo.
        echo See windows-troubleshooting.md for more detailed help.
        pause
        exit /b 1
    )
)

:: Start the containers
echo.
echo Starting Docker containers...
docker-compose -f docker-compose.demo.yml up -d

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start containers.
    echo Please check the error messages above.
    echo.
    echo Common issues on Windows:
    echo - Port conflicts with IIS or other web servers
    echo - Insufficient permissions for Docker
    echo - Path problems with Windows file paths
    echo.
    echo See windows-troubleshooting.md for more detailed help.
    pause
    exit /b 1
)

:: Wait for containers to start
echo.
echo Waiting for containers to start...
timeout /t 10 /nobreak > nul

:: Test the API
echo.
echo Testing API connection...
curl -s -o nul -w "%%{http_code}\n" http://localhost/api/health > api_status.txt
set /p API_STATUS=<api_status.txt
del api_status.txt

if "!API_STATUS!" == "200" (
    echo.
    echo ================================================
    echo SUCCESS! The Chakra demo is running.
    echo.
    echo You can access the application at:
    echo    Frontend: http://localhost
    echo    Backend API: http://localhost:8000
    echo    API Docs: http://localhost/api/docs
    echo ================================================
) else (
    echo.
    echo WARNING: API health check failed with status: !API_STATUS!
    echo The containers may need more time to initialize.
    echo.
    echo Try accessing the URLs manually after a minute:
    echo    Frontend: http://localhost
    echo    Backend API: http://localhost:8000
    echo    API Docs: http://localhost/api/docs
    echo.
    echo If you encounter issues, see windows-troubleshooting.md
)

echo.
echo To stop the containers, run:
echo    docker-compose -f docker-compose.demo.yml down
echo.

pause