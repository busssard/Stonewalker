"""
Bug-hunt regression tests for the shop / Stripe payment flow (F4, F8-F12).
"""

import json
import tempfile
import threading
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import Subscription
from ..models import Stone, QRPack
from ..stripe_service import StripeService
from ..validators import validate_stone_name
from .base import BaseQRTestCase


def _post_event(client, event):
    return client.post(
        reverse('stripe_webhook'), data=json.dumps(event),
        content_type='application/json', HTTP_STRIPE_SIGNATURE='t=1,v1=fake',
    )


# --- F4: premium subscriptions linked to the paying user -------------------

@override_settings(STRIPE_SECRET_KEY='sk_test_x', STRIPE_PRICE_MONTHLY='price_m')
class SubscriptionCheckoutTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('payer', 'payer@example.com', 'pw')
        self.product = {'id': 'premium_monthly', 'billing_interval': 'month'}

    @patch('main.stripe_service.stripe')
    def test_session_carries_user_id_onto_subscription(self, mock_stripe):
        mock_stripe.Customer.search.return_value = MagicMock(data=[])
        mock_stripe.Customer.create.return_value = MagicMock(id='cus_new')
        mock_stripe.checkout.Session.create.return_value = MagicMock(id='cs_1', url='https://x')

        StripeService.create_subscription_checkout(self.user, self.product, 'https://s', 'https://c')

        kwargs = mock_stripe.checkout.Session.create.call_args.kwargs
        self.assertEqual(kwargs['client_reference_id'], str(self.user.id))
        self.assertEqual(kwargs['subscription_data']['metadata']['user_id'], str(self.user.id))

    @patch('main.stripe_service.stripe')
    def test_reuses_existing_stripe_customer(self, mock_stripe):
        # An earlier (abandoned) checkout already created a Customer for this user.
        mock_stripe.Customer.search.return_value = MagicMock(data=[MagicMock(id='cus_old')])
        mock_stripe.checkout.Session.create.return_value = MagicMock(id='cs_1', url='https://x')

        StripeService.create_subscription_checkout(self.user, self.product, 'https://s', 'https://c')

        mock_stripe.Customer.create.assert_not_called()
        self.assertEqual(mock_stripe.checkout.Session.create.call_args.kwargs['customer'], 'cus_old')

    @patch('main.stripe_service.stripe')
    def test_reuses_customer_id_stored_on_subscription(self, mock_stripe):
        Subscription.objects.create(user=self.user, status='canceled', stripe_customer_id='cus_db')
        mock_stripe.checkout.Session.create.return_value = MagicMock(id='cs_1', url='https://x')

        StripeService.create_subscription_checkout(self.user, self.product, 'https://s', 'https://c')

        mock_stripe.Customer.create.assert_not_called()
        mock_stripe.Customer.search.assert_not_called()
        self.assertEqual(mock_stripe.checkout.Session.create.call_args.kwargs['customer'], 'cus_db')


@override_settings(DEBUG=True, STRIPE_WEBHOOK_SECRET='')
class SubscriptionWebhookLinkTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('payer', 'payer@example.com', 'pw')

    def _session_completed(self, **overrides):
        obj = {
            'id': 'cs_test', 'mode': 'subscription', 'status': 'complete',
            'payment_status': 'paid', 'customer': 'cus_1', 'subscription': 'sub_1',
            'client_reference_id': str(self.user.id),
            'metadata': {'user_id': str(self.user.id), 'plan': 'yearly'},
        }
        obj.update(overrides)
        return {'type': 'checkout.session.completed', 'data': {'object': obj}}

    def test_checkout_completed_links_subscription_to_user(self):
        resp = _post_event(self.client, self._session_completed())
        self.assertEqual(resp.status_code, 200)
        sub = Subscription.objects.get(user=self.user)
        self.assertEqual(sub.stripe_customer_id, 'cus_1')
        self.assertEqual(sub.stripe_subscription_id, 'sub_1')
        self.assertEqual(sub.plan, 'yearly')
        self.assertTrue(sub.grants_premium)

    def test_subscription_created_without_metadata_after_checkout_completed(self):
        # Order Stripe often uses: session.completed first, then subscription.created
        # whose object carries no metadata — must resolve via the stored customer id.
        _post_event(self.client, self._session_completed())
        _post_event(self.client, {'type': 'customer.subscription.created', 'data': {'object': {
            'id': 'sub_1', 'customer': 'cus_1', 'status': 'active',
            'items': {'data': [{'price': {'recurring': {'interval': 'year'}}}]},
            'current_period_start': 1700000000, 'current_period_end': 1731536000,
        }}})
        sub = Subscription.objects.get(user=self.user)
        self.assertEqual(sub.status, 'active')
        self.assertIsNotNone(sub.current_period_end)

    def test_client_reference_id_fallback(self):
        _post_event(self.client, self._session_completed(metadata={}))
        self.assertTrue(Subscription.objects.filter(user=self.user, stripe_subscription_id='sub_1').exists())

    def test_session_completed_does_not_clobber_newer_subscription_state(self):
        # subscription.created arrived first and recorded the real status/period.
        Subscription.objects.create(
            user=self.user, status='trialing', plan='yearly',
            stripe_customer_id='cus_1', stripe_subscription_id='sub_1',
        )
        _post_event(self.client, self._session_completed(payment_status='no_payment_required'))
        self.assertEqual(Subscription.objects.get(user=self.user).status, 'trialing')


