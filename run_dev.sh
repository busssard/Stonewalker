#!/bin/bash
# Run Django development server with PostgreSQL

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "Activated virtual environment"
else
    echo "Warning: Virtual environment not found at $SCRIPT_DIR/venv"
fi

# Check if DATABASE_URL is set, if not use default local PostgreSQL
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
    echo "Using default local PostgreSQL database"
fi

echo "Starting Django development server with PostgreSQL..."
echo "Database URL: $DATABASE_URL"
echo ""

cd source
python manage.py runserver
