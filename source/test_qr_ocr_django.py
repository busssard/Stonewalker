#!/usr/bin/env python3
"""
Django test to verify that downloaded QR code PNG images contain cleartext URL text using OCR.
"""

import os
import sys
import django
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from main.models import Stone
import uuid
import pytesseract
from PIL import Image
import io

class QROCRTest(TestCase):
    """Test QR code download with OCR verification"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='ocrtestuser',
            email='ocrtest@example.com',
            password='testpass123'
        )
        
        # Create test stone
        self.stone_uuid = uuid.uuid4()
        self.stone = Stone.objects.create(
            PK_stone='OCRTEST123',
            FK_user=self.user,
            description='OCR test stone',
            color='#FF0000',
            shape='circle',
            stone_type='hidden',
            uuid=self.stone_uuid
        )
        
        self.expected_url = f"http://localhost:8000/stone-link/{self.stone.uuid}/"
        
    @override_settings(ALLOWED_HOSTS=['testserver', 'localhost'])
    def test_qr_download_contains_cleartext_url(self):
        """Test that downloaded QR code PNG contains cleartext URL using OCR"""
        
        print(f"\n🔍 Testing QR code download with OCR verification...")
        print(f"   Stone: {self.stone.PK_stone}")
        print(f"   Expected URL: {self.expected_url}")
        
        client = Client()
        client.force_login(self.user)
        
        # Create a stone and generate QR code
        print("\n📝 Creating stone and generating QR code...")
        response = client.post('/add_stone/', {
            'PK_stone': 'OCRTEST123',
            'description': 'OCR test stone',
            'stone_type': 'hidden',
            'color': '#FF0000',
            'shape': 'circle'
        })
        
        self.assertEqual(response.status_code, 302, "Stone creation should succeed")
        print("✅ Stone created successfully")
        
        # Check session data
        session = client.session
        self.assertIn('qr_download_path', session, "Session should contain QR download path")
        self.assertIn('qr_stone_url', session, "Session should contain QR stone URL")
        print(f"✅ Session contains QR data: {session.get('qr_stone_url')}")
        
        # Download the QR code
        print("\n📥 Downloading QR code PNG...")
        download_response = client.get('/download-qr/')
        
        self.assertEqual(download_response.status_code, 200, "QR download should succeed")
        self.assertEqual(download_response.get('Content-Type'), 'image/png', "Should return PNG image")
        print("✅ QR code downloaded successfully")
        print(f"   Content-Type: {download_response.get('Content-Type')}")
        print(f"   Content-Disposition: {download_response.get('Content-Disposition')}")
        print(f"   File size: {len(download_response.content)} bytes")
        
        # Save the image for inspection
        with open('/tmp/qr_ocr_test_django.png', 'wb') as f:
            f.write(download_response.content)
        print("💾 Saved QR code to /tmp/qr_ocr_test_django.png")
        
        # Use OCR to extract text from the image
        print("\n🔍 Running OCR on downloaded PNG...")
        try:
            # Load the image
            img = Image.open(io.BytesIO(download_response.content))
            print(f"   Image size: {img.size}")
            print(f"   Image mode: {img.mode}")
            
            # Extract text using OCR with different configurations
            configs = [
                '--psm 3',  # Fully automatic page segmentation
                '--psm 4',  # Assume a single column of text
                '--psm 6',  # Assume a single uniform block of text
                '--psm 7',  # Treat the image as a single text line
                '--psm 8',  # Treat the image as a single word
                '--psm 13', # Raw line. Treat the image as a single text line
            ]
            
            found_url = False
            for config in configs:
                try:
                    extracted_text = pytesseract.image_to_string(img, config=config)
                    print(f"   Config {config}: '{extracted_text.strip()}'")
                    
                    if self.expected_url in extracted_text:
                        print(f"✅ SUCCESS: Expected URL found with config {config}!")
                        found_url = True
                        break
                        
                except Exception as e:
                    print(f"   Config {config} failed: {e}")
            
            if not found_url:
                print("❌ FAILURE: Expected URL not found in any OCR configuration")
                print(f"   Looking for: {self.expected_url}")
                
                # Try one more time with default config
                try:
                    default_text = pytesseract.image_to_string(img)
                    print(f"   Default config: '{default_text.strip()}'")
                    if self.expected_url in default_text:
                        print("✅ SUCCESS: Found URL with default config!")
                        found_url = True
                except Exception as e:
                    print(f"   Default config failed: {e}")
            
            self.assertTrue(found_url, f"Expected URL '{self.expected_url}' not found in OCR text")
            
        except Exception as e:
            self.fail(f"OCR failed: {e}")

if __name__ == '__main__':
    # Run the test
    import django
    from django.test.utils import get_runner
    from django.conf import settings
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["test_qr_ocr_django.QROCRTest.test_qr_download_contains_cleartext_url"])
    
    if failures:
        print(f"\n💥 TEST FAILED: {failures} failures")
        sys.exit(1)
    else:
        print(f"\n🎉 TEST PASSED: QR code PNG contains cleartext URL!")
        sys.exit(0)









