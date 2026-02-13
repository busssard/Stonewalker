"""
Shop and Stone Claiming Views
"""
import uuid as uuid_lib
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils.translation import gettext as _
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
import re
import logging

from .models import Stone, QRPack
from .qr_service import QRCodeService
from .shop_utils import get_enabled_products, get_product_config, get_categories, format_price

logger = logging.getLogger(__name__)


class CreateNewStoneView(LoginRequiredMixin, View):
    """Smart router: checks for unclaimed QR codes and directs user accordingly.

    - If user has an unclaimed stone from a purchased pack → redirect to claim it
    - Otherwise → auto-create a free QR and redirect to claim page
    """

    def get(self, request):
        # Find unclaimed stones belonging to the user's packs
        user_packs = QRPack.objects.filter(FK_user=request.user, status='fulfilled')
        for pack in user_packs:
            unclaimed_stone = pack.stones.filter(status='unclaimed').first()
            if unclaimed_stone:
                return redirect('claim_stone', stone_uuid=str(unclaimed_stone.uuid))

        # No unclaimed stones: provision a free single QR automatically
        free_product = get_product_config('free_single')
        if not free_product or not free_product.get('enabled', True):
            messages.error(request, _('Free QR codes are currently unavailable.'))
            return redirect('shop')

        pack = QRPack.objects.create(
            FK_user=request.user,
            pack_type=free_product['id'],
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
        QRCodeService.generate_qr_for_stone(stone, request)
        messages.success(request, _('Your free QR code is ready. Name your new stone now.'))
        return redirect('claim_stone', stone_uuid=str(stone.uuid))


class ClaimStoneView(LoginRequiredMixin, View):
    """Handle claiming an unclaimed stone"""
    template_name = 'main/claim_stone.html'

    def get(self, request, stone_uuid):
        """Show the claim stone form"""
        try:
            uuid_obj = uuid_lib.UUID(stone_uuid)
            stone = Stone.objects.get(uuid=uuid_obj)
        except (ValueError, Stone.DoesNotExist):
            messages.error(request, _('Stone not found.'))
            return redirect('stonewalker_start')

        if not stone.can_be_claimed():
            messages.error(request, _('This stone has already been claimed.'))
            return redirect('stone_link', stone_uuid=stone_uuid)

        return render(request, self.template_name, {
            'stone': stone,
            'stone_uuid': stone_uuid,
        })

    def post(self, request, stone_uuid):
        """Process the claim stone form"""
        try:
            uuid_obj = uuid_lib.UUID(stone_uuid)
            stone = Stone.objects.get(uuid=uuid_obj)
        except (ValueError, Stone.DoesNotExist):
            messages.error(request, _('Stone not found.'))
            return redirect('stonewalker_start')

        if not stone.can_be_claimed():
            messages.error(request, _('This stone has already been claimed.'))
            return redirect('stone_link', stone_uuid=stone_uuid)

        # Get form data
        stone_name = request.POST.get('stone_name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')

        # Validate description content
        from .validators import validate_no_contact_info
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            validate_no_contact_info(description)
        except DjangoValidationError as e:
            messages.error(request, e.message)
            return render(request, self.template_name, {
                'stone': stone,
                'stone_uuid': stone_uuid,
                'stone_name': stone_name,
                'description': description,
            })

        # Validate stone name
        errors = []

        if not stone_name:
            errors.append(_('Please enter a name for your stone.'))
        elif len(stone_name) > 10:
            errors.append(_('Stone name must be 10 characters or less.'))
        elif re.search(r'\s', stone_name):
            errors.append(_('Stone name cannot contain spaces.'))
        elif Stone.objects.filter(PK_stone=stone_name).exists():
            errors.append(_('This stone name is already taken. Please choose another.'))

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, self.template_name, {
                'stone': stone,
                'stone_uuid': stone_uuid,
                'stone_name': stone_name,
                'description': description,
            })

        # Claim the stone
        old_pk = stone.PK_stone  # Store old PK before changing

        # We need to handle the PK change carefully - create new stone and delete old
        try:
            # Update the stone fields
            stone.FK_user = request.user
            stone.status = 'draft'
            stone.claimed_at = timezone.now()
            stone.description = description[:500] if description else ''
            if image:
                stone.image = image

            # Handle PK change by deleting old and creating with new PK
            if old_pk != stone_name:
                # Get all the values we need
                stone_data = {
                    'uuid': stone.uuid,
                    'description': stone.description,
                    'FK_user': stone.FK_user,
                    'FK_pack': stone.FK_pack,
                    'image': stone.image,
                    'color': stone.color,
                    'shape': stone.shape,
                    'distance_km': stone.distance_km,
                    'stone_type': stone.stone_type,
                    'status': 'draft',
                    'qr_code_url': stone.qr_code_url,
                    'claimed_at': timezone.now(),
                }

                # Delete the old stone
                Stone.objects.filter(PK_stone=old_pk).delete()

                # Create with new PK
                stone = Stone.objects.create(PK_stone=stone_name, **stone_data)
            else:
                stone.save()

            # Regenerate QR code with new name
            QRCodeService.generate_qr_for_stone(stone, request)

            messages.success(
                request,
                _('Congratulations! You claimed "%(name)s"! You can now edit and personalize your stone.') % {'name': stone_name}
            )
            return redirect('stone_edit', pk=stone_name)

        except Exception as e:
            logger.error(f"Error claiming stone {stone_uuid}: {str(e)}")
            messages.error(request, _('An error occurred while claiming the stone. Please try again.'))
            return render(request, self.template_name, {
                'stone': stone,
                'stone_uuid': stone_uuid,
                'stone_name': stone_name,
                'description': description,
            })


