from django.views.generic import TemplateView
from .models import Stone, StoneMove, calculate_stone_distance, StoneScanAttempt
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
import uuid as uuid_lib


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
                    'user_picture': stone.FK_user.profile.get_picture_url(),
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
                            'user_picture': m.FK_user.profile.get_picture_url(),
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
        # Create stone with UUID (will be auto-generated)
        stone = Stone(
            PK_stone=PK_stone,
            description=description,
            FK_user=request.user,
            image=image,
            color=color,
            shape=shape
        )
        stone.save()  # This will generate the UUID
        
        # Create initial move for hunted stones
        if stone_type == 'hunted':
            StoneMove.objects.create(
                FK_stone=stone,
                FK_user=request.user,
                image=None,  # Do NOT add image to StoneMove for hunted stones
                comment='',
                latitude=float(latitude),
                longitude=float(longitude)
            )
        
        # Update distance
        stone.distance_km = calculate_stone_distance(stone)
        stone.save()
        
        # Generate QR code server-side using the stone's UUID
        # This happens AFTER stone creation to ensure robustness
        try:
            qr_url = request.build_absolute_uri(f'/stone-link/{stone.uuid}/')
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code to media directory
            import os
            from django.conf import settings
            qr_filename = f'qr_codes/{stone.PK_stone}_{stone.uuid}_qr.png'
            qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            qr_img.save(qr_path)
            
            # Store QR path in session for download
            request.session['qr_download_path'] = qr_filename
            request.session['qr_stone_name'] = stone.PK_stone
            request.session['qr_stone_uuid'] = str(stone.uuid)
            request.session['qr_stone_url'] = qr_url
            
            messages.success(request, f'Stone "{PK_stone}" added successfully! QR code generated. <a href="/download-qr/" class="avant-btn">Download QR Code</a>')
        except Exception as qr_error:
            # QR generation failed, but stone was created successfully
            # Log the error but don't fail the stone creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'QR code generation failed for stone {PK_stone}: {str(qr_error)}')
            
            # Clear any partial QR session data
            request.session.pop('qr_download_path', None)
            request.session.pop('qr_stone_name', None)
            request.session.pop('qr_stone_uuid', None)
            request.session.pop('qr_stone_url', None)
            
            messages.success(request, f'Stone "{PK_stone}" added successfully! Note: QR code generation failed, but you can generate it later.')
        
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
            
            # Check cooldown using new StoneScanAttempt model
            if request.user.is_authenticated and stone:
                if not StoneScanAttempt.can_scan_again(stone, request.user):
                    context['locked'] = True
                    context['lock_message'] = 'You have already scanned this stone in the last week. Please wait before scanning again.'
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request):
        PK_stone = request.POST.get('PK_stone')
        comment = request.POST.get('comment', '')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        image = request.FILES.get('image')
        
        try:
            stone = Stone.objects.get(PK_stone=PK_stone)
        except Stone.DoesNotExist:
            messages.error(request, 'Stone not found.')
            return render(request, self.template_name)
        
        # Check one-week blackout period
        if not StoneScanAttempt.can_scan_again(stone, request.user):
            messages.error(request, 'You have already scanned this stone in the last week. Please wait before scanning again.')
            return render(request, self.template_name, {'prefill_stone': PK_stone, 'locked': True, 'lock_message': 'You have already scanned this stone in the last week. Please wait before scanning again.'})
        
        try:
            # Record the scan attempt
            StoneScanAttempt.record_scan_attempt(stone, request.user, request)
            
            # Create the stone move
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


class StoneQRCodeView(View):
    def get(self, request, pk):
        # Generate the update link for this stone using UUID
        try:
            stone = Stone.objects.get(PK_stone=pk)
            # Use the stone-link URL instead of stonescan for consistency
            qr_url = request.build_absolute_uri(f'/stone-link/{stone.uuid}/')
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            response = HttpResponse(content_type="image/png")
            img.save(response, "PNG")
            return response
        except Stone.DoesNotExist:
            return HttpResponse("Stone not found", status=404)


