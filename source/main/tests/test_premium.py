"""
Tests for Premium Supporter tier — views, model, context processor, nav links, access control.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from accounts.models import Subscription, Profile


class PremiumModelTests(TestCase):
    """Tests for the Subscription model and Profile.is_premium property."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='premtest', password='pass123', email='prem@test.com'
        )

    def test_subscription_grants_premium_when_active(self):
        sub = Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.assertTrue(sub.grants_premium)
        self.assertTrue(sub.is_active)

    def test_subscription_grants_premium_when_trialing(self):
        sub = Subscription.objects.create(user=self.user, status='trialing', plan='monthly')
        self.assertTrue(sub.grants_premium)

    def test_subscription_not_premium_when_canceled_past_period(self):
        sub = Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() - timedelta(days=1),
            canceled_at=timezone.now() - timedelta(days=5),
        )
        self.assertFalse(sub.grants_premium)

    def test_subscription_premium_when_canceled_but_in_period(self):
        sub = Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() + timedelta(days=10),
            canceled_at=timezone.now() - timedelta(days=1),
        )
        self.assertTrue(sub.is_canceled_but_active)
        self.assertTrue(sub.grants_premium)

    def test_subscription_not_premium_when_past_due(self):
        sub = Subscription.objects.create(user=self.user, status='past_due', plan='monthly')
        self.assertFalse(sub.grants_premium)

    def test_subscription_not_premium_when_unpaid(self):
        sub = Subscription.objects.create(user=self.user, status='unpaid', plan='monthly')
        self.assertFalse(sub.grants_premium)

    def test_subscription_not_premium_when_incomplete(self):
        sub = Subscription.objects.create(user=self.user, status='incomplete', plan='monthly')
        self.assertFalse(sub.grants_premium)

    def test_profile_is_premium_with_active_subscription(self):
        Subscription.objects.create(user=self.user, status='active', plan='yearly')
        self.assertTrue(self.user.profile.is_premium)

    def test_profile_not_premium_without_subscription(self):
        self.assertFalse(self.user.profile.is_premium)

    def test_subscription_str(self):
        sub = Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.assertIn('premtest', str(sub))
        self.assertIn('Monthly', str(sub))

    def test_plan_choices(self):
        sub_m = Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.assertEqual(sub_m.get_plan_display(), 'Monthly ($3.99/mo)')

    def test_subscription_one_to_one(self):
        """Each user can only have one subscription."""
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Subscription.objects.create(user=self.user, status='active', plan='yearly')


