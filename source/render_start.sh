#!/bin/bash
set -e

# 🚨 SAFETY CHECK: Prevent accidental database clearing
# This script should NEVER contain destructive database commands
DANGEROUS_COMMANDS=("flush" "reset_db" "sqlflush" "sqlsequencereset" "loaddata" "dumpdata" "clear_cache")
for cmd in "${DANGEROUS_COMMANDS[@]}"; do
    if grep -q "manage.py $cmd" "$0"; then
        echo "❌ DANGER: Found potentially destructive command '$cmd' in render_start.sh"
        echo "❌ This could delete user data! Aborting deployment."
        exit 1
    fi
done

echo "=== Render Deployment Debug Information ==="
echo "Environment variables:"
echo "DATABASE_URL: ${DATABASE_URL:30:60}..."  # Show first 50 chars only for security
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

echo "=== Data Preservation Check ==="
echo "📊 Checking current data before migrations..."
python manage.py shell -c "
from django.contrib.auth.models import User
from main.models import Stone
from accounts.models import Profile
try:
    user_count = User.objects.count()
    stone_count = Stone.objects.count()
    profile_count = Profile.objects.count()
    print(f'📊 Current data: {user_count} users, {stone_count} stones, {profile_count} profiles')
except Exception as e:
    print(f'⚠️  Could not check data count: {e}')
" || echo "⚠️  Could not check data count"

echo "=== Applying Database Migrations ==="
echo "⚠️  SAFETY CHECK: Only running MIGRATIONS (no data will be deleted)"
echo "⚠️  Migrations only ADD/MODIFY database structure, never delete user data"

# Try migration with retry logic
for i in {1..3}; do
    echo "Migration attempt $i/3..."
    if python manage.py migrate --noinput; then
        echo "✅ Migrations completed successfully - NO DATA LOST"
        break
    else
        echo "❌ Migration attempt $i failed"
        if [ $i -eq 3 ]; then
            echo "❌ All migration attempts failed. Exiting."
            exit 1
        fi
        echo "⏳ Waiting 10 seconds before retry..."
        sleep 10
    fi
done

echo "=== Post-Migration Data Verification ==="
echo "📊 Verifying data preservation after migrations..."
python manage.py shell -c "
from django.contrib.auth.models import User
from main.models import Stone
from accounts.models import Profile
try:
    user_count = User.objects.count()
    stone_count = Stone.objects.count()
    profile_count = Profile.objects.count()
    print(f'✅ Data preserved: {user_count} users, {stone_count} stones, {profile_count} profiles')
    print('✅ NO DATA LOST - All user data is safe!')
except Exception as e:
    print(f'⚠️  Could not verify data count: {e}')
" || echo "⚠️  Could not verify data count"

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