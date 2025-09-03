#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Database settings (DJANGO DATABASES['default']):"
python manage.py shell -c "from django.conf import settings; import pprint; pprint.pp(settings.DATABASES['default'])" || echo "(skip) Could not print DB settings"

# Try to show current database and user if psql client is available
if command -v psql >/dev/null 2>&1; then
  python manage.py dbshell -c "select current_database();" || echo "(skip) dbshell current_database failed"
  python manage.py dbshell -c "select current_user;" || echo "(skip) dbshell current_user failed"
else
  echo "psql not found; skipping dbshell verification"
fi

echo "Starting Gunicorn..."
exec gunicorn app.wsgi:application --bind 0.0.0.0:10000 