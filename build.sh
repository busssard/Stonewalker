#!/bin/bash
# NOTE: This is a legacy Netlify build script. The project now deploys on Render
# (see DEPLOYMENT.md and render_build.sh). This file is kept for reference.

# Exit on any error
set -e

echo "Starting Netlify build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set environment variables for production
export DJANGO_SETTINGS_MODULE=app.conf.production.settings
export DEBUG=False
export ALLOWED_HOSTS=".netlify.app,.netlify.com"

# Create necessary directories
mkdir -p source/content/static
mkdir -p source/content/media

# Collect static files
echo "Collecting static files..."
cd source
python manage.py collectstatic --noinput --settings=app.conf.production.settings

# Run migrations
echo "Running database migrations..."
python manage.py migrate --settings=app.conf.production.settings

# Create a simple WSGI file for Netlify
echo "Creating WSGI configuration..."
cat > netlify_wsgi.py << 'EOF'
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.conf.production.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF

# Create a simple index.html for Netlify
echo "Creating index.html for Netlify..."
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>StoneWalker - A Global Stone Traveling Community</title>
    <meta name="description" content="Track the journeys of painted stones as they travel the world. Join the StoneWalker community!">
    <link rel="stylesheet" href="/static/css/styles.css">
    <link rel="icon" href="/static/favicon.ico">
    <style>
        body {
            font-family: 'Open Sans', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            text-align: center;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            max-width: 500px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        p {
            color: #666;
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        .loading {
            color: #667eea;
            font-weight: bold;
        }
        .note {
            font-size: 0.9em;
            color: #888;
            margin-top: 30px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>StoneWalker</h1>
        <p>A Global Stone Traveling Community</p>
        <p class="loading">Loading...</p>
        <div class="note">
            <p><strong>Note:</strong> This is a static deployment on Netlify.</p>
            <p>For full Django functionality, the backend needs to be deployed separately on a platform that supports Python/Django (like Heroku, Railway, or DigitalOcean).</p>
        </div>
    </div>
    <script>
        // Redirect to the main application after a short delay
        setTimeout(() => {
            window.location.href = '/stonewalker/';
        }, 3000);
    </script>
</body>
</html>
EOF

echo "Build process completed successfully!" 