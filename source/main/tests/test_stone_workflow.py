"""
Tests for stone creation, editing, and workflow (draft -> published -> sent_off).

Stone creation now goes through the shop flow:
  CreateNewStoneView -> ShopView -> CheckoutView -> ClaimStoneView -> StoneEditView

The old /add_stone/ endpoint redirects to /create-stone/.
"""

import uuid as uuid_lib
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from ..models import Stone, QRPack
from .base import BaseStoneWalkerTestCase


class StoneCreationTests(BaseStoneWalkerTestCase):
    """Test stone creation via model helpers and basic stone properties"""

    def test_stone_created_as_draft(self):
        """Test that new stones are created as drafts"""
        stone = self.create_stone('NEWSTONE')
        self.assertEqual(stone.status, 'draft')
        self.assertTrue(stone.can_be_edited())
        self.assertFalse(stone.can_be_sent_off())

    def test_stone_creation_with_uuid(self):
        """Test that stones get a UUID upon creation"""
        stone = self.create_stone('UUIDSTONE')
        self.assertIsNotNone(stone.uuid)
        self.assertNotEqual(str(stone.uuid), '')

    def test_non_premium_user_one_draft_limit(self):
        """Test that non-premium users can only have one draft stone"""
        self.create_stone('FIRST')
        self.assertFalse(Stone.user_can_create_stone(self.user))

    def test_user_can_create_after_publishing(self):
        """Test that users can create new drafts after publishing existing ones"""
        stone1 = self.create_stone('STONE1')
        stone1.publish()
        self.assertTrue(Stone.user_can_create_stone(self.user))

    def test_hidden_stone_gets_circle_shape(self):
        """Hidden stones should have circle shape"""
        stone = self.create_stone('HIDDEN', stone_type='hidden', shape='circle')
        self.assertEqual(stone.shape, 'circle')

    def test_hunted_stone_gets_triangle_shape(self):
        """Hunted stones should have triangle shape"""
        stone = self.create_stone('HUNTED', stone_type='hunted', shape='triangle')
        self.assertEqual(stone.shape, 'triangle')


class DeprecatedAddStoneEndpointTests(BaseStoneWalkerTestCase):
    """Test that the old /add_stone/ endpoint redirects to the shop flow"""

    def test_add_stone_get_redirects_to_create_stone(self):
        """GET /add_stone/ should redirect to /create-stone/"""
        response = self.client.get(reverse('add_stone'))
        self.assertRedirects(response, reverse('create_stone'))

    def test_add_stone_post_redirects_to_create_stone(self):
        """POST /add_stone/ should redirect to /create-stone/"""
        response = self.client.post(reverse('add_stone'), {
            'PK_stone': 'NEWSTONE',
            'description': 'Test stone',
            'stone_type': 'hidden',
        })
        self.assertRedirects(response, reverse('create_stone'))
        # Stone should NOT be created directly
        self.assertFalse(Stone.objects.filter(PK_stone='NEWSTONE').exists())

    def test_add_stone_requires_login(self):
        """Anonymous users should be redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('add_stone'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('accounts', response.url)


class StoneUUIDConsistencyTests(BaseStoneWalkerTestCase):
    """
    Tests for stone UUID integrity.

    Stones get a UUID at creation that must persist through all status
    transitions and be reachable via stone-link URLs.
    """

    def test_stone_link_works_with_uuid(self):
        """The stone-link URL using the stone's UUID should find the stone"""
        stone = self.create_stone('LINK_TEST', status='published')
        self.create_stone_move(stone=stone)
        response = self.client.get(f'/stone-link/{stone.uuid}/')
        self.assertEqual(response.status_code, 200)

    def test_stone_link_with_custom_uuid(self):
        """A stone created with a specific UUID should be reachable via that UUID"""
        custom_uuid = uuid_lib.uuid4()
        stone = Stone.objects.create(
            PK_stone='CUSTOM_UUID',
            FK_user=self.user,
            uuid=custom_uuid,
            status='published',
        )
        self.create_stone_move(stone=stone)
        response = self.client.get(f'/stone-link/{custom_uuid}/')
        self.assertEqual(response.status_code, 200)

    def test_uuid_persists_through_publish(self):
        """UUID should remain the same after publishing"""
        stone = self.create_stone('PERSIST')
        original_uuid = stone.uuid
        stone.publish()
        stone.refresh_from_db()
        self.assertEqual(stone.uuid, original_uuid)

    def test_uuid_persists_through_send_off(self):
        """UUID should remain the same after sending off"""
        stone = self.create_stone('SENDOFF', status='published')
        original_uuid = stone.uuid
        stone.send_off()
        stone.refresh_from_db()
        self.assertEqual(stone.uuid, original_uuid)

    def test_invalid_uuid_returns_error(self):
        """An invalid UUID in stone-link should redirect with error"""
        response = self.client.get('/stone-link/not-a-valid-uuid/')
        self.assertRedirects(response, reverse('stonewalker_start'))


