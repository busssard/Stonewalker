#!/bin/bash
# Run Django development server with PostgreSQL
# Optionally start Discourse forum for SSO testing

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Helper functions
start_discourse() {
    echo "Starting Discourse dev stack..."
    docker compose -f "$SCRIPT_DIR/forum/docker-compose.yml" up -d
    echo ""
    echo "Discourse starting at http://localhost:4200"
    echo "First boot takes 3-5 minutes. Check logs with:"
    echo "  docker compose -f forum/docker-compose.yml logs -f discourse"
    echo ""
    echo "Admin credentials: admin / admin123456"
    echo ""
}

stop_discourse() {
    echo "Stopping Discourse dev stack..."
    docker compose -f "$SCRIPT_DIR/forum/docker-compose.yml" down
}

# Handle commands
case "$1" in
    discourse-start)
        start_discourse
        exit 0
        ;;
    discourse-stop)
        stop_discourse
        exit 0
        ;;
    discourse-logs)
        docker compose -f "$SCRIPT_DIR/forum/docker-compose.yml" logs -f discourse
        exit 0
        ;;
    discourse-reset)
        echo "Resetting Discourse (deleting all data)..."
        docker compose -f "$SCRIPT_DIR/forum/docker-compose.yml" down -v
        exit 0
        ;;
    help)
        echo "Usage: ./run_dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  (none)           Start Django development server"
        echo "  discourse-start  Start Discourse forum in Docker"
        echo "  discourse-stop   Stop Discourse forum"
        echo "  discourse-logs   View Discourse logs"
        echo "  discourse-reset  Reset Discourse (delete all data)"
        echo "  help             Show this help"
        echo ""
        exit 0
        ;;
esac

# Activate virtual environment
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "Activated virtual environment"
else
    echo "Warning: Virtual environment not found at $SCRIPT_DIR/venv"
fi

# Check if DATABASE_URL is set, if not use default local PostgreSQL
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
    echo "Using default local PostgreSQL database"
fi

# Check if Discourse is running
if docker compose -f "$SCRIPT_DIR/forum/docker-compose.yml" ps --quiet discourse 2>/dev/null | grep -q .; then
    echo "Discourse forum running at http://localhost:4200"
fi

echo "Starting Django development server with PostgreSQL..."
echo "Database URL: $DATABASE_URL"
echo ""

cd source
python manage.py runserver
