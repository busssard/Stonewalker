"""
Stripe Payment Service for the Shop.
Handles Stripe Checkout Sessions and webhook processing.
"""
import stripe
import uuid as uuid_lib
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import QRPack, Stone
from .qr_service import QRCodeService

logger = logging.getLogger(__name__)


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

    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        StripeService.handle_checkout_completed(session)
    elif event_type == 'checkout.session.expired':
        session = event['data']['object']
        StripeService.handle_payment_failed(session)
    else:
        logger.debug(f"Unhandled event type: {event_type}")

    return HttpResponse(status=200)
