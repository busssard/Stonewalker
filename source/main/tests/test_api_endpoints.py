"""
Tests for API endpoints and AJAX functionality
"""

import json
import uuid as uuid_lib
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Stone
from .base import BaseStoneWalkerTestCase, BaseAnonymousTestCase


class StoneNameCheckAPITests(BaseAnonymousTestCase):
    """Test stone name checking API"""
    
    def test_check_available_name(self):
        """Test checking an available stone name"""
        response = self.client.get('/api/check_stone_name/', {'PK_stone': 'AVAILABLE'})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertFalse(data['taken'])
        self.assertEqual(data['PK_stone'], 'AVAILABLE')
    
    def test_check_taken_name(self):
        """Test checking a taken stone name"""
        # Create a stone with this name first
        user = self.create_user('testuser', 'testpass')
        Stone.objects.create(
            PK_stone='TAKEN',
            description='Test stone',
            FK_user=user
        )
        
        response = self.client.get('/api/check_stone_name/', {'PK_stone': 'TAKEN'})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['taken'])
        self.assertEqual(data['reason'], 'taken')
    
    def test_check_empty_name(self):
        """Test checking empty stone name"""
        response = self.client.get('/api/check_stone_name/', {'PK_stone': ''})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['taken'])
        self.assertEqual(data['reason'], 'empty')
    
    def test_check_name_with_whitespace(self):
        """Test checking stone name with whitespace"""
        response = self.client.get('/api/check_stone_name/', {'PK_stone': 'INVALID NAME'})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['taken'])
        self.assertEqual(data['reason'], 'whitespace')
    
    def create_user(self, username, password):
        """Helper to create user for anonymous test case"""
        from django.contrib.auth.models import User
        return User.objects.create_user(username=username, password=password)


class QRGenerationAPITests(BaseStoneWalkerTestCase):
    """Test QR code generation API"""
    
    def test_generate_qr_with_valid_params(self):
        """Test QR generation with valid parameters"""
        response = self.client.get('/api/generate-qr/', {
            'stone_name': 'TESTSTONE',
            'stone_uuid': str(uuid_lib.uuid4())
        })
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('qr_code', data)
        self.assertIn('qr_url', data)
        self.assertIn('stone_name', data)
        self.assertIn('stone_uuid', data)
    
    def test_generate_qr_missing_params(self):
        """Test QR generation with missing parameters"""
        # Missing stone_uuid
        response = self.client.get('/api/generate-qr/', {'stone_name': 'TEST'})
        self.assertEqual(response.status_code, 400)
        
        # Missing stone_name
        response = self.client.get('/api/generate-qr/', {'stone_uuid': 'test-uuid'})
        self.assertEqual(response.status_code, 400)
        
        # Missing both
        response = self.client.get('/api/generate-qr/')
        self.assertEqual(response.status_code, 400)
    
    def test_generate_qr_invalid_uuid(self):
        """Test QR generation with invalid UUID"""
        response = self.client.get('/api/generate-qr/', {
            'stone_name': 'TEST',
            'stone_uuid': 'invalid-uuid-format'
        })
        self.assertEqual(response.status_code, 400)


class EnhancedQRDownloadAPITests(BaseStoneWalkerTestCase):
    """Test enhanced QR download API"""
    
    def test_download_enhanced_qr(self):
        """Test downloading enhanced QR code"""
        response = self.client.get('/api/download-enhanced-qr/', {
            'stone_name': 'TESTSTONE',
            'stone_uuid': str(uuid_lib.uuid4())
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('stonewalker_qr.png', response['Content-Disposition'])
    
    def test_download_enhanced_qr_missing_params(self):
        """Test enhanced QR download with missing parameters"""
        response = self.client.get('/api/download-enhanced-qr/')
        self.assertEqual(response.status_code, 400)
        
        response = self.client.get('/api/download-enhanced-qr/', {'stone_name': 'TEST'})
        self.assertEqual(response.status_code, 400)
    
    def test_download_enhanced_qr_invalid_uuid(self):
        """Test enhanced QR download with invalid UUID"""
        response = self.client.get('/api/download-enhanced-qr/', {
            'stone_name': 'TEST',
            'stone_uuid': 'invalid-uuid'
        })
        self.assertEqual(response.status_code, 400)


class StoneUUIDCheckAPITests(BaseStoneWalkerTestCase):
    """Test stone UUID checking API"""
    
    def test_check_existing_uuid(self):
        """Test checking existing UUID"""
        stone = self.create_stone()
        
        response = self.client.get(f'/api/check-stone-uuid/{stone.uuid}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['exists'])
        self.assertEqual(data['uuid'], str(stone.uuid))
    
    def test_check_nonexistent_uuid(self):
        """Test checking non-existent UUID"""
        fake_uuid = str(uuid_lib.uuid4())
        
        response = self.client.get(f'/api/check-stone-uuid/{fake_uuid}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertFalse(data['exists'])
    
    def test_check_invalid_uuid_format(self):
        """Test checking invalid UUID format"""
        response = self.client.get('/api/check-stone-uuid/invalid-format/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertFalse(data['exists'])
        self.assertIn('error', data)
    
    def test_check_empty_uuid(self):
        """Test checking empty UUID"""
        response = self.client.get('/api/check-stone-uuid//')
        # This should hit a 404 due to URL routing
        self.assertEqual(response.status_code, 404)


class APIAuthenticationTests(BaseAnonymousTestCase):
    """Test API authentication requirements"""
    
    def test_qr_generation_no_auth_required(self):
        """Test that QR generation doesn't require authentication"""
        response = self.client.get('/api/generate-qr/', {
            'stone_name': 'TEST',
            'stone_uuid': str(uuid_lib.uuid4())
        })
        self.assertEqual(response.status_code, 200)
    
    def test_stone_name_check_no_auth_required(self):
        """Test that stone name checking doesn't require authentication"""
        response = self.client.get('/api/check_stone_name/', {'PK_stone': 'TEST'})
        self.assertEqual(response.status_code, 200)
    
    def test_enhanced_qr_download_no_auth_required(self):
        """Test that enhanced QR download doesn't require authentication"""
        response = self.client.get('/api/download-enhanced-qr/', {
            'stone_name': 'TEST',
            'stone_uuid': str(uuid_lib.uuid4())
        })
        self.assertEqual(response.status_code, 200)


class APIResponseFormatTests(BaseStoneWalkerTestCase):
    """Test API response formats and data structure"""
    
    def test_stone_name_check_response_format(self):
        """Test stone name check response format"""
        response = self.client.get('/api/check_stone_name/', {'PK_stone': 'TEST'})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('taken', data)
        self.assertIn('PK_stone', data)
        self.assertIsInstance(data['taken'], bool)
    
    def test_qr_generation_response_format(self):
        """Test QR generation response format"""
        response = self.client.get('/api/generate-qr/', {
            'stone_name': 'TEST',
            'stone_uuid': str(uuid_lib.uuid4())
        })
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('qr_code', data)
        self.assertIn('qr_url', data)
        self.assertIn('stone_name', data)
        self.assertIn('stone_uuid', data)
        self.assertIsInstance(data['success'], bool)
    
    def test_uuid_check_response_format(self):
        """Test UUID check response format"""
        stone = self.create_stone()
        
        response = self.client.get(f'/api/check-stone-uuid/{stone.uuid}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('exists', data)
        self.assertIn('uuid', data)
        self.assertIsInstance(data['exists'], bool)