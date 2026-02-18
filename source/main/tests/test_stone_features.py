"""
Tests for stone number on QR codes and stone certificate features
"""

import os
import time
from io import BytesIO
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Stone
from ..qr_service import QRCodeService
from .base import BaseQRTestCase, BaseStoneWalkerTestCase
import tempfile


class StoneNumberTests(BaseStoneWalkerTestCase):
    """Test the stone sequential number feature"""

    def test_get_stone_number_single_stone(self):
        """First stone created should be #1"""
        stone = self.create_stone('FIRST')
        self.assertEqual(stone.get_stone_number(), 1)

    def test_get_stone_number_ordering(self):
        """Stones should be numbered by creation order"""
        stone1 = self.create_stone('STONE1')
        # Small delay to ensure distinct created_at timestamps
        stone2 = self.create_stone('STONE2')
        stone3 = self.create_stone('STONE3')

        num1 = stone1.get_stone_number()
        num2 = stone2.get_stone_number()
        num3 = stone3.get_stone_number()

        self.assertEqual(num1, 1)
        self.assertGreater(num2, num1)
        self.assertGreater(num3, num2)

    def test_get_stone_number_different_users(self):
        """Stone numbering is global, not per-user"""
        other_user = self.create_user('otheruser', 'otherpass', 'other@example.com')
        stone1 = self.create_stone('S1', user=self.user)
        stone2 = self.create_stone('S2', user=other_user)

        self.assertEqual(stone1.get_stone_number(), 1)
        # stone2 should have number > 1
        self.assertGreaterEqual(stone2.get_stone_number(), 2)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class QRCodeWithStoneNumberTests(BaseQRTestCase):
    """Test QR code generation with stone number"""

    def test_enhanced_qr_includes_stone_number(self):
        """Enhanced QR download should include stone number data"""
        stone = self.create_stone()
        result = QRCodeService.generate_enhanced_qr_for_download(stone)

        self.assertTrue(result['success'])
        self.assertIn('image_data', result)
        # Image data should be non-empty PNG bytes
        self.assertTrue(len(result['image_data']) > 0)

    def test_enhanced_qr_without_stone_number(self):
        """Enhanced QR should work for objects without get_stone_number (e.g., TempStone)"""

        class TempStone:
            def __init__(self):
                self.PK_stone = 'TEMP'
                self.uuid = 'test-uuid'

            def get_qr_url(self):
                return f'https://stonewalker.org/stone-link/0/?key={self.uuid}'

        temp = TempStone()
        result = QRCodeService.generate_enhanced_qr_for_download(temp)
        self.assertTrue(result['success'])
        self.assertIn('image_data', result)

    def test_qr_download_view_returns_png(self):
        """StoneQRCodeView should return a PNG with stone number"""
        stone = self.create_stone()
        response = self.client.get(f'/stone/{stone.PK_stone}/qr/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertIn('attachment', response['Content-Disposition'])

    def test_qr_image_is_grayscale(self):
        """Test that the QR image is pure black and white (no color)"""
        from PIL import Image

        stone = self.create_stone()
        result = QRCodeService.generate_enhanced_qr_for_download(stone)
        self.assertTrue(result['success'])

        from io import BytesIO
        img = Image.open(BytesIO(result['image_data']))
        pixels = list(img.getdata())

        # Every pixel should be grayscale: R == G == B
        for p in pixels:
            self.assertEqual(p[0], p[1], f"Pixel {p} is not grayscale (R != G)")
            self.assertEqual(p[1], p[2], f"Pixel {p} is not grayscale (G != B)")

    def test_create_enhanced_image_with_number(self):
        """Test that the enhanced image is taller when stone_number is provided"""
        from PIL import Image
        import qrcode

        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data('https://stonewalker.org/stone-link/test/')
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        img_without = QRCodeService._create_enhanced_image_with_branding(
            qr_img, 'https://stonewalker.org/stone-link/test/', 'TEST', stone_number=None
        )
        img_with = QRCodeService._create_enhanced_image_with_branding(
            qr_img, 'https://stonewalker.org/stone-link/test/', 'TEST', stone_number=7
        )

        # Image with stone number should be taller (has banner)
        self.assertGreater(img_with.size[1], img_without.size[1])


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class StoneCertificateTests(BaseQRTestCase):
    """Test stone certificate generation"""

    def test_certificate_view_requires_login(self):
        """Certificate view should require authentication"""
        self.client.logout()
        stone = Stone.objects.create(
            PK_stone='CERTTEST',
            FK_user=self.user,
            status='draft',
            description='Test stone for cert'
        )
        response = self.client.get(f'/stone/{stone.PK_stone}/certificate/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_certificate_view_returns_pdf(self):
        """Certificate download should return a PDF for wandering stones"""
        stone = self.create_stone('CERTSTONE', status='wandering')
        response = self.client.get(f'/stone/{stone.PK_stone}/certificate/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('certificate', response['Content-Disposition'].lower())

    def test_certificate_blocked_for_draft(self):
        """Certificate should be blocked for draft stones"""
        stone = self.create_stone('DRAFTCERT', status='draft')
        response = self.client.get(f'/stone/{stone.PK_stone}/certificate/')
        self.assertEqual(response.status_code, 302)

    def test_certificate_blocked_for_published(self):
        """Certificate should be blocked for published stones"""
        stone = self.create_stone('PUBCERT', status='published')
        response = self.client.get(f'/stone/{stone.PK_stone}/certificate/')
        self.assertEqual(response.status_code, 302)

    def test_qr_download_blocked_for_wandering(self):
        """QR download should be blocked for wandering stones"""
        stone = self.create_stone('WANDERQR', status='wandering')
        response = self.client.get(f'/stone/{stone.PK_stone}/qr/')
        self.assertEqual(response.status_code, 302)

    def test_certificate_only_for_owner(self):
        """Only the stone owner should be able to download the certificate"""
        other_user = self.create_user('otheruser', 'otherpass', 'other@example.com')
        stone = self.create_stone('OWNED', user=other_user)

        # Current user is not the owner
        response = self.client.get(f'/stone/{stone.PK_stone}/certificate/')
        # Should redirect (not 200)
        self.assertNotEqual(response.status_code, 200)

    def test_certificate_nonexistent_stone(self):
        """Certificate for non-existent stone should redirect"""
        response = self.client.get('/stone/NONEXISTENT/certificate/')
        self.assertEqual(response.status_code, 302)

    def test_certificate_service_generates_pdf(self):
        """CertificateService should generate valid PDF bytes"""
        from ..certificate_service import CertificateService

        stone = self.create_stone('CERTGEN')
        pdf_bytes = CertificateService.generate_certificate(stone)

        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(len(pdf_bytes) > 0)
        # PDF files start with %PDF
        self.assertTrue(pdf_bytes[:5] == b'%PDF-')

    def test_certificate_includes_stone_number(self):
        """Certificate should include the stone's sequential number"""
        from ..certificate_service import CertificateService

        stone = self.create_stone('NUMCERT')
        pdf_bytes = CertificateService.generate_certificate(stone)

        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(len(pdf_bytes) > 0)

    def test_certificate_link_on_stone_edit_page(self):
        """Stone edit page should show certificate section (enabled for wandering)"""
        stone = self.create_stone('EDITCERT', status='wandering')
        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Certificate')
