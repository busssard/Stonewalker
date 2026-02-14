from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import activate


class LanguageSwitchingTests(TestCase):
    """Tests for language switching functionality"""

    def test_change_language_page_loads(self):
        """Change language page should load successfully"""
        response = self.client.get(reverse('change_language'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Change language')

    def test_language_switch_redirects_with_new_language(self):
        """Language switch should redirect to a URL with the new language prefix"""
        # Start on the index page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # Change language to French (submit without language prefix in next)
        response = self.client.post('/i18n/setlang/', {
            'language': 'fr',
            'next': '/'
        }, follow=True)

        # Should redirect to French version
        self.assertEqual(response.status_code, 200)
        # Check if we're on the French URL
        self.assertTrue(any('/fr/' in url for url, _ in response.redirect_chain))

    def test_language_switch_from_change_language_page(self):
        """Switching language from the change language page should update URL"""
        # Visit change language page
        response = self.client.get('/language/')
        self.assertEqual(response.status_code, 200)

        # Submit language change form (next without language prefix)
        response = self.client.post('/i18n/setlang/', {
            'language': 'es',
            'next': '/'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Check that we redirected to Spanish version
        self.assertTrue(any('/es/' in url for url, _ in response.redirect_chain))

    def test_language_cookie_is_set(self):
        """Language switch should set the language cookie"""
        response = self.client.post('/i18n/setlang/', {
            'language': 'de',
            'next': '/'
        })

        # Check that language cookie is set
        self.assertIn('django_language', response.cookies)
        self.assertEqual(response.cookies['django_language'].value, 'de')

    def test_language_persists_across_requests(self):
        """Language should persist across requests after switching"""
        # Switch to Russian
        response = self.client.post('/i18n/setlang/', {
            'language': 'ru',
            'next': '/'
        }, follow=True)

        # Check that language cookie is set
        self.assertIn('django_language', self.client.cookies)
        self.assertEqual(self.client.cookies['django_language'].value, 'ru')

        # Visit another page - the language cookie should cause it to use Russian
        response = self.client.get('/about/')
        # The cookie should be present and correct
        self.assertIn('django_language', self.client.cookies)
        self.assertEqual(self.client.cookies['django_language'].value, 'ru')

    def test_change_language_view_provides_correct_redirect_path(self):
        """ChangeLanguageView should strip language prefix from redirect path"""
        # Visit from a specific page with language prefix
        response = self.client.get('/language/', HTTP_REFERER='http://testserver/en/about/')
        self.assertEqual(response.status_code, 200)
        # Check that redirect_to is set to the referring page path WITHOUT language prefix
        self.assertIn('redirect_to', response.context)
        # Language prefix should be stripped so set_language can add the new one
        self.assertEqual(response.context['redirect_to'], '/about/')
