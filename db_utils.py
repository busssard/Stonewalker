#!/usr/bin/env python3
"""
Database utility functions for production PostgreSQL management.
This script provides CRUD operations for users and stones.
"""

import os
import sys
import json
import django
from pathlib import Path

# Add the source directory to Python path
source_dir = Path(__file__).parent / 'source'
sys.path.insert(0, str(source_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
os.environ.setdefault('IS_PRODUCTION', 'True')

# Load production database credentials
def load_production_credentials():
    """Load production database credentials from postgres_production.json"""
    creds_file = Path(__file__).parent / 'postgres_production.json'
    
    if not creds_file.exists():
        raise FileNotFoundError(f"Production credentials file not found: {creds_file}")
    
    with open(creds_file, 'r') as f:
        creds = json.load(f)
    
    # Set DATABASE_URL environment variable for Django
    database_url = f"postgresql://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"
    os.environ['DATABASE_URL'] = database_url
    
    return creds

# Initialize Django
def setup_django():
    """Initialize Django with production settings"""
    try:
        django.setup()
        return True
    except Exception as e:
        print(f"Error setting up Django: {e}")
        return False

# Database connection test
def test_connection():
    """Test database connection"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result[0] == 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    # Load credentials and setup Django
    try:
        creds = load_production_credentials()
        print(f"Loaded credentials for database: {creds['database']} on {creds['host']}")
        
        if setup_django():
            print("Django setup successful")
            if test_connection():
                print("Database connection successful")
            else:
                print("Database connection failed")
                sys.exit(1)
        else:
            print("Django setup failed")
            sys.exit(1)
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)
