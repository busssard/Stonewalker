"""
Pytest configuration for Django project with automatic translation compilation.
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# Add the source directory to Python path
source_dir = Path(__file__).parent / "source"
sys.path.insert(0, str(source_dir))

# Set Django settings and configure Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

def compile_translations():
    """Compile translations before running tests."""
    try:
        # Change to source directory
        os.chdir(source_dir)
        
        # Run translation compilation
        result = subprocess.run(
            ["python", "manage.py", "compilemessages"],
            capture_output=True,
            text=True,
            cwd=source_dir
        )
        
        if result.returncode == 0:
            print("✅ Translations compiled successfully")
        else:
            print(f"⚠️  Translation compilation warnings: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️  Translation compilation failed: {e}")
        # Don't fail tests if translation compilation fails
        pass

def pytest_configure(config):
    """Configure pytest and compile translations."""
    # Set Django settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    
    # Compile translations before tests
    compile_translations()

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location."""
    for item in items:
        # Mark tests in main app as integration tests
        if "main" in str(item.fspath):
            item.add_marker("integration")
        # Mark tests in accounts app as unit tests
        elif "accounts" in str(item.fspath):
            item.add_marker("unit") 