class StoneLinkView(View):
    """Handle stone-link functionality with cookie tracking and database storage"""
    
    def get(self, request, stone_uuid):
        try:
            # Parse UUID and find stone
            stone_uuid_obj = uuid_lib.UUID(stone_uuid)
            stone = Stone.objects.get(uuid=stone_uuid_obj)
        except (ValueError, Stone.DoesNotExist):
            messages.error(request, 'Invalid stone link.')
            return redirect('stonewalker_start')
        
        # If user is authenticated, record scan attempt
        if request.user.is_authenticated:
            StoneScanAttempt.record_scan_attempt(stone, request.user, request)
        
        # Check if this is user's first stone
        is_first_stone = False
        if request.user.is_authenticated:
            user_stone_count = StoneMove.objects.filter(FK_user=request.user).count()
            is_first_stone = user_stone_count == 0
        
        # Create response with cookie
        response = render(request, 'main/stone_found.html', {
            'stone': stone,
            'stone_uuid': stone_uuid,
            'is_first_stone': is_first_stone,
        })
        response.set_cookie(
            f'stone_scan_{stone_uuid}',
            timezone.now().isoformat(),
            max_age=7*24*60*60,  # 7 days
            httponly=True,
            samesite='Lax'
        )
        
        return response
    
    @method_decorator(login_required)
    def post(self, request, stone_uuid):
        try:
            # Parse UUID and find stone
            stone_uuid_obj = uuid_lib.UUID(stone_uuid)
            stone = Stone.objects.get(uuid=stone_uuid_obj)
        except (ValueError, Stone.DoesNotExist):
            messages.error(request, 'Invalid stone link.')
            return redirect('stonewalker_start')
        
        # Check one-week blackout period
        if not StoneScanAttempt.can_scan_again(stone, request.user):
            messages.error(request, 'You have already scanned this stone in the last week. Please wait before scanning again.')
            return redirect('stonewalker_start')
        
        # Get form data
        comment = request.POST.get('comment', '')
        image = request.FILES.get('image')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        new_latitude = request.POST.get('new_latitude')
        new_longitude = request.POST.get('new_longitude')
        
        # Validate coordinates
        try:
            lat = float(latitude) if latitude else None
            lng = float(longitude) if longitude else None
            if lat is None or lng is None:
                raise ValueError("Missing coordinates")
        except ValueError:
            messages.error(request, 'Please provide valid coordinates for where you found the stone.')
            return redirect(f'/stone-link/{stone_uuid}/')
        
        try:
            # Record the scan attempt
            StoneScanAttempt.record_scan_attempt(stone, request.user, request)
            
            # Create the stone move
            stone_move = StoneMove.objects.create(
                FK_stone=stone,
                FK_user=request.user,
                image=image,
                comment=comment,
                latitude=lat,
                longitude=lng
            )
            
            # Update stone distance
            stone.distance_km = calculate_stone_distance(stone)
            stone.save()
            
            # For hunted stones, store the new location for next week
            if stone.stone_type == 'hunted' and new_latitude and new_longitude:
                try:
                    new_lat = float(new_latitude)
                    new_lng = float(new_longitude)
                    # Store new location in session for next week placement
                    request.session[f'new_location_{stone_uuid}'] = {
                        'latitude': new_lat,
                        'longitude': new_lng,
                        'user_id': request.user.id,
                        'timestamp': timezone.now().isoformat()
                    }
                except ValueError:
                    messages.error(request, 'Please provide valid coordinates for the new location.')
                    return redirect(f'/stone-link/{stone_uuid}/')
            
            messages.success(request, 'Your stone find has been recorded!')
            return redirect(f'/stonewalker/?focus={stone.PK_stone}')
            
        except Exception as e:
            messages.error(request, f'Could not record stone find: {str(e)}')
            return redirect(f'/stone-link/{stone_uuid}/')


