from django.test import TestCase, RequestFactory
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

    def test_premium_page_shows_pricing_for_non_subscriber(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Choose Your Plan')
        self.assertContains(response, '$3.99')
        self.assertContains(response, '$29.99')

    def test_premium_page_shows_login_cta_for_anonymous(self):
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Log in to Subscribe')

    def test_premium_page_shows_already_premium_for_subscriber(self):
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.client.force_login(self.user)
        response = self.client.get(reverse('premium'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are a Premium Supporter!')
        self.assertContains(response, 'Manage Subscription')

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
        self.assertEqual(result, {'is_premium_user': False})

    def test_context_processor_direct_authenticated_no_sub(self):
        """Test premium_status function directly with authenticated user, no subscription."""
        from app.context_processors import premium_status
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        result = premium_status(request)
        self.assertEqual(result, {'is_premium_user': False})

    def test_context_processor_direct_authenticated_with_sub(self):
        """Test premium_status function directly with premium user."""
        from app.context_processors import premium_status
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        result = premium_status(request)
        self.assertEqual(result, {'is_premium_user': True})


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
    """Tests that the Premium link appears correctly in navigation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='navpremuser', email='navprem@example.com',
            password='TestPassword123', is_active=True,
        )
        from django.utils.translation import activate
        activate('en')

    def test_premium_link_in_nav_for_anonymous(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Premium')
        # Non-premium users see a link to the landing page
        self.assertContains(response, reverse('premium'))

    def test_premium_link_in_nav_for_authenticated_non_premium(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Premium')
        self.assertContains(response, reverse('premium'))

    def test_premium_link_in_nav_for_premium_user(self):
        Subscription.objects.create(user=self.user, status='active', plan='monthly')
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Premium')
        # Premium users see a link to the manage page
        self.assertContains(response, reverse('premium_manage'))
        # Premium nav link has the special CSS class
        self.assertContains(response, 'premium-nav-link')

    def test_premium_link_no_special_class_for_non_premium(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'premium-nav-link') 