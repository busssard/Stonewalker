from django.views.generic import TemplateView
from .models import Stone, StoneMove, calculate_stone_distance
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
import re
from math import radians, sin, cos, sqrt, atan2
import logging
logger = logging.getLogger(__name__)
import qrcode
from io import BytesIO
from django.http import HttpResponse
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import get_language, get_language_from_request
from django.conf import settings
from django.urls import reverse


class IndexPageView(TemplateView):
    template_name = 'main/index.html'


class ChangeLanguageView(TemplateView):
    template_name = 'main/change_language.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Set redirect to main page after language change
        context['redirect_to'] = reverse('stonewalker_start')
        return context


class StoneWalkerStartPageView(TemplateView):
    template_name = 'main/stonewalker_start.html'

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all stones
        stones = Stone.objects.all()
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
            moves = list(stone.moves.order_by('timestamp').all())
            # Use the stored distance_km field for display
            total_distance = stone.distance_km
            if moves:
                # Latest move for marker
                latest_move = moves[-1]
                stones_data.append({
                    'PK_stone': stone.PK_stone,
                    'uuid': str(stone.uuid),
                    'description': stone.description,
                    'created_at': stone.created_at.isoformat(),
                    'user': stone.FK_user.username,
                    'user_picture': stone.FK_user.profile.profile_picture.url if hasattr(stone.FK_user, 'profile') and stone.FK_user.profile.profile_picture else '/static/user_picture.png',
                    'image': stone.image.url if stone.image else '',
                    'color': stone.color,
                    'shape': stone.shape,
                    'latest_latitude': latest_move.latitude,
                    'latest_longitude': latest_move.longitude,
                    'latest_image': latest_move.image.url if latest_move.image else '',
                    'distance_km': round(total_distance, 1),
                    'moves': [
                        {
                            'latitude': m.latitude,
                            'longitude': m.longitude,
                            'timestamp': m.timestamp.isoformat() if m.timestamp else '',
                            'timestamp_display': m.timestamp.strftime('%b %d, %Y') if m.timestamp else '',
                            'image': m.image.url if m.image else '',
                            'comment': m.comment,
                            'user': m.FK_user.username,
                            'user_picture': m.FK_user.profile.profile_picture.url if hasattr(m.FK_user, 'profile') and m.FK_user.profile.profile_picture else '/static/user_picture.png',
                        } for m in moves
                    ]
                })
        context['stones_json'] = json.dumps(stones_data)
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
        my_stones = Stone.objects.filter(FK_user=user).prefetch_related('moves')
        for stone in my_stones:
            stone.distance_km = round(stone.distance_km, 1)
        context['my_stones'] = my_stones
        # Stones where user has moved but is not the creator
        moved_stone_ids = StoneMove.objects.filter(FK_user=user).exclude(FK_stone__FK_user=user).values_list('FK_stone', flat=True).distinct()
        my_interactions = Stone.objects.filter(PK_stone__in=moved_stone_ids).prefetch_related('moves')
        for stone in my_interactions:
            stone.distance_km = round(stone.distance_km, 1)
        context['my_interactions'] = my_interactions
        return context


@csrf_exempt  # For quick debug, remove in production
def debug_add_stone(request):
    if request.method == 'POST':
        PK_stone = request.POST.get('PK_stone')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        color = request.POST.get('color', '#4CAF50')
        shape = request.POST.get('shape', 'circle')
        user = request.user if request.user.is_authenticated else User.objects.first()
        if PK_stone and user:
            try:
                Stone.objects.create(
                    PK_stone=PK_stone,
                    description=description[:500],
                    FK_user=user,
                    image=image,
                    color=color,
                    shape=shape
                )
            except Exception as e:
                pass
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponse("Use POST to add a stone.")


@login_required
@require_POST
def add_stone(request):
    PK_stone = request.POST.get('PK_stone')
    description = request.POST.get('description', '')
    image = request.FILES.get('image')
    color = request.POST.get('color', '#4CAF50')
    shape = request.POST.get('shape', 'circle')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    stone_type = request.POST.get('stone_type', 'hidden')
    
    # Auto-select shape based on stone type
    if stone_type == 'hidden':
        shape = 'circle'
    elif stone_type == 'hunted':
        shape = 'triangle'
    
    if not PK_stone:
        messages.error(request, 'Missing required stone name.')
        return redirect('stonewalker_start')
    if len(description) > 500:
        description = description[:500]
    
    # Validate hunted stone location before creating the stone
    if stone_type == 'hunted':
        if not latitude or not longitude:
            messages.error(request, 'Location is required for hunted stones.')
            return redirect('stonewalker_start')
    
    try:
        stone = Stone(
            PK_stone=PK_stone,
            description=description,
            FK_user=request.user,
            image=image,
            color=color,
            shape=shape
        )
        stone.save()  # Ensure the image is saved to disk
        if stone_type == 'hunted':
            StoneMove.objects.create(
                FK_stone=stone,
                FK_user=request.user,
                image=None,  # Do NOT add image to StoneMove for hunted stones
                comment='',
                latitude=float(latitude),
                longitude=float(longitude)
            )
        # For hidden stones, do not create a StoneMove entry at creation
        # Update distance
        stone.distance_km = calculate_stone_distance(stone)
        stone.save()
        
        # Generate QR code for the stone
        qr_url = request.build_absolute_uri(f'/stonescan/?stone={stone.uuid}')
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to media directory
        import os
        from django.conf import settings
        qr_filename = f'qr_codes/{stone.PK_stone}_qr.png'
        qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        qr_img.save(qr_path)
        
        # Store QR path in session for download
        request.session['qr_download_path'] = qr_filename
        request.session['qr_stone_name'] = stone.PK_stone
        
        messages.success(request, f'Stone "{PK_stone}" added successfully! QR code generated. <a href="/download-qr/" class="avant-btn">Download QR Code</a>')
        return redirect(f'/stonewalker/?focus={PK_stone}')
    except Exception as e:
        messages.error(request, f'Could not add stone: {str(e)}')
    return redirect('stonewalker_start')


