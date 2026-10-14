"""Regression tests for the accounts bug hunt (docs/bug-hunt/tasks.md A2-A13)."""
import base64
import json
from urllib.parse import parse_qs, urlparse

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.discourse_sso import generate_discourse_payload
from accounts.models import Activation, EmailAddressState, NotificationPreference


def _decode_sso(query):
    params = parse_qs(query)
    payload = base64.b64decode(params['sso'][0]).decode()
    return {k: v[0] for k, v in parse_qs(payload).items()}


def _profile_post(**overrides):
    data = {'username': 'profileuser', 'email': 'profile@example.com', 'password1': '', 'password2': ''}
    data.update(overrides)
    return data


class ProfileTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser', email='profile@example.com', password='TestPassword123')
        self.client.force_login(self.user)


class DiscourseSSOActivationTests(TestCase):
    """A3: unverified emails must not be vouched for to Discourse."""

    def test_unconfirmed_user_gets_require_activation(self):
        u = User.objects.create_user('finder', 'finder@example.com', 'x')
        EmailAddressState.objects.create(user=u, email=u.email, is_confirmed=False)
        data = _decode_sso(generate_discourse_payload(u, 'n1', 'secret'))
        self.assertEqual(data.get('require_activation'), 'true')

    def test_confirmed_user_has_no_require_activation(self):
        u = User.objects.create_user('walker', 'walker@example.com', 'x')
        EmailAddressState.objects.create(user=u, email=u.email, is_confirmed=True)
        data = _decode_sso(generate_discourse_payload(u, 'n1', 'secret'))
        self.assertNotIn('require_activation', data)

    def test_pending_email_change_still_vouches_old_confirmed_email(self):
        u = User.objects.create_user('changer', 'old@example.com', 'x')
        EmailAddressState.objects.create(
            user=u, email='new@example.com', is_confirmed=False, old_email='old@example.com')
        data = _decode_sso(generate_discourse_payload(u, 'n1', 'secret'))
        self.assertEqual(data['email'], 'old@example.com')
        self.assertNotIn('require_activation', data)


class EmailChangeActivationTests(ProfileTestBase):
    """A4: change links must confirm exactly the address they were sent to."""

    def test_old_change_link_does_not_confirm_newer_address(self):
        self.client.post(reverse('accounts:change_profile'), _profile_post(email='first@example.com'))
        first = Activation.objects.get(user=self.user, email='first@example.com')
        # Cancel, then request a different address
        self.client.post(reverse('accounts:cancel_email_change'))
        self.client.post(reverse('accounts:change_profile'), _profile_post(email='second@example.com'))
        # The older activation is gone; even if it existed it must not apply
        self.assertFalse(Activation.objects.filter(pk=first.pk).exists())

        stale = Activation.objects.create(user=self.user, email='first@example.com', code='stalecode0000000000')
        self.client.get(reverse('accounts:change_email_activation', args=[stale.code]))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'profile@example.com')
        self.assertFalse(self.user.email_state.is_confirmed)

    def test_change_code_rejected_by_signup_activate_view(self):
        self.client.post(reverse('accounts:change_profile'), _profile_post(email='new@example.com'))
        act = Activation.objects.get(user=self.user, email='new@example.com')
        resp = self.client.get(reverse('accounts:activate', args=[act.code]))
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Activation.objects.filter(pk=act.pk).exists())

    def test_signup_code_rejected_by_change_email_view(self):
        act = Activation.objects.create(user=self.user, code='signupcode000000000')
        resp = self.client.get(reverse('accounts:change_email_activation', args=[act.code]))
        self.assertEqual(resp.status_code, 404)

    def test_matching_change_link_confirms(self):
        self.client.post(reverse('accounts:change_profile'), _profile_post(email='new@example.com'))
        act = Activation.objects.get(user=self.user, email='new@example.com')
        self.client.get(reverse('accounts:change_email_activation', args=[act.code]))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')
        self.assertTrue(self.user.email_state.is_confirmed)
        self.assertFalse(Activation.objects.filter(user=self.user).exclude(email='').exists())


class ProfileSavePreservesFieldsTests(ProfileTestBase):
    """A5: fields the form doesn't render must not be wiped on save."""

    def test_save_without_social_or_notify_fields_keeps_them(self):
        profile = self.user.profile
        profile.instagram_handle = 'stone_ig'
        profile.twitter_handle = 'stone_tw'
        profile.save()
        prefs, _ = NotificationPreference.objects.get_or_create(user=self.user)
        prefs.stone_scanned = True
        prefs.stone_moved = True
        prefs.weekly_digest = True
        prefs.save()

        resp = self.client.post(reverse('accounts:change_profile'), _profile_post(username='renamed'))
        self.assertEqual(resp.status_code, 302)

        profile.refresh_from_db()
        prefs.refresh_from_db()
        self.assertEqual(profile.instagram_handle, 'stone_ig')
        self.assertEqual(profile.twitter_handle, 'stone_tw')
        self.assertTrue(prefs.stone_scanned)
        self.assertTrue(prefs.stone_moved)
        self.assertTrue(prefs.weekly_digest)


