"""
Tests for stone scanning, finding, and stone-link functionality
"""

import uuid as uuid_lib
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from ..models import Stone, StoneMove, StoneScanAttempt
from .base import BaseStoneWalkerTestCase


class StoneLinkBlackoutTests(BaseStoneWalkerTestCase):
    """One-week blackout: a finder can record one find per stone per week.
    It is keyed on recorded finds, not on opening the QR link."""

    def setUp(self):
        super().setUp()
        self.maker = self.create_user('blackoutmaker', 'pw', email='bm@example.com')
        self.stone = self.create_stone('BLACKOUT', user=self.maker, status='wandering')

    def _find(self, comment='found'):
        return self.client.post(f'/stone-link/{self.stone.stone_number}/', {
            'stone_uuid': str(self.stone.uuid),
            'comment': comment,
            'latitude': '40.7128',
            'longitude': '-74.0060',
        })

    def test_second_find_within_week_rejected(self):
        self._find('first')
        self._find('second')
        self.assertEqual(StoneMove.objects.filter(FK_stone=self.stone, FK_user=self.user).count(), 1)

    def test_find_after_week_allowed(self):
        self._find('first')
        StoneMove.objects.filter(FK_stone=self.stone).update(timestamp=timezone.now() - timedelta(days=8))
        self._find('second')
        self.assertEqual(StoneMove.objects.filter(FK_stone=self.stone, FK_user=self.user).count(), 2)

    def test_reopening_link_before_submitting_keeps_form(self):
        """Reloading the scan link (e.g. GPS failed) must still show the form."""
        url = f'/stone-link/{self.stone.stone_number}/?key={self.stone.uuid}'
        self.client.get(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/stone_found.html')

    def test_find_on_non_wandering_stone_rejected(self):
        """Holding the key must not let anyone seal a published stone or add
        finds to drafts."""
        for status in ('draft', 'published'):
            self.stone.status = status
            self.stone.save()
            self._find(status)
            self.stone.refresh_from_db()
            self.assertEqual(self.stone.status, status)
        self.assertFalse(StoneMove.objects.filter(FK_stone=self.stone).exists())

    def test_legacy_stonescan_route_removed(self):
        self.assertEqual(self.client.get('/stonescan/').status_code, 404)


class StoneLinkTests(BaseStoneWalkerTestCase):
    """Test stone-link functionality (QR code target)"""

    def test_stone_link_view_loads(self):
        """Test that stone-link view loads correctly for wandering stones with key"""
        maker = self.create_user('linkmaker', 'pw')
        stone = self.create_stone(user=maker, status='wandering')

        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, stone.PK_stone)

    def test_stone_link_nonexistent_stone_number(self):
        """Test stone-link with non-existent stone number"""
        response = self.client.get('/stone-link/99999/')
        self.assertEqual(response.status_code, 302)  # Should redirect with error

    def test_stone_link_scan_attempt_recording(self):
        """Test that stone-link records scan attempts"""
        maker = self.create_user('scanmaker', 'pw')
        stone = self.create_stone(user=maker, status='wandering')

        # Visit stone-link page with key
        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')
        self.assertEqual(response.status_code, 200)

        # Check that scan attempt was recorded
        attempt = StoneScanAttempt.objects.filter(FK_stone=stone, FK_user=self.user).first()
        self.assertIsNotNone(attempt)

    def test_stone_link_move_submission(self):
        """Test submitting a move via stone-link"""
        stone = self.create_stone(status='wandering')

        response = self.client.post(f'/stone-link/{stone.stone_number}/', {
            'stone_uuid': str(stone.uuid),
            'comment': 'Found via QR code!',
            'latitude': '40.7128',
            'longitude': '-74.0060'
        })

        # Should redirect to map
        self.assertRedirects(response, f'/stonewalker/?focus={stone.PK_stone}')

        # Check that move was created
        move = StoneMove.objects.filter(FK_stone=stone, FK_user=self.user).first()
        self.assertIsNotNone(move)
        self.assertEqual(move.comment, 'Found via QR code!')

    def test_scan_then_submit_find_records_move(self):
        """Real QR flow: finder opens the scan link (GET), then submits the
        find form (POST). The GET must not block the POST via the blackout."""
        maker = self.create_user('flowmaker', 'pw', email='maker@example.com')
        stone = self.create_stone(user=maker, status='wandering')

        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(f'/stone-link/{stone.stone_number}/', {
            'stone_uuid': str(stone.uuid),
            'comment': 'Found it in the park',
            'latitude': '47.3769',
            'longitude': '8.5417',
        })
        self.assertRedirects(response, f'/stonewalker/?focus={stone.PK_stone}')
        self.assertTrue(StoneMove.objects.filter(FK_stone=stone, FK_user=self.user, is_confirmed=True).exists())

        # And the stone now shows up on the public map
        response = self.client.get('/stonewalker/')
        self.assertContains(response, stone.PK_stone)

    def test_public_page_without_key(self):
        """GET without ?key= shows public page for wandering stones"""
        stone = self.create_stone(status='wandering')
        self.create_stone_move(stone=stone)

        response = self.client.get(f'/stone-link/{stone.stone_number}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, stone.PK_stone)

    def test_wrong_key_rejected(self):
        """Wrong UUID key redirects to public page with error"""
        stone = self.create_stone(status='wandering')
        wrong_uuid = str(uuid_lib.uuid4())

        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={wrong_uuid}')
        self.assertEqual(response.status_code, 302)

    def test_legacy_url_redirects(self):
        """Old /stone-link/{uuid}/ redirects to new format"""
        stone = self.create_stone(status='wandering')

        response = self.client.get(f'/stone-link/{stone.uuid}/')
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/stone-link/{stone.stone_number}/', response.url)
        self.assertIn(f'key={stone.uuid}', response.url)


class CheckStoneUUIDTests(BaseStoneWalkerTestCase):
    """Test UUID checking API endpoint"""
    
    def test_check_existing_uuid(self):
        """Test checking existing UUID"""
        stone = self.create_stone()
        
        response = self.client.get(f'/api/check-stone-uuid/{stone.uuid}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['exists'])
        self.assertEqual(data['uuid'], str(stone.uuid))
    
    def test_check_nonexistent_uuid(self):
        """Test checking non-existent UUID"""
        fake_uuid = str(uuid_lib.uuid4())
        
        response = self.client.get(f'/api/check-stone-uuid/{fake_uuid}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertFalse(data['exists'])
    
    def test_check_invalid_uuid_format(self):
        """Test checking invalid UUID format"""
        response = self.client.get('/api/check-stone-uuid/invalid-uuid/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertFalse(data['exists'])
        self.assertIn('error', data)


class StoneSealOnScanTests(BaseStoneWalkerTestCase):
    """Test scan-based stone sealing (QR scan transitions stone to wandering)"""

    def test_scan_draft_shows_confirm_not_seal(self):
        """Scanning a draft stone must NOT auto-seal — it shows a confirm page."""
        stone = self.create_stone('DRAFTSL', status='draft')
        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')

        stone.refresh_from_db()
        self.assertEqual(stone.status, 'draft')  # NOT sealed by the scan
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seal')

    def test_scan_published_shows_confirm_not_seal(self):
        """Scanning a published stone shows the confirm page, doesn't auto-seal."""
        stone = self.create_stone('SEALME', status='published')
        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')

        stone.refresh_from_db()
        self.assertEqual(stone.status, 'published')  # unchanged
        self.assertEqual(response.status_code, 200)

    def test_send_off_post_seals_stone(self):
        """Posting the seal confirmation (send-off) transitions the stone to wandering."""
        stone = self.create_stone('SENDOFF', status='draft')
        response = self.client.post(f'/stone/{stone.PK_stone}/send-off/', {'confirm_no_image': '1'})
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'wandering')
        self.assertIsNotNone(stone.wandering_at)
        self.assertEqual(response.status_code, 302)

    def test_send_off_without_image_requires_confirmation(self):
        """Sealing a pictureless stone without the explicit confirmation is refused."""
        stone = self.create_stone('NOIMG', status='draft')
        response = self.client.post(f'/stone/{stone.PK_stone}/send-off/')
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'draft')  # not sealed
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'key={stone.uuid}', response.url)  # bounced back to confirm page

    def test_send_off_non_owner_cannot_seal(self):
        """A non-owner cannot seal via the send-off POST."""
        other = self.create_user('other2', 'pw')
        stone = self.create_stone('NOTYOURS', user=other, status='draft')
        response = self.client.post(f'/stone/{stone.PK_stone}/send-off/')
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'draft')  # unchanged
        self.assertEqual(response.status_code, 302)

    def test_non_owner_cannot_seal_stone(self):
        """A non-owner scanning a not-yet-wandering stone must NOT seal it.

        Sealing (start_wandering) is a state mutation reserved for the owner
        scanning their own printed QR. A non-owner GET must leave it untouched.
        """
        other_user = self.create_user('other', 'otherpass')
        stone = self.create_stone('OTHERSEAL', user=other_user, status='published')

        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')

        stone.refresh_from_db()
        self.assertEqual(stone.status, 'published')  # unchanged
        self.assertEqual(response.status_code, 302)

    def test_anonymous_get_does_not_seal_stone(self):
        """An unauthenticated GET (e.g. link-preview crawler) must never seal a stone."""
        self.client.logout()
        stone = self.create_stone('CRAWLER', status='published')

        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')

        stone.refresh_from_db()
        self.assertEqual(stone.status, 'published')  # unchanged
        self.assertEqual(response.status_code, 302)  # redirected to login
        self.assertIn('/log', response.url.lower() if response.url else '')

    def test_anonymous_finder_sees_email_form(self):
        """Anonymous scan of a wandering stone shows the find form with an email field."""
        self.client.logout()
        stone = self.create_stone('WANDER2', status='wandering')

        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="finder_email"')

    def test_owner_scans_published_stone_sees_confirm(self):
        """Owner scanning their own published stone sees the confirm page (no auto-seal)."""
        stone = self.create_stone('OWNSEAL', status='published')
        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')

        stone.refresh_from_db()
        self.assertEqual(stone.status, 'published')  # unchanged
        self.assertEqual(response.status_code, 200)

    def test_wandering_stone_shows_found_page(self):
        """Scanning a wandering stone (already found by someone else) shows the
        stone_found page, not seal again."""
        finder = self.create_user('earlyfinder', 'pw')
        stone = self.create_stone('WANDERER', status='wandering')
        self.create_stone_move(stone=stone, user=finder)
        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')

        stone.refresh_from_db()
        self.assertEqual(stone.status, 'wandering')  # Still wandering
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stone Found')