class StoneScanView(View):
    template_name = 'main/stone_scan.html'

    @method_decorator(login_required)
    def get(self, request):
        stone_param = request.GET.get('stone')
        context = {}
        if stone_param:
            # Try to find stone by UUID first, then by PK_stone
            stone = None
            try:
                # Try to parse as UUID first
                import uuid
                uuid_param = uuid.UUID(stone_param)
                stone = Stone.objects.get(uuid=uuid_param)
                context['stone_name'] = stone.PK_stone
                context['locked'] = True  # Lock the stone name
            except (ValueError, Stone.DoesNotExist):
                # If not a valid UUID, try as PK_stone
                try:
                    stone = Stone.objects.get(PK_stone=stone_param)
                    context['stone_name'] = stone_param
                    context['locked'] = True  # Lock the stone name
                except Stone.DoesNotExist:
                    messages.error(request, 'Stone not found.')
                    return render(request, self.template_name, context)
            
            # Check cooldown
            recent_move = None
            if request.user.is_authenticated:
                from main.models import StoneMove
                recent_move = StoneMove.objects.filter(FK_stone__PK_stone=context['stone_name'], FK_user=request.user, timestamp__gte=timezone.now()-timedelta(days=3)).first()
            if recent_move:
                context['locked'] = True
                context['lock_message'] = 'You have already updated this stone in the last 3 days. Please wait before updating again.'
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request):
        PK_stone = request.POST.get('PK_stone')
        comment = request.POST.get('comment', '')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        image = request.FILES.get('image')
        # Enforce cooldown on POST as well
        from main.models import StoneMove
        recent_move = StoneMove.objects.filter(FK_stone__PK_stone=PK_stone, FK_user=request.user, timestamp__gte=timezone.now()-timedelta(days=3)).first()
        if recent_move:
            messages.error(request, 'You have already updated this stone in the last 3 days. Please wait before updating again.')
            return render(request, self.template_name, {'prefill_stone': PK_stone, 'locked': True, 'lock_message': 'You have already updated this stone in the last 3 days. Please wait before updating again.'})
        try:
            stone = Stone.objects.get(PK_stone=PK_stone)
        except Stone.DoesNotExist:
            messages.error(request, 'Stone not found.')
            return render(request, self.template_name)
        try:
            StoneMove.objects.create(
                FK_stone=stone,
                FK_user=request.user,
            image=image,
            comment=comment,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None
        )
            # Update distance
            stone.distance_km = calculate_stone_distance(stone)
            stone.save()
            messages.success(request, 'Your scan has been added!')
            return redirect(f'/stonewalker/?focus={PK_stone}')
        except Exception as e:
            messages.error(request, f'Could not add scan: {str(e)}')
        return render(request, self.template_name, {'success': True})


def check_stone_name(request):
    PK_stone = request.GET.get('PK_stone', '').strip()
    if not PK_stone:
        # fallback for legacy 'name' param
        PK_stone = request.GET.get('name', '').strip()
    taken = False
    reason = None
    if not PK_stone:
        taken = True
        reason = 'empty'
    elif re.search(r'\s', PK_stone):
        taken = True
        reason = 'whitespace'
    elif Stone.objects.filter(PK_stone=PK_stone).exists():
        taken = True
        reason = 'taken'
    return JsonResponse({'taken': taken, 'reason': reason, 'PK_stone': PK_stone})


class StoneQRCodeView(View):
    def get(self, request, pk):
        # Generate the update link for this stone using UUID
        try:
            stone = Stone.objects.get(PK_stone=pk)
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(request.build_absolute_uri(f'/stonescan/?stone={stone.uuid}'))
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            response = HttpResponse(content_type="image/png")
            img.save(response, "PNG")
            return response
        except Stone.DoesNotExist:
            return HttpResponse("Stone not found", status=404)


@login_required
def download_qr_code(request):
    """Download the QR code that was generated after stone creation"""
    qr_path = request.session.get('qr_download_path')
    stone_name = request.session.get('qr_stone_name')
    
    if not qr_path or not stone_name:
        messages.error(request, 'No QR code available for download.')
        return redirect('stonewalker_start')
    
    try:
        from django.conf import settings
        import os
        full_path = os.path.join(settings.MEDIA_ROOT, qr_path)
        
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='image/png')
                response['Content-Disposition'] = f'attachment; filename="{stone_name}_qr.png"'
                return response
        else:
            messages.error(request, 'QR code file not found.')
            return redirect('stonewalker_start')
    except Exception as e:
        messages.error(request, f'Error downloading QR code: {str(e)}')
        return redirect('stonewalker_start')



