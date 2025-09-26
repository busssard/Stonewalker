#!/bin/bash
set -e

# 🚨 SAFETY CHECK: Build script should NEVER touch the database
# This script should only handle static files and dependencies
DANGEROUS_COMMANDS=("migrate" "flush" "reset_db" "sqlflush" "sqlsequencereset" "loaddata" "dumpdata" "clear_cache" "dbshell")
for cmd in "${DANGEROUS_COMMANDS[@]}"; do
    if grep -q "manage.py $cmd" "$0"; then
        echo "❌ DANGER: Found database command '$cmd' in render_build.sh"
        echo "❌ Build script should NEVER touch the database! Aborting build."
        exit 1
    fi
done

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