# --- F11: unsigned webhooks rejected outside DEBUG --------------------------

class WebhookSignatureTests(TestCase):

    def _pending_pack(self):
        user = User.objects.create_user('buyer', 'b@example.com', 'pw')
        return QRPack.objects.create(FK_user=user, pack_type='paid_10pack', status='pending', price_cents=999)

    @override_settings(DEBUG=False, STRIPE_WEBHOOK_SECRET='')
    def test_unsigned_event_rejected_in_production(self):
        pack = self._pending_pack()
        with patch.object(StripeService, 'handle_checkout_completed') as handler:
            resp = _post_event(self.client, {'type': 'checkout.session.completed', 'data': {
                'object': {'mode': 'payment', 'metadata': {'pack_id': str(pack.id)}}}})
        self.assertEqual(resp.status_code, 400)
        handler.assert_not_called()

    @override_settings(DEBUG=True, STRIPE_WEBHOOK_SECRET='')
    def test_unsigned_event_allowed_in_debug(self):
        with patch.object(StripeService, 'handle_checkout_completed') as handler:
            resp = _post_event(self.client, {'type': 'checkout.session.completed', 'data': {
                'object': {'mode': 'payment', 'metadata': {}}}})
        self.assertEqual(resp.status_code, 200)
        handler.assert_called_once()


# --- F8: stone number assignment is race-safe --------------------------------

class StoneNumberRaceTests(TestCase):

    def test_stale_max_retries_instead_of_integrity_error(self):
        Stone.objects.create(PK_stone='FIRST', status='unclaimed')  # gets #1
        real_aggregate = Stone.objects.aggregate
        calls = {'n': 0}

        def stale_then_real(*args, **kwargs):
            calls['n'] += 1
            if calls['n'] == 1:
                return {'stone_number__max': 0}  # another worker's insert not seen yet
            return real_aggregate(*args, **kwargs)

        with patch.object(Stone.objects, 'aggregate', side_effect=stale_then_real):
            stone = Stone.objects.create(PK_stone='SECOND', status='unclaimed')
        self.assertEqual(stone.stone_number, 2)

    def test_pk_collision_still_raises(self):
        from django.db import IntegrityError
        Stone.objects.create(PK_stone='DUP', status='unclaimed')
        with self.assertRaises(IntegrityError):
            Stone(PK_stone='DUP', status='unclaimed').save(force_insert=True)


# --- F8 / F9: pack fulfilment is complete and happens exactly once -------------