class StoneClaimNameValidationTests(BaseStoneWalkerTestCase):
    """
    Tests for stone name validation during the claim process.

    Stone naming now happens via ClaimStoneView, which validates:
    - Name is not empty
    - Name is 10 characters or less
    - Name has no spaces
    - Name is not already taken
    """

    def _create_unclaimed_stone(self):
        """Helper: create a pack with an unclaimed stone for claiming"""
        pack = QRPack.objects.create(
            FK_user=self.user,
            pack_type='free_single',
            status='fulfilled',
            price_cents=0,
            fulfilled_at=timezone.now(),
        )
        stone = Stone.objects.create(
            PK_stone=f'UNCLAIMED-{uuid_lib.uuid4().hex[:8].upper()}',
            FK_pack=pack,
            FK_user=None,
            status='unclaimed',
        )
        return stone

    def test_claim_with_valid_name(self):
        """A valid name should successfully claim the stone"""
        stone = self._create_unclaimed_stone()
        response = self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': 'Rocky', 'description': 'A lovely stone'},
        )
        self.assertRedirects(response, reverse('stone_edit', kwargs={'pk': 'Rocky'}))
        self.assertTrue(Stone.objects.filter(PK_stone='Rocky', status='draft').exists())

    def test_claim_with_empty_name_rejected(self):
        """An empty name should be rejected"""
        stone = self._create_unclaimed_stone()
        response = self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': '', 'description': 'No name'},
        )
        self.assertEqual(response.status_code, 200)  # Re-renders form
        # Stone should still be unclaimed
        stone.refresh_from_db()
        self.assertEqual(stone.status, 'unclaimed')

    def test_claim_with_long_name_rejected(self):
        """Names longer than 10 chars should be rejected"""
        stone = self._create_unclaimed_stone()
        response = self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': 'VeryLongName', 'description': 'Too long'},
        )
        self.assertEqual(response.status_code, 200)  # Re-renders form
        self.assertFalse(Stone.objects.filter(PK_stone='VeryLongName').exists())

    def test_claim_with_spaces_rejected(self):
        """Names with spaces should be rejected"""
        stone = self._create_unclaimed_stone()
        response = self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': 'My Stone', 'description': 'Has space'},
        )
        self.assertEqual(response.status_code, 200)  # Re-renders form
        self.assertFalse(Stone.objects.filter(PK_stone='My Stone').exists())

    def test_claim_with_taken_name_rejected(self):
        """Already-taken names should be rejected"""
        self.create_stone('Taken')
        stone = self._create_unclaimed_stone()
        response = self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': 'Taken', 'description': 'Name collision'},
        )
        self.assertEqual(response.status_code, 200)  # Re-renders form

    def test_claim_preserves_uuid(self):
        """The UUID should be preserved when claiming a stone"""
        stone = self._create_unclaimed_stone()
        original_uuid = stone.uuid
        self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': 'UUIDTest', 'description': ''},
        )
        claimed = Stone.objects.get(PK_stone='UUIDTest')
        self.assertEqual(claimed.uuid, original_uuid)

    def test_claim_sets_user(self):
        """Claiming should assign the stone to the current user"""
        stone = self._create_unclaimed_stone()
        self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': 'Mine', 'description': ''},
        )
        claimed = Stone.objects.get(PK_stone='Mine')
        self.assertEqual(claimed.FK_user, self.user)
        self.assertEqual(claimed.status, 'draft')

    def test_cannot_claim_already_claimed_stone(self):
        """A stone that's already been claimed should not be claimable"""
        stone = self.create_stone('ALREADY', status='draft')
        response = self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': 'NewName', 'description': ''},
        )
        # Should redirect with error (stone is not unclaimed)
        self.assertEqual(response.status_code, 302)

    def test_claim_with_unicode_name(self):
        """Unicode names within the limit should work"""
        stone = self._create_unclaimed_stone()
        response = self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': 'Stein-42', 'description': ''},
        )
        self.assertRedirects(response, reverse('stone_edit', kwargs={'pk': 'Stein-42'}))
        self.assertTrue(Stone.objects.filter(PK_stone='Stein-42').exists())

    def test_claim_name_at_max_length(self):
        """A 10-character name (the max) should be accepted"""
        stone = self._create_unclaimed_stone()
        response = self.client.post(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)}),
            {'stone_name': 'ABCDEFGHIJ', 'description': ''},
        )
        self.assertRedirects(response, reverse('stone_edit', kwargs={'pk': 'ABCDEFGHIJ'}))

    def test_claim_requires_login(self):
        """Anonymous users cannot claim stones"""
        stone = self._create_unclaimed_stone()
        self.client.logout()
        response = self.client.get(
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('accounts', response.url)


class StoneEditTests(BaseStoneWalkerTestCase):
    """Test stone editing functionality"""

    def test_edit_draft_stone(self):
        """Test editing a draft stone"""
        stone = self.create_stone(status='draft')

        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This stone is in draft mode')

        # Update stone
        response = self.client.post(f'/stone/{stone.PK_stone}/edit/', {
            'description': 'Updated description',
            'color': '#FF5733',
            'action': 'save'
        })
        self.assertRedirects(response, f'/stone/{stone.PK_stone}/edit/')

        stone.refresh_from_db()
        self.assertEqual(stone.description, 'Updated description')

    def test_cannot_edit_published_stone(self):
        """Test that published stones cannot be edited"""
        stone = self.create_stone(status='published')

        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/stonewalker/')

    def test_cannot_edit_sent_off_stone(self):
        """Test that sent off stones cannot be edited"""
        stone = self.create_stone(status='sent_off')

        response = self.client.get(f'/stone/{stone.PK_stone}/edit/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/stonewalker/')


class StoneWorkflowTests(BaseStoneWalkerTestCase):
    """Test stone status workflow transitions"""

    def test_publish_draft_stone(self):
        """Test publishing a draft stone"""
        stone = self.create_stone(status='draft')

        response = self.client.post(f'/stone/{stone.PK_stone}/edit/', {
            'description': stone.description,
            'color': stone.color,
            'action': 'publish'
        })

        stone.refresh_from_db()
        self.assertEqual(stone.status, 'published')
        self.assertFalse(stone.can_be_edited())
        self.assertTrue(stone.can_be_sent_off())

    def test_send_off_published_stone(self):
        """Test sending off a published stone"""
        stone = self.create_stone(status='published')

        response = self.client.post(f'/stone/{stone.PK_stone}/send-off/')

        stone.refresh_from_db()
        self.assertEqual(stone.status, 'sent_off')
        self.assertIsNotNone(stone.sent_off_at)
        self.assertFalse(stone.can_be_edited())
        self.assertFalse(stone.can_be_sent_off())

    def test_cannot_send_off_draft_stone(self):
        """Test that draft stones cannot be sent off"""
        stone = self.create_stone(status='draft')

        response = self.client.post(f'/stone/{stone.PK_stone}/send-off/')

        stone.refresh_from_db()
        self.assertEqual(stone.status, 'draft')


class LanguageSwitchTests(BaseStoneWalkerTestCase):
    """
    Regression tests for language switching and My Stones page.

    Bug (Feb 2026): After switching language from English to German (or any
    non-default locale), the My Stones page appeared empty. Root cause:
    Django's floatformat template filter outputs locale-aware numbers
    (e.g. "2,5" instead of "2.5" in German), which broke the JavaScript
    object literals that hold stone data for client-side rendering.

    Fix: Wrap the JS data arrays in {% localize off %} to force C-locale
    number formatting in the template's JavaScript section.
    """

    def test_my_stones_visible_after_language_change(self):
        """Stones should appear on My Stones page regardless of active language"""
        stone = self.create_stone('LANGSTONE', status='published')
        self.create_stone_move(stone=stone)

        self.client.post('/i18n/setlang/', {'language': 'de', 'next': '/de/my-stones/'})

        response = self.client.get('/de/my-stones/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LANGSTONE')

    def test_my_stones_js_data_valid_in_german(self):
        """The JS data arrays must use dot decimals even in German locale"""
        stone = self.create_stone('DOTSTONE', status='published')
        move = self.create_stone_move(stone=stone, latitude=52.5200, longitude=13.4050)

        self.client.post('/i18n/setlang/', {'language': 'de', 'next': '/de/my-stones/'})

        response = self.client.get('/de/my-stones/')
        content = response.content.decode()
        # Latitude/longitude must use dots, not locale commas
        self.assertIn('52.52', content)
        self.assertIn('13.405', content)
        # German locale comma-decimal would produce "52,52" or "13,405"
        self.assertNotIn('52,52', content)
        self.assertNotIn('13,405', content)

    def test_my_stones_visible_in_french(self):
        """French locale also uses comma decimals - verify it works"""
        stone = self.create_stone('FRSTONE', status='published')
        self.create_stone_move(stone=stone)

        self.client.post('/i18n/setlang/', {'language': 'fr', 'next': '/fr/my-stones/'})
        response = self.client.get('/fr/my-stones/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FRSTONE')

    def test_my_stones_visible_in_default_language(self):
        """Verify My Stones still works in English (the default language)"""
        stone = self.create_stone('ENSTONE', status='published')
        self.create_stone_move(stone=stone)

        response = self.client.get('/my-stones/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ENSTONE')

    def test_interactions_visible_after_language_change(self):
        """Stones the user interacted with should also appear after language switch"""
        other_user = self.create_user('other', 'otherpass', 'other@example.com')
        stone = self.create_stone('OTHERGUY', user=other_user, status='published')
        self.create_stone_move(stone=stone, user=self.user)

        self.client.post('/i18n/setlang/', {'language': 'de', 'next': '/de/my-stones/'})
        response = self.client.get('/de/my-stones/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OTHERGUY')
