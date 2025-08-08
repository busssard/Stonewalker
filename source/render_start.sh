#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn app.wsgi:application --bind 0.0.0.0:10000 