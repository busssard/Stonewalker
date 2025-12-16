"""
Tests for the new QR code system with stone status and editing
"""

import os
import tempfile
import shutil
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Stone, StoneMove
from .qr_service import QRCodeService


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class NewQRSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def tearDown(self):
        # Clean up temporary media files
        if hasattr(self, '_temp_media_root'):
            shutil.rmtree(self._temp_media_root, ignore_errors=True)

    def test_stone_creation_as_draft(self):
        """Test that new stones are created as drafts"""
        response = self.client.post('/add_stone/', {
            'PK_stone': 'TESTSTONE',
            'description': 'Test stone description',
            'color': '#FF5733',
            'stone_type': 'hidden'
        })
        
        stone = Stone.objects.get(PK_stone='TESTSTONE')
        self.assertEqual(stone.status, 'draft')
        self.assertTrue(stone.can_be_edited())
        self.assertFalse(stone.can_be_sent_off())

    def test_non_premium_user_one_draft_limit(self):
        """Test that non-premium users can only have one draft stone"""
        # Create first draft stone
        response = self.client.post('/add_stone/', {
            'PK_stone': 'TESTSTONE1',
            'description': 'First test stone',
            'stone_type': 'hidden'
        })
        self.assertRedirects(response, '/stone/TESTSTONE1/edit/')
        
        # Try to create second draft stone
        response = self.client.post('/add_stone/', {
            'PK_stone': 'TESTSTONE2', 
            'description': 'Second test stone',
            'stone_type': 'hidden'
        })
        
        # Should be redirected with error message
        self.assertRedirects(response, '/stonewalker/')
        self.assertFalse(Stone.objects.filter(PK_stone='TESTSTONE2').exists())

    def test_stone_editing_workflow(self):
        """Test the complete stone editing workflow"""
        # Create draft stone
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Original description',
            FK_user=self.user,
            status='draft'
        )
        
        # Test editing draft stone
        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Stone')
        self.assertContains(response, 'This stone is in draft mode')
        
        # Update stone
        response = self.client.post(f'/stone/{stone.PK_stone}/edit/', {
            'description': 'Updated description',
            'color': '#FF5733',
            'action': 'save'
        })
        self.assertRedirects(response, f'/stone/{stone.PK_stone}/edit/')
        
        stone.refresh_from_db()
        self.assertEqual(stone.description, 'Updated description')
        self.assertEqual(stone.color, '#FF5733')

    def test_stone_publishing_workflow(self):
        """Test publishing a draft stone"""
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user,
            status='draft'
        )
        
        # Publish the stone
        response = self.client.post(f'/stone/{stone.PK_stone}/edit/', {
            'description': 'Test stone',
            'action': 'publish'
        })
        
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'published')
        self.assertFalse(stone.can_be_edited())
        self.assertTrue(stone.can_be_sent_off())

    def test_stone_send_off_workflow(self):
        """Test sending off a published stone"""
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user,
            status='published'
        )
        
        # Send off the stone
        response = self.client.post(f'/stone/{stone.PK_stone}/send-off/')
        
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'sent_off')
        self.assertFalse(stone.can_be_edited())
        self.assertFalse(stone.can_be_sent_off())
        self.assertIsNotNone(stone.sent_off_at)

    def test_qr_code_generation_service(self):
        """Test the new QR code service"""
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user
        )
        
        # Generate QR code
        qr_result = QRCodeService.generate_qr_for_stone(stone)
        
        self.assertTrue(qr_result['success'])
        self.assertIn('qr_image_url', qr_result)
        self.assertIn('qr_file_path', qr_result)
        self.assertIn('stone_url', qr_result)
        
        # Verify file was created
        self.assertTrue(os.path.exists(qr_result['qr_file_path']))
        
        # Verify URL contains stone UUID
        self.assertIn(str(stone.uuid), qr_result['stone_url'])

    def test_qr_code_download_view(self):
        """Test downloading QR code through view"""
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user
        )
        
        response = self.client.get(f'/stone/{stone.PK_stone}/qr/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('TESTSTONE_qr.png', response['Content-Disposition'])

    def test_qr_code_persistent_url(self):
        """Test that QR codes have persistent URLs"""
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user
        )
        
        qr_url1 = stone.get_qr_url()
        qr_url2 = stone.get_qr_url()
        
        # URLs should be consistent
        self.assertEqual(qr_url1, qr_url2)
        self.assertIn(str(stone.uuid), qr_url1)
        self.assertIn('/stone-link/', qr_url1)

    def test_stone_link_view(self):
        """Test the stone-link view functionality"""
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user,
            status='published'  # Must be published to be scannable
        )
        
        response = self.client.get(f'/stone-link/{stone.uuid}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stone Found')
        self.assertContains(response, stone.PK_stone)

    def test_cannot_edit_published_stone(self):
        """Test that published stones cannot be edited"""
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user,
            status='published'
        )
        
        # Try to access edit page
        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        self.assertRedirects(response, '/stonewalker/')

    def test_cannot_edit_sent_off_stone(self):
        """Test that sent off stones cannot be edited"""
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user,
            status='sent_off'
        )
        
        # Try to access edit page  
        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        self.assertRedirects(response, '/stonewalker/')

    def test_user_can_create_new_draft_after_publishing(self):
        """Test that users can create new drafts after publishing existing ones"""
        # Create and publish a stone
        stone1 = Stone.objects.create(
            PK_stone='TESTSTONE1',
            description='First stone',
            FK_user=self.user,
            status='draft'
        )
        stone1.publish()
        
        # Now should be able to create another draft
        response = self.client.post('/add_stone/', {
            'PK_stone': 'TESTSTONE2',
            'description': 'Second stone',
            'stone_type': 'hidden'
        })
        
        self.assertRedirects(response, '/stone/TESTSTONE2/edit/')
        stone2 = Stone.objects.get(PK_stone='TESTSTONE2')
        self.assertEqual(stone2.status, 'draft')

    def test_my_stones_view_shows_status(self):
        """Test that my stones view shows stone statuses"""
        # Create stones with different statuses
        draft_stone = Stone.objects.create(
            PK_stone='DRAFT',
            description='Draft stone',
            FK_user=self.user,
            status='draft'
        )
        
        published_stone = Stone.objects.create(
            PK_stone='PUBLISHED',
            description='Published stone', 
            FK_user=self.user,
            status='published'
        )
        
        response = self.client.get('/my-stones/')
        self.assertEqual(response.status_code, 200)
        
        # Check that both stones are in context
        self.assertContains(response, 'DRAFT')
        self.assertContains(response, 'PUBLISHED')

    def test_qr_service_error_handling(self):
        """Test QR service handles errors gracefully"""
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user
        )
        
        # Test with invalid media path
        with override_settings(MEDIA_ROOT='/invalid/path'):
            qr_result = QRCodeService.generate_qr_for_stone(stone)
            self.assertFalse(qr_result['success'])
            self.assertIn('error', qr_result)