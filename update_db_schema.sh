#!/bin/bash

# Script to update the database schema for template-based consultations

# Move to the backend directory
cd "$(dirname "$0")/backend"

# Activate the Python virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install any missing dependencies
echo "Installing dependencies..."
pip install -q sqlalchemy

# Run the migration script
echo "Running database migration for template support..."
python -m app.scripts.update_db_for_templates

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo "✅ Database schema updated successfully"
else
    echo "❌ Failed to update database schema"
    exit 1
fi

echo "Done!"