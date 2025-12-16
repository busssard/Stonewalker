# Old QR Code Views - Extracted from main/views.py
# These views have various issues and are being replaced with a cleaner implementation

import qrcode
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
import uuid as uuid_lib
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import io
import base64


class StoneQRCodeView(View):
    """Old QR code view - generates QR for individual stones"""
    def get(self, request, pk):
        # Generate the update link for this stone using UUID
        try:
            from main.models import Stone
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


@login_required
def download_qr_code(request):
    """Old download QR code function with complex session management"""
    qr_path = request.session.get('qr_download_path')
    stone_name = request.session.get('qr_stone_name')
    qr_url = request.session.get('qr_stone_url')
    
    if not qr_path or not stone_name:
        messages.error(request, 'No QR code available for download.')
        return redirect('stonewalker_start')
    
    try:
        full_path = os.path.join(settings.MEDIA_ROOT, qr_path)
        
        if os.path.exists(full_path):
            # Load the existing QR code image
            qr_img = Image.open(full_path)
            
            # Create a 3:4 portrait format image with QR code at top and text at bottom
            # Calculate dimensions for 3:4 aspect ratio
            qr_size = qr_img.width  # QR code is square
            text_area_height = 120  # Generous space for text
            new_height = qr_size + text_area_height
            new_width = int(3 * new_height / 4)  # 3:4 aspect ratio
            
            # Create new image with white background
            new_img = Image.new('RGB', (new_width, new_height), 'white')
            
            # Paste QR code at the top, centered horizontally
            qr_x = (new_width - qr_size) // 2  # Center QR code horizontally
            new_img.paste(qr_img, (qr_x, 0))
            
            # Add cleartext URL at the bottom
            draw = ImageDraw.Draw(new_img)
            
            # Use a much larger font for better OCR readability
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 18)
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
            
            text_x = max(10, (new_width - text_width) // 2)  # Center text horizontally
            text_y = qr_size + 20  # Position text in the text area below QR code
            
            # Draw background rectangle for text
            padding = 4
            draw.rectangle([
                text_x - padding, text_y - padding,
                text_x + text_width + padding, text_y + text_height + padding
            ], fill='#f8f8f8', outline='#e0e0e0')
            
            # Draw the text with high contrast for better OCR
            draw.text((text_x, text_y), text, fill='#000000', font=font)
            
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
    """Old AJAX QR generation endpoint"""
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
    """Old regenerate QR code function"""
    try:
        from main.models import Stone
        stone = Stone.objects.get(PK_stone=stone_pk, FK_user=request.user)
        
        # Generate QR code server-side using the stone's UUID
        qr_url = request.build_absolute_uri(f'/stone-link/{stone.uuid}/')
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to media directory
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


# Old QR generation logic from add_stone view
def old_qr_generation_in_add_stone(request, stone):
    """This was embedded in the add_stone view - extracted for reference"""
    try:
        qr_url = request.build_absolute_uri(f'/stone-link/{stone.uuid}/')
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to media directory
        qr_filename = f'qr_codes/{stone.PK_stone}_{stone.uuid}_qr.png'
        qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        qr_img.save(qr_path)
        
        # Store QR path in session for download
        request.session['qr_download_path'] = qr_filename
        request.session['qr_stone_name'] = stone.PK_stone
        request.session['qr_stone_uuid'] = str(stone.uuid)
        request.session['qr_stone_url'] = qr_url
        
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'QR code generation failed: {str(e)}')
        
        # Clear any partial QR session data
        request.session.pop('qr_download_path', None)
        request.session.pop('qr_stone_name', None)
        request.session.pop('qr_stone_uuid', None)
        request.session.pop('qr_stone_url', None)
        return False