@patch('main.pdf_service.PDFService.generate_pack_pdf')
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PackFulfilmentTests(BaseQRTestCase):

    def _pack(self, status='pending', stones=0):
        pack = QRPack.objects.create(FK_user=self.user, pack_type='paid_10pack',
                                     status=status, price_cents=999)
        for i in range(stones):
            Stone.objects.create(PK_stone=f'UNCLAIMED-P{i}', FK_pack=pack, status='unclaimed')
        return pack

    def _session(self, pack):
        return {'mode': 'payment', 'metadata': {'pack_id': str(pack.id)}}

    def test_webhook_fulfils_full_pack(self, _pdf):
        pack = self._pack()
        StripeService.handle_checkout_completed(self._session(pack))
        pack.refresh_from_db()
        self.assertEqual(pack.status, 'fulfilled')
        self.assertEqual(pack.stones.count(), 10)

    def test_webhook_replay_does_not_duplicate(self, _pdf):
        pack = self._pack()
        StripeService.handle_checkout_completed(self._session(pack))
        StripeService.handle_checkout_completed(self._session(pack))
        self.assertEqual(pack.stones.count(), 10)

    def test_success_page_tops_up_partial_pack(self, _pdf):
        # A crashed fulfilment left a paid pack with only 4 of 10 stones.
        pack = self._pack(status='paid', stones=4)
        self.client.get(reverse('checkout_success') + f'?pack_id={pack.id}')
        pack.refresh_from_db()
        self.assertEqual(pack.stones.count(), 10)
        self.assertEqual(pack.status, 'fulfilled')

    def test_webhook_retry_tops_up_partial_pack(self, _pdf):
        pack = self._pack(status='paid', stones=4)
        StripeService.handle_checkout_completed(self._session(pack))
        pack.refresh_from_db()
        self.assertEqual(pack.stones.count(), 10)
        self.assertEqual(pack.status, 'fulfilled')

    def test_success_page_after_webhook_does_not_duplicate(self, _pdf):
        pack = self._pack()
        StripeService.handle_checkout_completed(self._session(pack))
        self.client.get(reverse('checkout_success') + f'?pack_id={pack.id}')
        self.assertEqual(pack.stones.count(), 10)


@patch('main.pdf_service.PDFService.generate_pack_pdf')
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ConcurrentFulfilmentTests(TransactionTestCase):
    """Webhook and success page racing on the same pack must yield one set of stones."""

    def test_success_page_during_webhook_fulfilment(self, _pdf):
        from accounts.models import TermsAcceptance
        user = User.objects.create_user('racer', 'r@example.com', 'pw')
        TermsAcceptance.objects.create(user=user)
        pack = QRPack.objects.create(FK_user=user, pack_type='paid_10pack', status='pending', price_cents=999)

        from .. import shop_utils
        real_get_config = shop_utils.get_product_config
        reached, go = threading.Event(), threading.Event()
        webhook_thread = {}

        def pausing_get_config(product_id):
            # Pause the webhook right before it creates stones.
            if threading.current_thread() is webhook_thread.get('t') and not reached.is_set():
                reached.set()
                go.wait(10)
            return real_get_config(product_id)

        def run_webhook():
            try:
                StripeService.handle_checkout_completed({'mode': 'payment', 'metadata': {'pack_id': str(pack.id)}})
            finally:
                connection.close()

        with patch('main.shop_utils.get_product_config', side_effect=pausing_get_config):
            t = threading.Thread(target=run_webhook)
            webhook_thread['t'] = t
            t.start()
            self.assertTrue(reached.wait(10))
            self.client.force_login(user)
            self.client.get(reverse('checkout_success') + f'?pack_id={pack.id}')
            go.set()
            t.join(20)

        self.assertEqual(Stone.objects.filter(FK_pack=pack).count(), 10)


# --- F10: stone name validation ---------------------------------------------

class ValidateStoneNameTests(TestCase):

    def test_valid_names(self):
        for name in ('Rocky', 'Stein-42', 'a_b', 'ABCDEFGHIJ', '7'):
            validate_stone_name(name)

    def test_invalid_names(self):
        cases = {
            '': 'empty', 'ABCDEFGHIJK': 'too_long', 'My Stone': 'whitespace',
            'a/b': 'invalid_chars', '..': 'invalid_chars', 'a\\b': 'invalid_chars',
            'a?b': 'invalid_chars', 'a.b': 'invalid_chars', 'a#b': 'invalid_chars',
            'Stéin': 'invalid_chars', '<b>': 'invalid_chars',
        }
        for name, code in cases.items():
            with self.assertRaises(ValidationError, msg=name) as ctx:
                validate_stone_name(name)
            self.assertEqual(ctx.exception.code, code, name)

    def test_check_stone_name_api_rejects_unsafe(self):
        resp = self.client.get('/api/check_stone_name/', {'PK_stone': 'a/b'})
        data = resp.json()
        self.assertTrue(data['taken'])
        self.assertEqual(data['reason'], 'invalid_chars')

    def test_check_stone_name_api_rejects_too_long(self):
        data = self.client.get('/api/check_stone_name/', {'PK_stone': 'ABCDEFGHIJK'}).json()
        self.assertTrue(data['taken'])
        self.assertEqual(data['reason'], 'too_long')


