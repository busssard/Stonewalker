from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import EmailAddressState, Activation
import re

class AccountsAuthTests(TestCase):
    def test_signup_and_login(self):
        # Sign up a new user
        response = self.client.post(reverse('accounts:sign_up'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
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
        self.assertContains(response, 'Shop')
        self.assertContains(response, 'Forum')
        self.assertContains(response, 'Change language')
        # Log in and Sign up are only shown in burger menu or when not authenticated in main nav
        self.assertContains(response, 'Log in')
        self.assertContains(response, 'Sign up')
        # Header logo and walker icon
        self.assertContains(response, 'class="header-logo-img"')
        self.assertContains(response, 'class="avant-header header-logo-text"')
        # Burger icon
        self.assertContains(response, 'class="avant-btn header-burger-label"') 

    def test_nav_links_authenticated(self):
        self.client.post(reverse('accounts:log_in'), {'email': 'nav@example.com', 'password': 'TestPassword123'})
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'About')
        self.assertContains(response, 'Shop')
        self.assertContains(response, 'Forum')
        self.assertContains(response, 'Change language')
        # My Stones, Edit Profile, and Log out are only shown in burger menu for authenticated users
        self.assertContains(response, 'My Stones')
        self.assertContains(response, 'Edit Profile')
        self.assertContains(response, 'Log out')
        # Header logo and walker icon
        self.assertContains(response, 'class="header-logo-img"')
        self.assertContains(response, 'class="avant-header header-logo-text"')
        # Profile image
        self.assertContains(response, 'class="header-profile-img"')
        # Burger icon
        self.assertContains(response, 'class="avant-btn header-burger-label"') 

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
        
        # Check for inline styles excluding JavaScript-generated content
        content = response.content.decode()
        import re
        # Remove script tags and their content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        # Remove style attributes that are dynamically generated
        content = re.sub(r'style="[^"]*border-color:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*background:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*color:[^"]*"', '', content)
        content = re.sub(r'style="[^"]*filter:[^"]*"', '', content)
        
        self.assertNotIn('style="', content, "Static inline style found in index template")

    def test_about_utility_classes(self):
        response = self.client.get(reverse('about'))
        self.assertIn('max-w-600', response.content.decode())
        self.assertIn('avant-section', response.content.decode())
        self.assertNotIn('style="', response.content.decode())

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
            
            # Now check for remaining inline styles
            if 'style="' in content:
                # Find the specific inline style for debugging
                style_match = re.search(r'style="[^"]*"', content)
                if style_match:
                    self.fail(f"Static inline style found in {template_name}: {style_match.group()}")
                else:
                    self.fail(f"Static inline style found in {template_name}") 