class ShopView(TemplateView):
    """Main shop page showing products from config"""
    template_name = 'main/shop.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dev_mode = getattr(settings, 'DEBUG', False)

        # Load products from config
        products = get_enabled_products()
        categories = get_categories()

        selected_category = self.request.GET.get('category', '').strip()
        selected_type = self.request.GET.get('type', '').strip()

        # Enhance products with user-specific info
        enhanced_products = []
        for product in products:
            enhanced = product.copy()

            # Free single QR is always unlimited to grow the user base
            if enhanced.get('id') == 'free_single':
                enhanced['limit_per_user'] = None

            # Check user limits
            if self.request.user.is_authenticated:
                limit = enhanced.get('limit_per_user')
                if limit:
                    user_count = QRPack.objects.filter(
                        FK_user=self.request.user,
                        pack_type=product['id'],
                        status__in=['paid', 'fulfilled']
                    ).count()
                    enhanced['disabled'] = user_count >= limit
                    enhanced['disabled_reason'] = _(
                        'You have already claimed this product'
                    ) if user_count >= limit else None
                else:
                    enhanced['disabled'] = False
                    enhanced['disabled_reason'] = None
            else:
                enhanced['disabled'] = False
                enhanced['disabled_reason'] = None

            # Format price display
            if enhanced.get('is_free'):
                enhanced['price_display'] = _('Free')
            else:
                enhanced['price_display'] = format_price(enhanced.get('price_cents', 0))

            # Calculate per-unit price for multi-packs
            pack_size = enhanced.get('pack_size', 1)
            if pack_size > 1 and not enhanced.get('is_free'):
                per_unit_cents = enhanced.get('price_cents', 0) // pack_size
                enhanced['price_per_unit'] = format_price(per_unit_cents)
            else:
                enhanced['price_per_unit'] = ''

            enhanced_products.append(enhanced)

        if selected_category:
            enhanced_products = [
                product for product in enhanced_products
                if product.get('category') == selected_category
            ]
        if selected_type:
            enhanced_products = [
                product for product in enhanced_products
                if product.get('type') == selected_type
            ]

        all_products = get_enabled_products()
        filter_categories = sorted({p.get('category') for p in all_products if p.get('category')})
        filter_types = sorted({p.get('type') for p in all_products if p.get('type')})

        context['products'] = enhanced_products
        context['product_count'] = len(enhanced_products)
        context['total_product_count'] = len(all_products)
        context['filter_categories'] = filter_categories
        context['filter_types'] = filter_types
        context['selected_category'] = selected_category
        context['selected_type'] = selected_type
        context['categories'] = categories
        context['stripe_public_key'] = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
        context['dev_mode'] = dev_mode

        # Add user's existing packs for re-download
        if self.request.user.is_authenticated:
            user_packs = QRPack.objects.filter(
                FK_user=self.request.user,
                status='fulfilled'
            ).prefetch_related('stones')
            context['user_packs'] = user_packs

        return context


