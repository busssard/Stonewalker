"""
Main app tests package

This package contains organized test modules for the main application.
All tests are organized by functionality for better maintainability.
"""

# Import all test modules to ensure they're discovered by Django's test runner
from .test_models import *
from .test_qr_system import *
from .test_stone_workflow import *
from .test_stone_scanning import *
from .test_ui_templates import *
from .test_api_endpoints import *