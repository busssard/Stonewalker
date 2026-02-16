#!/bin/bash
# Recreate the Python virtual environment from scratch.
# Useful when packages fail to install (e.g. reportlab on Python 3.8)
# or when the venv gets into a broken state.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "=== Recreating virtual environment ==="

# Deactivate current venv if active
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating current virtual environment..."
    deactivate 2>/dev/null || true
fi

# Remove existing venv
if [ -d "$VENV_DIR" ]; then
    echo "Removing existing venv at $VENV_DIR..."
    rm -rf "$VENV_DIR"
fi

# Create fresh venv
echo "Creating fresh virtual environment..."
python3 -m venv "$VENV_DIR"

# Upgrade pip
echo "Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip

# Install dependencies
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "WARNING: requirements.txt not found at $SCRIPT_DIR/requirements.txt"
fi

echo ""
echo "=== Virtual environment recreated successfully ==="
echo "Activate with: source $VENV_DIR/bin/activate"
