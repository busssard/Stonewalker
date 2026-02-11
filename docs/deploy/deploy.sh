#!/bin/bash
# =============================================================================
# StoneWalker Auto-Deploy Script
# Place at: /opt/stonewalker/deploy.sh
# Called by GitHub Actions (or manually) after a push to main.
# =============================================================================

set -euo pipefail

APP_DIR="/opt/stonewalker"
SOURCE_DIR="$APP_DIR/source"
VENV="$APP_DIR/venv/bin"
ENV_FILE="$APP_DIR/.env"
LOG_FILE="/var/log/stonewalker/deploy.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Deploy started ==="

# Load environment
export $(grep -v '^#' "$ENV_FILE" | xargs)

cd "$APP_DIR"

# Pull latest code
log "Pulling latest code..."
git fetch origin main
git reset --hard origin/main

# Install/update dependencies
log "Installing dependencies..."
$VENV/pip install -q -r requirements.txt

cd "$SOURCE_DIR"

# Run migrations
log "Running migrations..."
$VENV/python manage.py migrate --noinput

# Compile translations
log "Compiling translations..."
$VENV/python manage.py compilemessages 2>/dev/null || log "Warning: compilemessages failed (gettext missing?)"

# Collect static files
log "Collecting static files..."
$VENV/python manage.py collectstatic --noinput --clear -v 0

# Reload gunicorn (graceful — no downtime)
log "Reloading application..."
sudo systemctl reload stonewalker

log "=== Deploy complete ==="
