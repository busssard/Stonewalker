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

# Legacy compatibility test (moved from tests.py to resolve import conflict)
from django.test import TestCase
from django.contrib.auth.models import User
from main.models import Stone


class LegacyCompatibilityTests(TestCase):
    """Minimal tests to ensure backward compatibility"""

    def test_basic_functionality_still_works(self):
        """Test that basic functionality hasn't been broken by refactoring"""
        user = User.objects.create_user(username='testuser', password='testpass')

        stone = Stone.objects.create(
            PK_stone='LEGACY_TEST',
            description='Legacy compatibility test',
            FK_user=user
        )

        self.assertEqual(stone.PK_stone, 'LEGACY_TEST')
        self.assertEqual(stone.status, 'draft')
        self.assertIsNotNone(stone.uuid)
        self.assertTrue(stone.can_be_edited())