class ClaimStoneNameTests(BaseQRTestCase):

    def _claim(self, name):
        pack = QRPack.objects.create(FK_user=self.user, pack_type='free_single',
                                     status='fulfilled', price_cents=0, fulfilled_at=timezone.now())
        stone = Stone.objects.create(PK_stone='UNCLAIMED-NM', FK_pack=pack, status='unclaimed')
        resp = self.client.post(reverse('claim_stone', args=[stone.stone_number]),
                                {'stone_uuid': str(stone.uuid), 'stone_name': name})
        return resp, stone

    def test_rejects_path_characters(self):
        for name in ('a/b', '..', 'x?y', 'a\\b'):
            resp, stone = self._claim(name)
            self.assertEqual(resp.status_code, 200, name)  # form re-rendered with error
            self.assertFalse(Stone.objects.filter(PK_stone=name).exists(), name)
            stone.delete()

    def test_accepts_hyphen_and_underscore(self):
        resp, _ = self._claim('Ab_-9')
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Stone.objects.filter(PK_stone='Ab_-9', status='draft').exists())


# --- F12: single-QR download requires ownership -------------------------------

class DownloadStoneQROwnershipTests(BaseQRTestCase):

    def test_packless_stone_of_other_user_blocked(self):
        other = self.create_user('other', 'pw', 'other@example.com')
        stone = Stone.objects.create(PK_stone='OTHERS', FK_user=other, FK_pack=None, status='draft')
        with patch('main.shop_views.QRCodeService.create_download_response') as dl:
            resp = self.client.get(reverse('download_stone_qr', args=[stone.stone_number]))
        self.assertEqual(resp.status_code, 302)
        dl.assert_not_called()

    def test_packless_ownerless_stone_blocked(self):
        stone = Stone.objects.create(PK_stone='ORPHAN', FK_user=None, FK_pack=None, status='unclaimed')
        with patch('main.shop_views.QRCodeService.create_download_response') as dl:
            resp = self.client.get(reverse('download_stone_qr', args=[stone.stone_number]))
        self.assertEqual(resp.status_code, 302)
        dl.assert_not_called()

    def test_packless_own_stone_allowed(self):
        stone = Stone.objects.create(PK_stone='MINE', FK_user=self.user, FK_pack=None, status='draft')
        resp = self.client.get(reverse('download_stone_qr', args=[stone.stone_number]))
        self.assertEqual(resp.status_code, 200)

    def test_claimer_of_someone_elses_pack_stone_allowed(self):
        # A student who claimed a teacher's code may still download its QR.
        teacher = self.create_user('teacher', 'pw', 't@example.com')
        pack = QRPack.objects.create(FK_user=teacher, pack_type='free_single', status='fulfilled', price_cents=0)
        stone = Stone.objects.create(PK_stone='STUDENT', FK_user=self.user, FK_pack=pack, status='draft')
        resp = self.client.get(reverse('download_stone_qr', args=[stone.stone_number]))
        self.assertEqual(resp.status_code, 200)


# --- NEW-1: subscriptions are not sold as one-time shop products -------------

class ShopSubscriptionProductTests(BaseQRTestCase):

    def test_shop_does_not_list_premium_as_buy_now(self):
        resp = self.client.get(reverse('shop'))
        ids = [p['id'] for p in resp.context['products']]
        self.assertNotIn('premium_monthly', ids)
        self.assertNotIn('premium_yearly', ids)
        self.assertNotContains(resp, reverse('checkout', args=['premium_monthly']))

    @override_settings(STRIPE_SECRET_KEY='sk_test_x')
    def test_checkout_rejects_subscription_product(self):
        with patch('main.stripe_service.StripeService.create_checkout_session') as create:
            resp = self.client.post(reverse('checkout', args=['premium_monthly']))
        create.assert_not_called()
        self.assertRedirects(resp, reverse('premium'), fetch_redirect_response=False)
        self.assertFalse(QRPack.objects.filter(pack_type='premium_monthly').exists())


# --- NEW-10: free codes are only minted on POST --------------------------------

