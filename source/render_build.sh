#!/bin/bash
set -e

echo "Starting Render.com build process..."

# Upgrade pip and install build tools
echo "Upgrading pip and build tools..."
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel

# Install requirements
echo "Installing Python requirements..."
python -m pip install -r requirements.txt

# Change to source directory and collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!" 