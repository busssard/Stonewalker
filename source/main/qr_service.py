"""
New QR Code Service - Clean implementation with readable URLs and persistent codes
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)


class QRCodeService:
    """Clean QR code generation service with readable URLs"""
    
    DEFAULT_QR_SIZE = 400  # Larger size for better scanning
    TEXT_AREA_HEIGHT = 100
    ASPECT_RATIO = (3, 4)  # 3:4 portrait format
    
    @classmethod
    def generate_qr_for_stone(cls, stone, request=None):
        """
        Generate a QR code for a stone with readable URL underneath
        Returns the full URL to the QR code and the stone URL
        """
        try:
            # Generate the stone URL
            stone_url = stone.get_qr_url()
            
            # If we have a request, make it absolute
            if request:
                stone_url = request.build_absolute_uri(stone_url)
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(stone_url)
            qr.make(fit=True)
            
            # Generate QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Create final image with readable URL
            final_img = cls._create_image_with_text(qr_img, stone_url)
            
            # Save to file
            qr_filename = f'qr_codes/{stone.PK_stone}_{stone.uuid}.png'
            qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            
            final_img.save(qr_path, 'PNG', quality=95)
            
            # Return the media URL for the saved file
            qr_media_url = f'{settings.MEDIA_URL}{qr_filename}'
            
            logger.info(f"Generated QR code for stone {stone.PK_stone}: {qr_media_url}")
            
            return {
                'qr_image_url': qr_media_url,
                'qr_file_path': qr_path,
                'stone_url': stone_url,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Failed to generate QR code for stone {stone.PK_stone}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def _create_image_with_text(cls, qr_img, url_text):
        """
        Create a 3:4 portrait image with QR code at top and readable URL at bottom
        """
        # Calculate dimensions
        qr_size = cls.DEFAULT_QR_SIZE
        # Handle older PIL versions that don't have Image.Resampling
        try:
            resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            resample_method = Image.LANCZOS
        qr_img = qr_img.resize((qr_size, qr_size), resample_method)
        
        # Calculate total image size for 3:4 aspect ratio
        total_height = qr_size + cls.TEXT_AREA_HEIGHT
        total_width = int(3 * total_height / 4)
        
        # Create new image
        final_img = Image.new('RGB', (total_width, total_height), 'white')
        
        # Paste QR code centered at top
        qr_x = (total_width - qr_size) // 2
        final_img.paste(qr_img, (qr_x, 0))
        
        # Add text at bottom
        cls._add_readable_text(final_img, url_text, total_width, qr_size)
        
        return final_img
    
    @classmethod
    def _add_readable_text(cls, img, text, img_width, qr_bottom):
        """Add readable URL text below the QR code"""
        draw = ImageDraw.Draw(img)
        
        # Try different font sizes
        font_size = 16
        font = cls._get_font(font_size)
        
        # Calculate text dimensions (with fallback for older PIL versions)
        try:
            # Try newer textbbox method first
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            # Fallback to older textsize method
            text_width, text_height = draw.textsize(text, font=font)
        
        # If text is too wide, try smaller font
        if text_width > img_width - 20:
            font_size = 12
            font = cls._get_font(font_size)
            try:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            except AttributeError:
                text_width, text_height = draw.textsize(text, font=font)
        
        # If still too wide, wrap the text
        if text_width > img_width - 20:
            text_lines = cls._wrap_text(text, draw, font, img_width - 20)
        else:
            text_lines = [text]
        
        # Calculate starting position for text
        text_y = qr_bottom + 20
        line_height = text_height + 4
        
        for i, line in enumerate(text_lines):
            try:
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
            except AttributeError:
                line_width, _ = draw.textsize(line, font=font)
            line_x = (img_width - line_width) // 2
            
            # Draw background for text
            padding = 3
            bg_x1 = line_x - padding
            bg_y1 = text_y + (i * line_height) - padding
            bg_x2 = line_x + line_width + padding
            bg_y2 = text_y + (i * line_height) + line_height - padding
            
            draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], 
                          fill='#f5f5f5', outline='#ddd')
            
            # Draw the text
            draw.text((line_x, text_y + (i * line_height)), 
                     line, fill='#000000', font=font)
    
    @classmethod
    def _get_font(cls, size):
        """Get font with fallbacks"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Arial.ttf",
            "arial.ttf"
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except:
                continue
        
        # Fallback to default
        return ImageFont.load_default()
    
    @classmethod
    def _wrap_text(cls, text, draw, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                test_bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = test_bbox[2] - test_bbox[0]
            except AttributeError:
                test_width, _ = draw.textsize(test_line, font=font)
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word too long, force it
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    @classmethod
    def create_download_response(cls, stone, request=None):
        """
        Create an HTTP response for downloading the QR code with StoneWalker branding
        """
        try:
            # Generate enhanced QR code with branding for download
            enhanced_qr_result = cls.generate_enhanced_qr_for_download(stone, request)
            
            if not enhanced_qr_result['success']:
                return None
            
            # Create response with enhanced QR code
            response = HttpResponse(enhanced_qr_result['image_data'], content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{stone.PK_stone}_stonewalker_qr.png"'
            return response
                
        except Exception as e:
            logger.error(f"Failed to create download response for stone {stone.PK_stone}: {str(e)}")
            return None
    
    @classmethod
    def generate_enhanced_qr_for_download(cls, stone, request=None):
        """
        Generate an enhanced QR code with StoneWalker branding for download
        """
        try:
            # Generate the stone URL
            stone_url = stone.get_qr_url()
            
            # If we have a request, make it absolute
            if request:
                stone_url = request.build_absolute_uri(stone_url)
            
            # Create QR code optimized for small physical labels
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for durability
                box_size=8,  # Smaller box size for compact output
                border=2,    # Minimal border for space efficiency
            )
            qr.add_data(stone_url)
            qr.make(fit=True)
            
            # Generate QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Create enhanced image with branding
            enhanced_img = cls._create_enhanced_image_with_branding(qr_img, stone_url, stone.PK_stone)
            
            # Convert to bytes
            from io import BytesIO
            buffer = BytesIO()
            enhanced_img.save(buffer, format='PNG')
            image_data = buffer.getvalue()
            
            logger.info(f"Generated enhanced QR code for download: {stone.PK_stone}")
            
            return {
                'image_data': image_data,
                'stone_url': stone_url,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced QR code for stone {stone.PK_stone}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def _create_enhanced_image_with_branding(cls, qr_img, url_text, stone_name):
        """
        Create a compact QR code label for physical stones (2-5cm total size)
        """
        # Compact dimensions for stone labels
        qr_size = 200  # Much smaller QR code
        text_height = int(qr_size * 0.15)  # Text area is 15% of QR height
        padding = 4  # Minimal padding
        
        # Handle older PIL versions
        try:
            resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            resample_method = Image.LANCZOS
        
        qr_img = qr_img.resize((qr_size, qr_size), resample_method)
        
        # Compact layout: QR code + slim text underneath
        total_width = qr_size
        total_height = qr_size + text_height + padding
        
        # Create new image with white background
        final_img = Image.new('RGB', (total_width, total_height), 'white')
        
        # Paste QR code at top
        final_img.paste(qr_img, (0, 0))
        
        # Add compact text below QR code
        text_y = qr_size + 2  # Small gap
        cls._add_compact_text(final_img, total_width, text_y, text_height)
        
        return final_img
    
    @classmethod 
    def _add_compact_text(cls, img, img_width, text_y, text_height):
        """Add compact 'STONEWALKER.org' text underneath QR code for physical stones"""
        draw = ImageDraw.Draw(img)
        
        # Very small font for compact label
        font_size = max(8, int(text_height * 0.6))  # Font scales with available height
        font = cls._get_font(font_size)
        
        # Just the domain name
        text = "STONEWALKER.org"
        
        # Calculate text dimensions with fallback
        try:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height_actual = text_bbox[3] - text_bbox[1]
        except AttributeError:
            text_width, text_height_actual = draw.textsize(text, font=font)
        
        # Center the text
        text_x = (img_width - text_width) // 2
        text_y_centered = text_y + (text_height - text_height_actual) // 2
        
        # Draw text in dark gray
        draw.text((text_x, text_y_centered), text, fill='#333333', font=font)