class LastMinuteEditTests(BaseStoneWalkerTestCase):
    """Owner can still edit a sent-off stone via its QR link until anyone else
    scans or finds it."""

    def test_can_last_minute_edit_states(self):
        draft = self.create_stone('LMDRAFT', status='draft')
        self.assertFalse(draft.can_last_minute_edit())

        published = self.create_stone('LMPUB', status='published')
        self.assertTrue(published.can_last_minute_edit())

        wandering = self.create_stone('LMWANDER', status='wandering')
        self.assertTrue(wandering.can_last_minute_edit())

        # A find by another user locks it for good.
        finder = self.create_user('lmfinder', 'pw')
        found = self.create_stone('LMFOUND', status='wandering')
        self.create_stone_move(stone=found, user=finder)
        self.assertFalse(found.can_last_minute_edit())

    def test_owner_scan_of_unfound_wandering_stone_redirects_to_edit(self):
        stone = self.create_stone('LMSCAN', status='wandering')
        response = self.client.get(f'/stone-link/{stone.stone_number}/?key={stone.uuid}')
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/stone/{stone.PK_stone}/edit/', response.url)
        self.assertIn(f'key={stone.uuid}', response.url)

    def test_owner_can_save_last_minute_changes_with_key(self):
        stone = self.create_stone('LMEDIT', status='wandering')
        response = self.client.post(f'/stone/{stone.PK_stone}/edit/', {
            'action': 'save',
            'description': 'last minute description',
            'key': str(stone.uuid),
        })
        self.assertEqual(response.status_code, 302)
        stone.refresh_from_db()
        self.assertEqual(stone.description, 'last minute description')

    def test_edit_without_key_stays_locked_for_wandering_stone(self):
        stone = self.create_stone('LMNOKEY', status='wandering', description='original')
        response = self.client.post(f'/stone/{stone.PK_stone}/edit/', {
            'action': 'save',
            'description': 'sneaky change',
        })
        self.assertEqual(response.status_code, 302)
        stone.refresh_from_db()
        self.assertEqual(stone.description, 'original')

    def test_edit_with_key_locked_after_someone_else_scans(self):
        finder = self.create_user('lmlocker', 'pw')
        stone = self.create_stone('LMLOCKED', status='wandering', description='original')
        self.create_stone_move(stone=stone, user=finder)
        response = self.client.post(f'/stone/{stone.PK_stone}/edit/', {
            'action': 'save',
            'description': 'too late',
            'key': str(stone.uuid),
        })
        self.assertEqual(response.status_code, 302)
        stone.refresh_from_db()
        self.assertEqual(stone.description, 'original')


