from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.views.generic import TemplateView

from main.views import IndexPageView, ChangeLanguageView
from main.views import StoneWalkerStartPageView
from main.views import debug_add_stone
from main.views import MyStonesView
from main.views import add_stone, StoneScanView, check_stone_name
from main.views import StoneQRCodeView, StoneLinkView, check_stone_uuid, StoneEditView, StoneSendOffView, generate_qr_code_api, download_enhanced_qr_code

# Shop views
from main.shop_views import (
    ShopView, ClaimStoneView, CheckoutView,
    CheckoutSuccessView, DownloadPackPDFView, FreeQRView, DownloadStoneQRView
)
from main.stripe_service import stripe_webhook

# URLs that should not have language prefix
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    # API endpoints should not have language prefix
    path('api/generate-qr/', generate_qr_code_api, name='generate_qr_api'),
    path('api/download-enhanced-qr/', download_enhanced_qr_code, name='download_enhanced_qr'),
    path('api/check-stone-uuid/<str:uuid>/', check_stone_uuid, name='check_stone_uuid'),
    path('api/check_stone_name/', check_stone_name, name='check_stone_name'),
    # Stripe webhook (no language prefix, no CSRF)
    path('webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
]

# URLs that should have language prefix
urlpatterns += i18n_patterns(
    path('', StoneWalkerStartPageView.as_view(), name='index'),
    # path('', IndexPageView.as_view(), name='index'),
    path('stonewalker/', StoneWalkerStartPageView.as_view(), name='stonewalker_start'),
    path('debug/add_stone/', debug_add_stone, name='debug_add_stone'),

    path('my-stones/', MyStonesView.as_view(), name='my_stones'),
    path('add_stone/', add_stone, name='add_stone'),
    path('stonescan/', StoneScanView.as_view(), name='stone_scan'),
    path('forum/', TemplateView.as_view(template_name='main/forum.html'), name='forum'),

    # Shop URLs
    path('shop/', ShopView.as_view(), name='shop'),
    path('shop/checkout/<str:product_id>/', CheckoutView.as_view(), name='checkout'),
    path('shop/success/', CheckoutSuccessView.as_view(), name='checkout_success'),
    path('shop/download/<uuid:pack_id>/', DownloadPackPDFView.as_view(), name='download_pack_pdf'),
    path('shop/download-qr/<str:stone_uuid>/', DownloadStoneQRView.as_view(), name='download_stone_qr'),
    path('shop/free-qr/', FreeQRView.as_view(), name='free_qr'),

    # Stone claiming
    path('claim-stone/<str:stone_uuid>/', ClaimStoneView.as_view(), name='claim_stone'),

    path('about/', TemplateView.as_view(template_name='main/about.html'), name='about'),
    # New stone management URLs
    path('stone/<str:pk>/edit/', StoneEditView.as_view(), name='stone_edit'),
    path('stone/<str:pk>/qr/', StoneQRCodeView.as_view(), name='stone_qr'),
    path('stone/<str:pk>/send-off/', StoneSendOffView.as_view(), name='stone_send_off'),
    
    # Stone-link functionality
    path('stone-link/<str:stone_uuid>/', StoneLinkView.as_view(), name='stone_link'),
    
    # Debug and test pages
    path('debug/modals/', TemplateView.as_view(template_name='main/debug_modals.html'), name='debug_modals'),
    path('qr-test/', TemplateView.as_view(template_name='main/qr_test.html'), name='qr_test'),

    path('language/', ChangeLanguageView.as_view(), name='change_language'),

    path('accounts/', include('accounts.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
