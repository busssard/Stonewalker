"""
Base test classes and utilities for main app tests
"""

import tempfile
import shutil
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Stone, StoneMove, StoneScanAttempt


class BaseStoneWalkerTestCase(TestCase):
    """Base test case with common setup for StoneWalker tests"""

    def setUp(self):
        self.client = Client()
        self.user = self.create_user('testuser', 'testpass')
        self.client.login(username='testuser', password='testpass')
        # Accept terms for stone-related operations
        from accounts.models import TermsAcceptance
        TermsAcceptance.objects.get_or_create(user=self.user)
    
    def create_user(self, username='testuser', password='testpass', email='test@example.com'):
        """Helper method to create a test user"""
        return User.objects.create_user(username=username, password=password, email=email)
    
    def create_stone(self, pk_stone='TESTSTONE', user=None, status='draft', **kwargs):
        """Helper method to create a test stone"""
        if user is None:
            user = self.user
        
        defaults = {
            'description': 'Test stone description',
            'color': '#4CAF50',
            'stone_type': 'hidden',
            'FK_user': user,
            'status': status
        }
        defaults.update(kwargs)
        
        return Stone.objects.create(PK_stone=pk_stone, **defaults)
    
    def create_stone_move(self, stone=None, user=None, **kwargs):
        """Helper method to create a stone move"""
        if stone is None:
            stone = self.create_stone()
        if user is None:
            user = self.user
            
        defaults = {
            'FK_stone': stone,
            'FK_user': user,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'comment': 'Test move'
        }
        defaults.update(kwargs)
        
        return StoneMove.objects.create(**defaults)
    
    def create_test_image(self, name='test.jpg', content=b'fake image content'):
        """Helper method to create a test image file"""
        return SimpleUploadedFile(name, content, content_type='image/jpeg')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class BaseQRTestCase(BaseStoneWalkerTestCase):
    """Base test case for QR code related tests with temporary media directory"""
    
    def setUp(self):
        super().setUp()
        # Store the temp directory for cleanup
        self._temp_media_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temporary media files
        if hasattr(self, '_temp_media_dir'):
            shutil.rmtree(self._temp_media_dir, ignore_errors=True)
        super().tearDown()


class BaseAuthenticatedTestCase(BaseStoneWalkerTestCase):
    """Base test case for tests that require authentication"""
    pass


class BaseAnonymousTestCase(TestCase):
    """Base test case for tests that don't require authentication"""
    
    def setUp(self):
        self.client = Client()