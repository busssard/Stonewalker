"""Tests for backend features: stone share, signals, terms gate."""

from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from main.models import Stone, StoneMove
from accounts.models import TermsAcceptance, NotificationPreference


class StoneShareViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='shareuser', password='testpass123', email='share@example.com'
        )
        self.stone = Stone.objects.create(
            PK_stone='SHARESTONE',
            FK_user=self.user,
            description='A test stone for sharing',
            status='published',
        )

    def test_share_page_loads_public(self):
        """Share page should be accessible without login."""
        response = self.client.get(reverse('stone_share', kwargs={'pk': 'SHARESTONE'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SHARESTONE')
        self.assertContains(response, 'on StoneWalker')

    def test_share_page_has_og_tags(self):
        response = self.client.get(reverse('stone_share', kwargs={'pk': 'SHARESTONE'}))
        self.assertContains(response, 'SHARESTONE on StoneWalker')

    def test_share_page_has_share_buttons(self):
        response = self.client.get(reverse('stone_share', kwargs={'pk': 'SHARESTONE'}))
        self.assertContains(response, 'twitter.com/intent/tweet')
        self.assertContains(response, 'facebook.com/sharer')
        self.assertContains(response, 'wa.me')

    def test_share_page_shows_journey_stats(self):
        StoneMove.objects.create(
            FK_stone=self.stone, FK_user=self.user,
            latitude=40.7128, longitude=-74.0060, comment='NYC'
        )
        response = self.client.get(reverse('stone_share', kwargs={'pk': 'SHARESTONE'}))
        self.assertContains(response, 'km traveled')
        self.assertContains(response, 'scans')

    def test_share_page_404_for_missing_stone(self):
        response = self.client.get(reverse('stone_share', kwargs={'pk': 'NOSTONE'}))
        self.assertEqual(response.status_code, 404)

    def test_share_page_includes_owner(self):
        response = self.client.get(reverse('stone_share', kwargs={'pk': 'SHARESTONE'}))
        self.assertContains(response, 'shareuser')

    def test_share_page_shows_social_links(self):
        profile = self.user.profile
        profile.twitter_handle = 'stonewalker_tw'
        profile.save()
        response = self.client.get(reverse('stone_share', kwargs={'pk': 'SHARESTONE'}))
        self.assertContains(response, 'stonewalker_tw')


class SignalNotificationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='stoneowner', password='testpass123', email='owner@example.com'
        )
        self.scanner = User.objects.create_user(
            username='scanner', password='testpass123', email='scanner@example.com'
        )
        self.stone = Stone.objects.create(
            PK_stone='SIGNALSTONE',
            FK_user=self.owner,
            status='published',
        )

    @patch('main.signals.EmailMultiAlternatives')
    def test_signal_fires_on_stone_move(self, mock_email_cls):
        """Creating a StoneMove should trigger email notification to owner."""
        mock_email_cls.return_value.send.return_value = True
        StoneMove.objects.create(
            FK_stone=self.stone, FK_user=self.scanner,
            latitude=48.8566, longitude=2.3522, comment='Paris!'
        )
        mock_email_cls.assert_called_once()

    @patch('main.signals.EmailMultiAlternatives')
    def test_no_notification_when_owner_scans_own_stone(self, mock_email_cls):
        """Owner scanning their own stone should not trigger a notification."""
        StoneMove.objects.create(
            FK_stone=self.stone, FK_user=self.owner,
            latitude=48.8566, longitude=2.3522, comment='My own scan'
        )
        mock_email_cls.assert_not_called()

    @patch('main.signals.EmailMultiAlternatives')
    def test_no_notification_when_prefs_disabled(self, mock_email_cls):
        """No email if owner has disabled stone_scanned notifications."""
        NotificationPreference.objects.create(
            user=self.owner, stone_scanned=False, stone_moved=False
        )
        StoneMove.objects.create(
            FK_stone=self.stone, FK_user=self.scanner,
            latitude=48.8566, longitude=2.3522, comment='Disabled'
        )
        mock_email_cls.assert_not_called()


class TermsGateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='gateuser', password='testpass123', email='gate@example.com'
        )
        self.client.login(username='gateuser', password='testpass123')

    def test_add_stone_redirects_without_terms(self):
        """add_stone should redirect to terms if user hasn't accepted."""
        response = self.client.get(reverse('add_stone'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('terms', response.url)

    def test_add_stone_redirects_to_shop_with_terms(self):
        """add_stone should proceed to create_stone if terms accepted."""
        TermsAcceptance.objects.create(user=self.user)
        response = self.client.get(reverse('add_stone'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('create-stone', response.url)
