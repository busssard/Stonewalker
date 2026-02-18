"""
Tests for QR code generation, downloading, and display functionality
"""

import os
import json
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Stone
from ..qr_service import QRCodeService
from .base import BaseQRTestCase, BaseStoneWalkerTestCase


class QRCodeGenerationTests(BaseQRTestCase):
    """Test QR code generation functionality"""
    
    def test_qr_service_generates_qr_code(self):
        """Test that QR service can generate QR codes"""
        stone = self.create_stone()
        result = QRCodeService.generate_qr_for_stone(stone)
        
        self.assertTrue(result['success'])
        self.assertIn('qr_image_url', result)
        self.assertIn('stone_url', result)
    
    def test_qr_service_error_handling(self):
        """Test QR service handles errors gracefully"""
        # Test with invalid settings to force error
        with self.settings(MEDIA_ROOT='/invalid'):
            stone = self.create_stone()
            result = QRCodeService.generate_qr_for_stone(stone)
            self.assertFalse(result['success'])
            self.assertIn('error', result)
    
    def test_qr_api_endpoint(self):
        """Test the QR generation API endpoint"""
        import uuid
        test_uuid = str(uuid.uuid4())
        
        response = self.client.get('/api/generate-qr/', {
            'stone_name': 'TESTSTONE',
            'stone_uuid': test_uuid
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('qr_code', data)
        self.assertIn('qr_url', data)


class QRCodeDownloadTests(BaseQRTestCase):
    """Test QR code download functionality"""
    
    def test_download_regular_qr(self):
        """Test downloading regular QR code"""
        stone = self.create_stone()
        response = self.client.get(f'/stone/{stone.PK_stone}/qr/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_download_enhanced_qr(self):
        """Test downloading enhanced QR code with branding"""
        import uuid
        test_uuid = str(uuid.uuid4())
        
        response = self.client.get('/api/download-enhanced-qr/', {
            'stone_name': 'TESTSTONE',
            'stone_uuid': test_uuid
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_download_qr_missing_params(self):
        """Test QR download with missing parameters"""
        response = self.client.get('/api/download-enhanced-qr/')
        self.assertEqual(response.status_code, 400)
        
        response = self.client.get('/api/download-enhanced-qr/', {'stone_name': 'TEST'})
        self.assertEqual(response.status_code, 400)


class QRCodeDisplayTests(BaseStoneWalkerTestCase):
    """Test QR code display in templates and modals"""
    
    def test_qr_display_in_stone_edit(self):
        """Test that QR code section is displayed in stone edit page"""
        stone = self.create_stone()
        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QR Code')
        self.assertContains(response, 'Downloads')
    
    def test_qr_url_persistence(self):
        """Test that QR URLs are persistent"""
        stone = self.create_stone()
        qr_url = stone.get_qr_url()

        self.assertIsNotNone(qr_url)
        expected = f'https://stonewalker.org/stone-link/{stone.stone_number}/?key={stone.uuid}'
        self.assertEqual(qr_url, expected)
        # QR URL should remain the same after multiple calls
        self.assertEqual(qr_url, stone.get_qr_url())