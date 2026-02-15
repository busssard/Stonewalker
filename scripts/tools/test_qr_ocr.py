#!/usr/bin/env python3
"""
Test script to verify that downloaded QR code PNG images contain cleartext URL text using OCR.
This script will:
1. Create a test stone and generate a QR code
2. Download the QR code PNG
3. Use OCR to extract text from the image
4. Verify that the expected URL text is present
"""

import os
import sys
import django
from django.test import Client, override_settings
from django.contrib.auth.models import User
from main.models import Stone
import uuid
import pytesseract
from PIL import Image
import io
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

def test_qr_download_with_ocr():
    """Test that downloaded QR code PNG contains cleartext URL using OCR"""
    
    print("🔍 Testing QR code download with OCR verification...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='ocrtestuser', 
        defaults={'email': 'ocrtest@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Create test stone
    stone_uuid = uuid.uuid4()
    stone, created = Stone.objects.get_or_create(
        PK_stone='OCRTEST123',
        defaults={
            'FK_user': user,
            'description': 'OCR test stone',
            'color': '#FF0000',
            'shape': 'circle',
            'stone_type': 'hidden',
            'uuid': stone_uuid
        }
    )
    print(f"✅ Created test stone: {stone.PK_stone}")
    print(f"   UUID: {stone.uuid}")
    
    # Expected URL
    expected_url = f"http://localhost:8000/stone-link/{stone.uuid}/"
    print(f"   Expected URL: {expected_url}")
    
    # Test with proper settings
    with override_settings(ALLOWED_HOSTS=['testserver', 'localhost']):
        client = Client()
        client.force_login(user)
        
        # Create a stone and generate QR code
        print("\n📝 Creating stone and generating QR code...")
        response = client.post('/add_stone/', {
            'PK_stone': 'OCRTEST123',
            'description': 'OCR test stone',
            'stone_type': 'hidden',
            'color': '#FF0000',
            'shape': 'circle'
        })
        
        if response.status_code != 302:
            print(f"❌ Stone creation failed: {response.status_code}")
            return False
        
        print("✅ Stone created successfully")
        
        # Check session data
        session = client.session
        if 'qr_download_path' not in session:
            print("❌ No QR download path in session")
            return False
        
        print(f"✅ Session contains QR data: {session.get('qr_stone_url')}")
        
        # Download the QR code
        print("\n📥 Downloading QR code PNG...")
        download_response = client.get('/download-qr/')
        
        if download_response.status_code != 200:
            print(f"❌ QR download failed: {download_response.status_code}")
            return False
        
        if download_response.get('Content-Type') != 'image/png':
            print(f"❌ Wrong content type: {download_response.get('Content-Type')}")
            return False
        
        print("✅ QR code downloaded successfully")
        print(f"   Content-Type: {download_response.get('Content-Type')}")
        print(f"   Content-Disposition: {download_response.get('Content-Disposition')}")
        print(f"   File size: {len(download_response.content)} bytes")
        
        # Save the image for inspection
        with open('/tmp/qr_ocr_test.png', 'wb') as f:
            f.write(download_response.content)
        print("💾 Saved QR code to /tmp/qr_ocr_test.png")
        
        # Use OCR to extract text from the image
        print("\n🔍 Running OCR on downloaded PNG...")
        try:
            # Load the image
            img = Image.open(io.BytesIO(download_response.content))
            print(f"   Image size: {img.size}")
            print(f"   Image mode: {img.mode}")
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(img, config='--psm 6')
            print(f"   Extracted text: '{extracted_text.strip()}'")
            
            # Check if the expected URL is in the extracted text
            if expected_url in extracted_text:
                print("✅ SUCCESS: Expected URL found in OCR text!")
                return True
            else:
                print("❌ FAILURE: Expected URL not found in OCR text")
                print(f"   Looking for: {expected_url}")
                print(f"   Found text: {extracted_text.strip()}")
                
                # Try different OCR configurations
                print("\n🔄 Trying different OCR configurations...")
                configs = [
                    '--psm 3',  # Fully automatic page segmentation
                    '--psm 4',  # Assume a single column of text
                    '--psm 6',  # Assume a single uniform block of text
                    '--psm 7',  # Treat the image as a single text line
                    '--psm 8',  # Treat the image as a single word
                    '--psm 13', # Raw line. Treat the image as a single text line
                ]
                
                for config in configs:
                    try:
                        text = pytesseract.image_to_string(img, config=config)
                        if expected_url in text:
                            print(f"✅ Found URL with config {config}: {text.strip()}")
                            return True
                        else:
                            print(f"   Config {config}: '{text.strip()}'")
                    except Exception as e:
                        print(f"   Config {config} failed: {e}")
                
                return False
                
        except Exception as e:
            print(f"❌ OCR failed: {e}")
            return False

def main():
    """Main test function"""
    print("🚀 Starting QR Code OCR Test")
    print("=" * 50)
    
    try:
        success = test_qr_download_with_ocr()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 TEST PASSED: QR code PNG contains cleartext URL!")
        else:
            print("💥 TEST FAILED: QR code PNG does not contain cleartext URL!")
        
        return success
        
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)









