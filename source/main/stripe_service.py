"""
Stripe Payment Service for the Shop.
Handles Stripe Checkout Sessions, subscriptions, and webhook processing.
"""
import stripe
import uuid as uuid_lib
import logging
from datetime import datetime, timezone as dt_tz
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import QRPack, Stone
from .qr_service import QRCodeService

logger = logging.getLogger(__name__)

# Mapping from shop_config billing_interval to Stripe Price IDs
SUBSCRIPTION_PRICE_MAP = {
    'month': lambda: getattr(settings, 'STRIPE_PRICE_MONTHLY', ''),
    'year': lambda: getattr(settings, 'STRIPE_PRICE_YEARLY', ''),
}


class StripeService:
    """Handle Stripe payment operations."""

    @classmethod
    def _init_stripe(cls):
        """Initialize Stripe with secret key."""
        stripe.api_key = settings.STRIPE_SECRET_KEY

    @classmethod
    def create_checkout_session(cls, user, product, success_url, cancel_url):
        """
        Create a Stripe Checkout Session for a product.

        Args:
            user: Django User instance
            product: Product dict from shop_config.json
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel

        Returns:
            tuple: (session_id, checkout_url)

        Raises:
            Exception: If Stripe API call fails
        """
        cls._init_stripe()

        # Create pending QRPack
        pack = QRPack.objects.create(
            FK_user=user,
            pack_type=product['id'],
            status='pending',
            price_cents=product['price_cents'],
            currency='USD',
        )

        # Create Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product['name'],
                        'description': product.get('description', ''),
                    },
                    'unit_amount': product['price_cents'],
                },
                'quantity': 1,
            }],
            mode='payment',
            allow_promotion_codes=True,
            success_url=success_url + f'?pack_id={pack.id}',
            cancel_url=cancel_url,
            metadata={
                'pack_id': str(pack.id),
                'user_id': str(user.id),
                'product_id': product['id'],
            },
            customer_email=user.email if user.email else None,
        )

        # Store session ID in pack
        pack.stripe_payment_intent_id = session.id
        pack.save(update_fields=['stripe_payment_intent_id'])

        logger.info(f"Created checkout session {session.id} for pack {pack.id}")
        return session.id, session.url

    @classmethod
    def handle_checkout_completed(cls, session):
        """
        Handle successful checkout - fulfill the order.

        Args:
            session: Stripe Session object from webhook
        """
        pack_id = session.get('metadata', {}).get('pack_id')
        if not pack_id:
            logger.error("No pack_id in session metadata")
            return

        try:
            pack = QRPack.objects.get(id=pack_id)
        except QRPack.DoesNotExist:
            logger.error(f"Pack {pack_id} not found")
            return

        # Idempotency check - don't fulfill twice
        if pack.status in ['paid', 'fulfilled']:
            logger.info(f"Pack {pack_id} already processed, skipping")
            return

        # Update pack status
        pack.status = 'paid'
        pack.paid_at = timezone.now()
        pack.save(update_fields=['status', 'paid_at'])

        logger.info(f"Pack {pack_id} marked as paid, starting fulfillment")

        # Fulfill the order (create stones and PDF)
        cls._fulfill_pack(pack)

    @classmethod
    def _fulfill_pack(cls, pack):
        """
        Create stones and generate PDF for the pack.

        Args:
            pack: QRPack instance
        """
        from .shop_utils import get_product_config
        from .pdf_service import PDFService

        # Determine pack size from config
        product = get_product_config(pack.pack_type)
        pack_size = product.get('pack_size', 10) if product else 10

        # Create unclaimed stones
        stones = []
        for i in range(pack_size):
            temp_name = f'UNCLAIMED-{uuid_lib.uuid4().hex[:8].upper()}'
            stone = Stone.objects.create(
                PK_stone=temp_name,
                FK_pack=pack,
                FK_user=None,
                status='unclaimed',
            )
            # Generate QR code for each stone
            QRCodeService.generate_qr_for_stone(stone)
            stones.append(stone)
            logger.debug(f"Created stone {stone.PK_stone} for pack {pack.id}")

        # Generate PDF for multi-packs
        if pack_size > 1:
            try:
                PDFService.generate_pack_pdf(pack, stones)
                pack.pdf_generated = True
            except Exception as e:
                logger.error(f"Failed to generate PDF for pack {pack.id}: {e}")

        # Update pack status
        pack.status = 'fulfilled'
        pack.fulfilled_at = timezone.now()
        pack.save(update_fields=['pdf_generated', 'status', 'fulfilled_at'])

        logger.info(f"Fulfilled pack {pack.id} with {len(stones)} stones")

    @classmethod
    def _get_or_create_stripe_customer(cls, user):
        """Get or create a Stripe Customer for the user."""
        from accounts.models import Subscription
        cls._init_stripe()

        # Check if user already has a subscription with a customer ID
        try:
            sub = user.subscription
            if sub.stripe_customer_id:
                return sub.stripe_customer_id
        except Subscription.DoesNotExist:
            pass

        # Create new Stripe Customer
        customer = stripe.Customer.create(
            email=user.email,
            metadata={'user_id': str(user.id), 'username': user.username},
        )
        return customer.id

    @classmethod
    def create_subscription_checkout(cls, user, product, success_url, cancel_url):
        """
        Create a Stripe Checkout Session for a subscription product.

        Args:
            user: Django User instance
            product: Product dict from shop_config.json (must have is_subscription=True)
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel

        Returns:
            tuple: (session_id, checkout_url)
        """
        cls._init_stripe()

        billing_interval = product.get('billing_interval', 'month')
        price_id_fn = SUBSCRIPTION_PRICE_MAP.get(billing_interval)
        price_id = price_id_fn() if price_id_fn else ''

        if not price_id:
            raise ValueError(
                f"No Stripe Price ID configured for interval '{billing_interval}'. "
                f"Set STRIPE_PRICE_MONTHLY or STRIPE_PRICE_YEARLY in environment."
            )

        customer_id = cls._get_or_create_stripe_customer(user)

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            allow_promotion_codes=True,
            success_url=success_url + f'?subscription=1',
            cancel_url=cancel_url,
            metadata={
                'user_id': str(user.id),
                'product_id': product['id'],
                'plan': 'yearly' if billing_interval == 'year' else 'monthly',
            },
        )

        logger.info(f"Created subscription checkout {session.id} for user {user.id}")
        return session.id, session.url

    @classmethod
    def create_billing_portal_session(cls, user, return_url):
        """
        Create a Stripe Billing Portal session so the user can manage their subscription.

        Args:
            user: Django User instance
            return_url: URL to redirect after portal session

        Returns:
            str: Portal session URL
        """
        from accounts.models import Subscription
        cls._init_stripe()

        try:
            sub = user.subscription
            if not sub.stripe_customer_id:
                raise ValueError("No Stripe customer ID found")
        except Subscription.DoesNotExist:
            raise ValueError("No subscription found")

        portal_session = stripe.billing_portal.Session.create(
            customer=sub.stripe_customer_id,
            return_url=return_url,
        )
        return portal_session.url

    @classmethod
    def handle_subscription_event(cls, event_type, event_object):
        """
        Handle Stripe subscription lifecycle events.

        Args:
            event_type: Stripe event type string
            event_object: Event data object
        """
        from accounts.models import Subscription

        if event_type == 'customer.subscription.created':
            cls._handle_subscription_created(event_object)
        elif event_type == 'customer.subscription.updated':
            cls._handle_subscription_updated(event_object)
        elif event_type == 'customer.subscription.deleted':
            cls._handle_subscription_deleted(event_object)
        elif event_type == 'invoice.payment_failed':
            cls._handle_invoice_payment_failed(event_object)

    @classmethod
    def _handle_subscription_created(cls, stripe_sub):
        """Handle new subscription creation from webhook."""
        from accounts.models import Subscription
        from django.contrib.auth.models import User

        customer_id = stripe_sub.get('customer', '')
        stripe_sub_id = stripe_sub.get('id', '')
        status = stripe_sub.get('status', 'incomplete')

        # Determine plan from price interval
        items = stripe_sub.get('items', {}).get('data', [])
        interval = 'month'
        if items:
            interval = items[0].get('price', {}).get('recurring', {}).get('interval', 'month')
        plan = 'yearly' if interval == 'year' else 'monthly'

        # Find user by customer ID (check existing subs) or by metadata
        user = None
        existing_sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
        if existing_sub:
            user = existing_sub.user
        else:
            metadata = stripe_sub.get('metadata', {})
            user_id = metadata.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(id=int(user_id))
                except (User.DoesNotExist, ValueError):
                    pass

        if not user:
            logger.error(f"Cannot find user for subscription {stripe_sub_id}")
            return

        period_start = stripe_sub.get('current_period_start')
        period_end = stripe_sub.get('current_period_end')

        sub, created = Subscription.objects.update_or_create(
            user=user,
            defaults={
                'stripe_customer_id': customer_id,
                'stripe_subscription_id': stripe_sub_id,
                'plan': plan,
                'status': status,
                'current_period_start': datetime.fromtimestamp(period_start, tz=dt_tz.utc) if period_start else None,
                'current_period_end': datetime.fromtimestamp(period_end, tz=dt_tz.utc) if period_end else None,
            }
        )
        logger.info(f"{'Created' if created else 'Updated'} subscription for user {user.id}: {status}")

    @classmethod
    def _handle_subscription_updated(cls, stripe_sub):
        """Handle subscription update (plan change, renewal, cancellation schedule)."""
        from accounts.models import Subscription

        stripe_sub_id = stripe_sub.get('id', '')
        status = stripe_sub.get('status', '')
        cancel_at_period_end = stripe_sub.get('cancel_at_period_end', False)

        try:
            sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
        except Subscription.DoesNotExist:
            # Might be a new sub via update event — delegate to created handler
            cls._handle_subscription_created(stripe_sub)
            return

        period_start = stripe_sub.get('current_period_start')
        period_end = stripe_sub.get('current_period_end')

        sub.status = status
        if period_start:
            sub.current_period_start = datetime.fromtimestamp(period_start, tz=dt_tz.utc)
        if period_end:
            sub.current_period_end = datetime.fromtimestamp(period_end, tz=dt_tz.utc)
        if cancel_at_period_end:
            sub.canceled_at = timezone.now()
        elif sub.canceled_at and not cancel_at_period_end:
            # User resubscribed
            sub.canceled_at = None
        sub.save()
        logger.info(f"Updated subscription {stripe_sub_id}: status={status}")

    @classmethod
    def _handle_subscription_deleted(cls, stripe_sub):
        """Handle subscription cancellation (end of billing period)."""
        from accounts.models import Subscription

        stripe_sub_id = stripe_sub.get('id', '')
        try:
            sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
            sub.status = 'canceled'
            sub.canceled_at = timezone.now()
            sub.save(update_fields=['status', 'canceled_at', 'updated_at'])
            logger.info(f"Subscription {stripe_sub_id} canceled for user {sub.user.id}")
        except Subscription.DoesNotExist:
            logger.warning(f"Subscription {stripe_sub_id} not found for deletion")

    @classmethod
    def _handle_invoice_payment_failed(cls, invoice):
        """Handle failed invoice payment — mark subscription past_due."""
        from accounts.models import Subscription

        stripe_sub_id = invoice.get('subscription', '')
        if not stripe_sub_id:
            return

        try:
            sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
            sub.status = 'past_due'
            sub.save(update_fields=['status', 'updated_at'])
            logger.info(f"Subscription {stripe_sub_id} marked past_due due to failed payment")
        except Subscription.DoesNotExist:
            logger.warning(f"Subscription {stripe_sub_id} not found for payment failure")

    @classmethod
    def handle_payment_failed(cls, session):
        """
        Handle failed payment.

        Args:
            session: Stripe Session object from webhook
        """
        pack_id = session.get('metadata', {}).get('pack_id')
        if not pack_id:
            return

        try:
            pack = QRPack.objects.get(id=pack_id)
            pack.status = 'failed'
            pack.save(update_fields=['status'])
            logger.info(f"Pack {pack_id} marked as failed")
        except QRPack.DoesNotExist:
            logger.error(f"Pack {pack_id} not found for failed payment")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhooks.

    Endpoint: /webhooks/stripe/

    Verifies webhook signature and processes events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        logger.warning("Missing Stripe signature header")
        return HttpResponse(status=400)

    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    # In development without webhook secret, allow unverified requests
    if not webhook_secret:
        logger.warning("STRIPE_WEBHOOK_SECRET not set - webhook verification disabled")
        try:
            import json
            event = json.loads(payload)
        except Exception as e:
            logger.error(f"Invalid JSON payload: {e}")
            return HttpResponse(status=400)
    else:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return HttpResponse(status=400)

    # Handle the event
    event_type = event.get('type', '')
    event_object = event.get('data', {}).get('object', {})

    if event_type == 'checkout.session.completed':
        # Check if this is a subscription or one-time payment
        if event_object.get('mode') == 'subscription':
            # Subscription checkout completed — the actual subscription is handled
            # by customer.subscription.created event
            logger.info(f"Subscription checkout completed: {event_object.get('id')}")
        else:
            StripeService.handle_checkout_completed(event_object)
    elif event_type == 'checkout.session.expired':
        StripeService.handle_payment_failed(event_object)
    elif event_type in (
        'customer.subscription.created',
        'customer.subscription.updated',
        'customer.subscription.deleted',
        'invoice.payment_failed',
    ):
        StripeService.handle_subscription_event(event_type, event_object)
    else:
        logger.debug(f"Unhandled event type: {event_type}")

    return HttpResponse(status=200)
