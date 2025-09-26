#!/bin/bash
set -e

echo "=== Render Deployment Debug Information ==="
echo "Environment variables:"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..."  # Show first 50 chars only for security
echo "IS_PRODUCTION: $IS_PRODUCTION"
echo "DEBUG: $DEBUG"

echo "=== Network Connectivity Test ==="
# Test DNS resolution
if [[ "$DATABASE_URL" == postgres* ]]; then
    # Extract hostname from DATABASE_URL
    HOSTNAME=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    if [ -n "$HOSTNAME" ]; then
        echo "Testing DNS resolution for: $HOSTNAME"
        nslookup "$HOSTNAME" || echo "DNS resolution failed for $HOSTNAME"
        
        echo "Testing network connectivity:"
        # Extract port from DATABASE_URL
        PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        PORT=${PORT:-5432}  # Default to 5432 if not found
        echo "Testing connection to $HOSTNAME:$PORT"
        timeout 10 bash -c "echo > /dev/tcp/$HOSTNAME/$PORT" && echo "Connection successful" || echo "Connection failed"
    else
        echo "Could not extract hostname from DATABASE_URL"
    fi
else
    echo "DATABASE_URL does not start with postgres"
fi

echo "=== Database Configuration ==="
python manage.py shell -c "
from django.conf import settings
import os
print('DATABASE_URL from env:', os.environ.get('DATABASE_URL', 'NOT SET')[:50] + '...')
print('Database config:')
for key, value in settings.DATABASES['default'].items():
    if 'PASSWORD' in key.upper():
        print(f'  {key}: [HIDDEN]')
    else:
        print(f'  {key}: {value}')
" || echo "Could not print database configuration"

echo "=== Applying Database Migrations ==="
# Try migration with retry logic
for i in {1..3}; do
    echo "Migration attempt $i/3..."
    if python manage.py migrate --noinput; then
        echo "Migrations completed successfully"
        break
    else
        echo "Migration attempt $i failed"
        if [ $i -eq 3 ]; then
            echo "All migration attempts failed. Exiting."
            exit 1
        fi
        echo "Waiting 10 seconds before retry..."
        sleep 10
    fi
done

echo "PostgreSQL Database settings:"
python manage.py shell -c "from django.conf import settings; import pprint; pprint.pp(settings.DATABASES['default'])" || echo "(skip) Could not print DB settings"

# Show current database and user
if command -v psql >/dev/null 2>&1; then
  echo "Current database:"
  echo "select current_database();" | python manage.py dbshell || echo "(skip) dbshell current_database failed"
  echo "Current user:"
  echo "select current_user;" | python manage.py dbshell || echo "(skip) dbshell current_user failed"
else
  echo "psql not found; skipping dbshell verification"
fi

echo "Starting Gunicorn..."
exec gunicorn app.wsgi:application --bind 0.0.0.0:10000 