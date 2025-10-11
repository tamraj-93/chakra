@echo off
echo ===================================
echo Chakra Docker Setup for Windows
echo ===================================
echo.

echo Checking if Docker is running...
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running! Please start Docker Desktop first.
    echo.
    echo 1. Look for Docker Desktop icon in system tray
    echo 2. Start it and wait until it's fully running
    echo 3. Run this script again
    exit /b 1
)

echo Docker is running. Proceeding with setup...
echo.

echo Checking for WSL 2...
wsl --status | findstr "Default" > nul
if %errorlevel% neq 0 (
    echo WSL 2 may not be set up correctly.
    echo Please ensure WSL 2 is installed and set as default.
    echo Run: wsl --set-default-version 2
    pause
)

echo Ensuring script files use correct line endings...
echo Converting shell scripts to Unix format using Docker...
docker run --rm -v "%cd%:/app" alpine sh -c "apk add --no-cache dos2unix && find /app/docker -type f -name '*.sh' -exec dos2unix {} \;"

echo.
echo Building Docker containers...
docker-compose -f docker-compose.demo.yml build

if %errorlevel% neq 0 (
    echo.
    echo Error building Docker containers!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Starting Docker containers...
docker-compose -f docker-compose.demo.yml up -d

if %errorlevel% neq 0 (
    echo.
    echo Error starting Docker containers!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Waiting for services to initialize...
timeout /t 5 /nobreak > nul

echo.
echo =============================================
echo Setup complete! Services should be available:
echo.
echo Frontend: http://localhost
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost/docs
echo =============================================
echo.
echo To stop the services run: docker-compose -f docker-compose.demo.yml down
echo.
echo Testing API connection...
curl -X GET http://localhost/api/health

pause