class CheckoutView(LoginRequiredMixin, View):
    """Handle checkout for a product"""

    def post(self, request, product_id):
        product = get_product_config(product_id)

        if not product:
            messages.error(request, _('Product not found.'))
            return redirect('shop')

        if not product.get('enabled', True):
            messages.error(request, _('This product is not available.'))
            return redirect('shop')

        # Check user limits (free_single is always unlimited)
        limit = product.get('limit_per_user')
        if product_id == 'free_single':
            limit = None
        if limit:
            user_count = QRPack.objects.filter(
                FK_user=request.user,
                pack_type=product_id,
                status__in=['paid', 'fulfilled']
            ).count()
            if user_count >= limit:
                messages.error(request, _('You have already claimed this product.'))
                return redirect('shop')

        # Free products - fulfill immediately
        if product.get('is_free'):
            return self._handle_free_product(request, product)

        # Paid products - create Stripe session
        from .stripe_service import StripeService

        # Check if Stripe is configured
        if not settings.STRIPE_SECRET_KEY:
            logger.error("Stripe secret key not configured")
            messages.error(request, _('Payment system is not configured. Please contact support.'))
            return redirect('shop')

        success_url = request.build_absolute_uri(reverse('checkout_success'))
        cancel_url = request.build_absolute_uri(reverse('shop'))

        try:
            session_id, checkout_url = StripeService.create_checkout_session(
                request.user, product, success_url, cancel_url
            )
            return redirect(checkout_url)
        except Exception as e:
            logger.error(f"Failed to create checkout session: {e}")
            messages.error(request, _('Payment system error. Please try again.'))
            return redirect('shop')

    def _handle_free_product(self, request, product):
        """Handle free product fulfillment"""
        pack = QRPack.objects.create(
            FK_user=request.user,
            pack_type=product['id'],
            status='fulfilled',
            price_cents=0,
            fulfilled_at=timezone.now(),
        )

        # Create unclaimed stone(s)
        pack_size = product.get('pack_size', 1)
        stones = []
        for i in range(pack_size):
            temp_name = f'UNCLAIMED-{uuid_lib.uuid4().hex[:8].upper()}'
            stone = Stone.objects.create(
                PK_stone=temp_name,
                FK_pack=pack,
                FK_user=None,
                status='unclaimed',
            )
            QRCodeService.generate_qr_for_stone(stone, request)
            stones.append(stone)

        # For single QR, download immediately
        if pack_size == 1:
            response = QRCodeService.create_download_response(stones[0], request)
            if response:
                messages.success(request, _(
                    'Your free QR code has been generated! Print it and attach it to your stone.'
                ))
                return response
        else:
            # For multi-pack, generate PDF
            from .pdf_service import PDFService
            PDFService.generate_pack_pdf(pack, stones)
            pack.pdf_generated = True
            pack.save(update_fields=['pdf_generated'])
            messages.success(request, _('Your QR codes are ready for download!'))
            return redirect(reverse('checkout_success') + f'?pack_id={pack.id}')

        messages.error(request, _('Failed to generate QR code.'))
        return redirect('shop')


class FreeQRView(LoginRequiredMixin, View):
    """Generate a free single QR code (legacy endpoint)"""

    def get(self, request):
        # Check if user already claimed free QR
        existing_free = QRPack.objects.filter(
            FK_user=request.user,
            pack_type='free_single'
        ).exists()

        if existing_free:
            messages.error(request, _('You have already claimed your free QR code.'))
            return redirect('shop')

        # Create pack and unclaimed stone
        pack = QRPack.objects.create(
            FK_user=request.user,
            pack_type='free_single',
            status='fulfilled',
            price_cents=0,
            fulfilled_at=timezone.now(),
        )

        # Create unclaimed stone with temporary name
        temp_name = f'UNCLAIMED-{uuid_lib.uuid4().hex[:8].upper()}'
        stone = Stone.objects.create(
            PK_stone=temp_name,
            FK_pack=pack,
            FK_user=None,  # No owner yet
            status='unclaimed',
        )

        # Generate QR code
        result = QRCodeService.generate_qr_for_stone(stone, request)

        if result.get('success'):
            # Return the QR code as download
            response = QRCodeService.create_download_response(stone, request)
            if response:
                messages.success(request, _('Your free QR code has been generated! Print it and attach it to your stone.'))
                return response

        messages.error(request, _('Failed to generate QR code. Please try again.'))
        return redirect('shop')


