#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

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