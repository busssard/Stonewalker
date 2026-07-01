"""
Tests for the shop-based stone creation flow.

The "Create New Stone" button routes through CreateNewStoneView:
- If user has unclaimed QR → redirect to my-stones with message
- If no unclaimed QR + before threshold → create free QR → redirect to my-stones
- If no unclaimed QR + after threshold → redirect to shop
- In dev mode (DEBUG=True): free_single has no limit_per_user
"""

import uuid as uuid_lib
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from ..models import Stone, QRPack
from .base import BaseStoneWalkerTestCase


class UnconfirmedEmailGateTests(BaseStoneWalkerTestCase):
    """Phase 3: an email-unconfirmed (email-first) account cannot acquire/claim QRs."""

    def _login_unconfirmed(self):
        from django.contrib.auth.models import User
        from accounts.models import EmailAddressState
        u = User.objects.create(username='prov', email='prov@example.com', is_active=True)
        u.set_unusable_password(); u.save()
        EmailAddressState.objects.create(user=u, email='prov@example.com', is_confirmed=False)
        self.client.force_login(u)
        return u

    def test_unconfirmed_blocked_from_free_qr(self):
        self._login_unconfirmed()
        resp = self.client.get(reverse('free_qr'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('my-stones', resp.url)
        self.assertEqual(QRPack.objects.count(), 0)  # no QR minted

    def test_unconfirmed_blocked_from_create_stone(self):
        self._login_unconfirmed()
        resp = self.client.get(reverse('create_stone'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('my-stones', resp.url)
        self.assertEqual(QRPack.objects.count(), 0)


class DynamicPricingTests(BaseStoneWalkerTestCase):
    """Task 15A: 30 free unclaimed codes, $0.50/code beyond, premium unlimited."""

    def _give_unclaimed(self, user, n):
        pack = QRPack.objects.create(
            FK_user=user, pack_type='paid_30pack',
            status='fulfilled', price_cents=0, fulfilled_at=timezone.now(),
        )
        for i in range(n):
            Stone.objects.create(PK_stone=f'U{user.id}-{i}', FK_pack=pack, FK_user=None, status='unclaimed')

    def _make_premium(self, user):
        from accounts.models import Subscription
        Subscription.objects.create(user=user, plan='lifetime', status='active')

    def test_pack_free_within_allowance(self):
        self.assertTrue(Stone.pack_is_free_for_user(self.user, 30))   # 0 + 30 <= 30
        self._give_unclaimed(self.user, 1)
        self.assertFalse(Stone.pack_is_free_for_user(self.user, 30))  # 1 + 30 > 30
        self.assertTrue(Stone.pack_is_free_for_user(self.user, 29))   # 1 + 29 == 30

    def test_remaining_allowance(self):
        self.assertEqual(Stone.remaining_free_allowance(self.user), 30)
        self._give_unclaimed(self.user, 10)
        self.assertEqual(Stone.remaining_free_allowance(self.user), 20)

    def test_premium_unlimited_free(self):
        self._give_unclaimed(self.user, 40)
        self._make_premium(self.user)
        self.assertTrue(Stone.pack_is_free_for_user(self.user, 30))
        self.assertIsNone(Stone.remaining_free_allowance(self.user))

    def test_checkout_free_within_allowance(self):
        resp = self.client.post(reverse('checkout', args=['paid_3pack']))  # 0 + 3 <= 30
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            Stone.objects.filter(FK_pack__FK_user=self.user, status='unclaimed').count(), 3)

    def test_checkout_paid_beyond_allowance(self):
        self._give_unclaimed(self.user, 29)  # 29 + 3 > 30 -> paid path
        resp = self.client.post(reverse('checkout', args=['paid_3pack']))
        self.assertEqual(resp.status_code, 302)
        # Paid branch taken (Stripe not configured in tests) -> no free 3-pack minted
        self.assertFalse(QRPack.objects.filter(FK_user=self.user, pack_type='paid_3pack').exists())


class CreateNewStoneRouterTests(BaseStoneWalkerTestCase):
    """Test the CreateNewStoneView smart router"""

    def test_no_packs_creates_free_qr_before_threshold(self):
        """User with no packs before threshold gets a free QR and redirects to my-stones"""
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('my_stones'))
        # A new pack and unclaimed stone should have been created
        pack = QRPack.objects.filter(FK_user=self.user, pack_type='free_single').first()
        self.assertIsNotNone(pack)
        self.assertTrue(pack.stones.filter(status='unclaimed').exists())

    def test_no_unclaimed_stones_creates_free_qr_before_threshold(self):
        """User with packs but no unclaimed stones gets a free QR before threshold"""
        pack = QRPack.objects.create(
            FK_user=self.user,
            pack_type='free_single',
            status='fulfilled',
            price_cents=0,
            fulfilled_at=timezone.now(),
        )
        # Create a stone that's already claimed (draft status)
        Stone.objects.create(
            PK_stone='CLAIMED1',
            FK_pack=pack,
            FK_user=self.user,
            status='draft',
        )
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('my_stones'))
        # A new free pack should have been created
        self.assertEqual(
            QRPack.objects.filter(FK_user=self.user, pack_type='free_single').count(), 2
        )

    def test_at_free_allowance_redirects_to_shop(self):
        """A user who has used their 30 free codes is sent to the shop to buy more."""
        pack = QRPack.objects.create(
            FK_user=self.user, pack_type='paid_30pack',
            status='fulfilled', price_cents=0, fulfilled_at=timezone.now(),
        )
        for i in range(Stone.FREE_UNCLAIMED_CAP):
            Stone.objects.create(PK_stone=f'ALLOW{i}', FK_pack=pack, FK_user=None, status='unclaimed')
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('shop'))

    def test_unclaimed_stone_redirects_to_my_stones(self):
        """User with an unclaimed stone should be redirected to my-stones"""
        pack = QRPack.objects.create(
            FK_user=self.user,
            pack_type='free_single',
            status='fulfilled',
            price_cents=0,
            fulfilled_at=timezone.now(),
        )
        stone = Stone.objects.create(
            PK_stone='UNCLAIMED-TEST1',
            FK_pack=pack,
            FK_user=None,
            status='unclaimed',
        )
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('my_stones'))

    def test_multiple_packs_with_unclaimed_redirects_to_my_stones(self):
        """With multiple packs, unclaimed stone redirects to my-stones"""
        # Pack 1: all claimed
        pack1 = QRPack.objects.create(
            FK_user=self.user, pack_type='free_single',
            status='fulfilled', price_cents=0, fulfilled_at=timezone.now(),
        )
        Stone.objects.create(
            PK_stone='CLAIMED-A', FK_pack=pack1,
            FK_user=self.user, status='draft',
        )
        # Pack 2: has unclaimed
        pack2 = QRPack.objects.create(
            FK_user=self.user, pack_type='paid_10pack',
            status='fulfilled', price_cents=999, fulfilled_at=timezone.now(),
        )
        unclaimed = Stone.objects.create(
            PK_stone='UNCLAIMED-B', FK_pack=pack2,
            FK_user=None, status='unclaimed',
        )
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('my_stones'))

    def test_requires_login(self):
        """Anonymous users should be redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('create_stone'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('accounts', response.url)


class ShopDevModeTests(BaseStoneWalkerTestCase):
    """Test dev mode overrides in the shop.

    SHOP_VISIBLE_USER_THRESHOLD=0 disables the QR-per-user limit so these
    tests focus purely on dev-mode vs prod-mode shop behaviour.
    """

    @override_settings(DEBUG=True, SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_dev_mode_banner_shown(self):
        """Dev mode banner should appear in the shop page"""
        response = self.client.get(reverse('shop'))
        self.assertContains(response, 'Local dev sale')

    @override_settings(DEBUG=False, SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_prod_mode_no_banner(self):
        """Dev mode banner should not appear in production"""
        response = self.client.get(reverse('shop'))
        self.assertNotContains(response, 'Local dev sale')

    @override_settings(DEBUG=True, SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_dev_mode_free_single_not_disabled(self):
        """In dev mode, free_single should not be disabled even after claiming"""
        # Create an existing fulfilled free_single pack
        QRPack.objects.create(
            FK_user=self.user, pack_type='free_single',
            status='fulfilled', price_cents=0, fulfilled_at=timezone.now(),
        )
        response = self.client.get(reverse('shop'))
        # The "Get Free" button should still be present (not replaced by "Claimed")
        self.assertContains(response, 'Get Free')

    @override_settings(DEBUG=False, SHOP_VISIBLE_USER_THRESHOLD=0)
    @override_settings(DEBUG=False)
    def test_shop_price_display_is_dynamic(self):
        """A pack shows Free within the allowance and its price once it would exceed it."""
        resp = self.client.get(reverse('shop'))
        prods = {p['id']: p for p in resp.context['products']}
        self.assertEqual(prods['paid_3pack']['price_display'], 'Free')  # 0 + 3 <= 30
        # Fill the free allowance
        pack = QRPack.objects.create(
            FK_user=self.user, pack_type='paid_30pack',
            status='fulfilled', price_cents=0, fulfilled_at=timezone.now(),
        )
        for i in range(Stone.FREE_UNCLAIMED_CAP):
            Stone.objects.create(PK_stone=f'D{i}', FK_pack=pack, FK_user=None, status='unclaimed')
        resp = self.client.get(reverse('shop'))
        prods = {p['id']: p for p in resp.context['products']}
        self.assertNotEqual(prods['paid_3pack']['price_display'], 'Free')  # now priced

    @override_settings(DEBUG=True, SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_dev_mode_checkout_allows_multiple_free(self):
        """In dev mode, user can checkout free_single multiple times"""
        # First checkout
        response = self.client.post(reverse('checkout', kwargs={'product_id': 'free_single'}))
        # Should succeed (either redirect to success or download)
        self.assertIn(response.status_code, [200, 302])
        self.assertEqual(QRPack.objects.filter(FK_user=self.user, pack_type='free_single').count(), 1)

        # Second checkout should also succeed in dev mode
        response = self.client.post(reverse('checkout', kwargs={'product_id': 'free_single'}))
        self.assertIn(response.status_code, [200, 302])
        self.assertEqual(QRPack.objects.filter(FK_user=self.user, pack_type='free_single').count(), 2)

    @override_settings(DEBUG=False)
    def test_prod_mode_multiple_free_within_allowance(self):
        """In production, repeated free singles are allowed while within the allowance."""
        self.client.post(reverse('checkout', kwargs={'product_id': 'free_single'}))
        self.client.post(reverse('checkout', kwargs={'product_id': 'free_single'}))
        self.assertEqual(QRPack.objects.filter(FK_user=self.user, pack_type='free_single').count(), 2)


class ShopFlowEndToEndTests(BaseStoneWalkerTestCase):
    """End-to-end tests for the complete create stone flow"""

    def test_full_flow_create_stone_before_threshold(self):
        """Full flow before threshold: create-stone creates free QR → my-stones → claim"""
        # Step 1: No unclaimed QR, before threshold → creates free QR → my-stones
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('my_stones'))

        # Verify pack and unclaimed stone were created
        pack = QRPack.objects.get(FK_user=self.user, pack_type='free_single')
        unclaimed = pack.stones.filter(status='unclaimed').first()
        self.assertIsNotNone(unclaimed)

        # Step 2: Now create-stone should redirect to my-stones with message (unclaimed exists)
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('my_stones'))

    def test_full_flow_at_allowance_to_shop(self):
        """Once the free allowance is used up, create-stone routes to the shop."""
        pack = QRPack.objects.create(
            FK_user=self.user, pack_type='paid_30pack',
            status='fulfilled', price_cents=0, fulfilled_at=timezone.now(),
        )
        for i in range(Stone.FREE_UNCLAIMED_CAP):
            Stone.objects.create(PK_stone=f'FL{i}', FK_pack=pack, FK_user=None, status='unclaimed')
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('shop'))

    def test_stonewalker_page_has_create_stone_link(self):
        """The stonewalker start page should link to create-stone route"""
        response = self.client.get(reverse('stonewalker_start'))
        self.assertContains(response, reverse('create_stone'))
