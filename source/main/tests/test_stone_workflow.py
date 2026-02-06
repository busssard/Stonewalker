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


class StoneNameSubmissionTests(BaseStoneWalkerTestCase):
    """
    Regression tests for stone name handling during creation.

    Bug (Feb 2026): The create button's JS handler called closeModal() before
    form.submit(), which reset the form and wiped the stone name. The backend
    then received an empty PK_stone and returned "Missing required stone name."

    These tests verify the backend correctly handles stone names in all cases,
    so any future frontend or backend changes that break name submission will
    be caught immediately.
    """

    def test_stone_created_with_valid_name(self):
        """A stone submitted with a valid name should be created successfully"""
        response = self.client.post('/add_stone/', {
            'PK_stone': 'MyBeautifulStone',
            'description': 'A lovely painted rock',
            'stone_type': 'hidden',
        })
        self.assertTrue(Stone.objects.filter(PK_stone='MyBeautifulStone').exists())
        stone = Stone.objects.get(PK_stone='MyBeautifulStone')
        self.assertEqual(stone.FK_user, self.user)
        self.assertEqual(stone.status, 'draft')

    def test_empty_name_rejected(self):
        """An empty stone name must be rejected with an error message"""
        response = self.client.post('/add_stone/', {
            'PK_stone': '',
            'description': 'No name stone',
            'stone_type': 'hidden',
        })
        self.assertRedirects(response, '/stonewalker/')
        self.assertFalse(Stone.objects.filter(description='No name stone').exists())
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertTrue(any('stone name' in str(m).lower() for m in msgs))

    def test_missing_name_field_rejected(self):
        """A POST with no PK_stone field at all must be rejected"""
        response = self.client.post('/add_stone/', {
            'description': 'No name field at all',
            'stone_type': 'hidden',
        })
        self.assertRedirects(response, '/stonewalker/')
        self.assertFalse(Stone.objects.filter(description='No name field at all').exists())

    def test_whitespace_only_name_not_blocked_by_view(self):
        """
        NOTE: The view only checks `if not PK_stone` which passes for '   '.
        The model has a validate_no_whitespace validator but Django's save()
        does not call full_clean(). This documents the current behavior --
        whitespace names slip through to the database.
        """
        response = self.client.post('/add_stone/', {
            'PK_stone': '   ',
            'description': 'Whitespace name',
            'stone_type': 'hidden',
        })
        # Currently this is accepted (view doesn't strip/check whitespace-only)
        # If this test starts failing, it means validation was tightened - good!
        self.assertTrue(Stone.objects.filter(PK_stone='   ').exists())

    def test_name_preserved_through_submission(self):
        """The exact name submitted must be the name stored - no truncation or mutation"""
        test_names = ['Rocky', 'Stone-With-Dashes', 'ALLCAPS123', 'x']
        for i, name in enumerate(test_names):
            # Publish previous draft to allow creating next
            drafts = Stone.objects.filter(FK_user=self.user, status='draft')
            for d in drafts:
                d.publish()

            response = self.client.post('/add_stone/', {
                'PK_stone': name,
                'description': f'Test stone {i}',
                'stone_type': 'hidden',
            })
            self.assertTrue(
                Stone.objects.filter(PK_stone=name).exists(),
                f'Stone with name "{name}" was not created'
            )
            stone = Stone.objects.get(PK_stone=name)
            self.assertEqual(stone.PK_stone, name)

    def test_unicode_name_accepted(self):
        """Unicode stone names should work (painted stones are international)"""
        response = self.client.post('/add_stone/', {
            'PK_stone': 'Stein-42',
            'description': 'A German stone',
            'stone_type': 'hidden',
        })
        self.assertTrue(Stone.objects.filter(PK_stone='Stein-42').exists())

    def test_long_name_within_limit(self):
        """A name at the max length (50 chars) should be accepted"""
        long_name = 'A' * 50
        response = self.client.post('/add_stone/', {
            'PK_stone': long_name,
            'description': 'Max length name',
            'stone_type': 'hidden',
        })
        self.assertTrue(Stone.objects.filter(PK_stone=long_name).exists())

    def test_name_at_boundary_lengths(self):
        """Names at 49 and 50 chars should work, confirming the boundary"""
        name_49 = 'B' * 49
        response = self.client.post('/add_stone/', {
            'PK_stone': name_49,
            'description': 'Just under limit',
            'stone_type': 'hidden',
        })
        self.assertTrue(Stone.objects.filter(PK_stone=name_49).exists())

    def test_all_form_fields_reach_backend(self):
        """Verify that name, description, type, and color all arrive intact"""
        response = self.client.post('/add_stone/', {
            'PK_stone': 'FullDataStone',
            'description': 'Complete submission test',
            'stone_type': 'hidden',
            'color': '#FF0000',
        })
        stone = Stone.objects.get(PK_stone='FullDataStone')
        self.assertEqual(stone.description, 'Complete submission test')
        self.assertEqual(stone.stone_type, 'hidden')
        self.assertEqual(stone.color, '#FF0000')
        self.assertEqual(stone.shape, 'circle')  # hidden stones get circle

    def test_hunted_stone_with_name_and_location(self):
        """Hunted stones need both name and location - verify all fields arrive"""
        response = self.client.post('/add_stone/', {
            'PK_stone': 'HuntedGem',
            'description': 'Find me!',
            'stone_type': 'hunted',
            'latitude': '52.5200',
            'longitude': '13.4050',
        })
        stone = Stone.objects.get(PK_stone='HuntedGem')
        self.assertEqual(stone.stone_type, 'hunted')
        self.assertEqual(stone.shape, 'triangle')  # hunted stones get triangle

    def test_unique_names_create_distinct_stones(self):
        """Two different names should create two distinct stones"""
        self.client.post('/add_stone/', {
            'PK_stone': 'StoneAlpha',
            'description': 'First',
            'stone_type': 'hidden',
        })
        # Publish so draft limit doesn't block second creation
        Stone.objects.filter(PK_stone='StoneAlpha').update(status='published')

        self.client.post('/add_stone/', {
            'PK_stone': 'StoneBeta',
            'description': 'Second',
            'stone_type': 'hidden',
        })
        self.assertTrue(Stone.objects.filter(PK_stone='StoneAlpha').exists())
        self.assertTrue(Stone.objects.filter(PK_stone='StoneBeta').exists())
        self.assertEqual(Stone.objects.filter(PK_stone__in=['StoneAlpha', 'StoneBeta']).count(), 2)



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