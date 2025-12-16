"""
Tests for stone creation, editing, and workflow (draft -> published -> sent_off)
"""

from django.urls import reverse
from django.contrib import messages
from ..models import Stone
from .base import BaseStoneWalkerTestCase


class StoneCreationTests(BaseStoneWalkerTestCase):
    """Test stone creation functionality"""
    
    def test_stone_created_as_draft(self):
        """Test that new stones are created as drafts"""
        response = self.client.post('/add_stone/', {
            'PK_stone': 'NEWSTONE',
            'description': 'Test stone description',
            'color': '#FF5733',
            'stone_type': 'hidden'
        })
        
        stone = Stone.objects.get(PK_stone='NEWSTONE')
        self.assertEqual(stone.status, 'draft')
        self.assertTrue(stone.can_be_edited())
        self.assertFalse(stone.can_be_sent_off())
    
    def test_stone_creation_with_uuid(self):
        """Test that stones get a UUID upon creation"""
        response = self.client.post('/add_stone/', {
            'PK_stone': 'UUIDSTONE',
            'description': 'Test stone',
            'stone_type': 'hidden'
        })
        
        stone = Stone.objects.get(PK_stone='UUIDSTONE')
        self.assertIsNotNone(stone.uuid)
        self.assertNotEqual(str(stone.uuid), '')
    
    def test_non_premium_user_one_draft_limit(self):
        """Test that non-premium users can only have one draft stone"""
        # Create first draft stone
        response = self.client.post('/add_stone/', {
            'PK_stone': 'FIRST',
            'description': 'First stone',
            'stone_type': 'hidden'
        })
        self.assertRedirects(response, '/stone/FIRST/edit/')
        
        # Try to create second draft stone
        response = self.client.post('/add_stone/', {
            'PK_stone': 'SECOND',
            'description': 'Second stone',
            'stone_type': 'hidden'
        })
        
        # Should be redirected with error
        self.assertRedirects(response, '/stonewalker/')
        self.assertFalse(Stone.objects.filter(PK_stone='SECOND').exists())
    
    def test_user_can_create_after_publishing(self):
        """Test that users can create new drafts after publishing existing ones"""
        # Create and publish first stone
        stone1 = self.create_stone('STONE1')
        stone1.publish()
        
        # Should be able to create another stone now
        response = self.client.post('/add_stone/', {
            'PK_stone': 'STONE2',
            'description': 'Second stone',
            'stone_type': 'hidden'
        })
        
        self.assertRedirects(response, '/stone/STONE2/edit/')
        self.assertTrue(Stone.objects.filter(PK_stone='STONE2').exists())
    
    def test_stone_type_validation(self):
        """Test stone type validation"""
        # Ensure no existing draft stones interfere
        Stone.objects.filter(FK_user=self.user, status='draft').delete()
        
        # Test hidden stone (no location required)
        response = self.client.post('/add_stone/', {
            'PK_stone': 'HIDDEN',
            'description': 'Hidden stone',
            'stone_type': 'hidden'
        })
        self.assertRedirects(response, '/stone/HIDDEN/edit/')
        
        # Publish first stone to allow creating second
        hidden_stone = Stone.objects.get(PK_stone='HIDDEN')
        hidden_stone.publish()
        
        # Test hunted stone (location required)
        response = self.client.post('/add_stone/', {
            'PK_stone': 'HUNTED',
            'description': 'Hunted stone',
            'stone_type': 'hunted',
            'latitude': '40.7128',
            'longitude': '-74.0060'
        })
        self.assertRedirects(response, '/stone/HUNTED/edit/')


class StoneEditingTests(BaseStoneWalkerTestCase):
    """Test stone editing functionality"""
    
    def test_edit_draft_stone(self):
        """Test editing a draft stone"""
        stone = self.create_stone(status='draft')
        
        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        self.assertEqual(response.status_code, 200)
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
    
    def test_cannot_edit_published_stone(self):
        """Test that published stones cannot be edited"""
        stone = self.create_stone(status='published')
        
        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        self.assertEqual(response.status_code, 302)  # Should redirect with error message
        self.assertRedirects(response, '/stonewalker/')
    
    def test_cannot_edit_sent_off_stone(self):
        """Test that sent off stones cannot be edited"""
        stone = self.create_stone(status='sent_off')
        
        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        self.assertEqual(response.status_code, 302)  # Should redirect with error message
        self.assertRedirects(response, '/stonewalker/')


class StoneWorkflowTests(BaseStoneWalkerTestCase):
    """Test stone status workflow transitions"""
    
    def test_publish_draft_stone(self):
        """Test publishing a draft stone"""
        stone = self.create_stone(status='draft')
        
        response = self.client.post(f'/stone/{stone.PK_stone}/edit/', {
            'description': stone.description,
            'color': stone.color,
            'action': 'publish'
        })
        
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'published')
        self.assertFalse(stone.can_be_edited())
        self.assertTrue(stone.can_be_sent_off())
    
    def test_send_off_published_stone(self):
        """Test sending off a published stone"""
        stone = self.create_stone(status='published')
        
        response = self.client.post(f'/stone/{stone.PK_stone}/send-off/')
        
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'sent_off')
        self.assertIsNotNone(stone.sent_off_at)
        self.assertFalse(stone.can_be_edited())
        self.assertFalse(stone.can_be_sent_off())
    
    def test_cannot_send_off_draft_stone(self):
        """Test that draft stones cannot be sent off"""
        stone = self.create_stone(status='draft')
        
        response = self.client.post(f'/stone/{stone.PK_stone}/send-off/')
        
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'draft')  # Should remain unchanged