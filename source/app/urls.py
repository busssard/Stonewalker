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
from main.views import StoneQRCodeView, download_qr_code

# URLs that should not have language prefix
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
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
    path('api/check_stone_name/', check_stone_name, name='check_stone_name'),
    path('forum/', TemplateView.as_view(template_name='main/forum.html'), name='forum'),
    path('shop/', TemplateView.as_view(template_name='main/shop.html'), name='shop'),
    path('about/', TemplateView.as_view(template_name='main/about.html'), name='about'),
    path('stone/<str:pk>/qr/', StoneQRCodeView.as_view(), name='stone_qr'),
    path('download-qr/', download_qr_code, name='download_qr'),

    path('language/', ChangeLanguageView.as_view(), name='change_language'),

    path('accounts/', include('accounts.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
