@echo off
echo ===================================
echo Fixing Healthcare Templates in Docker
echo ===================================
echo.

echo Checking if Docker is running...
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running! Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Checking if containers are running...
docker ps | find "chakra-backend-demo" > nul
if %errorlevel% neq 0 (
    echo The chakra-backend-demo container is not running!
    echo Please run windows-docker-setup.bat or win-start.bat first.
    pause
    exit /b 1
)

echo Creating templates directory in the container...
docker exec chakra-backend-demo mkdir -p /app/backend/data/templates

echo Copying healthcare templates into the container...

echo ^{^
  ^"id^": ^"healthcare-ehr-hosting-sla^",^
  ^"name^": ^"Healthcare EHR Hosting SLA^",^
  ^"description^": ^"A template to guide healthcare providers through creating SLAs for EHR hosting services^",^
  ^"domain^": ^"Healthcare^",^
  ^"version^": ^"1.0^",^
  ^"tags^": [^"healthcare^", ^"EHR^", ^"cloud hosting^", ^"HIPAA^", ^"medical data^"],^
  ^"initial_system_prompt^": ^"You are Chakra, an AI assistant specializing in healthcare SLAs. Your goal is to help healthcare providers create comprehensive service level agreements for Electronic Health Record (EHR) hosting services.^"^
^} > template.json

docker cp template.json chakra-backend-demo:/app/backend/data/templates/healthcare_ehr_hosting_sla.json
del template.json

echo ^{^
  ^"id^": ^"healthcare-telehealth-sla^",^
  ^"name^": ^"Healthcare Telehealth Platform SLA^",^
  ^"description^": ^"A template for creating SLAs for telehealth platforms with focus on availability and HIPAA compliance^",^
  ^"domain^": ^"Healthcare^",^
  ^"version^": ^"1.0^",^
  ^"tags^": [^"healthcare^", ^"telehealth^", ^"video^", ^"HIPAA^"],^
  ^"initial_system_prompt^": ^"You are Chakra, an AI assistant specializing in healthcare SLAs. Your goal is to help create comprehensive service level agreements for telehealth platforms.^"^
^} > template.json

docker cp template.json chakra-backend-demo:/app/backend/data/templates/healthcare_telehealth_sla.json
del template.json

echo ^{^
  ^"id^": ^"healthcare-hipaa-cloud-sla^",^
  ^"name^": ^"HIPAA-Compliant Cloud Service SLA^",^
  ^"description^": ^"A template for creating HIPAA-compliant cloud service SLAs for healthcare organizations^",^
  ^"domain^": ^"Healthcare^",^
  ^"version^": ^"1.0^",^
  ^"tags^": [^"healthcare^", ^"cloud^", ^"HIPAA^", ^"compliance^", ^"PHI^"],^
  ^"initial_system_prompt^": ^"You are Chakra, an AI assistant specializing in healthcare SLAs. Your goal is to help create HIPAA-compliant service level agreements for cloud services.^"^
^} > template.json

docker cp template.json chakra-backend-demo:/app/backend/data/templates/healthcare_hipaa_cloud_sla.json
del template.json

echo Patching the demo API to include healthcare templates...

echo import json > patch.py
echo import os >> patch.py
echo. >> patch.py
echo def get_healthcare_templates(): >> patch.py
echo     """Get all healthcare templates from the templates directory""" >> patch.py
echo     templates = [] >> patch.py
echo     templates_dir = "/app/backend/data/templates" >> patch.py
echo. >> patch.py
echo     # List all JSON files in the directory >> patch.py
echo     if os.path.exists(templates_dir): >> patch.py
echo         for filename in os.listdir(templates_dir): >> patch.py
echo             if filename.endswith('.json'): >> patch.py
echo                 filepath = os.path.join(templates_dir, filename) >> patch.py
echo                 try: >> patch.py
echo                     with open(filepath, 'r') as f: >> patch.py
echo                         template_data = json.load(f) >> patch.py
echo                     >> patch.py
echo                     # Create template metadata >> patch.py
echo                     template = { >> patch.py
echo                         'id': template_data.get('id', os.path.splitext(filename)[0]), >> patch.py
echo                         'name': template_data.get('name', 'Unnamed Template'), >> patch.py
echo                         'description': template_data.get('description', ''), >> patch.py
echo                         'domain': template_data.get('domain', ''), >> patch.py
echo                         'tags': template_data.get('tags', []), >> patch.py
echo                         'filename': filename >> patch.py
echo                     } >> patch.py
echo                     templates.append(template) >> patch.py
echo                 except Exception as e: >> patch.py
echo                     print(f"Error loading template {filename}: {str(e)}") >> patch.py
echo     else: >> patch.py
echo         print(f"Templates directory does not exist: {templates_dir}") >> patch.py
echo. >> patch.py
echo     return templates >> patch.py

docker cp patch.py chakra-backend-demo:/app/get_healthcare_templates.py
del patch.py

echo Patching demo_main.py to include healthcare template endpoints...

echo # Patch for healthcare templates > patch_main.py
echo from fastapi import APIRouter, HTTPException >> patch_main.py
echo from fastapi.responses import JSONResponse >> patch_main.py
echo import sys, os >> patch_main.py
echo. >> patch_main.py
echo # Insert healthcare templates code >> patch_main.py
echo sys.path.append('/app') >> patch_main.py
echo from get_healthcare_templates import get_healthcare_templates >> patch_main.py
echo. >> patch_main.py
echo # Add healthcare templates endpoints >> patch_main.py
echo @app.get("/api/healthcare-templates") >> patch_main.py
echo @app.get("/api/v1/healthcare-templates") >> patch_main.py
echo async def healthcare_templates_endpoint(): >> patch_main.py
echo     """Get all healthcare templates""" >> patch_main.py
echo     templates = get_healthcare_templates() >> patch_main.py
echo     return templates >> patch_main.py
echo. >> patch_main.py
echo @app.get("/api/healthcare-templates/{template_id}") >> patch_main.py
echo @app.get("/api/v1/healthcare-templates/{template_id}") >> patch_main.py
echo async def healthcare_template_by_id(template_id: str): >> patch_main.py
echo     """Get a specific healthcare template by ID""" >> patch_main.py
echo     templates = get_healthcare_templates() >> patch_main.py
echo     for template in templates: >> patch_main.py
echo         if template['id'] == template_id: >> patch_main.py
echo             return template >> patch_main.py
echo     raise HTTPException(status_code=404, detail=f"Healthcare template not found: {template_id}") >> patch_main.py
echo. >> patch_main.py
echo logger.info("Healthcare template endpoints added") >> patch_main.py

docker cp patch_main.py chakra-backend-demo:/app/patch_main.py
del patch_main.py

echo Restarting the container to apply changes...
docker restart chakra-backend-demo

echo Waiting for container to restart...
timeout /t 5 /nobreak > nul

echo =====================================
echo Healthcare templates have been fixed!
echo =====================================
echo You should now be able to see healthcare templates in your application.
echo.
echo Testing the healthcare templates API endpoint...

curl -s http://localhost:8000/api/healthcare-templates

echo.
echo.
echo If you see template data above, the fix was successful.
echo If not, please check the container logs for errors:
echo    docker logs chakra-backend-demo
echo.

pause