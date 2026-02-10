"""
Tests for the shop-based stone creation flow.

The "Create New Stone" button routes through the shop:
- If user has an unclaimed QR → redirect straight to claim
- If no unclaimed QR → redirect to shop
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

    def test_no_packs_redirects_to_shop(self):
        """User with no packs should be redirected to the shop"""
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('shop'))

    def test_no_unclaimed_stones_redirects_to_shop(self):
        """User with packs but no unclaimed stones should go to shop"""
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
        self.assertRedirects(response, reverse('shop'))

    def test_unclaimed_stone_redirects_to_claim(self):
        """User with an unclaimed stone should be redirected to the claim page"""
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
        self.assertRedirects(
            response,
            reverse('claim_stone', kwargs={'stone_uuid': str(stone.uuid)})
        )

    def test_multiple_packs_finds_first_unclaimed(self):
        """With multiple packs, the first unclaimed stone should be found"""
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
        self.assertRedirects(
            response,
            reverse('claim_stone', kwargs={'stone_uuid': str(unclaimed.uuid)})
        )

    def test_requires_login(self):
        """Anonymous users should be redirected to login"""
        self.client.logout()
        response = self.client.get(reverse('create_stone'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('accounts', response.url)


class ShopDevModeTests(BaseStoneWalkerTestCase):
    """Test dev mode overrides in the shop"""

    @override_settings(DEBUG=True)
    def test_dev_mode_banner_shown(self):
        """Dev mode banner should appear in the shop page"""
        response = self.client.get(reverse('shop'))
        self.assertContains(response, 'Local dev sale')

    @override_settings(DEBUG=False)
    def test_prod_mode_no_banner(self):
        """Dev mode banner should not appear in production"""
        response = self.client.get(reverse('shop'))
        self.assertNotContains(response, 'Local dev sale')

    @override_settings(DEBUG=True)
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

    @override_settings(DEBUG=False)
    def test_prod_mode_free_single_disabled_after_claim(self):
        """In production, free_single should be disabled after claiming"""
        QRPack.objects.create(
            FK_user=self.user, pack_type='free_single',
            status='fulfilled', price_cents=0, fulfilled_at=timezone.now(),
        )
        response = self.client.get(reverse('shop'))
        self.assertContains(response, 'Claimed')

    @override_settings(DEBUG=True)
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
    """End-to-end tests for the complete create stone → shop → claim flow"""

    @override_settings(DEBUG=True)
    def test_full_flow_no_qr_to_shop_to_claim(self):
        """Full flow: create-stone → shop → checkout → create-stone → claim"""
        # Step 1: No unclaimed QR, should go to shop
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(response, reverse('shop'))

        # Step 2: Checkout free single
        response = self.client.post(reverse('checkout', kwargs={'product_id': 'free_single'}))
        self.assertIn(response.status_code, [200, 302])

        # Verify pack and unclaimed stone were created
        pack = QRPack.objects.get(FK_user=self.user, pack_type='free_single')
        unclaimed = pack.stones.filter(status='unclaimed').first()
        self.assertIsNotNone(unclaimed)

        # Step 3: Now create-stone should redirect to claim
        response = self.client.get(reverse('create_stone'))
        self.assertRedirects(
            response,
            reverse('claim_stone', kwargs={'stone_uuid': str(unclaimed.uuid)})
        )

    def test_stonewalker_page_has_create_stone_link(self):
        """The stonewalker start page should link to create-stone route"""
        response = self.client.get(reverse('stonewalker_start'))
        self.assertContains(response, reverse('create_stone'))
