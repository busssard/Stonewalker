#!/bin/bash
set -e

echo "Starting Render.com build process (source/render_build.sh)..."

# Upgrade pip and install build tools
echo "Upgrading pip and build tools..."
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel

# Install requirements (from repo root if available)
if [ -f ../requirements.txt ]; then
  echo "Installing Python requirements from ../requirements.txt..."
  python -m pip install -r ../requirements.txt
elif [ -f requirements.txt ]; then
  echo "Installing Python requirements from ./requirements.txt..."
  python -m pip install -r requirements.txt
fi

# Collect static files from within source directory
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!" 