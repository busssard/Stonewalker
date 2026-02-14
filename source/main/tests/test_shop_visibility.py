from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from app.context_processors import shop_visibility


class ShopVisibilityTests(TestCase):
    """Tests for shop visibility based on user count threshold"""

    def setUp(self):
        # Clear all users
        User.objects.all().delete()

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=3)
    def test_shop_hidden_below_threshold(self):
        """Shop should be hidden when user count is below threshold"""
        # Create 2 users (below threshold of 3)
        User.objects.create_user(username='user1', password='test')
        User.objects.create_user(username='user2', password='test')

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Shop link should not be in the navigation
        self.assertNotContains(response, reverse('shop'))

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=3)
    def test_shop_visible_at_threshold(self):
        """Shop should be visible when user count reaches threshold"""
        # Create exactly 3 users
        User.objects.create_user(username='user1', password='test')
        User.objects.create_user(username='user2', password='test')
        User.objects.create_user(username='user3', password='test')

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Shop link should be in the navigation
        self.assertContains(response, reverse('shop'))

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=3)
    def test_shop_visible_above_threshold(self):
        """Shop should be visible when user count is above threshold"""
        # Create 5 users (above threshold of 3)
        for i in range(5):
            User.objects.create_user(username=f'user{i}', password='test')

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Shop link should be in the navigation
        self.assertContains(response, reverse('shop'))

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=5)
    def test_shop_visibility_custom_threshold(self):
        """Shop visibility should respect custom threshold setting"""
        # Create 4 users (below custom threshold of 5)
        for i in range(4):
            User.objects.create_user(username=f'user{i}', password='test')

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('shop'))

        # Add one more user to reach threshold
        User.objects.create_user(username='user4', password='test')

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('shop'))

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=3)
    def test_context_processor_returns_correct_values(self):
        """Context processor should return correct user_count and shop_visible"""
        # Create 2 users
        User.objects.create_user(username='user1', password='test')
        User.objects.create_user(username='user2', password='test')

        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')

        context = shop_visibility(request)
        self.assertEqual(context['user_count'], 2)
        self.assertFalse(context['shop_visible'])

        # Add 1 more user to reach threshold
        User.objects.create_user(username='user3', password='test')

        context = shop_visibility(request)
        self.assertEqual(context['user_count'], 3)
        self.assertTrue(context['shop_visible'])

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=3)
    def test_shop_visibility_for_authenticated_users(self):
        """Shop visibility should work the same for authenticated users"""
        # Create a user and log in
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # Only 1 user, below threshold
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('shop'))

        # Create 2 more users to reach threshold
        User.objects.create_user(username='user1', password='test')
        User.objects.create_user(username='user2', password='test')

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('shop'))