class PremiumViewTests(TestCase):
    """Tests for premium landing, manage, checkout, and billing views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='viewtest', password='pass123', email='view@test.com'
        )

    def test_premium_landing_anonymous(self):
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Premium Supporter')
        self.assertContains(response, 'Log in to Subscribe')

    def test_premium_landing_authenticated_no_sub(self):
        self.client.login(username='viewtest', password='pass123')
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Subscribe Monthly')
        self.assertContains(response, 'Subscribe Yearly')
        self.assertNotContains(response, 'Log in to Subscribe')

    def test_premium_landing_shows_features(self):
        response = self.client.get(reverse('premium'))
        self.assertContains(response, 'Journey Analytics')
        self.assertContains(response, 'Premium Badge')
        self.assertContains(response, 'Priority Support')
        self.assertContains(response, 'Early Access')

    def test_premium_landing_shows_faq(self):
        response = self.client.get(reverse('premium'))
        self.assertContains(response, 'Can I cancel anytime?')
        self.assertContains(response, 'What happens to my stones if I cancel?')

    def test_premium_landing_with_active_sub(self):
        self.client.login(username='viewtest', password='pass123')
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        response = self.client.get(reverse('premium'))
        self.assertContains(response, 'You are a Premium Supporter!')
        self.assertContains(response, 'Manage Subscription')

    def test_premium_manage_requires_login(self):
        response = self.client.get(reverse('premium_manage'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('log-in', response.url)

    def test_premium_manage_no_subscription(self):
        self.client.login(username='viewtest', password='pass123')
        response = self.client.get(reverse('premium_manage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You do not have an active subscription')
        self.assertContains(response, 'Become a Premium Supporter')

    def test_premium_manage_with_active_sub(self):
        self.client.login(username='viewtest', password='pass123')
        Subscription.objects.create(
            user=self.user, status='active', plan='yearly',
            current_period_end=timezone.now() + timedelta(days=30),
        )
        response = self.client.get(reverse('premium_manage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active')
        self.assertContains(response, 'Open Billing Portal')

    def test_premium_manage_canceled_but_active_sub(self):
        """Canceled-but-still-in-period sub shows Active badge + access until date."""
        self.client.login(username='viewtest', password='pass123')
        Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() + timedelta(days=5),
            canceled_at=timezone.now() - timedelta(days=1),
        )
        response = self.client.get(reverse('premium_manage'))
        # grants_premium is True (in period), so template shows Active badge
        self.assertContains(response, 'Active')
        self.assertContains(response, 'Access until')

    def test_premium_manage_canceled_expired_sub(self):
        """Fully expired canceled sub shows Canceled badge."""
        self.client.login(username='viewtest', password='pass123')
        Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() - timedelta(days=1),
            canceled_at=timezone.now() - timedelta(days=10),
        )
        response = self.client.get(reverse('premium_manage'))
        self.assertContains(response, 'Canceled')

    def test_premium_checkout_requires_login(self):
        response = self.client.post(reverse('premium_checkout'), {'plan': 'monthly'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('log-in', response.url)

    def test_premium_checkout_invalid_plan(self):
        self.client.login(username='viewtest', password='pass123')
        response = self.client.post(reverse('premium_checkout'), {'plan': 'invalid'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('premium'))

    def test_premium_checkout_redirects_if_already_subscribed(self):
        self.client.login(username='viewtest', password='pass123')
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        response = self.client.post(reverse('premium_checkout'), {'plan': 'monthly'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('premium_manage'))

    def test_premium_checkout_no_stripe_key(self):
        self.client.login(username='viewtest', password='pass123')
        with self.settings(STRIPE_SECRET_KEY=''):
            response = self.client.post(reverse('premium_checkout'), {'plan': 'monthly'})
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('premium'))

    def test_premium_billing_requires_login(self):
        response = self.client.post(reverse('premium_billing'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('log-in', response.url)


class PremiumContextProcessorTests(TestCase):
    """Tests for the premium_status context processor."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='ctxtest', password='pass123', email='ctx@test.com'
        )

    def test_anonymous_user_not_premium(self):
        response = self.client.get(reverse('premium'))
        self.assertFalse(response.context.get('is_premium_user', True))

    def test_authenticated_user_not_premium(self):
        self.client.login(username='ctxtest', password='pass123')
        response = self.client.get(reverse('premium'))
        self.assertFalse(response.context['is_premium_user'])

    def test_premium_user_is_premium(self):
        self.client.login(username='ctxtest', password='pass123')
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        response = self.client.get(reverse('premium'))
        self.assertTrue(response.context['is_premium_user'])


class PremiumNavTests(TestCase):
    """Tests for premium link behavior in navigation."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='navtest', password='pass123', email='nav@test.com'
        )

    def test_nav_shows_premium_link_anonymous(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('premium'))

    def test_nav_shows_premium_link_non_subscriber(self):
        self.client.login(username='navtest', password='pass123')
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('premium'))

    def test_nav_shows_premium_manage_for_subscriber(self):
        self.client.login(username='navtest', password='pass123')
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('premium_manage'))


class PremiumRequiredDecoratorTests(TestCase):
    """Tests for the premium_required decorator and PremiumRequiredMixin."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dectest', password='pass123', email='dec@test.com'
        )

    def test_premium_required_redirects_anonymous(self):
        """Anonymous users should be redirected to login."""
        from main.premium_views import premium_required
        from django.http import HttpRequest, HttpResponse

        @premium_required
        def dummy_view(request):
            return HttpResponse('ok')

        request = HttpRequest()
        request.user = type('AnonymousUser', (), {'is_authenticated': False})()
        request.META = {'SERVER_NAME': 'localhost', 'SERVER_PORT': '8000'}
        response = dummy_view(request)
        self.assertEqual(response.status_code, 302)

    def test_premium_required_redirects_non_premium(self):
        """Non-premium users should be redirected to premium landing."""
        self.client.login(username='dectest', password='pass123')
        # Use the client to test a view that uses premium_required,
        # or test the logic directly by checking redirect for manage page
        # (PremiumManageView requires login but not premium — test the decorator separately)
        from main.premium_views import premium_required
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/some-premium-page/')
        request.user = self.user

        # Add message storage to the request
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)

        from django.http import HttpResponse

        @premium_required
        def dummy_view(req):
            return HttpResponse('ok')

        response = dummy_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('premium', response.url)


class PremiumWebhookTests(TestCase):
    """Tests for Stripe webhook handling of subscription events."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='whtest', password='pass123', email='wh@test.com'
        )

    def test_handle_subscription_created(self):
        from main.stripe_service import StripeService
        event_object = {
            'id': 'sub_test123',
            'customer': 'cus_test123',
            'status': 'active',
            'items': {'data': [{'price': {'recurring': {'interval': 'month'}}}]},
            'current_period_start': 1700000000,
            'current_period_end': 1702592000,
            'metadata': {'user_id': str(self.user.id)},
        }
        StripeService._handle_subscription_created(event_object)

        sub = Subscription.objects.get(user=self.user)
        self.assertEqual(sub.status, 'active')
        self.assertEqual(sub.plan, 'monthly')
        self.assertEqual(sub.stripe_customer_id, 'cus_test123')
        self.assertEqual(sub.stripe_subscription_id, 'sub_test123')

    def test_handle_subscription_updated(self):
        from main.stripe_service import StripeService
        sub = Subscription.objects.create(
            user=self.user, status='active', plan='monthly',
            stripe_subscription_id='sub_upd123', stripe_customer_id='cus_upd',
        )
        event_object = {
            'id': 'sub_upd123',
            'status': 'active',
            'cancel_at_period_end': True,
            'current_period_start': 1700000000,
            'current_period_end': 1702592000,
        }
        StripeService._handle_subscription_updated(event_object)
        sub.refresh_from_db()
        self.assertIsNotNone(sub.canceled_at)

    def test_handle_subscription_deleted(self):
        from main.stripe_service import StripeService
        sub = Subscription.objects.create(
            user=self.user, status='active', plan='monthly',
            stripe_subscription_id='sub_del123',
        )
        StripeService._handle_subscription_deleted({'id': 'sub_del123'})
        sub.refresh_from_db()
        self.assertEqual(sub.status, 'canceled')
        self.assertIsNotNone(sub.canceled_at)

    def test_handle_invoice_payment_failed(self):
        from main.stripe_service import StripeService
        sub = Subscription.objects.create(
            user=self.user, status='active', plan='monthly',
            stripe_subscription_id='sub_fail123',
        )
        StripeService._handle_invoice_payment_failed({'subscription': 'sub_fail123'})
        sub.refresh_from_db()
        self.assertEqual(sub.status, 'past_due')

    def test_handle_subscription_created_yearly(self):
        from main.stripe_service import StripeService
        event_object = {
            'id': 'sub_yr123',
            'customer': 'cus_yr123',
            'status': 'active',
            'items': {'data': [{'price': {'recurring': {'interval': 'year'}}}]},
            'current_period_start': 1700000000,
            'current_period_end': 1731536000,
            'metadata': {'user_id': str(self.user.id)},
        }
        StripeService._handle_subscription_created(event_object)
        sub = Subscription.objects.get(user=self.user)
        self.assertEqual(sub.plan, 'yearly')
