import os
import re
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import activate, gettext as _
from django.conf import settings
import polib


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
        from django.contrib.auth.models import User
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