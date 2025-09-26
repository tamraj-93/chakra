# Chakra SLM AI Assistant Frontend

Angular-based frontend for the Chakra SLM AI Assistant.

## Setup

### Option 1: Using the Setup Script (Recommended)

1. Run the setup script from the project root:
   ```
   ./scripts/setup_frontend.sh
   ```
   This will install dependencies and set up the environment.

### Option 2: Manual Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install --legacy-peer-deps
   ```

3. Start development server:
   ```
   npm start -- --port 4201
   ```

> Note: We use port 4201 to avoid conflicts with other services that might be using the default Angular port (4200).

## Project Structure

- `src/app/components`: Reusable UI components
- `src/app/pages`: Application pages/screens
- `src/app/services`: API and business logic services
- `src/app/models`: Data models and interfaces

## Key Features

- Chat interface for SLA consultation
- Template configuration and customization
- Document preview and export

## Backend Connection

The frontend is configured to connect to the backend API at the URL specified in `src/environments/environment.ts`. By default, it connects to `http://localhost:8000/api`.

## Known Issues and Solutions

### Authentication

The frontend expects authentication endpoints at `/auth/login` and `/auth/register`, which are not fully implemented in the backend yet. Until they are implemented, the login and registration functionality will not work.

### Running on a Different Port

If you need to run the Angular application on a different port:

```
npm start -- --port <port_number>
```

### Troubleshooting

1. If you encounter dependency issues during installation, try using the `--legacy-peer-deps` flag:
   ```
   npm install --legacy-peer-deps
   ```

2. If you get compilation errors related to missing interfaces, check that all required interfaces are defined locally in the component files. The project does not currently fully support using shared models across frontend and backend.