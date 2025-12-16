"""
Tests for models and model methods
"""

import uuid as uuid_lib
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from ..models import Stone, StoneMove, StoneScanAttempt, calculate_stone_distance
from .base import BaseStoneWalkerTestCase


class StoneModelTests(BaseStoneWalkerTestCase):
    """Test Stone model functionality"""
    
    def test_stone_creation_generates_uuid(self):
        """Test that stones automatically get UUIDs"""
        stone = self.create_stone()
        self.assertIsNotNone(stone.uuid)
        self.assertIsInstance(stone.uuid, uuid_lib.UUID)
    
    def test_unique_uuids(self):
        """Test that each stone gets a unique UUID"""
        stone1 = self.create_stone('STONE1')
        stone2 = self.create_stone('STONE2')
        self.assertNotEqual(stone1.uuid, stone2.uuid)
    
    def test_stone_status_defaults_to_draft(self):
        """Test that stones default to draft status"""
        stone = self.create_stone()
        self.assertEqual(stone.status, 'draft')
    
    def test_can_be_edited_logic(self):
        """Test stone editing permission logic"""
        # Draft stones can be edited
        draft = self.create_stone(status='draft')
        self.assertTrue(draft.can_be_edited())
        
        # Published stones cannot be edited
        published = self.create_stone('PUB', status='published')
        self.assertFalse(published.can_be_edited())
        
        # Sent off stones cannot be edited
        sent_off = self.create_stone('SENT', status='sent_off')
        self.assertFalse(sent_off.can_be_edited())
    
    def test_can_be_sent_off_logic(self):
        """Test stone send-off permission logic"""
        # Draft stones cannot be sent off
        draft = self.create_stone(status='draft')
        self.assertFalse(draft.can_be_sent_off())
        
        # Published stones can be sent off
        published = self.create_stone('PUB', status='published')
        self.assertTrue(published.can_be_sent_off())
        
        # Already sent off stones cannot be sent off again
        sent_off = self.create_stone('SENT', status='sent_off')
        self.assertFalse(sent_off.can_be_sent_off())
    
    def test_publish_method(self):
        """Test stone publish method"""
        stone = self.create_stone(status='draft')
        
        result = stone.publish()
        self.assertTrue(result)
        self.assertEqual(stone.status, 'published')
        
        # Cannot publish already published stone
        result = stone.publish()
        self.assertFalse(result)
    
    def test_send_off_method(self):
        """Test stone send off method"""
        stone = self.create_stone(status='published')
        
        result = stone.send_off()
        self.assertTrue(result)
        self.assertEqual(stone.status, 'sent_off')
        self.assertIsNotNone(stone.sent_off_at)
        
        # Cannot send off draft stone
        draft = self.create_stone('DRAFT', status='draft')
        result = draft.send_off()
        self.assertFalse(result)
    
    def test_get_qr_url(self):
        """Test QR URL generation"""
        stone = self.create_stone()
        qr_url = stone.get_qr_url()
        
        self.assertIsNotNone(qr_url)
        self.assertIn(str(stone.uuid), qr_url)
        self.assertIn('/stone-link/', qr_url)
    
    def test_user_can_create_stone_logic(self):
        """Test user stone creation permission logic"""
        # New user can create stone
        self.assertTrue(Stone.user_can_create_stone(self.user))
        
        # User with draft stone cannot create another
        self.create_stone(status='draft')
        self.assertFalse(Stone.user_can_create_stone(self.user))
        
        # User can create after publishing draft
        stone = Stone.objects.get(FK_user=self.user, status='draft')
        stone.publish()
        self.assertTrue(Stone.user_can_create_stone(self.user))
    
    def test_get_user_draft_stone(self):
        """Test getting user's draft stone"""
        # No draft initially
        self.assertIsNone(Stone.get_user_draft_stone(self.user))
        
        # Create draft
        draft = self.create_stone(status='draft')
        retrieved = Stone.get_user_draft_stone(self.user)
        self.assertEqual(draft, retrieved)
        
        # Publish it, should return None again
        draft.publish()
        self.assertIsNone(Stone.get_user_draft_stone(self.user))


