from django.views.generic import TemplateView, DetailView
from .models import Stone, StoneMove, calculate_stone_distance, StoneScanAttempt, QRPack
import json
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Prefetch
import re
from math import radians, sin, cos, sqrt, atan2
import logging
logger = logging.getLogger(__name__)


# json.dumps output is inlined into <script> blocks with |safe; escape the
# characters that could close the tag or start markup (same as json_script).
_JSON_SCRIPT_ESCAPES = {ord('<'): '\\u003C', ord('>'): '\\u003E', ord('&'): '\\u0026'}


def _script_safe_json(data):
    return json.dumps(data).translate(_JSON_SCRIPT_ESCAPES)


# URL builders that keep the active language prefix (hardcoded '/stone/...'
# paths fall back to English under prefix_default_language=False).
def _map_focus_url(pk):
    return f"{reverse('stonewalker_start')}?{urllib.parse.urlencode({'focus': pk})}"


def _stone_edit_url(pk, key=None):
    url = reverse('stone_edit', kwargs={'pk': pk})
    return f'{url}?key={key}' if key else url


def _prepend_journey_origin(stone, moves_data):
    """Put a hidden stone's private hiding spot at the start of a public
    journey — only once it has confirmed finds (moves_data non-empty)."""
    origin = stone.journey_origin()
    if origin and moves_data:
        moves_data.insert(0, {
            'latitude': origin[0], 'longitude': origin[1],
            'timestamp': '', 'timestamp_display': '',
            'user': gettext('Hiding spot'), 'comment': '',
        })


def _is_stone_owner(request, stone):
    # Explicit: unclaimed stones (FK_user_id None) must not match anonymous
    # visitors (user.id None).
    return request.user.is_authenticated and stone.FK_user_id == request.user.id


def _parse_lat_lng(lat, lng):
    """Parse a lat/lng pair from form input; (None, None) if missing/invalid."""
    try:
        lat, lng = float(lat), float(lng)
    except (TypeError, ValueError):
        return None, None
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None, None
    return lat, lng


def _stone_link_key_url(stone):
    return f"{reverse('stone_link', kwargs={'stone_number': stone.stone_number})}?key={stone.uuid}"
import qrcode
from io import BytesIO
from django.http import HttpResponse
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import get_language, get_language_from_request, gettext
from django.conf import settings
from django.urls import reverse
import uuid as uuid_lib
import urllib.parse


class IndexPageView(TemplateView):
    template_name = 'main/index.html'