class ProfileUnconfirmedEmailTests(ProfileTestBase):
    """A6: profile must be savable while the email is unconfirmed."""

    def setUp(self):
        super().setUp()
        EmailAddressState.objects.create(user=self.user, email=self.user.email, is_confirmed=False)

    def test_email_input_is_not_disabled(self):
        resp = self.client.get(reverse('accounts:change_profile'))
        self.assertNotContains(resp, 'disabled autocomplete="email"')
        self.assertContains(resp, 'readonly')

    def test_save_without_email_field_succeeds(self):
        data = _profile_post(username='renamed')
        del data['email']
        resp = self.client.post(reverse('accounts:change_profile'), data)
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'renamed')
        self.assertEqual(self.user.email, 'profile@example.com')


    def test_cannot_change_unverified_email(self):
        # Change + cancel would otherwise flag the unverified address as confirmed
        self.client.post(reverse('accounts:change_profile'), _profile_post(email='other@example.com'))
        self.client.post(reverse('accounts:cancel_email_change'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email_state.email, 'profile@example.com')
        self.assertFalse(self.user.email_state.is_confirmed)


class ProfileModalTests(ProfileTestBase):
    """A7: the header modal gets a script-free fragment and a JSON success."""

    def test_modal_fragment_has_no_inline_script(self):
        resp = self.client.get(reverse('accounts:change_profile') + '?modal=1')
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, '<script')
        self.assertNotContains(resp, '<html')

    def test_modal_success_returns_json(self):
        resp = self.client.post(
            reverse('accounts:change_profile') + '?modal=1', _profile_post(username='renamed'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content), {'success': True})

    def test_modal_invalid_returns_fragment(self):
        User.objects.create_user('taken', 'taken@example.com', 'x')
        resp = self.client.post(
            reverse('accounts:change_profile') + '?modal=1', _profile_post(username='taken'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id="profile-form"')
        self.assertNotContains(resp, '<html')

    def test_page_loads_profile_modal_script(self):
        resp = self.client.get(reverse('my_stones'))
        self.assertContains(resp, 'js/profile-modal.js')


class PasswordResetConfirmsEmailTests(TestCase):
    """A8: completing a password reset proves email ownership."""

    def _reset(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        resp = self.client.get(reverse('accounts:restore_password_confirm', args=[uid, token]))
        return self.client.post(resp.url, {'new_password1': 'FreshPass12345', 'new_password2': 'FreshPass12345'})

    def test_reset_confirms_email_and_releases_finds(self):
        from main.models import Stone, StoneMove
        u = User.objects.create(username='finder', email='finder@example.com', is_active=True)
        u.set_unusable_password()
        u.save()
        EmailAddressState.objects.create(user=u, email=u.email, is_confirmed=False)
        stone = Stone.objects.create(PK_stone='WANDERER', status='wandering')
        move = StoneMove.objects.create(
            FK_stone=stone, FK_user=u, latitude=40.0, longitude=-74.0, comment='hi', is_confirmed=False)

        self._reset(u)

        u.refresh_from_db()
        move.refresh_from_db()
        self.assertTrue(u.check_password('FreshPass12345'))
        self.assertTrue(u.email_state.is_confirmed)
        self.assertTrue(move.is_confirmed)

    def test_reset_does_not_confirm_pending_new_email(self):
        u = User.objects.create_user('changer', 'old@example.com', 'x')
        EmailAddressState.objects.create(
            user=u, email='new@example.com', is_confirmed=False, old_email='old@example.com')
        self._reset(u)
        u.refresh_from_db()
        self.assertFalse(u.email_state.is_confirmed)
        self.assertEqual(u.email, 'old@example.com')


@override_settings(ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE=True)
class UsernameAndEmailChangeTests(ProfileTestBase):
    """A9: username change must persist when the email changes too."""

    def test_username_saved_with_email_change(self):
        self.client.post(reverse('accounts:change_profile'),
                         _profile_post(username='renamed', email='new@example.com'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'renamed')
        self.assertEqual(self.user.email_state.email, 'new@example.com')


class SignUpPendingEmailTests(TestCase):
    """A10: signing up with an email pending on another account must not 500."""

    def test_signup_with_pending_email_is_rejected(self):
        other = User.objects.create_user('other', 'other@example.com', 'x')
        EmailAddressState.objects.create(
            user=other, email='wanted@example.com', is_confirmed=False, old_email='other@example.com')
        resp = self.client.post(reverse('accounts:sign_up'), {
            'username': 'newbie', 'email': 'Wanted@example.com',
            'password1': 'TestPassword123', 'password2': 'TestPassword123', 'accept_terms': 'on',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='newbie').exists())


class LowSeverityTests(TestCase):
    """A13 odds and ends."""

    def test_html_lang_is_set(self):
        resp = self.client.get(reverse('accounts:log_in'))
        self.assertContains(resp, '<html lang="en">')

    def test_signup_log_in_link_keeps_next(self):
        resp = self.client.get(reverse('accounts:sign_up') + '?next=/my-stones/')
        self.assertContains(resp, reverse('accounts:log_in') + '?next=/my-stones/')

    def test_trans_strings_in_inline_js_are_js_escaped(self):
        from django.utils import translation
        u = User.objects.create_user('jsuser', 'js@example.com', 'x')
        self.client.force_login(u)
        with translation.override('fr'):
            resp = self.client.get(reverse('accounts:change_profile'))
        script = resp.content.decode().split('const originalProfilePic', 1)[1]
        self.assertNotIn('&#x27;', script)
        self.assertNotIn('&quot;', script)


class ProfilePasswordChangeTests(ProfileTestBase):
    """NEW-4: changing the password needs the current one and a confirmed email."""

    def test_wrong_current_password_rejected(self):
        resp = self.client.post(reverse('accounts:change_profile'), _profile_post(
            current_password='nope', password1='NewPassword123', password2='NewPassword123'))
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('TestPassword123'))

    def test_missing_current_password_rejected(self):
        self.client.post(reverse('accounts:change_profile'), _profile_post(
            password1='NewPassword123', password2='NewPassword123'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('TestPassword123'))

    def test_correct_current_password_accepted(self):
        self.client.post(reverse('accounts:change_profile'), _profile_post(
            current_password='TestPassword123', password1='NewPassword123', password2='NewPassword123'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123'))

    def test_provisional_user_cannot_set_password_before_confirming(self):
        self.user.set_unusable_password()
        self.user.save()
        EmailAddressState.objects.create(user=self.user, email=self.user.email, is_confirmed=False)
        self.client.force_login(self.user)
        resp = self.client.post(reverse('accounts:change_profile'), _profile_post(
            password1='NewPassword123', password2='NewPassword123'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'confirm your email')
        self.user.refresh_from_db()
        self.assertFalse(self.user.has_usable_password())

    def test_current_password_field_rendered_for_password_users(self):
        resp = self.client.get(reverse('accounts:change_profile'))
        self.assertContains(resp, 'name="current_password"')
        resp = self.client.get(reverse('accounts:change_profile') + '?modal=1')
        self.assertContains(resp, 'name="current_password"')


class CancelEmailChangeTests(TestCase):
    """NEW-5: cancelling must not confirm an address that was never verified."""

    def test_cancel_without_old_email_does_not_confirm(self):
        u = User.objects.create_user('p', 'unverified@example.com', 'x')
        EmailAddressState.objects.create(user=u, email=u.email, is_confirmed=False)
        self.client.force_login(u)
        self.client.post(reverse('accounts:cancel_email_change'))
        u.refresh_from_db()
        self.assertFalse(u.email_state.is_confirmed)

    def test_cancel_restores_verified_old_email(self):
        # old_email is only ever stored when user.email was verified
        u2 = User.objects.create_user('q', 'q@example.com', 'TestPassword123')
        EmailAddressState.objects.create(user=u2, email='q@example.com', is_confirmed=True)
        self.client.force_login(u2)
        self.client.post(reverse('accounts:change_profile'), {
            'username': 'q', 'email': 'q2@example.com', 'password1': '', 'password2': ''})
        u2.refresh_from_db()
        self.assertEqual(u2.email_state.old_email, 'q@example.com')
        self.client.post(reverse('accounts:cancel_email_change'))
        u2.refresh_from_db()
        self.assertTrue(u2.email_state.is_confirmed)
        self.assertEqual(u2.email, 'q@example.com')


class ResendActivationLinkTests(TestCase):
    """NEW-19: the resend-activation page is reachable from the login page."""

    def test_login_page_links_to_resend_activation(self):
        resp = self.client.get(reverse('accounts:log_in'))
        self.assertContains(resp, reverse('accounts:resend_activation_code'))
