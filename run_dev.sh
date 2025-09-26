#!/bin/bash
# Run Django development server with PostgreSQL

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
