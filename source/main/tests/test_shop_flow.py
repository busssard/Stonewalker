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

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_no_unclaimed_stones_redirects_to_shop_after_threshold(self):
        """User with no unclaimed stones goes to shop after threshold"""
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
    def test_prod_mode_free_single_disabled_after_claim(self):
        """In production, free_single should be disabled after claiming"""
        QRPack.objects.create(
            FK_user=self.user, pack_type='free_single',
            status='fulfilled', price_cents=0, fulfilled_at=timezone.now(),
        )
        response = self.client.get(reverse('shop'))
        self.assertContains(response, 'Claimed')

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

    @override_settings(DEBUG=False, SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_prod_mode_checkout_blocks_second_free(self):
        """In production, second free_single checkout should be blocked"""
        # First checkout
        self.client.post(reverse('checkout', kwargs={'product_id': 'free_single'}))
        self.assertEqual(QRPack.objects.filter(FK_user=self.user, pack_type='free_single').count(), 1)

        # Second checkout should be blocked
        response = self.client.post(reverse('checkout', kwargs={'product_id': 'free_single'}))
        self.assertRedirects(response, reverse('shop'))
        # Still only 1 pack
        self.assertEqual(QRPack.objects.filter(FK_user=self.user, pack_type='free_single').count(), 1)


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

    @override_settings(SHOP_VISIBLE_USER_THRESHOLD=0)
    def test_full_flow_after_threshold_to_shop(self):
        """After threshold: create-stone → shop → checkout → create-stone → my-stones"""
        # Step 1: No unclaimed QR, after threshold → shop
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('shop'))

        # Step 2: Checkout free single
        response = self.client.post(reverse('checkout', kwargs={'product_id': 'free_single'}))
        self.assertIn(response.status_code, [200, 302])

        # Verify pack and unclaimed stone were created
        pack = QRPack.objects.get(FK_user=self.user, pack_type='free_single')
        unclaimed = pack.stones.filter(status='unclaimed').first()
        self.assertIsNotNone(unclaimed)

        # Step 3: Now create-stone should redirect to my-stones (unclaimed exists)
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('my_stones'))

    def test_stonewalker_page_has_create_stone_link(self):
        """The stonewalker start page should link to create-stone route"""
        response = self.client.get(reverse('stonewalker_start'))
        self.assertContains(response, reverse('create_stone'))
