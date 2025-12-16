#!/usr/bin/env python3
"""
Simple test to verify that downloaded QR code PNG images contain cleartext URL text using OCR.
This test directly calls the download_qr_code function with mock session data.
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User
from main.models import Stone
from main.views import download_qr_code
import uuid
import pytesseract
from PIL import Image
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

def test_qr_download_with_ocr():
    """Test that downloaded QR code PNG contains cleartext URL using OCR"""
    
    print("🔍 Testing QR code download with OCR verification...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='ocrtestuser2', 
        defaults={'email': 'ocrtest2@example.com'}
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
        PK_stone='OCRTEST456',
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
    
    # Generate QR code manually
    print("\n📝 Generating QR code...")
    import qrcode
    from django.conf import settings
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(expected_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white')
    
    # Save QR code to media directory
    qr_filename = f'qr_codes/{stone.PK_stone}_{stone.uuid}_qr.png'
    qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    qr_img.save(qr_path)
    print(f"✅ QR code saved to: {qr_path}")
    
    # Create mock request with session data
    factory = RequestFactory()
    request = factory.get('/download-qr/')
    request.user = user
    
    # Mock session data
    request.session = {
        'qr_download_path': qr_filename,
        'qr_stone_name': stone.PK_stone,
        'qr_stone_uuid': str(stone.uuid),
        'qr_stone_url': expected_url
    }
    
    # Call the download function
    print("\n📥 Calling download_qr_code function...")
    try:
        response = download_qr_code(request)
        
        if response.status_code != 200:
            print(f"❌ Download failed: {response.status_code}")
            return False
        
        if response.get('Content-Type') != 'image/png':
            print(f"❌ Wrong content type: {response.get('Content-Type')}")
            return False
        
        print("✅ QR code download successful")
        print(f"   Content-Type: {response.get('Content-Type')}")
        print(f"   Content-Disposition: {response.get('Content-Disposition')}")
        print(f"   File size: {len(response.content)} bytes")
        
        # Save the image for inspection
        with open('/tmp/qr_ocr_test_simple.png', 'wb') as f:
            f.write(response.content)
        print("💾 Saved QR code to /tmp/qr_ocr_test_simple.png")
        
        # Use OCR to extract text from the image
        print("\n🔍 Running OCR on downloaded PNG...")
        try:
            # Load the image
            img = Image.open(io.BytesIO(response.content))
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
                    
                    if expected_url in extracted_text:
                        print(f"✅ SUCCESS: Expected URL found with config {config}!")
                        found_url = True
                        break
                        
                except Exception as e:
                    print(f"   Config {config} failed: {e}")
            
            if not found_url:
                print("❌ FAILURE: Expected URL not found in any OCR configuration")
                print(f"   Looking for: {expected_url}")
                
                # Try one more time with default config
                try:
                    default_text = pytesseract.image_to_string(img)
                    print(f"   Default config: '{default_text.strip()}'")
                    if expected_url in default_text:
                        print("✅ SUCCESS: Found URL with default config!")
                        found_url = True
                except Exception as e:
                    print(f"   Default config failed: {e}")
            
            return found_url
            
        except Exception as e:
            print(f"❌ OCR failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Download function failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting QR Code OCR Test (Simple)")
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









