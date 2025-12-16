"""
Main tests module - imports organized tests from tests package

This file maintains backward compatibility while using the new organized test structure.
All actual test code is now in the main/tests/ package for better organization.
"""

# Import all tests from the organized test package
from .tests import *

# Keep a few critical tests inline for legacy compatibility
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from .models import Stone


class LegacyCompatibilityTests(TestCase):
    """Minimal tests to ensure backward compatibility"""
    
    def test_basic_functionality_still_works(self):
        """Test that basic functionality hasn't been broken by refactoring"""
        # Create a user
        user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create a stone
        stone = Stone.objects.create(
            PK_stone='LEGACY_TEST',
            description='Legacy compatibility test',
            FK_user=user
        )
        
        # Verify basic attributes
        self.assertEqual(stone.PK_stone, 'LEGACY_TEST')
        self.assertEqual(stone.status, 'draft')
        self.assertIsNotNone(stone.uuid)
        self.assertTrue(stone.can_be_edited())