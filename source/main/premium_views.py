"""
Premium Supporter Views
Handles subscription landing page, checkout, management, and billing portal.
"""
import logging
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.conf import settings
from django.urls import reverse
from functools import wraps

from .shop_utils import get_product_config

logger = logging.getLogger(__name__)


def premium_required(view_func):
    """Decorator that requires the user to have an active premium subscription."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not request.user.profile.is_premium:
            messages.info(request, _('This feature requires a Premium Supporter subscription.'))
            return redirect('premium')
        return view_func(request, *args, **kwargs)
    return _wrapped


class PremiumRequiredMixin(LoginRequiredMixin):
    """Mixin that requires an active premium subscription."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.profile.is_premium:
            messages.info(request, _('This feature requires a Premium Supporter subscription.'))
            return redirect('premium')
        return super().dispatch(request, *args, **kwargs)


class PremiumView(TemplateView):
    """Premium supporter landing/marketing page with subscription options."""
    template_name = 'main/premium.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        monthly = get_product_config('premium_monthly')
        yearly = get_product_config('premium_yearly')

        context['monthly_plan'] = monthly
        context['yearly_plan'] = yearly
        context['features'] = monthly.get('features', []) if monthly else []

        # Check if user already has a subscription
        if self.request.user.is_authenticated:
            try:
                sub = self.request.user.subscription
                context['subscription'] = sub
                context['is_premium'] = sub.grants_premium
            except Exception:
                context['subscription'] = None
                context['is_premium'] = False
        else:
            context['subscription'] = None
            context['is_premium'] = False

        # Premium pricing is hidden until the community reaches SHOP_VISIBLE_USER_THRESHOLD
        # users. Before that, early users get lifetime premium for free (no need to show
        # prices). After the threshold, the features list is still shown but now with
        # pricing cards and subscribe buttons. This prevents confusion during early growth
        # when all users get premium automatically.
        from django.contrib.auth.models import User
        threshold = getattr(settings, 'SHOP_VISIBLE_USER_THRESHOLD', 1000)
        user_count = User.objects.count()
        context['show_pricing'] = user_count >= threshold

        context['stripe_public_key'] = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
        return context


class PremiumCheckoutView(LoginRequiredMixin, View):
    """Handle premium subscription checkout."""

    def post(self, request):
        plan = request.POST.get('plan', 'monthly')
        product_id = f'premium_{plan}'
        product = get_product_config(product_id)

        if not product:
            messages.error(request, _('Invalid plan selected.'))
            return redirect('premium')

        # Check if user already has an active subscription
        try:
            existing = request.user.subscription
            if existing.grants_premium:
                messages.info(request, _('You already have an active subscription. Manage it below.'))
                return redirect('premium_manage')
        except Exception:
            pass

        # Check Stripe configuration
        if not settings.STRIPE_SECRET_KEY:
            messages.error(request, _('Payment system is not configured. Please contact support.'))
            return redirect('premium')

        from .stripe_service import StripeService

        success_url = request.build_absolute_uri(reverse('premium_manage'))
        cancel_url = request.build_absolute_uri(reverse('premium'))

        try:
            session_id, checkout_url = StripeService.create_subscription_checkout(
                request.user, product, success_url, cancel_url
            )
            return redirect(checkout_url)
        except ValueError as e:
            logger.error(f"Subscription checkout config error: {e}")
            messages.error(request, _('Payment system is not fully configured. Please contact support.'))
            return redirect('premium')
        except Exception as e:
            logger.error(f"Failed to create subscription checkout: {e}")
            messages.error(request, _('Payment error. Please try again.'))
            return redirect('premium')


class PremiumManageView(LoginRequiredMixin, TemplateView):
    """Subscription management page — status, cancel, resubscribe."""
    template_name = 'main/premium_manage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            sub = self.request.user.subscription
            context['subscription'] = sub
            context['is_premium'] = sub.grants_premium
        except Exception:
            context['subscription'] = None
            context['is_premium'] = False

        return context


class PremiumBillingPortalView(LoginRequiredMixin, View):
    """Redirect to Stripe Billing Portal for subscription management."""

    def post(self, request):
        from .stripe_service import StripeService

        return_url = request.build_absolute_uri(reverse('premium_manage'))

        try:
            portal_url = StripeService.create_billing_portal_session(request.user, return_url)
            return redirect(portal_url)
        except ValueError as e:
            messages.error(request, _('No active subscription found.'))
            return redirect('premium')
        except Exception as e:
            logger.error(f"Failed to create billing portal session: {e}")
            messages.error(request, _('Could not open billing portal. Please try again.'))
            return redirect('premium_manage')