class MintOnPostOnlyTests(BaseQRTestCase):

    def test_create_stone_get_does_not_mint(self):
        resp = self.client.get(reverse('create_stone'))
        self.assertTemplateUsed(resp, 'main/create_stone_confirm.html')
        self.assertContains(resp, 'method="post"')
        self.assertFalse(QRPack.objects.filter(FK_user=self.user).exists())

    def test_create_stone_post_mints(self):
        resp = self.client.post(reverse('create_stone'))
        self.assertRedirects(resp, reverse('my_stones'), fetch_redirect_response=False)
        self.assertTrue(Stone.objects.filter(FK_pack__FK_user=self.user, status='unclaimed').exists())

    def test_free_qr_get_does_not_mint(self):
        resp = self.client.get(reverse('free_qr'))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(QRPack.objects.filter(FK_user=self.user).exists())

    def test_free_qr_post_mints(self):
        resp = self.client.post(reverse('free_qr'))
        self.assertEqual(resp.status_code, 200)  # QR download
        self.assertTrue(QRPack.objects.filter(FK_user=self.user, pack_type='free_single').exists())

    def test_create_stone_requires_csrf(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        resp = client.post(reverse('create_stone'))
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(QRPack.objects.filter(FK_user=self.user).exists())

    def test_entry_points_use_post_forms(self):
        url = reverse('create_stone')
        for page in ('stonewalker_start', 'my_stones'):
            html = self.client.get(reverse(page)).content.decode()
            self.assertRegex(html, r'<form[^>]*method="post"[^>]*action="%s"' % url, page)


# --- NEW-11: success page verifies payment with Stripe when the webhook is late ---

@patch('main.pdf_service.PDFService.generate_pack_pdf')
@override_settings(STRIPE_SECRET_KEY='sk_test_x', MEDIA_ROOT=tempfile.mkdtemp())
class SuccessPageStripeVerificationTests(BaseQRTestCase):

    def _pack(self, pack_type='paid_10pack'):
        return QRPack.objects.create(FK_user=self.user, pack_type=pack_type, status='pending',
                                     price_cents=500, stripe_payment_intent_id='cs_test_1')

    def _session(self, pack, payment_status):
        return {'id': 'cs_test_1', 'mode': 'payment', 'payment_status': payment_status,
                'metadata': {'pack_id': str(pack.id)}}

    @patch('main.stripe_service.stripe.checkout.Session.retrieve')
    def test_paid_session_fulfilled_without_webhook(self, retrieve, _pdf):
        pack = self._pack()
        retrieve.return_value = self._session(pack, 'paid')
        self.client.get(reverse('checkout_success') + f'?pack_id={pack.id}')
        retrieve.assert_called_once_with('cs_test_1')
        pack.refresh_from_db()
        self.assertEqual(pack.status, 'fulfilled')
        self.assertEqual(pack.stones.count(), 10)

    @patch('main.stripe_service.stripe.checkout.Session.retrieve')
    def test_unpaid_session_not_fulfilled(self, retrieve, _pdf):
        pack = self._pack()
        retrieve.return_value = self._session(pack, 'unpaid')
        self.client.get(reverse('checkout_success') + f'?pack_id={pack.id}')
        pack.refresh_from_db()
        self.assertEqual(pack.status, 'pending')
        self.assertEqual(pack.stones.count(), 0)

    @patch('main.stripe_service.stripe.checkout.Session.retrieve')
    def test_session_for_other_pack_ignored(self, retrieve, _pdf):
        pack = self._pack()
        retrieve.return_value = {'id': 'cs_test_1', 'payment_status': 'paid',
                                 'metadata': {'pack_id': '00000000-0000-0000-0000-000000000000'}}
        self.client.get(reverse('checkout_success') + f'?pack_id={pack.id}')
        pack.refresh_from_db()
        self.assertEqual(pack.status, 'pending')

    @patch('main.stripe_service.stripe.checkout.Session.retrieve', side_effect=Exception('down'))
    def test_stripe_error_leaves_pack_pending(self, retrieve, _pdf):
        pack = self._pack()
        resp = self.client.get(reverse('checkout_success') + f'?pack_id={pack.id}')
        self.assertEqual(resp.status_code, 200)
        pack.refresh_from_db()
        self.assertEqual(pack.status, 'pending')

    @patch('main.stripe_service.stripe.checkout.Session.retrieve')
    def test_paid_single_code_shows_download(self, retrieve, _pdf):
        pack = self._pack(pack_type='free_single')
        retrieve.return_value = self._session(pack, 'paid')
        resp = self.client.get(reverse('checkout_success') + f'?pack_id={pack.id}')
        stone = pack.stones.get()
        self.assertContains(resp, reverse('download_stone_qr', args=[stone.stone_number]))
