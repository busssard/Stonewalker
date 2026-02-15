"""Tests for Terms of Use, Social Media Profiles, and Notification Preferences."""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import (
    Profile, TermsAcceptance, NotificationPreference,
)


class TermsAcceptanceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='termstester', password='testpass123', email='terms@example.com'
        )

    def test_create_terms_acceptance(self):
        ta = TermsAcceptance.objects.create(user=self.user)
        self.assertEqual(ta.version, '1.0')
        self.assertIsNotNone(ta.accepted_at)
        self.assertEqual(ta.user, self.user)

    def test_terms_acceptance_str(self):
        ta = TermsAcceptance.objects.create(user=self.user)
        self.assertIn('termstester', str(ta))
        self.assertIn('1.0', str(ta))

    def test_one_to_one_constraint(self):
        TermsAcceptance.objects.create(user=self.user)
        with self.assertRaises(Exception):
            TermsAcceptance.objects.create(user=self.user)


class SignUpWithTermsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_without_terms_fails(self):
        response = self.client.post(reverse('accounts:sign_up'), {
            'username': 'newuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            # accept_terms not included
        })
        # Form should show error, not redirect
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_signup_with_terms_succeeds(self):
        response = self.client.post(reverse('accounts:sign_up'), {
            'username': 'newuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'accept_terms': 'on',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(user, 'terms_acceptance'))


class TermsPageTests(TestCase):
    def test_terms_page_loads(self):
        response = self.client.get(reverse('terms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Terms of Use')

    def test_terms_page_has_key_sections(self):
        response = self.client.get(reverse('terms'))
        self.assertContains(response, 'Stone Ownership')
        self.assertContains(response, 'Age Requirement')
        self.assertContains(response, 'Content Guidelines')


class NotificationPreferenceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='notifuser', password='testpass123', email='notif@example.com'
        )

    def test_defaults(self):
        prefs = NotificationPreference.objects.create(user=self.user)
        self.assertTrue(prefs.stone_scanned)
        self.assertTrue(prefs.stone_moved)
        self.assertFalse(prefs.weekly_digest)

    def test_str(self):
        prefs = NotificationPreference.objects.create(user=self.user)
        self.assertIn('notifuser', str(prefs))


class SocialMediaProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='socialuser', password='testpass123', email='social@example.com'
        )
        self.profile = self.user.profile

    def test_social_fields_default_empty(self):
        self.assertEqual(self.profile.facebook_url, '')
        self.assertEqual(self.profile.instagram_handle, '')
        self.assertEqual(self.profile.twitter_handle, '')
        self.assertEqual(self.profile.mastodon_handle, '')
        self.assertEqual(self.profile.tiktok_handle, '')

    def test_has_social_links_false_when_empty(self):
        self.assertFalse(self.profile.has_social_links())

    def test_has_social_links_true_with_twitter(self):
        self.profile.twitter_handle = 'stonewalker'
        self.profile.save()
        self.assertTrue(self.profile.has_social_links())

    def test_get_share_handle_twitter(self):
        self.profile.twitter_handle = 'stonewalker'
        self.profile.save()
        self.assertEqual(self.profile.get_share_handle(), '@stonewalker')

    def test_get_share_handle_instagram_fallback(self):
        self.profile.instagram_handle = 'stonewalker_ig'
        self.profile.save()
        self.assertEqual(self.profile.get_share_handle(), '@stonewalker_ig')

    def test_get_share_handle_username_fallback(self):
        self.assertEqual(self.profile.get_share_handle(), 'socialuser')

    def test_save_social_via_profile_edit(self):
        self.client = Client()
        self.client.login(username='socialuser', password='testpass123')
        response = self.client.post(reverse('accounts:change_profile'), {
            'username': 'socialuser',
            'email': 'social@example.com',
            'facebook_url': 'https://facebook.com/stonewalker',
            'instagram_handle': 'stone_ig',
            'twitter_handle': 'stone_tw',
            'mastodon_handle': '@stone@mastodon.social',
            'tiktok_handle': 'stone_tk',
            'notify_stone_scanned': 'on',
            'notify_stone_moved': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.facebook_url, 'https://facebook.com/stonewalker')
        self.assertEqual(self.profile.instagram_handle, 'stone_ig')
        self.assertEqual(self.profile.twitter_handle, 'stone_tw')
