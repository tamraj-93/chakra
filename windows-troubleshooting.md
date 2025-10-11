# Windows Troubleshooting Guide for Chakra Project

This guide addresses common issues when running the Chakra project on Windows systems.

## Docker Startup Issues

### Problem: "Docker Desktop is not running"
- **Solution**: Open Docker Desktop from your Start menu or system tray
- **Verification**: Look for the Docker icon in your system tray - it should not be displaying any warning signs

### Problem: "Failed to start Docker Desktop"
- **Solution**: 
  1. Ensure Hyper-V and Windows Subsystem for Linux are enabled in Windows Features
  2. Restart your computer
  3. Try starting Docker Desktop as an Administrator

## WSL 2 Issues

### Problem: "WSL 2 installation is incomplete"
- **Solution**:
  1. Open PowerShell as Administrator
  2. Run: `wsl --install` 
  3. Restart your computer

### Problem: "Error: 0x80370102 - The virtual machine could not be started"
- **Solution**: 
  1. Enable virtualization in BIOS/UEFI
  2. Open PowerShell as Administrator
  3. Run: `Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform`
  4. Restart your computer

## Line Ending Issues

### Problem: "bash: /app/entrypoint.sh: /bin/bash^M: bad interpreter" 
- **Solution**: This is a CRLF/LF line ending issue
  1. Use the provided `windows-docker-setup.bat` script which handles this automatically
  2. Or manually convert line endings with Git Bash: `find . -type f -name "*.sh" -exec dos2unix {} \;`

## Port Conflicts

### Problem: "Error starting userland proxy: Bind for 0.0.0.0:80: unexpected error Permission denied" 
- **Solution**: Port 80 is being used by another application
  1. Check if IIS, Apache, or other web servers are running
  2. Edit `docker-compose.demo.yml` to use a different port:
     ```yaml
     services:
       frontend:
         ports:
           - "8080:80"  # Change from 80:80 to 8080:80
     ```
  3. Then access the app at http://localhost:8080 instead

### Problem: "Error starting userland proxy: Bind for 0.0.0.0:8000: unexpected error Permission denied"
- **Solution**: Port 8000 is already in use
  1. Edit `docker-compose.demo.yml` to use a different port:
     ```yaml
     services:
       backend:
         ports:
           - "8001:8000"  # Change from 8000:8000 to 8001:8000
     ```
  2. Then access the API at http://localhost:8001

## Communication Issues Between Containers

### Problem: "Cannot access API from frontend"
- **Solution**:
  1. Check Docker container status: `docker ps`
  2. Check logs for both containers:
     - `docker logs chakra_frontend_1`
     - `docker logs chakra_backend_1`
  3. Ensure both containers are on the same Docker network:
     - `docker network ls`
     - `docker network inspect chakra_default`

## Windows Anti-Virus or Firewall Issues

### Problem: "Connection timed out" or "Connection refused"
- **Solution**:
  1. Check if Windows Defender Firewall is blocking Docker
  2. Add exceptions for Docker in your antivirus software
  3. Temporarily disable firewall to test if it's causing the issue

## Displaying the Application

### Problem: "Blank page when accessing frontend"
- **Solution**:
  1. Clear your browser cache
  2. Try a different browser
  3. Check browser console for errors (F12 key)
  4. Check frontend container logs: `docker logs chakra_frontend_1`