from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.urls import reverse


class EmailTemplateTests(TestCase):
    """Test that email templates render correctly with all required variables."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )

    def test_activate_profile_html_template(self):
        """Test activate_profile.html renders with required variables."""
        context = {
            'subject': 'Profile activation',
            'uri': 'http://testserver/accounts/activate/test-code-123/',
        }

        html_content = render_to_string('accounts/emails/activate_profile.html', context)

        # Check for StoneWalker branding
        self.assertIn('StoneWalker', html_content)
        self.assertIn('#4CAF50', html_content)  # Brand color

        # Check that the activation link is present
        self.assertIn(context['uri'], html_content)

        # Check for responsive design elements
        self.assertIn('max-width: 600px', html_content)

        # Check for footer
        self.assertIn('Track painted stones around the world', html_content)

    def test_activate_profile_txt_template(self):
        """Test activate_profile.txt renders with required variables."""
        context = {
            'subject': 'Profile activation',
            'uri': 'http://testserver/accounts/activate/test-code-123/',
        }

        text_content = render_to_string('accounts/emails/activate_profile.txt', context)

        # Check for StoneWalker branding
        self.assertIn('STONEWALKER', text_content)

        # Check that the activation link is present
        self.assertIn(context['uri'], text_content)

        # Check for footer
        self.assertIn('Track painted stones around the world', text_content)

    def test_restore_password_html_template(self):
        """Test restore_password_email.html renders with required variables."""
        context = {
            'subject': 'Restore password',
            'uri': 'http://testserver/accounts/restore/uid123/token456/',
        }

        html_content = render_to_string('accounts/emails/restore_password_email.html', context)

        # Check for StoneWalker branding
        self.assertIn('StoneWalker', html_content)
        self.assertIn('#4CAF50', html_content)

        # Check that the reset link is present
        self.assertIn(context['uri'], html_content)

        # Check for responsive design elements
        self.assertIn('max-width: 600px', html_content)

        # Check for footer
        self.assertIn('Track painted stones around the world', html_content)

    def test_restore_password_txt_template(self):
        """Test restore_password_email.txt renders with required variables."""
        context = {
            'subject': 'Restore password',
            'uri': 'http://testserver/accounts/restore/uid123/token456/',
        }

        text_content = render_to_string('accounts/emails/restore_password_email.txt', context)

        # Check for StoneWalker branding
        self.assertIn('STONEWALKER', text_content)

        # Check that the reset link is present
        self.assertIn(context['uri'], text_content)

        # Check for footer
        self.assertIn('Track painted stones around the world', text_content)

    def test_change_email_html_template(self):
        """Test change_email.html renders with required variables."""
        context = {
            'subject': 'Change email',
            'uri': 'http://testserver/accounts/change-email/test-code-123/',
        }

        html_content = render_to_string('accounts/emails/change_email.html', context)

        # Check for StoneWalker branding
        self.assertIn('StoneWalker', html_content)
        self.assertIn('#4CAF50', html_content)

        # Check that the change email link is present
        self.assertIn(context['uri'], html_content)

        # Check for responsive design elements
        self.assertIn('max-width: 600px', html_content)

        # Check for footer
        self.assertIn('Track painted stones around the world', html_content)

    def test_change_email_txt_template(self):
        """Test change_email.txt renders with required variables."""
        context = {
            'subject': 'Change email',
            'uri': 'http://testserver/accounts/change-email/test-code-123/',
        }

        text_content = render_to_string('accounts/emails/change_email.txt', context)

        # Check for StoneWalker branding
        self.assertIn('STONEWALKER', text_content)

        # Check that the change email link is present
        self.assertIn(context['uri'], text_content)

        # Check for footer
        self.assertIn('Track painted stones around the world', text_content)

    def test_forgotten_username_html_template(self):
        """Test forgotten_username.html renders with required variables."""
        context = {
            'subject': 'Your username',
            'username': 'testuser123',
        }

        html_content = render_to_string('accounts/emails/forgotten_username.html', context)

        # Check for StoneWalker branding
        self.assertIn('StoneWalker', html_content)
        self.assertIn('#4CAF50', html_content)

        # Check that the username is present
        self.assertIn(context['username'], html_content)

        # Check for responsive design elements
        self.assertIn('max-width: 600px', html_content)

        # Check for footer
        self.assertIn('Track painted stones around the world', html_content)

    def test_forgotten_username_txt_template(self):
        """Test forgotten_username.txt renders with required variables."""
        context = {
            'subject': 'Your username',
            'username': 'testuser123',
        }

        text_content = render_to_string('accounts/emails/forgotten_username.txt', context)

        # Check for StoneWalker branding
        self.assertIn('STONEWALKER', text_content)

        # Check that the username is present
        self.assertIn(context['username'], text_content)

        # Check for footer
        self.assertIn('Track painted stones around the world', text_content)
