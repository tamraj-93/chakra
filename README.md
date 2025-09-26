# Chakra - SLM AI Assistant

A comprehensive AI assistant for Service Level Management (SLM) that helps organizations create, manage, and optimize their Service Level Agreements (SLAs).

## Project Structure

- `/frontend`: Angular-based web application
- `/backend`: FastAPI-based API server
- `/shared`: Shared models and utilities
- `/docs`: Documentation
- `/scripts`: Helper scripts for development

## Getting Started

### Option 1: Using Setup Scripts (Recommended)

Run the provided setup scripts to set up both the backend and frontend:

```bash
# Setup and start the backend server
./scripts/setup_backend.sh
cd backend
./venv/bin/uvicorn app.main:app --reload

# In a separate terminal
# Setup and start the frontend server
./scripts/setup_frontend.sh
cd frontend
npm start -- --port 4201
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend
npm install --legacy-peer-deps
npm start -- --port 4201
```

### Accessing the Application

- Backend API: http://localhost:8000
- Backend API Documentation: http://localhost:8000/docs
- Frontend Application: http://localhost:4201

## Features

- SLA Discovery & Consultation
- SLA Template Generation
- Metric Selection & Threshold Setting
- SLA Performance Analysis
- Compliance & Audit Support

## Development Status

### Implemented
- Basic backend API structure with FastAPI
- Frontend UI components using Angular
- Database models for users, consultations, and templates
- Environment setup for both frontend and backend

### In Progress
- Authentication system (frontend expects endpoints that aren't implemented yet)
- Integration between frontend and backend services
- Complete API implementation for all features

### Known Issues
1. **Authentication**: The frontend expects authentication endpoints at `/auth/login` and `/auth/register` which are not implemented in the backend yet.
2. **Integration**: Some endpoints referenced in the frontend are not fully implemented in the backend.

Check individual README files in the `/backend` and `/frontend` directories for more detailed information.