class ImpressumView(TemplateView):
    template_name = 'main/impressum.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import os
        json_path = os.path.join(os.path.dirname(__file__), 'impressum.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            context['impressum'] = json.load(f)
        return context


class PrivacyView(TemplateView):
    template_name = 'main/privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import os
        json_path = os.path.join(os.path.dirname(__file__), 'impressum.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            context['impressum'] = json.load(f)
        return context


class ChangeLanguageView(TemplateView):
    template_name = 'main/change_language.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Redirect back to the referring page after language change.
        # Using '/' as fallback if no referer is available.
        referer = self.request.META.get('HTTP_REFERER', '/')
        # Extract just the path to avoid open redirect issues
        from urllib.parse import urlparse
        parsed = urlparse(referer)
        redirect_to = parsed.path or '/'

        # Strip the language prefix from the redirect path so Django's set_language
        # can redirect to the correct URL with the new language prefix
        import re
        # Match language codes like /en/, /fr/, /es/, etc. at the start of the path
        redirect_to = re.sub(r'^/(en|ru|zh-hans|fr|es|de|it)/', '/', redirect_to)

        context['redirect_to'] = redirect_to
        return context


class StoneWalkerStartPageView(TemplateView):
    template_name = 'main/stonewalker_start.html'

    def get_client_ip(self):
        from .models import client_ip
        return client_ip(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all stones with related data pre-fetched to avoid N+1 queries
        stones = Stone.objects.select_related(
            'FK_user', 'FK_user__profile'
        ).prefetch_related(
            Prefetch(
                'moves',
                # Public map: confirmed finds only (new finds are confirmed at
                # once; is_confirmed=False remains only for legacy held finds).
                queryset=StoneMove.objects.filter(is_confirmed=True).order_by('timestamp').select_related(
                    'FK_user', 'FK_user__profile'
                ),
            ),
        ).all()
        # For each stone, get all moves ordered by timestamp
        stones_data = []
        logger.info(f"Calculating distances for {len(stones)} stones")
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in km
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        for stone in stones:
            # Use prefetched moves (already ordered by timestamp via Prefetch)
            moves = list(stone.moves.all())
            # Use the stored distance_km field for display
            total_distance = stone.distance_km
            if moves:
                # Latest move for marker
                latest_move = moves[-1]
                # Hidden stones: the private hiding spot becomes the start of
                # the line once there is a confirmed find (never before).
                origin = stone.journey_origin()
                stones_data.append({
                    'PK_stone': stone.PK_stone,
                    'uuid': str(stone.uuid),
                    'description': stone.description,
                    'created_at': stone.created_at.isoformat(),
                    'user': stone.FK_user.username,
                    'user_picture': stone.FK_user.profile.get_picture_url(),
                    'image': stone.image.url if stone.image else '',
                    'color': stone.color,
                    'shape': stone.shape,
                    'stone_type': stone.stone_type,
                    'latest_latitude': latest_move.latitude,
                    'latest_longitude': latest_move.longitude,
                    'latest_image': latest_move.image.url if latest_move.image else '',
                    'distance_km': round(total_distance, 1),
                    'origin': {'latitude': origin[0], 'longitude': origin[1]} if origin else None,
                    'moves': [
                        {
                            'latitude': m.latitude,
                            'longitude': m.longitude,
                            'timestamp': m.timestamp.isoformat() if m.timestamp else '',
                            'timestamp_display': m.timestamp.strftime('%b %d, %Y') if m.timestamp else '',
                            'image': m.image.url if m.image else '',
                            'comment': m.comment,
                            'user': m.FK_user.username,
                            'user_picture': m.FK_user.profile.get_picture_url(),
                        } for m in moves
                    ]
                })
        context['stones_json'] = _script_safe_json(stones_data)
        # Welcome modal logic (IP/session based)
        show_welcome_modal = False
        if not self.request.user.is_authenticated:
            ip = self.get_client_ip()
            last_visit = self.request.session.get(f'last_visit_{ip}')
            now = timezone.now().timestamp()
            if not last_visit or now - last_visit > 3600:
                show_welcome_modal = True
                self.request.session[f'last_visit_{ip}'] = now
        context['show_welcome_modal'] = show_welcome_modal
        return context


class MyStonesView(LoginRequiredMixin, TemplateView):
    template_name = 'main/my_stones.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        my_stones = Stone.objects.filter(FK_user=user).select_related(
            'FK_user', 'FK_user__profile'
        ).prefetch_related('moves')
        for stone in my_stones:
            stone.distance_km = round(stone.distance_km, 1)
        context['my_stones'] = my_stones
        # Owned stones with finds waiting on the finder's email confirmation
        context['stones_with_held_finds'] = Stone.objects.filter(
            FK_user=user, moves__is_confirmed=False
        ).distinct()

        # Unclaimed QR codes from user's packs
        unclaimed_stones = Stone.objects.filter(
            FK_pack__FK_user=user,
            status='unclaimed',
        ).select_related('FK_pack')
        context['unclaimed_stones'] = unclaimed_stones
        context['has_unclaimed'] = unclaimed_stones.exists()

        # Fulfilled packs for re-downloading QR codes / pack PDFs
        context['user_packs'] = QRPack.objects.filter(
            FK_user=user, status='fulfilled'
        ).prefetch_related('stones')

        # Stones where user has moved but is not the creator
        moved_stone_ids = StoneMove.objects.filter(FK_user=user).exclude(FK_stone__FK_user=user).values_list('FK_stone', flat=True).distinct()
        my_interactions = Stone.objects.filter(PK_stone__in=moved_stone_ids).select_related(
            'FK_user', 'FK_user__profile'
        ).prefetch_related('moves')
        for stone in my_interactions:
            stone.distance_km = round(stone.distance_km, 1)
        context['my_interactions'] = my_interactions
        return context




@login_required
def add_stone(request):
    """Deprecated: redirects to the shop-based stone creation flow.

    Stone creation now goes through: create-stone → shop → checkout → claim.
    This endpoint is kept for backwards compatibility with old bookmarks/links.
    """
    # Check terms acceptance before allowing stone creation
    if not hasattr(request.user, 'terms_acceptance'):
        messages.error(request, 'You must accept the Terms of Use before creating a stone.')
        return redirect('terms')
    messages.info(request, 'Stone creation now goes through the shop. Please use the button below to create a stone.')
    return redirect('create_stone')


def check_stone_name(request):
    PK_stone = request.GET.get('PK_stone', '').strip()
    if not PK_stone:
        # fallback for legacy 'name' param
        PK_stone = request.GET.get('name', '').strip()
    from django.core.exceptions import ValidationError as DjangoValidationError
    from .validators import validate_stone_name
    taken = False
    reason = None
    try:
        validate_stone_name(PK_stone)
    except DjangoValidationError as e:
        taken = True
        reason = e.code  # empty / too_long / whitespace / invalid_chars
    else:
        if Stone.objects.filter(PK_stone=PK_stone).exists():
            taken = True
            reason = 'taken'
    return JsonResponse({'taken': taken, 'reason': reason, 'PK_stone': PK_stone})


def check_stone_uuid(request, uuid):
    """Check if a UUID exists in the database"""
    uuid_param = uuid.strip()
    
    if not uuid_param:
        return JsonResponse({'exists': False, 'error': 'No UUID provided'})
    
    try:
        # Validate UUID format
        uuid_obj = uuid_lib.UUID(uuid_param)
        exists = Stone.objects.filter(uuid=uuid_obj).exists()
        return JsonResponse({'exists': exists, 'uuid': uuid_param})
    except ValueError:
        return JsonResponse({'exists': False, 'error': 'Invalid UUID format'})


class StoneEditView(LoginRequiredMixin, TemplateView):
    template_name = 'main/stone_edit.html'
    
    @staticmethod
    def _last_minute_unlocked(request, stone):
        """Last-minute editing (published/sent-off, nobody else scanned yet) is
        unlocked only via the QR link's key — never by URL alone."""
        key = request.GET.get('key') or request.POST.get('key')
        if not key:
            return False
        try:
            if uuid_lib.UUID(key) != stone.uuid:
                return False
        except ValueError:
            return False
        return stone.can_last_minute_edit()

    def get(self, request, pk):
        try:
            stone = Stone.objects.get(PK_stone=pk, FK_user=request.user)
            last_minute = self._last_minute_unlocked(request, stone)
            # Allow viewing the edit page for all owned stones (template handles readonly)
            return render(request, self.template_name, {
                'stone': stone,
                'last_minute': last_minute,
                'editable': stone.can_be_edited() or last_minute,
                # Finds waiting on the finder's email confirmation; the owner
                # can approve them (StoneApproveFindView).
                'held_finds': stone.moves.filter(is_confirmed=False).select_related('FK_user').order_by('timestamp'),
            })
        except Stone.DoesNotExist:
            messages.error(request, 'Stone not found or you do not have permission to edit it.')
            return redirect('stonewalker_start')

    def post(self, request, pk):
        try:
            stone = Stone.objects.get(PK_stone=pk, FK_user=request.user)
            last_minute = self._last_minute_unlocked(request, stone)
            if not (stone.can_be_edited() or last_minute):
                messages.error(request, f'Stone "{stone.PK_stone}" cannot be edited because it has been {stone.status}.')
                return redirect('stonewalker_start')
            
            # Validate description content
            description = request.POST.get('description', '')[:500]
            from .validators import validate_no_contact_info
            from django.core.exceptions import ValidationError as DjangoValidationError
            try:
                validate_no_contact_info(description)
            except DjangoValidationError as e:
                messages.error(request, e.message)
                return redirect(_stone_edit_url(pk))

            # Update stone fields
            stone.description = description
            image = request.FILES.get('image')
            if image:
                stone.image = image
            color = request.POST.get('color', stone.color)
            if re.fullmatch(r'#[0-9a-fA-F]{6}', color or ''):
                stone.color = color
            # Type is fixed once sealed: the hiding spot was stored (hidden) or
            # published as a StoneMove (hunted) according to it.
            stone_type = request.POST.get('stone_type', stone.stone_type)
            if stone_type in ('hidden', 'hunted') and stone.status != 'wandering':
                stone.stone_type = stone_type
            
            action = request.POST.get('action')
            if action == 'save':
                stone.save()
                messages.success(request, f'Stone "{stone.PK_stone}" updated successfully!')
                if last_minute:
                    return redirect(_stone_edit_url(pk, stone.uuid))
                return redirect(_stone_edit_url(pk))
            elif action == 'publish':
                if stone.publish():
                    messages.success(request, f'Stone "{stone.PK_stone}" published successfully! It\'s now visible on the map.')
                    return redirect(_map_focus_url(pk))
                else:
                    messages.error(request, 'Could not publish stone.')
                    return redirect(_stone_edit_url(pk))
            messages.error(request, 'Unknown action.')
            return redirect(_stone_edit_url(pk))

        except Stone.DoesNotExist:
            messages.error(request, 'Stone not found or you do not have permission to edit it.')
            return redirect('stonewalker_start')
        except Exception as e:
            messages.error(request, f'Error updating stone: {str(e)}')
            return redirect(_stone_edit_url(pk))


class StoneApproveFindView(LoginRequiredMixin, View):
    """Owner approves a held find whose finder never confirmed their email,
    so it goes on the map (POST only)."""

    def post(self, request, pk, move_id):
        from .models import approve_held_find
        stone = get_object_or_404(Stone, PK_stone=pk, FK_user=request.user)
        move = get_object_or_404(StoneMove, pk=move_id, FK_stone=stone, is_confirmed=False)
        with transaction.atomic():
            approve_held_find(move)
        messages.success(request, gettext('Find approved — your stone is on the map.'))
        return redirect(_map_focus_url(stone.PK_stone))


class StoneQRCodeView(View):
    """Download QR code for a stone"""
    @method_decorator(login_required)
    def get(self, request, pk):
        try:
            stone = Stone.objects.get(PK_stone=pk, FK_user=request.user)
            if not stone.can_download_qr():
                messages.error(request, 'QR code download is not available for wandering stones.')
                return redirect('stone_edit', pk=pk)
            from .qr_service import QRCodeService
            response = QRCodeService.create_download_response(stone, request)
            if response:
                return response
            else:
                messages.error(request, 'Failed to generate QR code.')
                return redirect('stonewalker_start')
        except Stone.DoesNotExist:
            messages.error(request, 'Stone not found or you do not have permission to access it.')
            return redirect('stonewalker_start')


class StoneCertificateView(View):
    """Download a creation certificate for a stone"""
    @method_decorator(login_required)
    def get(self, request, pk):
        try:
            stone = Stone.objects.get(PK_stone=pk, FK_user=request.user)
            if not stone.can_download_certificate():
                messages.error(request, 'Certificate is only available after the stone has been sealed (wandering).')
                return redirect('stone_edit', pk=pk)
            from .certificate_service import CertificateService
            pdf_bytes = CertificateService.generate_certificate(stone)
            if pdf_bytes:
                response = HttpResponse(pdf_bytes, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{stone.PK_stone}_certificate.pdf"'
                return response
            else:
                messages.error(request, 'Failed to generate certificate.')
                return redirect('stonewalker_start')
        except Stone.DoesNotExist:
            messages.error(request, 'Stone not found or you do not have permission to access it.')
            return redirect('stonewalker_start')


class StoneSendOffView(View):
    """Seal a stone (start its journey). Reached from the scan confirm page's
    'Seal & start journey' button (a POST), so sealing is intentional and never
    happens on a bare GET/scan."""
    @method_decorator(login_required)
    def post(self, request, pk):
        try:
            stone = Stone.objects.get(PK_stone=pk, FK_user=request.user)
        except Stone.DoesNotExist:
            messages.error(request, 'Stone not found or you do not have permission to access it.')
            return redirect('stonewalker_start')

        if not stone.can_start_wandering():
            messages.info(request, "This stone can't be sealed right now.")
            return redirect('stone_edit', pk=pk)

        # Sealing without a picture must be a conscious choice.
        if not stone.image and not request.POST.get('confirm_no_image'):
            messages.error(request, "Your stone has no picture. Please confirm you want to let it roam without one.")
            return redirect(_stone_link_key_url(stone))

        # Where it's being hidden. Hidden stones keep this private until the
        # first confirmed find; hunted stones are meant to be searched for, so
        # their spot goes on the map right away (hunted requires it).
        lat, lng = _parse_lat_lng(request.POST.get('latitude'), request.POST.get('longitude'))
        if stone.stone_type == 'hunted' and lat is None:
            messages.error(request, 'Hunted stones need a location. Set where you are hiding it on the map.')
            return redirect(_stone_link_key_url(stone))

        with transaction.atomic():
            stone.hide_latitude, stone.hide_longitude = lat, lng
            stone.save(update_fields=['hide_latitude', 'hide_longitude'])
            stone.start_wandering()
            if stone.stone_type == 'hunted':
                StoneMove.objects.create(FK_stone=stone, FK_user=request.user, latitude=lat, longitude=lng)
            StoneScanAttempt.record_scan_attempt(stone, request.user, request)
        if stone.stone_type == 'hunted':
            messages.success(request, 'Your stone is sealed and on the map — let the hunt begin!')
        else:
            messages.success(request, 'Your stone is sealed! It appears on the map once someone finds it.')
        return redirect('stone_link', stone_number=stone.stone_number)


class StoneLinkView(View):
    """Handle stone-link functionality.

    URL format: /stone-link/{stone_number}/?key={uuid}
    - Without ?key= → public page (view-only)
    - With ?key= → scan/claim flow (QR code target)
    """

    def _render_public_page(self, request, stone):
        """Render the public stone page (same as StoneShareView)."""
        stone = Stone.objects.select_related('FK_user', 'FK_user__profile').get(pk=stone.pk)
        moves = list(stone.moves.filter(is_confirmed=True).order_by('timestamp').all())
        num_moves = len(moves)
        distance = round(stone.distance_km, 1)
        owner = stone.FK_user
        profile = owner.profile if owner else None

        share_url = request.build_absolute_uri(request.path)
        stone_title = f'{stone.PK_stone} on StoneWalker'
        share_handle = profile.get_share_handle() if profile else ''
        share_text = f'Check out the journey of {stone.PK_stone}'
        if share_handle:
            share_text += f' by {share_handle}'
        share_text += f' - {distance} km traveled!'
        encoded_text = urllib.parse.quote(share_text)
        encoded_url = urllib.parse.quote(share_url)

        twitter_url = f'https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}'
        facebook_url = f'https://www.facebook.com/sharer/sharer.php?u={encoded_url}'
        whatsapp_url = f'https://wa.me/?text={encoded_text}%20{encoded_url}'

        moves_data = []
        for m in moves:
            moves_data.append({
                'latitude': m.latitude,
                'longitude': m.longitude,
                'timestamp': m.timestamp.isoformat() if m.timestamp else '',
                'timestamp_display': m.timestamp.strftime('%b %d, %Y') if m.timestamp else '',
                'user': m.FK_user.username if m.FK_user else '',
                'comment': m.comment,
            })
        _prepend_journey_origin(stone, moves_data)

        stone_image_url = ''
        if stone.image:
            stone_image_url = request.build_absolute_uri(stone.image.url)

        context = {
            'stone': stone,
            'moves': moves,
            'moves_json': _script_safe_json(moves_data),
            'num_moves': num_moves,
            'distance': distance,
            'owner': owner,
            'profile': profile,
            'share_url': share_url,
            'stone_title': stone_title,
            'share_text': share_text,
            'stone_image_url': stone_image_url,
            'twitter_url': twitter_url,
            'facebook_url': facebook_url,
            'whatsapp_url': whatsapp_url,
        }
        return render(request, 'main/stone_share.html', context)

    def get(self, request, stone_number):
        try:
            stone = Stone.objects.get(stone_number=stone_number)
        except Stone.DoesNotExist:
            messages.error(request, 'Invalid stone link.')
            return redirect('stonewalker_start')

        key = request.GET.get('key')

        # No key → public page (or redirect for unclaimed)
        if not key:
            # Unclaimed codes and drafts have no public page (sequential
            # numbers would make unreleased stones enumerable); owner excepted.
            if stone.status in ('unclaimed', 'draft') and not _is_stone_owner(request, stone):
                return redirect('stonewalker_start')
            return self._render_public_page(request, stone)

        # Validate key matches stone UUID
        try:
            key_uuid = uuid_lib.UUID(key)
        except ValueError:
            messages.error(request, 'Invalid stone link.')
            return redirect('stone_link', stone_number=stone.stone_number)
        if key_uuid != stone.uuid:
            messages.error(request, 'Invalid stone link.')
            return redirect('stone_link', stone_number=stone.stone_number)

        # --- Key present: scan/claim flow ---

        # Unclaimed → redirect to claim page
        if stone.is_unclaimed():
            if request.user.is_authenticated:
                return redirect(f'{reverse("claim_stone", kwargs={"stone_number": stone.stone_number})}?key={stone.uuid}')
            else:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(
                    next=request.get_full_path(),
                    login_url='accounts:log_in'
                )

        # Draft/published → show a confirm/finish page instead of auto-sealing.
        # Scanning must NOT instantly seal: the owner needs a chance to add a
        # photo/description and edit first, then seal intentionally (a POST to
        # stone_send_off). Sealing on GET would also let crawlers seal.
        if stone.status in ('draft', 'published'):
            from django.contrib.auth.views import redirect_to_login
            if not request.user.is_authenticated:
                return redirect_to_login(next=request.get_full_path(), login_url='accounts:log_in')
            if stone.FK_user_id != request.user.id:
                messages.info(request, "This stone hasn't started its journey yet.")
                return redirect('stonewalker_start')
            return render(request, 'main/stone_seal_confirm.html', {
                'stone': stone,
                'stone_uuid': str(stone.uuid),
            })

        # Wandering stone — show the find form. Anonymous finders get an email
        # field (email-first signup): the find goes on the map right away and
        # they confirm their account by email afterwards.
        is_first_stone = False
        is_owner = False
        if request.user.is_authenticated:
            # Owner scanning their own sent-off stone that nobody else has
            # scanned yet → last-minute edit window (must be checked before the
            # scan blackout, which the seal scan-attempt already triggered).
            if stone.FK_user_id == request.user.id and stone.can_last_minute_edit():
                messages.info(request, "Nobody has found your stone yet — you can still make last-minute changes.")
                return redirect(_stone_edit_url(stone.PK_stone, stone.uuid))
            # Already recorded a find this week → public page (strips key).
            # Keyed on finds, not scan attempts: opening the link records an
            # attempt, so gating on attempts would block the form's own POST.
            if StoneMove.found_recently(stone, request.user):
                return redirect('stone_link', stone_number=stone.stone_number)
            StoneScanAttempt.record_scan_attempt(stone, request.user, request)
            user_stone_count = StoneMove.objects.filter(FK_user=request.user).count()
            is_first_stone = user_stone_count == 0
            is_owner = stone.FK_user == request.user

        response = render(request, 'main/stone_found.html', {
            'stone': stone,
            'stone_uuid': str(stone.uuid),
            'is_first_stone': is_first_stone,
            'is_owner': is_owner,
        })
        response.set_cookie(
            f'stone_scan_{stone.uuid}',
            timezone.now().isoformat(),
            max_age=7*24*60*60,  # 7 days
            httponly=True,
            samesite='Lax'
        )

        return response

    def _resolve_anonymous_finder(self, request, stone):
        """Resolve (or create) the account for an email-first anonymous find.

        Returns (user, redirect_or_None). On any validation problem or when the
        email already belongs to a real account, returns (None, <redirect>).
        """
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        from django.contrib.auth import login
        from django.contrib.auth.views import redirect_to_login
        from django.utils.crypto import get_random_string
        from accounts.models import EmailAddressState, TermsAcceptance, is_email_confirmed

        back = redirect('stone_link', stone_number=stone.stone_number)
        email = request.POST.get('finder_email', '').strip().lower()
        try:
            validate_email(email)
        except DjangoValidationError:
            messages.error(request, 'Please enter a valid email address to record your find.')
            return None, back
        if not request.POST.get('accept_terms'):
            messages.error(request, 'Please accept the Terms of Use to record your find.')
            return None, back

        existing = User.objects.filter(email__iexact=email).first()
        if existing and (is_email_confirmed(existing) or existing.has_usable_password()):
            # Real account already exists (possibly with an email change
            # pending) — don't create a duplicate and never log in on the
            # strength of a typed email; send them to the login page.
            next_url = f'{reverse("stone_link", kwargs={"stone_number": stone.stone_number})}?key={stone.uuid}'
            messages.info(request, 'That email already has a StoneWalker account. Please log in to record your find.')
            return None, redirect_to_login(next=next_url, login_url='accounts:log_in')

        if not existing and EmailAddressState.objects.filter(email__iexact=email).exists():
            # Address is pending as a new email on another account — it's
            # spoken for (and unique on EmailAddressState); don't create a user.
            messages.info(request, 'That email is already linked to a StoneWalker account. Please log in to record your find.')
            next_url = f'{reverse("stone_link", kwargs={"stone_number": stone.stone_number})}?key={stone.uuid}'
            return None, redirect_to_login(next=next_url, login_url='accounts:log_in')

        if existing:
            # Earlier unconfirmed provisional account: attach the find to it,
            # but don't log in — typing an email proves nothing.
            return existing, None
        else:
            # Lenient per-IP backstop against bot floods. Set high enough that a
            # classroom finding stones from one school network won't hit it.
            # Finds also need the stone's QR key, which limits abuse to people
            # who actually had the stone in hand.
            from .models import client_ip
            ip = client_ip(request)
            limit = getattr(settings, 'ANONYMOUS_FIND_IP_HOURLY_LIMIT', 100)
            if ip:
                hour_ago = timezone.now() - timedelta(hours=1)
                recent = StoneScanAttempt.objects.filter(ip_address=ip, scan_time__gte=hour_ago).count()
                if recent >= limit:
                    messages.error(request, 'Too many submissions from your network right now. Please try again later.')
                    return None, back
            user = User.objects.create(username=get_random_string(12), email=email, is_active=True)
            user.set_unusable_password()
            user.save()
            user.username = f'user_{user.id}'
            user.save(update_fields=['username'])
            EmailAddressState.objects.get_or_create(user=user, defaults={'email': email, 'is_confirmed': False})
            TermsAcceptance.objects.get_or_create(user=user)

        login(request, user)  # soft session so they can browse My Stones now
        return user, None

    def _send_find_confirmation(self, request, user, stone):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from accounts.utils import send_find_confirmation_email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return send_find_confirmation_email(request, user.email, token, uid, stone.PK_stone)

    def post(self, request, stone_number):
        # Look up stone by stone_number, validate UUID from hidden form field
        stone_uuid = request.POST.get('stone_uuid', '')
        try:
            stone = Stone.objects.get(stone_number=stone_number)
            uuid_obj = uuid_lib.UUID(stone_uuid)
            if uuid_obj != stone.uuid:
                raise ValueError("UUID mismatch")
        except (Stone.DoesNotExist, ValueError):
            messages.error(request, 'Invalid stone link.')
            return redirect('stonewalker_start')

        # Finds are only for sealed (wandering) stones — same rule as get().
        # Sealing is the owner's deliberate POST to stone_send_off, never a
        # side effect of someone holding the key submitting this form.
        if stone.status != 'wandering':
            messages.info(request, "This stone hasn't started its journey yet.")
            return redirect('stonewalker_start')

        # Resolve finder: logged-in user, or an email-first provisional account.
        anonymous = not request.user.is_authenticated
        if anonymous:
            user, bounce = self._resolve_anonymous_finder(request, stone)
            if bounce is not None:
                return bounce
        else:
            user = request.user

        # Finds on sent-off stones go on the map immediately (owner's choice,
        # 2026-11-10: waiting on the finder's email hid real finds). Finders
        # without a confirmed account still get the account-confirmation email.
        from accounts.models import is_email_confirmed
        unconfirmed_finder = anonymous or (not is_email_confirmed(user) and not user.has_usable_password())

        # Check one-week blackout period (per finder, based on recorded finds)
        if StoneMove.found_recently(stone, user):
            messages.error(request, 'You have already scanned this stone in the last week. Please wait before scanning again.')
            return redirect('stonewalker_start')

        # Get form data
        comment = request.POST.get('comment', '')
        image = request.FILES.get('image')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        new_latitude = request.POST.get('new_latitude')
        new_longitude = request.POST.get('new_longitude')

        # Validate comment content
        from .validators import validate_no_contact_info
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            validate_no_contact_info(comment)
        except DjangoValidationError as e:
            messages.error(request, e.message)
            return redirect('stone_link', stone_number=stone.stone_number)

        # Validate coordinates
        try:
            lat = float(latitude) if latitude else None
            lng = float(longitude) if longitude else None
            if lat is None or lng is None:
                raise ValueError("Missing coordinates")
        except ValueError:
            messages.error(request, 'Please provide valid coordinates for where you found the stone.')
            return redirect('stone_link', stone_number=stone.stone_number)

        try:
            # Create the stone move and record the attempt together, so a
            # failed save can't leave the finder locked out without a find.
            with transaction.atomic():
                stone_move = StoneMove.objects.create(
                    FK_stone=stone,
                    FK_user=user,
                    image=image,
                    comment=comment,
                    latitude=lat,
                    longitude=lng,
                    is_confirmed=True,
                )
                StoneScanAttempt.record_scan_attempt(stone, user, request)

            stone.distance_km = calculate_stone_distance(stone)
            stone.save(update_fields=['distance_km'])

            # For hunted stones, store the new location for next week
            if stone.stone_type == 'hunted' and new_latitude and new_longitude:
                try:
                    new_lat = float(new_latitude)
                    new_lng = float(new_longitude)
                    request.session[f'new_location_{stone.uuid}'] = {
                        'latitude': new_lat,
                        'longitude': new_lng,
                        'user_id': user.id,
                        'timestamp': timezone.now().isoformat()
                    }
                except ValueError:
                    messages.error(request, 'Please provide valid coordinates for the new location.')
                    return redirect('stone_link', stone_number=stone.stone_number)

            if unconfirmed_finder:
                if self._send_find_confirmation(request, user, stone):
                    messages.success(request, 'Your find is on the map! Check your email to confirm your StoneWalker account.')
                else:
                    messages.success(request, 'Your find is on the map!')
                return redirect(_map_focus_url(stone.PK_stone))

            messages.success(request, 'Your stone find has been recorded!')
            return redirect(_map_focus_url(stone.PK_stone))

        except Exception as e:
            messages.error(request, f'Could not record stone find: {str(e)}')
            return redirect('stone_link', stone_number=stone.stone_number)


class StoneLinkLegacyRedirectView(View):
    """Redirect old /stone-link/{uuid}/ URLs to new /stone-link/{number}/?key={uuid} format."""

    def get(self, request, stone_uuid):
        try:
            stone = Stone.objects.get(uuid=stone_uuid)
        except Stone.DoesNotExist:
            messages.error(request, 'Invalid stone link.')
            return redirect('stonewalker_start')
        return redirect(f'{reverse("stone_link", kwargs={"stone_number": stone.stone_number})}?key={stone.uuid}')


def generate_qr_code_api(request):
    """
    API endpoint for QR code generation that works for any valid UUID
    (even if stone doesn't exist in database yet)
    """
    stone_name = request.GET.get('stone_name')
    stone_uuid = request.GET.get('stone_uuid')
    
    if not stone_name or not stone_uuid:
        return JsonResponse({'error': 'Missing stone name or UUID'}, status=400)
    
    try:
        # Validate UUID format
        uuid_obj = uuid_lib.UUID(stone_uuid)

        # Try to find existing stone for proper URL, fall back for preview
        try:
            stone = Stone.objects.get(uuid=uuid_obj)
            qr_url = stone.get_qr_url()
        except Stone.DoesNotExist:
            qr_url = f'https://{Stone.PRODUCTION_DOMAIN}/stone-link/0/?key={stone_uuid}'
        
        # Create QR code
        import qrcode
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        import base64
        import os
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Generate QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Create 3:4 portrait format with text
        qr_size = 400
        text_area_height = 100
        total_height = qr_size + text_area_height
        total_width = int(3 * total_height / 4)
        
        # Handle older PIL versions
        try:
            resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            resample_method = Image.LANCZOS
            
        qr_img = qr_img.resize((qr_size, qr_size), resample_method)
        
        # Create final image
        final_img = Image.new('RGB', (total_width, total_height), 'white')
        qr_x = (total_width - qr_size) // 2
        final_img.paste(qr_img, (qr_x, 0))
        
        # Add readable text
        draw = ImageDraw.Draw(final_img)
        font_size = 16
        
        # Try to get a font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Calculate text dimensions with fallback
        try:
            text_bbox = draw.textbbox((0, 0), qr_url, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(qr_url, font=font)
        
        # If text too wide, use smaller font
        if text_width > total_width - 20:
            font_size = 12
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except:
                font = ImageFont.load_default()
            try:
                text_bbox = draw.textbbox((0, 0), qr_url, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            except AttributeError:
                text_width, text_height = draw.textsize(qr_url, font=font)
        
        # Position text
        text_x = (total_width - text_width) // 2
        text_y = qr_size + 20
        
        # Draw background for text
        padding = 3
        draw.rectangle([
            text_x - padding, text_y - padding,
            text_x + text_width + padding, text_y + text_height + padding
        ], fill='#f5f5f5', outline='#ddd')
        
        # Draw text
        draw.text((text_x, text_y), qr_url, fill='#000000', font=font)
        
        # Convert to base64
        buffer = BytesIO()
        final_img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return JsonResponse({
            'success': True,
            'qr_code': qr_base64,
            'qr_url': qr_url,
            'stone_name': stone_name,
            'stone_uuid': stone_uuid
        })
        
    except ValueError:
        return JsonResponse({'error': 'Invalid UUID format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error generating QR code: {str(e)}'}, status=500)


def download_enhanced_qr_code(request):
    """
    Download enhanced QR code with StoneWalker branding
    Works for both existing stones and preview downloads
    """
    stone_name = request.GET.get('stone_name')
    stone_uuid = request.GET.get('stone_uuid')
    
    if not stone_name or not stone_uuid:
        return JsonResponse({'error': 'Missing stone name or UUID'}, status=400)
    
    try:
        # Validate UUID format
        uuid_obj = uuid_lib.UUID(stone_uuid)
        
        # Try to find existing stone for proper URL, fall back for preview
        try:
            real_stone = Stone.objects.get(uuid=uuid_obj)
            temp_stone = real_stone
        except Stone.DoesNotExist:
            class TempStone:
                def __init__(self, name, uuid_str):
                    self.PK_stone = name
                    self.uuid = uuid_str

                def get_qr_url(self):
                    return f'https://{Stone.PRODUCTION_DOMAIN}/stone-link/0/?key={self.uuid}'

            temp_stone = TempStone(stone_name, stone_uuid)

        # Generate enhanced QR code
        from .qr_service import QRCodeService
        enhanced_result = QRCodeService.generate_enhanced_qr_for_download(temp_stone, request)
        
        if enhanced_result['success']:
            response = HttpResponse(enhanced_result['image_data'], content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{stone_name}_stonewalker_qr.png"'
            return response
        else:
            return JsonResponse({'error': 'Failed to generate enhanced QR code'}, status=500)
            
    except ValueError:
        return JsonResponse({'error': 'Invalid UUID format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error generating enhanced QR code: {str(e)}'}, status=500)


class StoneShareView(View):
    """Public share page for a stone's journey."""

    def get(self, request, pk):
        stone = get_object_or_404(
            Stone.objects.select_related('FK_user', 'FK_user__profile'),
            PK_stone=pk,
        )
        if stone.status in ('unclaimed', 'draft') and not _is_stone_owner(request, stone):
            raise Http404
        moves = list(stone.moves.filter(is_confirmed=True).order_by('timestamp').all())
        num_moves = len(moves)
        distance = round(stone.distance_km, 1)
        owner = stone.FK_user
        profile = owner.profile if owner else None

        # Build share URLs
        share_url = request.build_absolute_uri(request.path)
        stone_title = f'{stone.PK_stone} on StoneWalker'
        share_handle = profile.get_share_handle() if profile else ''
        share_text = f'Check out the journey of {stone.PK_stone}'
        if share_handle:
            share_text += f' by {share_handle}'
        share_text += f' - {distance} km traveled!'
        encoded_text = urllib.parse.quote(share_text)
        encoded_url = urllib.parse.quote(share_url)

        twitter_url = f'https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}'
        facebook_url = f'https://www.facebook.com/sharer/sharer.php?u={encoded_url}'
        whatsapp_url = f'https://wa.me/?text={encoded_text}%20{encoded_url}'

        # Build moves data for the map
        moves_data = []
        for m in moves:
            moves_data.append({
                'latitude': m.latitude,
                'longitude': m.longitude,
                'timestamp': m.timestamp.isoformat() if m.timestamp else '',
                'timestamp_display': m.timestamp.strftime('%b %d, %Y') if m.timestamp else '',
                'user': m.FK_user.username if m.FK_user else '',
                'comment': m.comment,
            })
        _prepend_journey_origin(stone, moves_data)

        # Stone image URL for OG tag
        stone_image_url = ''
        if stone.image:
            stone_image_url = request.build_absolute_uri(stone.image.url)

        context = {
            'stone': stone,
            'moves': moves,
            'moves_json': _script_safe_json(moves_data),
            'num_moves': num_moves,
            'distance': distance,
            'owner': owner,
            'profile': profile,
            'share_url': share_url,
            'stone_title': stone_title,
            'share_text': share_text,
            'stone_image_url': stone_image_url,
            'twitter_url': twitter_url,
            'facebook_url': facebook_url,
            'whatsapp_url': whatsapp_url,
        }
        return render(request, 'main/stone_share.html', context)