class DownloadPackPDFView(LoginRequiredMixin, View):
    """Download the PDF for a QR pack"""

    def get(self, request, pack_id):
        try:
            pack = QRPack.objects.get(id=pack_id, FK_user=request.user)
        except QRPack.DoesNotExist:
            messages.error(request, _('Pack not found.'))
            return redirect('shop')

        if not pack.pdf_generated:
            messages.error(request, _('PDF not yet generated.'))
            return redirect('shop')

        # Import here to avoid circular import
        from .pdf_service import PDFService
        response = PDFService.get_download_response(pack)

        if response:
            pack.download_count += 1
            pack.save(update_fields=['download_count'])
            return response

        messages.error(request, _('PDF file not found.'))
        return redirect('shop')


class DownloadStoneQRView(LoginRequiredMixin, View):
    """Download QR code for a single stone from a pack"""

    def get(self, request, stone_uuid):
        try:
            uuid_obj = uuid_lib.UUID(stone_uuid)
            stone = Stone.objects.get(uuid=uuid_obj)
        except (ValueError, Stone.DoesNotExist):
            messages.error(request, _('Stone not found.'))
            return redirect('shop')

        # Check if user owns the pack this stone belongs to
        if stone.FK_pack and stone.FK_pack.FK_user != request.user:
            messages.error(request, _('You do not have access to this QR code.'))
            return redirect('shop')

        # Generate QR if needed and return download
        response = QRCodeService.create_download_response(stone, request)
        if response:
            return response

        messages.error(request, _('Failed to generate QR code.'))
        return redirect('shop')


class CheckoutSuccessView(LoginRequiredMixin, TemplateView):
    """Handle successful checkout"""
    template_name = 'main/checkout_success.html'

    def get(self, request, *args, **kwargs):
        pack_id = request.GET.get('pack_id')

        if not pack_id:
            messages.error(request, _('Invalid checkout session.'))
            return redirect('shop')

        try:
            pack = QRPack.objects.get(id=pack_id, FK_user=request.user)
        except QRPack.DoesNotExist:
            messages.error(request, _('Order not found.'))
            return redirect('shop')

        # For paid packs, the webhook should have fulfilled it
        # For free packs, it's already fulfilled
        # Give a brief grace period for webhook processing
        if pack.status == 'pending':
            # Check if payment was actually completed via Stripe
            messages.info(request, _('Payment processing. Please refresh in a moment.'))

        # If paid but not yet fulfilled by webhook, fulfill now as fallback
        if pack.status == 'paid' and not pack.pdf_generated:
            self._generate_pack_pdf(pack)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pack_id = self.request.GET.get('pack_id')

        try:
            pack = QRPack.objects.get(id=pack_id, FK_user=self.request.user)
            context['pack'] = pack
            context['stones'] = pack.stones.all()
        except QRPack.DoesNotExist:
            pass

        return context

    def _generate_pack_pdf(self, pack):
        """Generate the PDF with QR codes for the pack (fallback if webhook didn't)"""
        from .pdf_service import PDFService
        from .shop_utils import get_product_config

        # Get pack size from config
        product = get_product_config(pack.pack_type)
        pack_size = product.get('pack_size', 10) if product else 10

        # Create unclaimed stones if none exist
        existing_stones = list(pack.stones.all())
        if not existing_stones:
            stones = []
            for i in range(pack_size):
                temp_name = f'UNCLAIMED-{uuid_lib.uuid4().hex[:8].upper()}'
                stone = Stone.objects.create(
                    PK_stone=temp_name,
                    FK_pack=pack,
                    FK_user=None,
                    status='unclaimed',
                )
                QRCodeService.generate_qr_for_stone(stone)
                stones.append(stone)
        else:
            stones = existing_stones

        # Generate PDF
        PDFService.generate_pack_pdf(pack, stones)
        pack.pdf_generated = True
        pack.status = 'fulfilled'
        pack.fulfilled_at = timezone.now()
        pack.save()