class DeferredFindTests(BaseStoneWalkerTestCase):
    """Phase 2: anonymous email-first find creates a held submission + provisional user."""

    def test_anonymous_find_creates_pending_move_and_user(self):
        from django.contrib.auth.models import User
        from accounts.models import is_email_confirmed
        self.client.logout()
        stone = self.create_stone('HELDONE', status='wandering')

        resp = self.client.post(f'/stone-link/{stone.stone_number}/', {
            'stone_uuid': str(stone.uuid),
            'finder_email': 'newfinder@example.com',
            'accept_terms': 'on',
            'comment': 'found on a walk',
            'latitude': '48.2', 'longitude': '16.3',
        })
        self.assertEqual(resp.status_code, 302)  # -> my_stones

        user = User.objects.get(email='newfinder@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.has_usable_password())
        self.assertFalse(is_email_confirmed(user))
        move = StoneMove.objects.get(FK_stone=stone, FK_user=user)
        self.assertFalse(move.is_confirmed)  # held
        # soft-logged-in
        self.assertEqual(str(self.client.session.get('_auth_user_id')), str(user.id))

    def test_pending_find_hidden_from_public_map(self):
        from django.contrib.auth.models import User
        self.client.logout()
        stone = self.create_stone('HELDMAP', status='wandering')
        self.client.post(f'/stone-link/{stone.stone_number}/', {
            'stone_uuid': str(stone.uuid), 'finder_email': 'hidden@example.com',
            'accept_terms': 'on', 'comment': 'x', 'latitude': '1.0', 'longitude': '2.0',
        })
        # public map JSON must not include this stone's held find location
        self.client.logout()
        resp = self.client.get('/stonewalker/')
        self.assertNotContains(resp, 'hidden@example.com')  # sanity: no email leak
        # the stone has no confirmed moves, so it should not be a marker
        stone.refresh_from_db()
        confirmed = stone.moves.filter(is_confirmed=True).count()
        self.assertEqual(confirmed, 0)

    def test_existing_confirmed_email_redirected_to_login(self):
        self.client.logout()
        stone = self.create_stone('HELDDUP', status='wandering')
        # self.user already exists (confirmed by default / legacy = confirmed)
        resp = self.client.post(f'/stone-link/{stone.stone_number}/', {
            'stone_uuid': str(stone.uuid),
            'finder_email': self.user.email,
            'accept_terms': 'on', 'comment': 'x', 'latitude': '1.0', 'longitude': '2.0',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/log', resp.url.lower())
        # no move created for the existing account via this path
        self.assertFalse(StoneMove.objects.filter(FK_stone=stone).exists())

    def test_ip_throttle_backstop(self):
        from django.test import override_settings
        from django.contrib.auth.models import User
        self.client.logout()
        s1 = self.create_stone('THR1', status='wandering')
        s2 = self.create_stone('THR2', status='wandering')
        common = {'accept_terms': 'on', 'comment': 'x', 'latitude': '1.0', 'longitude': '2.0'}
        with override_settings(ANONYMOUS_FIND_IP_HOURLY_LIMIT=1):
            self.client.post(f'/stone-link/{s1.stone_number}/',
                             {**common, 'stone_uuid': str(s1.uuid), 'finder_email': 'a@example.com'})
            self.client.post(f'/stone-link/{s2.stone_number}/',
                             {**common, 'stone_uuid': str(s2.uuid), 'finder_email': 'b@example.com'})
        self.assertTrue(User.objects.filter(email='a@example.com').exists())
        self.assertFalse(User.objects.filter(email='b@example.com').exists())  # throttled

    def test_cleanup_removes_stale_provisional_only(self):
        from django.core.management import call_command
        from django.contrib.auth.models import User
        from accounts.models import EmailAddressState

        def provisional(name, days_old, confirmed=False, usable=False):
            u = User.objects.create(username=name, email=f'{name}@example.com', is_active=True)
            if usable:
                u.set_password('pw12345')
            else:
                u.set_unusable_password()
            u.save()
            User.objects.filter(pk=u.pk).update(
                date_joined=timezone.now() - timedelta(days=days_old))
            EmailAddressState.objects.create(user=u, email=u.email, is_confirmed=confirmed)
            return u

        stale = provisional('stale', 30)            # old, unconfirmed, passwordless -> delete
        recent = provisional('recent', 1)           # too new -> keep
        pending_signup = provisional('signup', 30, usable=True)  # has password -> keep

        call_command('cleanup_unconfirmed', '--days', '14')

        self.assertFalse(User.objects.filter(pk=stale.pk).exists())
        self.assertTrue(User.objects.filter(pk=recent.pk).exists())
        self.assertTrue(User.objects.filter(pk=pending_signup.pk).exists())

class AnonymousFindAccountSafetyTests(BaseStoneWalkerTestCase):
    """Typing an email into the anonymous find form must never log the
    visitor into an existing account."""

    def _anon_find(self, stone, email):
        return self.client.post(f'/stone-link/{stone.stone_number}/', {
            'stone_uuid': str(stone.uuid), 'finder_email': email,
            'accept_terms': 'on', 'comment': 'x', 'latitude': '1.0', 'longitude': '2.0',
        })

    def test_existing_provisional_account_not_logged_in(self):
        from django.contrib.auth.models import User
        from accounts.models import EmailAddressState
        self.client.logout()
        victim = User.objects.create(username='provisional', email='prov@example.com')
        victim.set_unusable_password()
        victim.save()
        EmailAddressState.objects.create(user=victim, email='prov@example.com', is_confirmed=False)
        stone = self.create_stone('ANONPROV', status='wandering')

        self._anon_find(stone, 'prov@example.com')

        self.assertIsNone(self.client.session.get('_auth_user_id'))
        # The find is still recorded, held, under that account
        move = StoneMove.objects.get(FK_stone=stone, FK_user=victim)
        self.assertFalse(move.is_confirmed)

    def test_account_with_pending_email_change_not_logged_in(self):
        from django.contrib.auth.models import User
        from accounts.models import EmailAddressState
        self.client.logout()
        victim = User.objects.create_user('realuser', 'real@example.com', 'pw')
        # Pending email change marks the state unconfirmed
        EmailAddressState.objects.create(user=victim, email='new@example.com', is_confirmed=False, old_email='real@example.com')
        stone = self.create_stone('ANONREAL', status='wandering')

        response = self._anon_find(stone, 'real@example.com')

        self.assertIsNone(self.client.session.get('_auth_user_id'))
        self.assertIn('log-in', response.url)
        self.assertFalse(StoneMove.objects.filter(FK_stone=stone).exists())


class MapDataEscapingTests(BaseStoneWalkerTestCase):
    """User text inlined into <script> JSON must not be able to close the tag."""

    def test_script_breakout_escaped_on_map_and_share_page(self):
        payload = '</script><img src=x onerror=alert(1)>'
        maker = self.create_user('xssmaker', 'pw', email='xss@example.com')
        stone = self.create_stone('XSSSTONE', user=maker, status='wandering', description=payload)
        self.create_stone_move(stone=stone, comment=payload)

        for url in ('/stonewalker/', f'/stone-link/{stone.stone_number}/'):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, payload)


class HeldFindNotificationTests(BaseStoneWalkerTestCase):
    """Owners hear about a find only once it is confirmed."""

    def test_owner_notified_on_confirm_not_on_hold(self):
        from django.core import mail
        from ..models import confirm_pending_finds
        owner = self.create_user('notifyowner', 'pw', email='owner@example.com')
        finder = self.create_user('notifyfinder', 'pw', email='finder@example.com')
        stone = self.create_stone('NOTIFYME', user=owner, status='wandering')

        mail.outbox = []
        self.create_stone_move(stone=stone, user=finder, is_confirmed=False)
        self.assertFalse([m for m in mail.outbox if 'owner@example.com' in m.to])

        confirm_pending_finds(finder)
        self.assertTrue([m for m in mail.outbox if 'owner@example.com' in m.to])


class ProvisionalFinderHoldTests(BaseStoneWalkerTestCase):
    """Every find by a still-unconfirmed email-first account stays held,
    not just the first one."""

    def test_second_find_with_soft_session_is_held(self):
        from django.contrib.auth.models import User
        self.client.logout()
        first = self.create_stone('HOLDA', status='wandering')
        second = self.create_stone('HOLDB', status='wandering')
        for stone in (first, second):
            self.client.post(f'/stone-link/{stone.stone_number}/', {
                'stone_uuid': str(stone.uuid), 'finder_email': 'soft@example.com',
                'accept_terms': 'on', 'comment': 'x', 'latitude': '1.0', 'longitude': '2.0',
            })
        finder = User.objects.get(email='soft@example.com')
        self.assertEqual(StoneMove.objects.filter(FK_user=finder).count(), 2)
        self.assertFalse(StoneMove.objects.filter(FK_user=finder, is_confirmed=True).exists())

    def test_email_pending_on_other_account_does_not_500(self):
        from django.contrib.auth.models import User
        from accounts.models import EmailAddressState
        self.client.logout()
        other = User.objects.create_user('pendingowner', 'old@example.com', 'pw')
        EmailAddressState.objects.create(user=other, email='pending@example.com', is_confirmed=False, old_email='old@example.com')
        stone = self.create_stone('PENDCLASH', status='wandering')
        response = self.client.post(f'/stone-link/{stone.stone_number}/', {
            'stone_uuid': str(stone.uuid), 'finder_email': 'pending@example.com',
            'accept_terms': 'on', 'comment': 'x', 'latitude': '1.0', 'longitude': '2.0',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(email='pending@example.com').exists())


class UnreleasedStonePrivacyTests(BaseStoneWalkerTestCase):
    """Draft stones have no public page for non-owners."""

    def test_draft_hidden_from_others_visible_to_owner(self):
        other = self.create_user('draftowner', 'pw', email='do@example.com')
        stone = self.create_stone('SECRETDR', user=other, status='draft')
        self.assertEqual(self.client.get(f'/stone-link/{stone.stone_number}/').status_code, 302)
        self.assertEqual(self.client.get(f'/stone/{stone.PK_stone}/share/').status_code, 404)

        own = self.create_stone('MYDRAFT', status='draft')
        self.assertEqual(self.client.get(f'/stone/{own.PK_stone}/share/').status_code, 200)


class HidingSpotTests(BaseStoneWalkerTestCase):
    """Option 1c: the hiding spot is captured at seal time, kept private for
    hidden stones until the first confirmed find, public at once for hunted."""

    HIDE = {'latitude': '46.9480', 'longitude': '7.4474'}  # Bern

    def _seal(self, stone, **extra):
        data = {'confirm_no_image': '1', **extra}
        return self.client.post(f'/stone/{stone.PK_stone}/send-off/', data)

    def test_hidden_stone_spot_private_until_found(self):
        stone = self.create_stone('HIDESPOT', status='published')
        self._seal(stone, **self.HIDE)
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'wandering')
        self.assertAlmostEqual(stone.hide_latitude, 46.948)

        # Not on the map, and the coordinates don't leak anywhere public
        self.client.logout()
        for url in ('/stonewalker/', f'/stone-link/{stone.stone_number}/', f'/stone/{stone.PK_stone}/share/'):
            self.assertNotContains(self.client.get(url), '46.948')

        # First confirmed find reveals it as the journey start
        finder = self.create_user('spotfinder', 'pw', email='sf@example.com')
        self.create_stone_move(stone=stone, user=finder, latitude=47.3769, longitude=8.5417)
        response = self.client.get('/stonewalker/')
        self.assertContains(response, '46.948')
        self.assertContains(response, 'HIDESPOT')

    def test_distance_counts_from_hiding_spot(self):
        from ..models import calculate_stone_distance
        stone = self.create_stone('DISTSPOT', status='published')
        self._seal(stone, **self.HIDE)
        stone.refresh_from_db()
        finder = self.create_user('distfinder', 'pw', email='df@example.com')
        self.create_stone_move(stone=stone, user=finder, latitude=47.3769, longitude=8.5417)
        # Bern -> Zurich is ~95 km
        self.assertTrue(90 < calculate_stone_distance(stone) < 100)

    def test_seal_without_location_still_allowed_for_hidden(self):
        stone = self.create_stone('NOSPOT', status='published')
        self._seal(stone)
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'wandering')
        self.assertIsNone(stone.hide_latitude)

    def test_hunted_requires_location_and_goes_public(self):
        stone = self.create_stone('HUNTSPOT', status='published', stone_type='hunted')
        self._seal(stone)
        stone.refresh_from_db()
        self.assertNotEqual(stone.status, 'wandering')

        self._seal(stone, **self.HIDE)
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'wandering')
        self.assertTrue(stone.moves.filter(FK_user=self.user, is_confirmed=True).exists())
        self.client.logout()
        self.assertContains(self.client.get('/stonewalker/'), 'HUNTSPOT')

    def test_invalid_coordinates_ignored(self):
        stone = self.create_stone('BADSPOT', status='published')
        self._seal(stone, latitude='999', longitude='abc')
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'wandering')
        self.assertIsNone(stone.hide_latitude)


class ReviewRegressionTests(BaseStoneWalkerTestCase):
    """Regressions caught in the combined-diff review."""

    def test_unclaimed_stone_hidden_from_anonymous(self):
        stone = Stone.objects.create(PK_stone='UNCLAIMED-ANON', FK_user=None, status='unclaimed')
        self.client.logout()
        self.assertEqual(self.client.get(f'/stone-link/{stone.stone_number}/').status_code, 302)
        self.assertEqual(self.client.get(f'/stone/{stone.PK_stone}/share/').status_code, 404)

    def test_stone_type_locked_after_sealing(self):
        stone = self.create_stone('TYPELOCK', status='wandering', stone_type='hidden')
        self.client.post(f'/stone/{stone.PK_stone}/edit/', {
            'action': 'save', 'description': 'x', 'stone_type': 'hunted', 'key': str(stone.uuid),
        })
        stone.refresh_from_db()
        self.assertEqual(stone.stone_type, 'hidden')
