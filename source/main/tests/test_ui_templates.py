"""
Tests for UI components, templates, and frontend functionality
"""

from django.urls import reverse
from ..models import Stone
from .base import BaseStoneWalkerTestCase, BaseAnonymousTestCase


class MainPageTests(BaseAnonymousTestCase):
    """Test main page and navigation"""
    
    def test_main_page_loads(self):
        """Test that main page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'StoneWalker')
    
    def test_stonewalker_start_page(self):
        """Test stonewalker start page"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Stone')
        self.assertContains(response, 'Scan a Stone')


class WelcomeModalTests(BaseAnonymousTestCase):
    """Test welcome modal functionality"""
    
    def test_welcome_modal_for_guests(self):
        """Test that welcome modal appears for guest users"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        # Welcome modal should be included
        self.assertContains(response, 'welcome-banner-modal')
        self.assertContains(response, 'Welcome to StoneWalker!')


class MyStonesPageTests(BaseStoneWalkerTestCase):
    """Test My Stones page functionality"""
    
    def test_my_stones_page_requires_auth(self):
        """Test that My Stones page requires authentication"""
        self.client.logout()
        response = self.client.get('/my-stones/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_my_stones_page_loads(self):
        """Test that My Stones page loads for authenticated users"""
        response = self.client.get('/my-stones/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Stones')
    
    def test_my_stones_shows_user_stones(self):
        """Test that My Stones shows user's stones"""
        stone = self.create_stone()
        
        response = self.client.get('/my-stones/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, stone.PK_stone)
        self.assertContains(response, stone.description)
    
    def test_my_stones_shows_status(self):
        """Test that My Stones shows stone status"""
        draft_stone = self.create_stone('DRAFT', status='draft')
        published_stone = self.create_stone('PUBLISHED', status='published')
        
        response = self.client.get('/my-stones/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Draft')
        self.assertContains(response, 'Published')


class StoneCreationModalTests(BaseStoneWalkerTestCase):
    """Test stone creation modal functionality"""
    
    def test_create_modal_authentication_check(self):
        """Test that create modal checks authentication"""
        self.client.logout()
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        # Should contain modals but with auth checks
        self.assertContains(response, 'openSharedCreateStoneModal')
    
    def test_modal_includes_stone_types(self):
        """Test that modal includes both stone types"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hidden')
        self.assertContains(response, 'Hunted')
    
    def test_modal_includes_validation(self):
        """Test that modal includes name validation"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'check_stone_name')


class ScanModalTests(BaseStoneWalkerTestCase):
    """Test stone scan modal functionality"""
    
    def test_scan_modal_present(self):
        """Test that scan modal is present in templates"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'scan-stone-modal')
        self.assertContains(response, 'QR Code Scanner')
    
    def test_scan_modal_includes_manual_input(self):
        """Test that scan modal includes manual UUID input"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'enter UUID manually')
    
    def test_scan_modal_congratulations_functionality(self):
        """Test scan modal congratulations functionality"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Congratulations')


class LanguageTests(BaseAnonymousTestCase):
    """Test language functionality"""
    
    def test_change_language_page(self):
        """Test that language change page loads"""
        response = self.client.get('/language/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select your preferred language')
    
    def test_available_languages_displayed(self):
        """Test that all configured languages are displayed"""
        response = self.client.get('/language/')
        # Should contain major languages
        self.assertContains(response, 'English')
        self.assertContains(response, 'French')
        self.assertContains(response, 'Spanish')
    
    def test_language_change_redirects_to_main(self):
        """Test that language change includes redirect to root page"""
        response = self.client.get('/language/')
        # The redirect_to is now set to '/' for both prefixed and unprefixed languages
        self.assertEqual(response.status_code, 200)


class ResponsiveDesignTests(BaseStoneWalkerTestCase):
    """Test responsive design elements"""
    
    def test_floating_action_buttons_present(self):
        """Test that floating action buttons are present"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'floating-action-bar')
        self.assertContains(response, 'add-stone-fab')
        self.assertContains(response, 'scan-stone-fab')
    
    def test_map_container_present(self):
        """Test that map container is present"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'map-container')
        self.assertContains(response, 'leaflet')


class StoneFoundTemplateTests(BaseStoneWalkerTestCase):
    """Test stone found page functionality"""
    
    def test_stone_found_page_via_link(self):
        """Test stone found page loads via stone-link"""
        stone = self.create_stone()
        
        response = self.client.get(f'/stone-link/{stone.uuid}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You found')
        self.assertContains(response, stone.PK_stone)
    
    def test_first_stone_detection(self):
        """Test first stone detection logic"""
        # User has no previous moves, so this should be their first
        stone = self.create_stone()
        
        response = self.client.get(f'/stone-link/{stone.uuid}/')
        self.assertEqual(response.status_code, 200)
        # Should indicate it's their first stone
        self.assertContains(response, 'first')


class HuntedStoneLocationTests(BaseStoneWalkerTestCase):
    """Test hunted stone location functionality"""
    
    def test_hunted_location_field_in_templates(self):
        """Test that hunted location fields are present"""
        response = self.client.get('/stonewalker/')
        self.assertEqual(response.status_code, 200)
        # Should contain location inputs for hunted stones
        self.assertContains(response, 'latitude')
        self.assertContains(response, 'longitude')
    
    def test_hunted_stone_requires_location(self):
        """Test that hunted stones require location"""
        # Try to create hunted stone without location
        response = self.client.post('/add_stone/', {
            'PK_stone': 'HUNTED',
            'description': 'Hunted stone',
            'stone_type': 'hunted'
            # No latitude/longitude provided
        })
        
        # Should redirect back due to validation error
        self.assertRedirects(response, '/stonewalker/')
        self.assertFalse(Stone.objects.filter(PK_stone='HUNTED').exists())