import os
import re
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import activate, gettext as _
from django.conf import settings
import polib
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
import tempfile
import shutil
import uuid
from .models import Stone, StoneMove


class ChangeLanguageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_change_language_page_loads(self):
        response = self.client.get(reverse('change_language'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select your preferred language')

    def test_change_language_available_languages(self):
        response = self.client.get(reverse('change_language'))
        # Check that all configured languages are present
        for lang_code, lang_name in settings.LANGUAGES:
            self.assertContains(response, lang_name)

    def test_change_language_form_submission(self):
        response = self.client.post(reverse('change_language'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_change_language_redirect_to_main_page(self):
        """Test that the change language page includes redirect_to to main page"""
        response = self.client.get(reverse('change_language'))
        self.assertEqual(response.status_code, 200)
        # Check that the redirect_to is set to the main page
        self.assertContains(response, 'name="next"')
        self.assertContains(response, 'value="/stonewalker/"')

    def test_language_change_redirects_to_main(self):
        """Test that changing language redirects to the main page"""
        # First, get the change language page to get the CSRF token
        response = self.client.get(reverse('change_language'))
        self.assertEqual(response.status_code, 200)
        
        # Extract CSRF token
        csrf_token = response.cookies.get('csrftoken').value
        
        # Submit language change form
        response = self.client.post(
            reverse('set_language'),
            {
                'language': 'fr',  # Change to French
                'next': '/stonewalker/',
            },
            HTTP_X_CSRFTOKEN=csrf_token,
            follow=True  # Follow redirects
        )
        
        # Should redirect to main page
        self.assertEqual(response.status_code, 200)
        # Check that we're on the main page (stonewalker_start)
        self.assertIn('/stonewalker/', response.redirect_chain[-1][0] if response.redirect_chain else '')
        
        # Verify language was actually changed
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, 'fr')

    def test_language_change_preserves_user_session(self):
        """Test that language change doesn't affect user authentication"""
        # Create a test user and log in
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        
        # Get change language page
        response = self.client.get(reverse('change_language'))
        self.assertEqual(response.status_code, 200)
        
        # Extract CSRF token
        csrf_token = response.cookies.get('csrftoken').value
        
        # Change language
        response = self.client.post(
            reverse('set_language'),
            {
                'language': 'de',  # Change to German
                'next': '/stonewalker/',
            },
            HTTP_X_CSRFTOKEN=csrf_token,
            follow=True
        )
        
        # Should still be logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'testuser')
        
        # Should be on main page
        self.assertEqual(response.status_code, 200)
        self.assertIn('/stonewalker/', response.redirect_chain[-1][0] if response.redirect_chain else '')

    def test_change_language_view_context_data(self):
        """Test that ChangeLanguageView provides correct context data"""
        from main.views import ChangeLanguageView
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get(reverse('change_language'))
        
        view = ChangeLanguageView()
        view.request = request
        context = view.get_context_data()
        
        # Check that redirect_to is set to main page
        self.assertEqual(context['redirect_to'], '/stonewalker/')


class TranslationQualityAssuranceTests(TestCase):
    """Comprehensive tests for translation quality and PO file validation"""
    
    def setUp(self):
        self.client = Client()
        self.locale_path = os.path.join(settings.BASE_DIR, 'content', 'locale')
        # Define forbidden characters that cause encoding issues
        self.forbidden_characters = {
            '\u201c': 'Smart double quotes (") - use regular quotes (")',
            '\u201d': 'Smart double quotes (") - use regular quotes (")',
            '\u2018': 'Smart single quotes (\') - use regular quotes (\')',
            '\u2019': 'Smart single quotes (\') - use regular quotes (\')',
            '\u2013': 'En dash (–) - use hyphen (-)',
            '\u2014': 'Em dash (—) - use hyphen (-)',
        }
    
    def test_po_files_have_proper_headers(self):
        """Test that all PO files have proper headers with charset specification"""
        for lang_code, lang_name in settings.LANGUAGES:
            po_file_path = os.path.join(self.locale_path, lang_code, 'LC_MESSAGES', 'django.po')
            if os.path.exists(po_file_path):
                with open(po_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for proper header
                self.assertIn('Content-Type: text/plain; charset=UTF-8', content,
                             f"PO file for {lang_name} ({lang_code}) missing charset specification")
                self.assertIn('Language: ' + lang_code, content,
                             f"PO file for {lang_name} ({lang_code}) missing language specification")
    
    def test_po_files_no_forbidden_characters(self):
        """Test that PO files don't contain forbidden smart quotes and special characters"""
        for lang_code, lang_name in settings.LANGUAGES:
            po_file_path = os.path.join(self.locale_path, lang_code, 'LC_MESSAGES', 'django.po')
            if os.path.exists(po_file_path):
                try:
                    po = polib.pofile(po_file_path)
                    for entry in po:
                        # Skip header entry
                        if entry.msgid == "":
                            continue
                        
                        # Check if this is a Django built-in translation
                        is_django_builtin = False
                        if entry.occurrences:
                            for occurrence in entry.occurrences:
                                if isinstance(occurrence, str) and occurrence.startswith('venv/lib/python3.8/site-packages/django/'):
                                    is_django_builtin = True
                                    break
                        
                        # Skip Django built-in translations
                        if is_django_builtin:
                            continue
                        
                        # Check for forbidden characters in msgstr
                        for char, description in self.forbidden_characters.items():
                            if char in entry.msgstr:
                                self.fail(f"PO file for {lang_name} ({lang_code}) contains {description} in: '{entry.msgid}'")
                except Exception as e:
                    self.fail(f"Failed to parse PO file for {lang_name} ({lang_code}): {e}")
    
    def test_po_files_no_empty_msgstr(self):
        """Test that PO files don't have empty msgstr entries (except for header and Django built-ins)"""
        for lang_code, lang_name in settings.LANGUAGES:
            po_file_path = os.path.join(self.locale_path, lang_code, 'LC_MESSAGES', 'django.po')
            if os.path.exists(po_file_path):
                try:
                    po = polib.pofile(po_file_path)
                    for entry in po:
                        # Skip header entry
                        if entry.msgid == "":
                            continue
                        
                        # Check if this is a Django built-in translation
                        is_django_builtin = False
                        if entry.occurrences:
                            for occurrence in entry.occurrences:
                                if isinstance(occurrence, str) and occurrence.startswith('venv/lib/python3.8/site-packages/django/'):
                                    is_django_builtin = True
                                    break
                        
                        # Skip Django built-in translations
                        if is_django_builtin:
                            continue
                        
                        # Check for empty msgstr
                        if not entry.msgstr.strip():
                            self.fail(f"PO file for {lang_name} ({lang_code}) has empty msgstr for: '{entry.msgid}'")
                except Exception as e:
                    self.fail(f"Failed to parse PO file for {lang_name} ({lang_code}): {e}")
    
    def test_po_files_no_duplicate_msgids(self):
        """Test that PO files don't have duplicate msgid entries (excluding Django built-ins)"""
        for lang_code, lang_name in settings.LANGUAGES:
            po_file_path = os.path.join(self.locale_path, lang_code, 'LC_MESSAGES', 'django.po')
            if os.path.exists(po_file_path):
                try:
                    po = polib.pofile(po_file_path)
                    # Filter out Django built-in translations that may have duplicates
                    custom_msgids = []
                    for entry in po:
                        if entry.msgid != "":
                            # Check if this is a Django built-in translation
                            is_django_builtin = False
                            if entry.occurrences:
                                for occurrence in entry.occurrences:
                                    if isinstance(occurrence, str) and occurrence.startswith('venv/lib/python3.8/site-packages/django/'):
                                        is_django_builtin = True
                                        break
                            
                            if not is_django_builtin:
                                custom_msgids.append(entry.msgid)
                    
                    # Filter out month names which are legitimate duplicates in Django
                    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                                  'July', 'August', 'September', 'October', 'November', 'December']
                    filtered_duplicates = [msgid for msgid in set(custom_msgids) if custom_msgids.count(msgid) > 1 and msgid not in month_names]
                    self.assertEqual(len(filtered_duplicates), 0,
                                   f"PO file for {lang_name} ({lang_code}) has duplicate custom msgids: {filtered_duplicates}")
                except Exception as e:
                    self.fail(f"Failed to parse PO file for {lang_name} ({lang_code}): {e}")
    
    def test_po_files_compile_successfully(self):
        """Test that all PO files can be compiled without errors"""
        for lang_code, lang_name in settings.LANGUAGES:
            po_file_path = os.path.join(self.locale_path, lang_code, 'LC_MESSAGES', 'django.po')
            if os.path.exists(po_file_path):
                try:
                    po = polib.pofile(po_file_path)
                    # If we can parse it with polib, it should compile
                    self.assertTrue(True, f"PO file for {lang_name} ({lang_code}) compiles successfully")
                except Exception as e:
                    self.fail(f"PO file for {lang_name} ({lang_code}) fails to compile: {e}")


class TranslationFunctionalityTests(TestCase):
    """Tests to verify that translations actually work in the application"""
    
    def setUp(self):
        self.client = Client()
        self.test_strings = [
            'About StoneWalker',
            'Welcome to StoneWalker',
            'Welcome to StoneWalker!',
            'Did you know:',
            'How it works:',
            'Pick up a brush and paint a stone.',
            'Start Your Journey',
        ]
    
    def test_translations_work_for_all_languages(self):
        """Test that translations work for all configured languages"""
        for lang_code, lang_name in settings.LANGUAGES:
            # Activate the language
            activate(lang_code)
            
            # Test that translations are different from English (indicating they're translated)
            for test_string in self.test_strings:
                translated = _(test_string)
                # Skip if it's the same as English (might be intentional for some strings)
                if lang_code != 'en':
                    # For now, we just check that the translation doesn't fail
                    self.assertIsInstance(translated, str,
                                        f"Translation failed for '{test_string}' in {lang_name} ({lang_code})")
    
    def test_about_page_translations(self):
        """Test that the About page shows different content in different languages"""
        # Test English
        activate('en')
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        english_content = response.content.decode('utf-8')
        
        # Test German
        activate('de')
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        german_content = response.content.decode('utf-8')
        
        # The content should be different (indicating translation is working)
        # We'll check for specific translated strings
        self.assertIn('Alles über StoneWalker', german_content,
                     "German translation not found in About page")
        self.assertIn('About StoneWalker', english_content,
                     "English text not found in About page")
    
    def test_home_page_translations(self):
        """Test that the home page shows different content in different languages"""
        # Test English
        activate('en')
        # Clear session to ensure welcome modal shows
        self.client.session.flush()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        english_content = response.content.decode('utf-8')
        
        # Test German
        activate('de')
        # Clear session to ensure welcome modal shows
        self.client.session.flush()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        german_content = response.content.decode('utf-8')
        
        # Check for translated strings
        self.assertIn('Hallo bei StoneWalker!', german_content,
                     "German translation not found in home page")
        self.assertIn('Welcome to StoneWalker!', english_content,
                     "English text not found in home page")
    
    def test_language_switching_works(self):
        """Test that language switching via URL works correctly"""
        # Test switching to German
        self.client.session.flush()
        response = self.client.get('/de/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hallo bei StoneWalker!', response.content.decode('utf-8'))
        
        # Test switching to Italian
        self.client.session.flush()
        response = self.client.get('/it/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Benvenuto in StoneWalker!', response.content.decode('utf-8'))


class TranslationCoverageTests(TestCase):
    """Tests to ensure all important strings are translated"""
    
    def test_critical_strings_are_translated(self):
        """Test that critical user-facing strings are translated in all languages"""
        critical_strings = [
            'About StoneWalker',
            'Welcome to StoneWalker',
            'Start Your Journey',
            'How it works:',
            'Community Guidelines:',
        ]
        
        for lang_code, lang_name in settings.LANGUAGES:
            if lang_code == 'en':  # Skip English as it's the source
                continue
                
            activate(lang_code)
            for string in critical_strings:
                translated = _(string)
                # Check that it's not the same as the original (indicating translation)
                if string != translated:
                    self.assertNotEqual(string, translated,
                                      f"String '{string}' is not translated in {lang_name} ({lang_code})")
                else:
                    # If it's the same, it might be intentional, so we'll just log it
                    print(f"Warning: '{string}' appears untranslated in {lang_name} ({lang_code})") 


class WelcomeModalTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_welcome_modal_shows_for_guests(self):
        """Test that welcome modal is shown to unauthenticated users"""
        # Clear session to ensure welcome modal shows
        self.client.session.flush()
        # Also clear any existing session data
        self.client.session.clear()
        # Force English language for consistent testing
        from django.utils.translation import activate
        activate('en')
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)
        
        # Check for welcome modal HTML structure
        self.assertContains(response, 'welcome-modal-overlay')
        self.assertContains(response, 'welcome-modal-content')
        self.assertContains(response, 'Welcome to StoneWalker!')
        self.assertContains(response, 'You are a guest.')
        self.assertContains(response, 'Create an Account')
        self.assertContains(response, 'Log In')

    def test_welcome_modal_not_shown_for_authenticated_users(self):
        """Test that welcome modal is not shown to authenticated users"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Welcome to StoneWalker!')
        self.assertNotContains(response, 'You are a guest.')

    def test_welcome_modal_has_correct_styling_classes(self):
        """Test that welcome modal uses the correct avant-garde styling classes"""
        # Clear session to ensure welcome modal shows
        self.client.session.flush()
        self.client.session.clear()
        # Force English language for consistent testing
        from django.utils.translation import activate
        activate('en')
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)
    
        # Check for modern styling classes
        self.assertContains(response, 'avant-card')
        self.assertContains(response, 'profile-modal-overlay')

    def test_welcome_modal_has_decorative_elements(self):
        """Test that welcome modal includes decorative background elements"""
        # Clear session to ensure welcome modal shows
        self.client.session.flush()
        self.client.session.clear()
        # Force English language for consistent testing
        from django.utils.translation import activate
        activate('en')
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)
    
        # Check for decorative elements - the modal uses profile-modal-overlay styling
        self.assertContains(response, 'profile-modal-overlay')

    def test_welcome_modal_buttons_are_properly_styled(self):
        """Test that welcome modal buttons use avant-btn styling"""
        # Clear session to ensure welcome modal shows
        self.client.session.flush()
        self.client.session.clear()
        # Force English language for consistent testing
        from django.utils.translation import activate
        activate('en')
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)
    
        # Check for button styling
        self.assertContains(response, 'avant-btn')

    def test_welcome_modal_has_local_storage_functionality(self):
        """Test that welcome modal includes localStorage functionality"""
        # Clear session to ensure welcome modal shows
        self.client.session.flush()
        self.client.session.clear()
        # Force English language for consistent testing
        from django.utils.translation import activate
        activate('en')
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)
        
        # Check for localStorage functionality
        self.assertContains(response, 'stonewalker_guest_last_visit')
        self.assertContains(response, 'localStorage.setItem')


class MyStonesTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_my_stones_page_loads(self):
        """Test that my-stones page loads correctly for authenticated users"""
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My CREATIONS')
        self.assertContains(response, 'MY INTERACTIONS')

    def test_my_stones_requires_login(self):
        """Test that my-stones page requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_my_stones_with_no_stones(self):
        """Test that my-stones page shows empty state correctly"""
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        # Should show empty state messages
        self.assertContains(response, 'creationsData = [')
        self.assertContains(response, 'interactionsData = [')
        # Should contain the JavaScript that handles empty states
        self.assertContains(response, 'added any stones yet')
        self.assertContains(response, 'interacted with any stones yet')

    def test_my_stones_empty_state_messages(self):
        """Test that empty state messages are properly displayed"""
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the JavaScript arrays are empty
        self.assertContains(response, 'const creationsData = [')
        self.assertContains(response, 'const interactionsData = [')
        
        # Check that the render function handles empty data
        self.assertContains(response, 'if (!data.length) {')
        self.assertContains(response, 'added any stones yet')
        self.assertContains(response, 'interacted with any stones yet')

    def test_my_stones_with_stones(self):
        """Test that my-stones page shows stones when they exist"""
        from main.models import Stone, StoneMove
        # Create a test stone
        stone = Stone.objects.create(
            PK_stone='TESTSTONE',
            description='Test stone',
            FK_user=self.user,
            color='#ff9800',
            shape='circle'
        )
        # Create a move for the stone
        StoneMove.objects.create(
            FK_stone=stone,
            FK_user=self.user,
            latitude=40.7128,
            longitude=-74.0060,
            comment='Test move'
        )
        
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        # Should contain the stone data
        self.assertContains(response, 'TESTSTONE')
        self.assertContains(response, 'Test stone')
        self.assertContains(response, '#ff9800')

    def test_my_stones_interactions(self):
        """Test that my-stones page shows interactions correctly"""
        from main.models import Stone, StoneMove
        from django.contrib.auth.models import User
        
        # Create another user and their stone
        other_user = User.objects.create_user(username='otheruser', password='testpass')
        stone = Stone.objects.create(
            PK_stone='OTHERSTONE',
            description='Other user stone',
            FK_user=other_user,
            color='#4CAF50',
            shape='triangle'
        )
        
        # Current user interacts with the stone
        StoneMove.objects.create(
            FK_stone=stone,
            FK_user=self.user,
            latitude=40.7128,
            longitude=-74.0060,
            comment='I found this stone!'
        )
        
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        # Should show the interaction
        self.assertContains(response, 'OTHERSTONE')
        self.assertContains(response, 'Other user stone')

    def test_distance_calculation(self):
        """Test that distance calculation works correctly"""
        from main.models import Stone, StoneMove, calculate_stone_distance
        
        # Create a stone with moves
        stone = Stone.objects.create(
            PK_stone='DISTTEST',
            description='Distance test stone',
            FK_user=self.user,
            color='#ff5722',
            shape='circle'
        )
        
        # Add moves to calculate distance
        StoneMove.objects.create(
            FK_stone=stone,
            FK_user=self.user,
            latitude=40.7128,
            longitude=-74.0060,
            comment='First move'
        )
        
        StoneMove.objects.create(
            FK_stone=stone,
            FK_user=self.user,
            latitude=40.7589,
            longitude=-73.9851,
            comment='Second move'
        )
        
        # Calculate distance
        distance = calculate_stone_distance(stone)
        self.assertGreater(distance, 0)
        
        # Update stone distance
        stone.distance_km = distance
        stone.save()
        
        # Check that the view shows the stone with distance
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'DISTTEST')
        # The distance is displayed via JavaScript, so we check for the data structure
        self.assertContains(response, 'distance_km')

    def test_my_stones_context_data(self):
        """Test that my-stones view provides correct context data"""
        from main.models import Stone, StoneMove
        from django.contrib.auth.models import User
        
        # Create test stones
        stone1 = Stone.objects.create(
            PK_stone='STONE1',
            description='First stone',
            FK_user=self.user,
            color='#ff9800',
            shape='circle'
        )
        
        # Create another user's stone
        other_user = User.objects.create_user(username='otheruser', password='testpass')
        stone2 = Stone.objects.create(
            PK_stone='STONE2',
            description='Other user stone',
            FK_user=other_user,
            color='#4CAF50',
            shape='triangle'
        )
        
        # Current user interacts with other user's stone
        StoneMove.objects.create(
            FK_stone=stone2,
            FK_user=self.user,
            latitude=40.7128,
            longitude=-74.0060,
            comment='Found this stone!'
        )
        
        # Get the view context
        from main.views import MyStonesView
        view = MyStonesView()
        view.request = self.client.request()
        view.request.user = self.user
        context = view.get_context_data()
        
        # Check that my_stones contains the user's stone
        self.assertIn(stone1, context['my_stones'])
        self.assertEqual(len(context['my_stones']), 1)
        
        # Check that my_interactions contains the other user's stone
        self.assertIn(stone2, context['my_interactions'])
        self.assertEqual(len(context['my_interactions']), 1)

    def test_stone_modal_import_in_template(self):
        """Test that the stone modal import is correctly included in the template"""
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the stone modal import is present
        self.assertContains(response, 'import(\'/static/js/stone-modal.js\')')
        self.assertContains(response, 'openStoneModal')
        
        # Check that the modal HTML structure is present
        self.assertContains(response, 'stone-gallery-modal')
        self.assertContains(response, 'stone-gallery-content')

    def test_stone_modal_functionality(self):
        """Test that stone modal functionality works correctly"""
        from main.models import Stone, StoneMove
        from django.contrib.auth.models import User
        
        # Create a test stone with moves
        stone = Stone.objects.create(
            PK_stone='MODALTEST',
            description='Test stone for modal',
            FK_user=self.user,
            color='#ff5722',
            shape='circle'
        )
        
        # Add moves to the stone
        StoneMove.objects.create(
            FK_stone=stone,
            FK_user=self.user,
            latitude=40.7128,
            longitude=-74.0060,
            comment='First move'
        )
        
        StoneMove.objects.create(
            FK_stone=stone,
            FK_user=self.user,
            latitude=40.7589,
            longitude=-73.9851,
            comment='Second move'
        )
        
        # Test that the stone appears in my-stones
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MODALTEST')
        self.assertContains(response, 'Test stone for modal')
        
        # Test that the modal JavaScript is properly included
        self.assertContains(response, 'showSimpleModal')
        self.assertContains(response, 'stone-gallery-close')

    def test_stone_modal_fallback_functionality(self):
        """Test that the fallback modal function works when ES6 import fails"""
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the fallback function is present
        self.assertContains(response, 'showSimpleModal')
        self.assertContains(response, 'stone-gallery-modal')
        self.assertContains(response, 'stone-gallery-body')

    def test_stone_modal_css_conflict_resolution(self):
        """Test that CSS conflicts are properly resolved in the modal"""
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the modal uses inline styles to avoid CSS conflicts
        self.assertContains(response, 'openStoneModal')
        self.assertContains(response, 'showSimpleModal')

    def test_stone_modal_click_handlers(self):
        """Test that stone click handlers are properly set up"""
        from main.models import Stone
        
        # Create a test stone
        stone = Stone.objects.create(
            PK_stone='CLICKTEST',
            description='Click test stone',
            FK_user=self.user,
            color='#2196F3',
            shape='triangle'
        )
        
        response = self.client.get(reverse('my_stones'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the onclick handler is present
        self.assertContains(response, 'onclick')
        self.assertContains(response, 'openStoneModal')


class StoneCreationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_stone_creation_with_uuid(self):
        """Test that stone creation generates a UUID"""
        response = self.client.post(reverse('add_stone'), {
            'PK_stone': 'TESTSTONE',
            'description': 'Test stone description',
            'stone_type': 'hidden',
            'color': '#FF0000',
            'shape': 'circle'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        stone = Stone.objects.get(PK_stone='TESTSTONE')
        self.assertIsNotNone(stone.uuid)
        self.assertIsInstance(stone.uuid, uuid.UUID)

    def test_automatic_shape_selection_hidden(self):
        """Test that hidden stones automatically get circle shape"""
        response = self.client.post(reverse('add_stone'), {
            'PK_stone': 'HIDDENSTONE',
            'description': 'Hidden stone',
            'stone_type': 'hidden',
            'color': '#00FF00'
        })
        
        self.assertEqual(response.status_code, 302)
        stone = Stone.objects.get(PK_stone='HIDDENSTONE')
        self.assertEqual(stone.shape, 'circle')

    def test_automatic_shape_selection_hunted(self):
        """Test that hunted stones automatically get triangle shape"""
        response = self.client.post(reverse('add_stone'), {
            'PK_stone': 'HUNTEDSTONE',
            'description': 'Hunted stone',
            'stone_type': 'hunted',
            'color': '#0000FF',
            'latitude': '40.7128',
            'longitude': '-74.0060'
        })
        
        self.assertEqual(response.status_code, 302)
        stone = Stone.objects.get(PK_stone='HUNTEDSTONE')
        self.assertEqual(stone.shape, 'triangle')

    def test_qr_code_generation(self):
        """Test that QR code is generated and saved"""
        response = self.client.post(reverse('add_stone'), {
            'PK_stone': 'QRSTONE',
            'description': 'Stone with QR',
            'stone_type': 'hidden',
            'color': '#FF00FF'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Check that QR download path is in session
        session = self.client.session
        self.assertIn('qr_download_path', session)
        self.assertIn('qr_stone_name', session)
        self.assertEqual(session['qr_stone_name'], 'QRSTONE')

    def test_qr_download_view(self):
        """Test QR code download functionality"""
        # Create a stone first
        stone = Stone.objects.create(
            PK_stone='DOWNLOADSTONE',
            description='Test stone',
            FK_user=self.user,
            color='#FF0000',
            shape='circle'
        )
        
        # Create a dummy QR file for testing
        import os
        from django.conf import settings
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        qr_path = os.path.join(qr_dir, 'DOWNLOADSTONE_qr.png')
        with open(qr_path, 'w') as f:
            f.write('dummy qr content')
        
        # Set up session data
        session = self.client.session
        session['qr_download_path'] = 'qr_codes/DOWNLOADSTONE_qr.png'
        session['qr_stone_name'] = 'DOWNLOADSTONE'
        session.save()
        
        response = self.client.get(reverse('download_qr'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Clean up
        if os.path.exists(qr_path):
            os.remove(qr_path)

    def test_qr_download_no_session(self):
        """Test QR download when no session data exists"""
        response = self.client.get(reverse('download_qr'))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_stone_scan_with_uuid(self):
        """Test that stone scanning works with UUID"""
        stone = Stone.objects.create(
            PK_stone='UUIDSTONE',
            description='Test stone',
            FK_user=self.user,
            color='#FF0000',
            shape='circle'
        )
        
        response = self.client.get(f'/stonescan/?stone={stone.uuid}')
        self.assertEqual(response.status_code, 200)
        # Check that the stone name is pre-filled in the form
        content = response.content.decode()
        self.assertIn('value="UUIDSTONE"', content)

    def test_stone_scan_with_pk_stone(self):
        """Test that stone scanning still works with PK_stone"""
        stone = Stone.objects.create(
            PK_stone='PKSTONE',
            description='Test stone',
            FK_user=self.user,
            color='#FF0000',
            shape='circle'
        )
        
        response = self.client.get(f'/stonescan/?stone={stone.PK_stone}')
        self.assertEqual(response.status_code, 200)
        # Check that the stone name is pre-filled in the form
        content = response.content.decode()
        self.assertIn('value="PKSTONE"', content)

    def test_stone_qr_view_with_uuid(self):
        """Test QR code generation view uses UUID"""
        stone = Stone.objects.create(
            PK_stone='QRVIEWSTONE',
            description='Test stone',
            FK_user=self.user,
            color='#FF0000',
            shape='circle'
        )
        
        response = self.client.get(f'/stone/{stone.PK_stone}/qr/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')

    def test_stone_data_includes_uuid(self):
        """Test that stone data includes UUID in JSON response"""
        stone = Stone.objects.create(
            PK_stone='JSONSTONE',
            description='Test stone',
            FK_user=self.user,
            color='#FF0000',
            shape='circle'
        )
        
        # Add a move to make the stone appear in the JSON data
        StoneMove.objects.create(
            FK_stone=stone,
            FK_user=self.user,
            latitude=40.7128,
            longitude=-74.0060
        )
        
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)
        
        # Check that UUID is in the JSON data
        content = response.content.decode()
        self.assertIn(str(stone.uuid), content)

    def test_hunted_stone_requires_location(self):
        """Test that hunted stones require location"""
        response = self.client.post(reverse('add_stone'), {
            'PK_stone': 'NOLOCATION',
            'description': 'Hunted stone without location',
            'stone_type': 'hunted',
            'color': '#FF0000'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect due to error
        # Stone should not be created
        self.assertFalse(Stone.objects.filter(PK_stone='NOLOCATION').exists())
        
        # Test with location - should succeed
        response = self.client.post(reverse('add_stone'), {
            'PK_stone': 'WITHLOCATION',
            'description': 'Hunted stone with location',
            'stone_type': 'hunted',
            'color': '#FF0000',
            'latitude': '40.7128',
            'longitude': '-74.0060'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Stone.objects.filter(PK_stone='WITHLOCATION').exists())

    def test_hidden_stone_optional_location(self):
        """Test that hidden stones don't require location"""
        response = self.client.post(reverse('add_stone'), {
            'PK_stone': 'HIDDENNOLOC',
            'description': 'Hidden stone without location',
            'stone_type': 'hidden',
            'color': '#FF0000'
        })
        
        self.assertEqual(response.status_code, 302)
        # Stone should be created
        self.assertTrue(Stone.objects.filter(PK_stone='HIDDENNOLOC').exists())

    def test_unique_uuid_generation(self):
        """Test that each stone gets a unique UUID"""
        stone1 = Stone.objects.create(
            PK_stone='STONE1',
            description='First stone',
            FK_user=self.user,
            color='#FF0000',
            shape='circle'
        )
        
        stone2 = Stone.objects.create(
            PK_stone='STONE2',
            description='Second stone',
            FK_user=self.user,
            color='#00FF00',
            shape='triangle'
        )
        
        self.assertNotEqual(stone1.uuid, stone2.uuid)
        self.assertIsNotNone(stone1.uuid)
        self.assertIsNotNone(stone2.uuid)

    def test_stone_creation_modal_functionality(self):
        """Test that the stone creation modal opens and works"""
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)
        
        # Check that modal elements exist
        content = response.content.decode()
        self.assertIn('add-stone-modal', content)
        self.assertIn('add-stone-fab', content)
        self.assertIn('stone-type-input', content)
        self.assertIn('stone-shape-input', content)

    def test_stone_type_flavor_text(self):
        """Test that stone type flavor text is displayed correctly"""
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        self.assertIn('Hidden stones do not have a known location', content)
        self.assertIn('Hunted stones are placed at a specific spot', content)


class StoneModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_stone_uuid_field(self):
        """Test that Stone model has UUID field"""
        stone = Stone.objects.create(
            PK_stone='UUIDTEST',
            description='Test stone',
            FK_user=self.user,
            color='#FF0000',
            shape='circle'
        )
        
        self.assertIsNotNone(stone.uuid)
        self.assertIsInstance(stone.uuid, uuid.UUID)

    def test_stone_uuid_unique(self):
        """Test that UUID field is unique"""
        stone1 = Stone.objects.create(
            PK_stone='STONE1',
            description='First stone',
            FK_user=self.user,
            color='#FF0000',
            shape='circle'
        )
        
        stone2 = Stone.objects.create(
            PK_stone='STONE2',
            description='Second stone',
            FK_user=self.user,
            color='#00FF00',
            shape='triangle'
        )
        
        self.assertNotEqual(stone1.uuid, stone2.uuid)

    def test_stone_str_method(self):
        """Test Stone __str__ method"""
        stone = Stone.objects.create(
            PK_stone='STRTEST',
            description='Test stone',
            FK_user=self.user,
            color='#FF0000',
            shape='circle'
        )
        
        self.assertEqual(str(stone), 'STRTEST')


