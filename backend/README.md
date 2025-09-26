````markdown
# Chakra - SLM AI Assistant Backend

FastAPI-based backend for the Chakra SLM AI Assistant.

## Setup

### Option 1: Using the Setup Script (Recommended)

1. Run the setup script from the project root:
   ```
   ./scripts/setup_backend.sh
   ```
   This will create a virtual environment, install dependencies, and set up any necessary configuration.

2. Start the development server:
   ```
   cd backend
   ./venv/bin/uvicorn app.main:app --reload
   ```

### Option 2: Manual Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```
   python -m uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Project Structure

- `app/main.py`: Application entry point
- `app/api/`: API endpoints and routers
- `app/core/`: Core functionality (config, security)
- `app/models/`: Database models
- `app/services/`: Business logic and external services

## Known Issues and Solutions

### Authentication Endpoints
The frontend is currently expecting authentication endpoints at `/auth/login` and `/auth/register` which are not yet implemented in the backend. The following endpoints need to be implemented:

1. POST `/auth/login` - For user authentication
2. POST `/auth/register` - For user registration

Currently, there is a user creation endpoint at `/users/` but it's not integrated with the authentication flow.

### Running the Server
If you encounter issues running the server:

1. Ensure you're in the correct directory:
   ```
   cd /path/to/project/backend
   ```

2. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

3. Run the server using the full path to uvicorn in the virtual environment:
   ```
   ./venv/bin/uvicorn app.main:app --reload
   ```

4. If you need to use a different port (e.g., if port 8000 is already in use):
   ```
   ./venv/bin/uvicorn app.main:app --reload --port 8001
   ```