class StoneMoveModelTests(BaseStoneWalkerTestCase):
    """Test StoneMove model functionality"""
    
    def test_stone_move_creation(self):
        """Test creating stone moves"""
        stone = self.create_stone()
        move = self.create_stone_move(stone=stone)
        
        self.assertEqual(move.FK_stone, stone)
        self.assertEqual(move.FK_user, self.user)
        self.assertIsNotNone(move.timestamp)
    
    def test_stone_move_updates_distance(self):
        """Test that stone moves update total distance"""
        stone = self.create_stone()
        
        # First move
        move1 = self.create_stone_move(
            stone=stone, 
            latitude=40.7128, 
            longitude=-74.0060
        )
        
        # Second move
        move2 = self.create_stone_move(
            stone=stone, 
            latitude=40.7589, 
            longitude=-73.9851
        )
        
        # Calculate distance and update stone
        stone.distance_km = calculate_stone_distance(stone)
        stone.save()
        
        # Should have some distance now
        self.assertGreater(stone.distance_km, 0)


class StoneScanAttemptModelTests(BaseStoneWalkerTestCase):
    """Test StoneScanAttempt model functionality"""
    
    def test_scan_attempt_creation(self):
        """Test creating scan attempts"""
        stone = self.create_stone()
        
        attempt = StoneScanAttempt.record_scan_attempt(stone, self.user, None)
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.FK_stone, stone)
        self.assertEqual(attempt.FK_user, self.user)
        self.assertIsNotNone(attempt.scan_time)
    
    def test_can_scan_again_logic(self):
        """Test scan blackout period logic"""
        stone = self.create_stone()
        
        # Can scan initially
        self.assertTrue(StoneScanAttempt.can_scan_again(stone, self.user))
        
        # Record scan attempt
        StoneScanAttempt.record_scan_attempt(stone, self.user, None)
        
        # Cannot scan again immediately
        self.assertFalse(StoneScanAttempt.can_scan_again(stone, self.user))
        
        # Simulate old scan attempt (over 7 days)
        attempt = StoneScanAttempt.objects.get(FK_stone=stone, FK_user=self.user)
        attempt.scan_time = timezone.now() - timedelta(days=8)
        attempt.save()
        
        # Should be able to scan again now
        self.assertTrue(StoneScanAttempt.can_scan_again(stone, self.user))
    
    def test_different_users_can_scan_same_stone(self):
        """Test that different users can scan the same stone"""
        stone = self.create_stone()
        other_user = self.create_user('otheruser', 'otherpass')
        
        # First user scans
        StoneScanAttempt.record_scan_attempt(stone, self.user, None)
        self.assertFalse(StoneScanAttempt.can_scan_again(stone, self.user))
        
        # Other user should still be able to scan
        self.assertTrue(StoneScanAttempt.can_scan_again(stone, other_user))


class DistanceCalculationTests(BaseStoneWalkerTestCase):
    """Test distance calculation functionality"""
    
    def test_calculate_distance_no_moves(self):
        """Test distance calculation for stone with no moves"""
        stone = self.create_stone()
        distance = calculate_stone_distance(stone)
        self.assertEqual(distance, 0)
    
    def test_calculate_distance_single_move(self):
        """Test distance calculation for stone with one move"""
        stone = self.create_stone()
        self.create_stone_move(stone=stone)
        
        distance = calculate_stone_distance(stone)
        self.assertEqual(distance, 0)  # Single move = no distance
    
    def test_calculate_distance_multiple_moves(self):
        """Test distance calculation for stone with multiple moves"""
        stone = self.create_stone()
        
        # NYC coordinates
        self.create_stone_move(
            stone=stone, 
            latitude=40.7128, 
            longitude=-74.0060
        )
        
        # Boston coordinates (approximately 300km away)
        self.create_stone_move(
            stone=stone, 
            latitude=42.3601, 
            longitude=-71.0589
        )
        
        distance = calculate_stone_distance(stone)
        
        # Should be approximately 300km
        self.assertGreater(distance, 250)
        self.assertLess(distance, 350)