@login_required
def download_qr_code(request):
    """Download the QR code that was generated after stone creation with cleartext URL"""
    qr_path = request.session.get('qr_download_path')
    stone_name = request.session.get('qr_stone_name')
    qr_url = request.session.get('qr_stone_url')
    
    if not qr_path or not stone_name:
        messages.error(request, 'No QR code available for download.')
        return redirect('stonewalker_start')
    
    try:
        from django.conf import settings
        import os
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        full_path = os.path.join(settings.MEDIA_ROOT, qr_path)
        
        if os.path.exists(full_path):
            # Load the existing QR code image
            qr_img = Image.open(full_path)
            
            # Create a new image with extra space for the cleartext URL
            # Add 60px height for text (increased for larger font)
            new_width = qr_img.width
            new_height = qr_img.height + 60
            
            # Create new image with white background
            new_img = Image.new('RGB', (new_width, new_height), 'white')
            
            # Paste QR code at the top
            new_img.paste(qr_img, (0, 0))
            
            # Add cleartext URL at the bottom
            draw = ImageDraw.Draw(new_img)
            
            # Try to use a larger font for better OCR readability
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 14)
                except:
                    font = ImageFont.load_default()
            
            # Calculate text position (centered)
            text = qr_url or "QR Code URL"
            try:
                # Try newer textbbox method first
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except AttributeError:
                # Fallback to older textsize method
                text_width, text_height = draw.textsize(text, font=font)
            
            # Ensure text fits within the image width
            if text_width > new_width:
                # If text is too wide, use a smaller font
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except:
                    # If still too wide, truncate the text
                    while text_width > new_width - 10 and len(text) > 10:
                        text = text[:-1]
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
            
            text_x = max(5, (new_width - text_width) // 2)  # Ensure text is not positioned off-screen
            text_y = qr_img.height + 10  # More space from QR code
            
            # Draw background rectangle for text
            padding = 4
            draw.rectangle([
                text_x - padding, text_y - padding,
                text_x + text_width + padding, text_y + text_height + padding
            ], fill='#f8f8f8', outline='#e0e0e0')
            
            # Draw the text
            draw.text((text_x, text_y), text, fill='#666', font=font)
            
            # Save to bytes
            img_io = io.BytesIO()
            new_img.save(img_io, format='PNG')
            img_io.seek(0)
            
            response = HttpResponse(img_io.getvalue(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{stone_name}_qr_with_url.png"'
            return response
        else:
            messages.error(request, 'QR code file not found.')
            return redirect('stonewalker_start')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error downloading QR code: {str(e)}')
        messages.error(request, f'Error downloading QR code: {str(e)}')
        return redirect('stonewalker_start')


def generate_qr_code(request):
    """Generate QR code for a stone and return as JSON"""
    stone_name = request.GET.get('stone_name')
    stone_uuid = request.GET.get('stone_uuid')
    
    if not stone_name or not stone_uuid:
        return JsonResponse({'error': 'Missing stone name or UUID'}, status=400)
    
    try:
        # Validate UUID format
        uuid_lib.UUID(stone_uuid)
        
        # Generate QR code
        qr_url = request.build_absolute_uri(f'/stone-link/{stone_uuid}/')
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for download
        import base64
        from io import BytesIO
        
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
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


@login_required
def regenerate_qr_code(request, stone_pk):
    """Regenerate QR code for an existing stone"""
    try:
        stone = Stone.objects.get(PK_stone=stone_pk, FK_user=request.user)
        
        # Generate QR code server-side using the stone's UUID
        qr_url = request.build_absolute_uri(f'/stone-link/{stone.uuid}/')
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to media directory
        import os
        from django.conf import settings
        qr_filename = f'qr_codes/{stone.PK_stone}_{stone.uuid}_qr.png'
        qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        qr_img.save(qr_path)
        
        # Store QR path in session for download
        request.session['qr_download_path'] = qr_filename
        request.session['qr_stone_name'] = stone.PK_stone
        request.session['qr_stone_uuid'] = str(stone.uuid)
        request.session['qr_stone_url'] = qr_url
        
        messages.success(request, f'QR code regenerated for stone "{stone.PK_stone}"! <a href="/download-qr/" class="avant-btn">Download QR Code</a>')
        return redirect(f'/stonewalker/?focus={stone.PK_stone}')
        
    except Stone.DoesNotExist:
        messages.error(request, 'Stone not found or you do not have permission to access it.')
        return redirect('stonewalker_start')
    except Exception as e:
        messages.error(request, f'Could not regenerate QR code: {str(e)}')
        return redirect('stonewalker_start')



