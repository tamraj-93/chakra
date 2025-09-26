# Development Setup Guide

This document provides instructions for setting up the development environment for the Chakra SLM AI Assistant project.

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 14+
- Git

## Backend Setup

1. Create a Python virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
echo "DATABASE_URL=postgresql://user:password@localhost:5432/chakra" >> .env
echo "SECRET_KEY=your-secret-key" >> .env
```

4. Initialize the database:

```bash
# We'll add Alembic migrations in the future
# For now, the tables will be created automatically when the app starts
```

5. Run the development server:

```bash
uvicorn app.main:app --reload
```

## Frontend Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Run the development server:

```bash
npm start
```

## Development Workflow

1. Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and test locally

3. Commit changes:

```bash
git add .
git commit -m "Description of your changes"
```

4. Push to the repository:

```bash
git push origin feature/your-feature-name
```

## API Documentation

The API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc