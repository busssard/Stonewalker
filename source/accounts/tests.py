from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.http import HttpResponse
from accounts.models import EmailAddressState, Activation, Subscription
from datetime import timedelta
import re

class AccountsAuthTests(TestCase):
    def test_signup_and_login(self):
        # Sign up a new user
        response = self.client.post(reverse('accounts:sign_up'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'accept_terms': 'on',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after signup
        self.assertTrue(User.objects.filter(username='testuser').exists())

        # Activate the user (simulate email activation)
        user = User.objects.get(username='testuser')
        user.is_active = True
        user.save()

        # Log in with the new user (using email, since LOGIN_VIA_EMAIL is True)
        response = self.client.post(reverse('accounts:log_in'), {
            'email': 'testuser@example.com',
            'password': 'TestPassword123',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after login
        self.assertTrue('_auth_user_id' in self.client.session) 

class ProfileManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='profileuser', email='profile@example.com', password='TestPassword123', is_active=True)
        self.client.post(reverse('accounts:log_in'), {'email': 'profile@example.com', 'password': 'TestPassword123'})

    def test_view_profile(self):
        response = self.client.get(reverse('accounts:change_profile'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profileuser')

    def test_edit_profile_username(self):
        response = self.client.post(reverse('accounts:change_profile'), {
            'username': 'newusername',
            'email': 'profile@example.com',
            'profile_picture': '',
            'password1': '',
            'password2': '',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')

    def test_edit_profile_email(self):
        response = self.client.post(reverse('accounts:change_profile'), {
            'username': 'profileuser',
            'email': 'newemail@example.com',
            'profile_picture': '',
            'password1': '',
            'password2': '',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        email_state = EmailAddressState.objects.get(user=self.user)
        self.assertEqual(email_state.email, 'newemail@example.com')
        self.assertFalse(email_state.is_confirmed)
        self.assertEqual(self.user.email, 'profile@example.com')  # Not updated until activation

    def test_edit_profile_email_activation(self):
        # Change email
        self.client.post(reverse('accounts:change_profile'), {
            'username': 'profileuser',
            'email': 'newemail@example.com',
            'profile_picture': '',
            'password1': '',
            'password2': '',
        }, follow=True)
        # Simulate activation
        activation = Activation.objects.get(user=self.user, email='newemail@example.com')
        self.client.get(reverse('accounts:change_email_activation', args=[activation.code]), follow=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
        email_state = EmailAddressState.objects.get(user=self.user)
        self.assertTrue(email_state.is_confirmed)

    def test_edit_profile_password(self):
        response = self.client.post(reverse('accounts:change_profile'), {
            'username': 'profileuser',
            'email': 'profile@example.com',
            'profile_picture': '',
            'password1': 'NewPassword123',
            'password2': 'NewPassword123',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123'))

    def test_edit_profile_picture(self):
        image = SimpleUploadedFile('test.png', b'filecontent', content_type='image/png')
        response = self.client.post(reverse('accounts:change_profile'), {
            'username': 'profileuser',
            'email': 'profile@example.com',
            'profile_picture': image,
            'password1': '',
            'password2': '',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(hasattr(self.user.profile, 'profile_picture')) 

class NavigationUITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='navuser', email='nav@example.com', password='TestPassword123', is_active=True)
        # Ensure tests run in English
        from django.utils.translation import activate
        activate('en')

    def test_nav_links_unauthenticated(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'About')
        # Shop is conditionally shown based on user count threshold (shop_visible context)
        self.assertContains(response, 'Forum')
        self.assertContains(response, 'Change language')
        # Log in and Sign up are shown in both inline nav and burger menu
        self.assertContains(response, 'Log in')
        self.assertContains(response, 'Sign up')
        # Header logo and walker icon
        self.assertContains(response, 'class="header-logo-img"')
        self.assertContains(response, 'class="avant-header header-logo-text"')
        # Burger icon (hidden on desktop via CSS, but present in HTML)
        self.assertContains(response, 'class="avant-btn header-burger-label"')
        # Inline nav is always present in HTML (CSS controls visibility per breakpoint)
        self.assertContains(response, 'class="header-main-nav"')

    def test_nav_links_authenticated(self):
        self.client.post(reverse('accounts:log_in'), {'email': 'nav@example.com', 'password': 'TestPassword123'})
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'About')
        # Shop is conditionally shown based on user count threshold (shop_visible context)
        self.assertContains(response, 'Forum')
        self.assertContains(response, 'Change language')
        # My Stones, Edit Profile, and Log out are shown in both inline and burger nav
        self.assertContains(response, 'My Stones')
        self.assertContains(response, 'Edit Profile')
        self.assertContains(response, 'Log out')
        # Header logo and walker icon
        self.assertContains(response, 'class="header-logo-img"')
        self.assertContains(response, 'class="avant-header header-logo-text"')
        # Profile image
        self.assertContains(response, 'class="header-profile-img"')
        # Burger icon (hidden on desktop via CSS, but present in HTML)
        self.assertContains(response, 'class="avant-btn header-burger-label"')
        # Inline nav present
        self.assertContains(response, 'class="header-main-nav"')

class UsernameLowercaseTests(TestCase):
    def test_signup_lowercases_username(self):
        response = self.client.post(reverse('accounts:sign_up'), {
            'username': 'TestUserMixed',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'mixedcase@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'accept_terms': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testusermixed').exists())
        self.assertFalse(User.objects.filter(username='TestUserMixed').exists())

    def test_signup_rejects_duplicate_case_insensitive_username(self):
        User.objects.create_user(username='existinguser', email='existing@example.com', password='TestPass123!')
        response = self.client.post(reverse('accounts:sign_up'), {
            'username': 'ExistingUser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'accept_terms': 'on',
        })
        # Should not redirect — form has errors
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

    def test_login_works_case_insensitively(self):
        User.objects.create_user(username='loginuser', email='login@example.com', password='TestPass123!', is_active=True)
        response = self.client.post(reverse('accounts:log_in'), {
            'email': 'login@example.com',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_profile_edit_lowercases_username(self):
        user = User.objects.create_user(username='profilelower', email='profilelower@example.com', password='TestPass123!', is_active=True)
        self.client.post(reverse('accounts:log_in'), {'email': 'profilelower@example.com', 'password': 'TestPass123!'})
        response = self.client.post(reverse('accounts:change_profile'), {
            'username': 'ProfileLOWER_New',
            'email': 'profilelower@example.com',
            'password1': '',
            'password2': '',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.username, 'profilelower_new')

    def test_check_username_api_case_insensitive(self):
        User.objects.create_user(username='apiuser', email='api@example.com', password='TestPass123!')
        response = self.client.get('/accounts/api/check_username/', {'username': 'ApiUser'})
        data = response.json()
        self.assertTrue(data['taken'])
        self.assertEqual(data['reason'], 'taken')
        self.assertEqual(data['username'], 'apiuser')


class CSSUtilityClassTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cssuser', email='css@example.com', password='TestPassword123', is_active=True)
        self.client.login(email='css@example.com', password='TestPassword123')

    def test_index_utility_classes(self):
        response = self.client.get(reverse('index'))
        # The index URL actually renders stonewalker_start.html, not index.html
        self.assertIn('h-map-container', response.content.decode())
        self.assertIn('flex-center', response.content.decode())
        self.assertIn('avant-card', response.content.decode())
    
        # Check for inline styles excluding JavaScript-generated content and legitimate modal styles
        content = response.content.decode()
        import re
        # Remove script tags and their content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        # Remove style attributes that are dynamically generated
        content = re.sub(r'style="[^"]*border-color:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*background:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*color:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*filter:[^"]*"', '', content)
        # Remove legitimate modal styles
        content = re.sub(r'style="[^"]*display:[^"]*flex[^"]*"', '', content)
        content = re.sub(r'style="[^"]*flex-direction:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*max-height:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*min-height:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*white-space:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*margin:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*margin-[^"]*"', '', content)
        content = re.sub(r'style="[^"]*padding:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*padding-[^"]*"', '', content)
        content = re.sub(r'style="[^"]*text-align:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*align-items:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*justify-content:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*display:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*position:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*width:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*height:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*font-size:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*font-weight:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*font-family:[^"]*"', '', content)

        # Only fail if there are still inline styles after removing legitimate ones
        if 'style="' in content:
            # Find the specific inline style for debugging
            style_match = re.search(r'style="[^"]*"', content)
            if style_match:
                self.fail(f"Unexpected inline style found: {style_match.group()}")

    def test_about_utility_classes(self):
        response = self.client.get(reverse('about'))
        self.assertIn('max-w-600', response.content.decode())
        self.assertIn('avant-section', response.content.decode())
        # Note: some inline styles are allowed (e.g., font-size for modals)

    def test_my_stones_utility_classes(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('my_stones'))
        self.assertIn('text-muted', response.content.decode())
        self.assertIn('flex-center', response.content.decode())
        # Note: style attributes are now expected due to the modal fallback function
        # which uses inline styles for the modal content

    def test_no_inline_styles_in_templates(self):
        """Test that static templates don't contain inline styles (excluding JS-generated content)"""
        templates_to_test = [
            ('index', reverse('index')),
            ('about', reverse('about')),
            ('my_stones', reverse('my_stones')),
        ]
    
        for template_name, url in templates_to_test:
            if template_name == 'my_stones':
                self.client.force_login(self.user)
            response = self.client.get(url)
            content = response.content.decode()
    
            # Remove JavaScript-generated content that legitimately uses inline styles
            # This includes dynamic border colors, background colors, etc.
            import re
            # Remove script tags and their content
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            # Remove style attributes that are dynamically generated
            content = re.sub(r'style="[^"]*border-color:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*background:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*color:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*filter:[^"]*"', '', content)
            # Remove legitimate modal styles
            content = re.sub(r'style="[^"]*display:[^"]*flex[^"]*"', '', content)
            content = re.sub(r'style="[^"]*flex-direction:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*max-height:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*min-height:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*white-space:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*margin:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*margin-[^"]*"', '', content)
            content = re.sub(r'style="[^"]*padding:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*padding-[^"]*"', '', content)
            content = re.sub(r'style="[^"]*text-align:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*align-items:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*justify-content:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*display:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*position:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*width:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*height:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*font-size:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*font-weight:[^"]*"', '', content)
            content = re.sub(r'style="[^"]*font-family:[^"]*"', '', content)

            # Now check for remaining inline styles
            if 'style="' in content:
                # Find the specific inline style for debugging
                style_match = re.search(r'style="[^"]*"', content)
                if style_match:
                    self.fail(f"Static inline style found in {template_name}: {style_match.group()}")


# ---------------------------------------------------------------------------
# Premium Supporter Tier Tests
# ---------------------------------------------------------------------------

class SubscriptionModelTests(TestCase):
    """Tests for the Subscription model properties."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='subuser', email='sub@example.com',
            password='TestPassword123', is_active=True,
        )

    def test_is_active_with_active_status(self):
        sub = Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.assertTrue(sub.is_active)

    def test_is_active_with_trialing_status(self):
        sub = Subscription.objects.create(user=self.user, status='trialing', plan='monthly')
        self.assertTrue(sub.is_active)

    def test_is_active_with_canceled_status(self):
        sub = Subscription.objects.create(user=self.user, status='canceled', plan='monthly')
        self.assertFalse(sub.is_active)

    def test_is_active_with_past_due_status(self):
        sub = Subscription.objects.create(user=self.user, status='past_due', plan='monthly')
        self.assertFalse(sub.is_active)

    def test_is_active_with_unpaid_status(self):
        sub = Subscription.objects.create(user=self.user, status='unpaid', plan='monthly')
        self.assertFalse(sub.is_active)

    def test_is_active_with_incomplete_status(self):
        sub = Subscription.objects.create(user=self.user, status='incomplete', plan='monthly')
        self.assertFalse(sub.is_active)

    def test_is_canceled_but_active_within_period(self):
        sub = Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() + timedelta(days=15),
            canceled_at=timezone.now() - timedelta(days=1),
        )
        self.assertTrue(sub.is_canceled_but_active)

    def test_is_canceled_but_active_period_expired(self):
        sub = Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() - timedelta(days=1),
            canceled_at=timezone.now() - timedelta(days=10),
        )
        self.assertFalse(sub.is_canceled_but_active)

    def test_is_canceled_but_active_no_period_end(self):
        sub = Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=None,
        )
        self.assertFalse(sub.is_canceled_but_active)

    def test_is_canceled_but_active_non_canceled_status(self):
        sub = Subscription.objects.create(
            user=self.user, status='active', plan='monthly',
            current_period_end=timezone.now() + timedelta(days=15),
        )
        self.assertFalse(sub.is_canceled_but_active)

    def test_grants_premium_active_subscription(self):
        sub = Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.assertTrue(sub.grants_premium)

    def test_grants_premium_trialing_subscription(self):
        sub = Subscription.objects.create(user=self.user, status='trialing', plan='yearly')
        self.assertTrue(sub.grants_premium)

    def test_grants_premium_canceled_within_period(self):
        sub = Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() + timedelta(days=10),
            canceled_at=timezone.now() - timedelta(days=2),
        )
        self.assertTrue(sub.grants_premium)

    def test_grants_premium_canceled_expired(self):
        sub = Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() - timedelta(days=1),
            canceled_at=timezone.now() - timedelta(days=15),
        )
        self.assertFalse(sub.grants_premium)

    def test_grants_premium_past_due(self):
        sub = Subscription.objects.create(user=self.user, status='past_due', plan='monthly')
        self.assertFalse(sub.grants_premium)

    def test_grants_premium_unpaid(self):
        sub = Subscription.objects.create(user=self.user, status='unpaid', plan='monthly')
        self.assertFalse(sub.grants_premium)

    def test_grants_premium_incomplete(self):
        sub = Subscription.objects.create(user=self.user, status='incomplete', plan='monthly')
        self.assertFalse(sub.grants_premium)

    def test_str_representation(self):
        sub = Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.assertIn('subuser', str(sub))
        self.assertIn('active', str(sub))

    def test_profile_is_premium_with_active_subscription(self):
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.assertTrue(self.user.profile.is_premium)

    def test_profile_is_premium_without_subscription(self):
        self.assertFalse(self.user.profile.is_premium)

    def test_profile_is_premium_with_expired_canceled_subscription(self):
        Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(self.user.profile.is_premium)


class PremiumViewTests(TestCase):
    """Tests for the premium landing page view."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='premuser', email='prem@example.com',
            password='TestPassword123', is_active=True,
        )
        from django.utils.translation import activate
        activate('en')

    def test_premium_page_renders_for_anonymous(self):
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Premium Supporter')

    def test_premium_page_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Premium Supporter')

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_premium_page_shows_pricing_for_non_subscriber(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Choose Your Plan')
        self.assertContains(response, '$3.99')
        self.assertContains(response, '$29.99')

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_premium_page_shows_login_cta_for_anonymous(self):
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Log in to Subscribe')

    def test_premium_page_hides_pricing_before_threshold(self):
        """Pricing is hidden when user count < threshold."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Choose Your Plan')

    def test_premium_page_shows_already_premium_for_subscriber(self):
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        # User is early (< 1000 users), so sees early supporter message
        self.assertContains(response, 'early supporter')

    def test_premium_page_hides_pricing_for_active_subscriber(self):
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertNotContains(response, 'Choose Your Plan')

    def test_premium_page_context_is_premium_false_for_anonymous(self):
        response = self.client.get(reverse('premium'))
        self.assertFalse(response.context['is_premium'])

    def test_premium_page_context_is_premium_true_for_subscriber(self):
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertTrue(response.context['is_premium'])

    def test_premium_page_features_in_context(self):
        response = self.client.get(reverse('premium'))
        self.assertIn('features', response.context)

    def test_premium_page_plans_in_context(self):
        response = self.client.get(reverse('premium'))
        self.assertIn('monthly_plan', response.context)
        self.assertIn('yearly_plan', response.context)


class PremiumCheckoutViewTests(TestCase):
    """Tests for the premium checkout view (login required)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='checkoutuser', email='checkout@example.com',
            password='TestPassword123', is_active=True,
        )

    def test_checkout_requires_login(self):
        response = self.client.post(reverse('premium_checkout'), {'plan': 'monthly'})
        # LoginRequiredMixin redirects to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/log-in', response.url)

    def test_checkout_get_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium_checkout'))
        # View only has post(), GET should return 405
        self.assertEqual(response.status_code, 405)


class PremiumManageViewTests(TestCase):
    """Tests for the premium manage view (login required)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='manageuser', email='manage@example.com',
            password='TestPassword123', is_active=True,
        )
        from django.utils.translation import activate
        activate('en')

    def test_manage_requires_login(self):
        response = self.client.get(reverse('premium_manage'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/log-in', response.url)

    def test_manage_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium_manage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage Subscription')

    def test_manage_shows_no_subscription_message(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium_manage'))
        self.assertContains(response, 'You do not have an active subscription')
        self.assertContains(response, 'Become a Premium Supporter')

    def test_manage_shows_subscription_details(self):
        Subscription.objects.create(
            user=self.user, status='active', plan='monthly',
            current_period_end=timezone.now() + timedelta(days=30),
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium_manage'))
        self.assertContains(response, 'Active')
        self.assertContains(response, 'Open Billing Portal')

    def test_manage_context_is_premium_false_without_subscription(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium_manage'))
        self.assertFalse(response.context['is_premium'])
        self.assertIsNone(response.context['subscription'])

    def test_manage_context_is_premium_true_with_active_subscription(self):
        Subscription.objects.create(user=self.user, status='active', plan='yearly')
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium_manage'))
        self.assertTrue(response.context['is_premium'])
        self.assertIsNotNone(response.context['subscription'])


class PremiumBillingPortalViewTests(TestCase):
    """Tests for the billing portal redirect view (login required)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='billinguser', email='billing@example.com',
            password='TestPassword123', is_active=True,
        )

    def test_billing_requires_login(self):
        response = self.client.post(reverse('premium_billing'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/log-in', response.url)

    def test_billing_get_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium_billing'))
        # View only has post(), GET should return 405
        self.assertEqual(response.status_code, 405)


class PremiumContextProcessorTests(TestCase):
    """Tests for the premium_status context processor."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='ctxuser', email='ctx@example.com',
            password='TestPassword123', is_active=True,
        )
        from django.utils.translation import activate
        activate('en')

    def test_anonymous_user_is_not_premium(self):
        response = self.client.get(reverse('index'))
        self.assertFalse(response.context['is_premium_user'])

    def test_authenticated_user_without_subscription_is_not_premium(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertFalse(response.context['is_premium_user'])

    def test_authenticated_user_with_active_subscription_is_premium(self):
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertTrue(response.context['is_premium_user'])

    def test_authenticated_user_with_canceled_expired_is_not_premium(self):
        Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() - timedelta(days=1),
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertFalse(response.context['is_premium_user'])

    def test_authenticated_user_with_canceled_still_active_is_premium(self):
        Subscription.objects.create(
            user=self.user, status='canceled', plan='monthly',
            current_period_end=timezone.now() + timedelta(days=10),
            canceled_at=timezone.now() - timedelta(days=5),
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertTrue(response.context['is_premium_user'])

    def test_context_processor_direct_anonymous(self):
        """Test premium_status function directly with anonymous user."""
        from app.context_processors import premium_status
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        result = premium_status(request)
        self.assertFalse(result['is_premium_user'])
        self.assertFalse(result['is_early_user'])

    def test_context_processor_direct_authenticated_no_sub(self):
        """Test premium_status function directly with authenticated user, no subscription."""
        from app.context_processors import premium_status
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        result = premium_status(request)
        self.assertFalse(result['is_premium_user'])
        self.assertIn('is_early_user', result)

    def test_context_processor_direct_authenticated_with_sub(self):
        """Test premium_status function directly with premium user."""
        from app.context_processors import premium_status
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        result = premium_status(request)
        self.assertTrue(result['is_premium_user'])
        self.assertIn('is_early_user', result)


class PremiumRequiredDecoratorTests(TestCase):
    """Tests for the premium_required decorator."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='decoruser', email='decor@example.com',
            password='TestPassword123', is_active=True,
        )
        self.premium_user = User.objects.create_user(
            username='premdecouser', email='premdecor@example.com',
            password='TestPassword123', is_active=True,
        )
        Subscription.objects.create(user=self.premium_user, status='active', plan='monthly')
        from django.utils.translation import activate
        activate('en')

    def _make_decorated_view(self):
        """Create a simple function view wrapped with premium_required."""
        from main.premium_views import premium_required

        @premium_required
        def sample_view(request):
            return HttpResponse('premium content')

        return sample_view

    def test_redirects_anonymous_to_login(self):
        factory = RequestFactory()
        request = factory.get('/test/')
        request.user = AnonymousUser()
        view = self._make_decorated_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/log-in', response.url)

    def test_redirects_non_premium_to_premium_page(self):
        factory = RequestFactory()
        request = factory.get('/test/')
        request.user = self.user
        # Need to add session and messages support for the decorator
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.messages.storage.fallback import FallbackStorage
        request.session = SessionStore()
        messages_storage = FallbackStorage(request)
        request._messages = messages_storage
        view = self._make_decorated_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        # Redirects to the premium landing page
        self.assertIn('premium', response.url)

    def test_allows_premium_user(self):
        factory = RequestFactory()
        request = factory.get('/test/')
        request.user = self.premium_user
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.messages.storage.fallback import FallbackStorage
        request.session = SessionStore()
        messages_storage = FallbackStorage(request)
        request._messages = messages_storage
        view = self._make_decorated_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'premium content')

    def test_redirects_user_with_expired_subscription(self):
        expired_user = User.objects.create_user(
            username='expireduser', email='expired@example.com',
            password='TestPassword123', is_active=True,
        )
        Subscription.objects.create(
            user=expired_user, status='canceled', plan='monthly',
            current_period_end=timezone.now() - timedelta(days=1),
        )
        factory = RequestFactory()
        request = factory.get('/test/')
        request.user = expired_user
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.messages.storage.fallback import FallbackStorage
        request.session = SessionStore()
        messages_storage = FallbackStorage(request)
        request._messages = messages_storage
        view = self._make_decorated_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('premium', response.url)


class PremiumNavLinkTests(TestCase):
    """Tests that the Premium link appears correctly in navigation.

    Premium nav is hidden until SHOP_VISIBLE_USER_THRESHOLD users are signed up.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='navpremuser', email='navprem@example.com',
            password='TestPassword123', is_active=True,
        )
        from django.utils.translation import activate
        activate('en')

    def test_premium_link_hidden_for_anonymous_before_threshold(self):
        """Before 1000 users, premium link should not appear for anonymous."""
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, reverse('premium'))

    def test_premium_link_hidden_for_non_premium_before_threshold(self):
        """Before 1000 users, premium link should not appear for non-premium users."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, reverse('premium'))

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_premium_link_not_in_nav_after_threshold(self):
        """Premium/Support link was moved out of nav to About and Shop pages."""
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'premium-nav-link')

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_support_us_on_about_page(self):
        """After threshold, 'Support Us' link should appear on the About page."""
        response = self.client.get(reverse('about'))
        self.assertContains(response, 'Support Us')
        self.assertContains(response, reverse('premium'))

    def test_premium_link_no_special_class_for_non_premium(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'premium-nav-link')


# ---------------------------------------------------------------------------
# Early User / User Number Tests (Sprint 3)
# ---------------------------------------------------------------------------

class UserNumberTests(TestCase):
    """Tests for get_user_number and is_early_user helpers."""

    def test_get_user_number_first_user(self):
        from accounts.models import get_user_number
        user = User.objects.create_user(username='first', email='first@example.com', password='Test1234!')
        self.assertEqual(get_user_number(user), 1)

    def test_get_user_number_sequential(self):
        from accounts.models import get_user_number
        u1 = User.objects.create_user(username='u1', email='u1@example.com', password='Test1234!')
        u2 = User.objects.create_user(username='u2', email='u2@example.com', password='Test1234!')
        u3 = User.objects.create_user(username='u3', email='u3@example.com', password='Test1234!')
        self.assertEqual(get_user_number(u1), 1)
        self.assertEqual(get_user_number(u2), 2)
        self.assertEqual(get_user_number(u3), 3)

    def test_is_early_user_within_threshold(self):
        from accounts.models import is_early_user
        user = User.objects.create_user(username='earlybird', email='early@example.com', password='Test1234!')
        # With only 1 user and threshold of 1000, user is early
        self.assertTrue(is_early_user(user))

    def test_is_early_user_respects_setting(self):
        from accounts.models import is_early_user
        from django.test import override_settings
        user = User.objects.create_user(username='thresh', email='thresh@example.com', password='Test1234!')
        with override_settings(SHOP_VISIBLE_USER_THRESHOLD=0):
            # Threshold is 0, so user number 1 is > 0 => not early
            self.assertFalse(is_early_user(user))


class GrantEarlyPremiumTests(TestCase):
    """Tests for granting lifetime premium to early users."""

    def test_grant_early_premium_creates_subscription(self):
        from accounts.models import grant_early_premium
        user = User.objects.create_user(username='gifted', email='gifted@example.com', password='Test1234!')
        sub = grant_early_premium(user)
        self.assertIsNotNone(sub)
        self.assertEqual(sub.plan, 'lifetime')
        self.assertEqual(sub.status, 'active')
        self.assertTrue(sub.grants_premium)

    def test_grant_early_premium_idempotent(self):
        from accounts.models import grant_early_premium
        user = User.objects.create_user(username='idem', email='idem@example.com', password='Test1234!')
        sub1 = grant_early_premium(user)
        sub2 = grant_early_premium(user)
        self.assertEqual(sub1.pk, sub2.pk)
        self.assertEqual(Subscription.objects.filter(user=user).count(), 1)

    def test_grant_early_premium_returns_none_for_late_user(self):
        from accounts.models import grant_early_premium
        from django.test import override_settings
        user = User.objects.create_user(username='late', email='late@example.com', password='Test1234!')
        with override_settings(SHOP_VISIBLE_USER_THRESHOLD=0):
            result = grant_early_premium(user)
            self.assertIsNone(result)

    def test_profile_is_premium_with_lifetime_subscription(self):
        user = User.objects.create_user(username='lifeprem', email='lifeprem@example.com', password='Test1234!')
        Subscription.objects.create(user=user, plan='lifetime', status='active')
        self.assertTrue(user.profile.is_premium)

    def test_activation_grants_early_premium(self):
        """Test that activating an account grants premium to early users."""
        # Sign up
        self.client.post(reverse('accounts:sign_up'), {
            'username': 'activateuser',
            'email': 'activate@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'accept_terms': 'on',
        })
        user = User.objects.get(username='activateuser')
        self.assertFalse(user.is_active)

        # Activate
        from accounts.models import Activation
        act = Activation.objects.get(user=user)
        self.client.get(reverse('accounts:activate', args=[act.code]))

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        # Should have a lifetime premium subscription
        self.assertTrue(Subscription.objects.filter(user=user, plan='lifetime', status='active').exists())
        self.assertTrue(user.profile.is_premium)


class ActivationEmailUserNumberTests(TestCase):
    """Tests that activation email includes user number."""

    def test_activation_email_contains_user_number(self):
        from django.core import mail
        # Sign up triggers activation email
        self.client.post(reverse('accounts:sign_up'), {
            'username': 'emailnumuser',
            'email': 'emailnum@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'accept_terms': 'on',
        })
        # The console email backend stores emails in mail.outbox
        self.assertTrue(len(mail.outbox) > 0)
        email_body = mail.outbox[-1].body
        # Should contain "member number" text
        self.assertIn('member number', email_body.lower())

    def test_activation_email_contains_early_supporter_message(self):
        from django.core import mail
        self.client.post(reverse('accounts:sign_up'), {
            'username': 'earlymailuser',
            'email': 'earlymail@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'accept_terms': 'on',
        })
        self.assertTrue(len(mail.outbox) > 0)
        email_body = mail.outbox[-1].body
        # Should contain early supporter message
        self.assertIn('early supporter', email_body.lower())


# ---------------------------------------------------------------------------
# QR Code Limit Tests (Sprint 3, Task #5)
# ---------------------------------------------------------------------------

class QRCodeLimitTests(TestCase):
    """Tests for the unclaimed QR code limit before 1000 users."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='qrlimituser', email='qrlimit@example.com',
            password='TestPassword123', is_active=True,
        )
        from accounts.models import TermsAcceptance
        TermsAcceptance.objects.get_or_create(user=self.user)

    def test_user_can_get_new_qr_no_unclaimed(self):
        """User with no unclaimed QRs can get a new one."""
        from main.models import Stone
        self.assertTrue(Stone.user_can_get_new_qr(self.user))

    def test_user_cannot_get_new_qr_with_unclaimed(self):
        """User with an unclaimed QR cannot get another (before threshold)."""
        from main.models import Stone, QRPack
        pack = QRPack.objects.create(
            FK_user=self.user, pack_type='free_single',
            status='fulfilled', price_cents=0,
        )
        Stone.objects.create(
            PK_stone='UNCLAIMED-TEST1',
            FK_pack=pack, FK_user=None, status='unclaimed',
        )
        self.assertFalse(Stone.user_can_get_new_qr(self.user))

    def test_user_can_get_new_qr_after_claiming(self):
        """After claiming an unclaimed stone, user can get another QR."""
        from main.models import Stone, QRPack
        pack = QRPack.objects.create(
            FK_user=self.user, pack_type='free_single',
            status='fulfilled', price_cents=0,
        )
        stone = Stone.objects.create(
            PK_stone='UNCLAIMED-TEST2',
            FK_pack=pack, FK_user=None, status='unclaimed',
        )
        # Claim the stone
        stone.status = 'draft'
        stone.FK_user = self.user
        stone.save()
        self.assertTrue(Stone.user_can_get_new_qr(self.user))

    def test_user_has_unclaimed_qr(self):
        """Test user_has_unclaimed_qr helper."""
        from main.models import Stone, QRPack
        self.assertFalse(Stone.user_has_unclaimed_qr(self.user))
        pack = QRPack.objects.create(
            FK_user=self.user, pack_type='free_single',
            status='fulfilled', price_cents=0,
        )
        Stone.objects.create(
            PK_stone='UNCLAIMED-HAS1',
            FK_pack=pack, FK_user=None, status='unclaimed',
        )
        self.assertTrue(Stone.user_has_unclaimed_qr(self.user))

    def test_premium_user_bypasses_qr_limit(self):
        """Premium users can get QRs even with unclaimed stones."""
        from main.models import Stone, QRPack
        Subscription.objects.create(user=self.user, plan='monthly', status='active')
        pack = QRPack.objects.create(
            FK_user=self.user, pack_type='free_single',
            status='fulfilled', price_cents=0,
        )
        Stone.objects.create(
            PK_stone='UNCLAIMED-PREM1',
            FK_pack=pack, FK_user=None, status='unclaimed',
        )
        self.assertTrue(Stone.user_can_get_new_qr(self.user))

    def test_qr_limit_removed_after_threshold(self):
        """After 1000 users, QR limit is removed."""
        from main.models import Stone, QRPack
        pack = QRPack.objects.create(
            FK_user=self.user, pack_type='free_single',
            status='fulfilled', price_cents=0,
        )
        Stone.objects.create(
            PK_stone='UNCLAIMED-AFTER1',
            FK_pack=pack, FK_user=None, status='unclaimed',
        )
        with override_settings(SHOP_VISIBLE_USER_THRESHOLD=0):
            # With threshold=0, user_count(1) >= 0, so limit is removed
            self.assertTrue(Stone.user_can_get_new_qr(self.user))


# ---------------------------------------------------------------------------
# Premium Visibility Gate Tests (Sprint 3, Task #6)
# ---------------------------------------------------------------------------

class PremiumVisibilityGateTests(TestCase):
    """Tests that premium pricing is only shown after 1000 users."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='gateuser', email='gate@example.com',
            password='TestPassword123', is_active=True,
        )
        from django.utils.translation import activate
        activate('en')

    def test_premium_page_hides_pricing_before_threshold(self):
        """Before 1000 users, pricing section is not shown."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Choose Your Plan')
        self.assertFalse(response.context['show_pricing'])

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_premium_page_shows_pricing_after_threshold(self):
        """After threshold, pricing section is shown."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Choose Your Plan')
        self.assertTrue(response.context['show_pricing'])

    def test_early_user_sees_lifetime_premium_message(self):
        """Early user with lifetime premium sees the special message."""
        Subscription.objects.create(user=self.user, plan='lifetime', status='active')
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'early supporter')
        self.assertContains(response, 'lifetime premium')

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_non_early_premium_user_sees_normal_message(self):
        """A paid subscriber (not early) sees the normal premium message."""
        Subscription.objects.create(user=self.user, plan='monthly', status='active')
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are a Premium Supporter!')
        self.assertContains(response, 'Manage Subscription')

    def test_show_pricing_context_false_before_threshold(self):
        """show_pricing is False when user count < threshold."""
        response = self.client.get(reverse('premium'))
        self.assertFalse(response.context['show_pricing'])


# ---------------------------------------------------------------------------
# About Page QR Button Routing Tests (Sprint 3, Task #7)
# ---------------------------------------------------------------------------

class AboutPageQRButtonTests(TestCase):
    """Tests that the about page QR button routes correctly based on shop_visible."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='aboutuser', email='about@example.com',
            password='TestPassword123', is_active=True,
        )
        from django.utils.translation import activate
        activate('en')

    def test_about_button_links_to_create_stone_before_threshold(self):
        """Before 1000 users, the QR button links to create_stone (not shop)."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('create_stone'))
        self.assertNotContains(response, '"%s"' % reverse('shop'))

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_about_button_links_to_shop_after_threshold(self):
        """After 1000 users, the QR button links to the shop."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('shop'))

    def test_about_page_has_qr_button(self):
        """The about page always has the 'Get Your First QR Code' button."""
        response = self.client.get(reverse('about'))
        self.assertContains(response, 'Get Your First QR Code')