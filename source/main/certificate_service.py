"""
Certificate Service for generating stone creation certificates as PDF.
Creates a professional, print-ready A4 certificate using reportlab.
"""

import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from django.conf import settings
from django.utils.translation import gettext as _
import logging
import qrcode

logger = logging.getLogger(__name__)


class CertificateService:
    """Generate a printable stone creation certificate as PDF."""

    PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 x 841.89 points

    # Colors
    COLOR_PRIMARY = HexColor('#4CAF50')
    COLOR_PRIMARY_DARK = HexColor('#388E3C')
    COLOR_TEXT = HexColor('#333333')
    COLOR_LIGHT_TEXT = HexColor('#666666')
    COLOR_BORDER = HexColor('#E0E0E0')
    COLOR_GOLD = HexColor('#D4AF37')

    @classmethod
    def generate_certificate(cls, stone):
        """
        Generate a certificate PDF for a stone.

        Args:
            stone: Stone model instance

        Returns:
            bytes: PDF file content
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        cls._draw_border(c)
        cls._draw_header(c)
        cls._draw_stone_image(c, stone)
        cls._draw_certification_text(c, stone)
        cls._draw_stone_details(c, stone)
        cls._draw_qr_code(c, stone)
        cls._draw_footer(c)

        c.save()
        return buffer.getvalue()

    @classmethod
    def _draw_border(cls, c):
        """Draw a decorative border around the certificate"""
        margin = 15 * mm
        # Outer border
        c.setStrokeColor(cls.COLOR_PRIMARY)
        c.setLineWidth(2)
        c.rect(margin, margin, cls.PAGE_WIDTH - 2 * margin, cls.PAGE_HEIGHT - 2 * margin)

        # Inner border
        inner_margin = 18 * mm
        c.setStrokeColor(cls.COLOR_BORDER)
        c.setLineWidth(0.5)
        c.rect(inner_margin, inner_margin,
               cls.PAGE_WIDTH - 2 * inner_margin,
               cls.PAGE_HEIGHT - 2 * inner_margin)

    @classmethod
    def _draw_header(cls, c):
        """Draw the StoneWalker branding header"""
        center_x = cls.PAGE_WIDTH / 2

        # Main title
        c.setFillColor(cls.COLOR_PRIMARY)
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(center_x, cls.PAGE_HEIGHT - 50 * mm, "StoneWalker")

        # Subtitle
        c.setFillColor(cls.COLOR_GOLD)
        c.setFont("Helvetica", 16)
        c.drawCentredString(center_x, cls.PAGE_HEIGHT - 60 * mm, _("Certificate of Creation"))

        # Decorative line
        line_y = cls.PAGE_HEIGHT - 65 * mm
        c.setStrokeColor(cls.COLOR_PRIMARY)
        c.setLineWidth(1)
        c.line(center_x - 80 * mm, line_y, center_x + 80 * mm, line_y)

    @classmethod
    def _draw_stone_image(cls, c, stone):
        """Draw the stone's image if available"""
        center_x = cls.PAGE_WIDTH / 2
        img_size = 50 * mm
        img_y = cls.PAGE_HEIGHT - 125 * mm

        if stone.image:
            try:
                img_path = os.path.join(settings.MEDIA_ROOT, stone.image.name)
                if os.path.exists(img_path):
                    img = ImageReader(img_path)
                    c.drawImage(
                        img,
                        center_x - img_size / 2,
                        img_y,
                        width=img_size,
                        height=img_size,
                        preserveAspectRatio=True,
                        anchor='c'
                    )
                    return
            except Exception as e:
                logger.warning(f"Could not load stone image for certificate: {e}")

        # Placeholder circle if no image
        c.setStrokeColor(cls.COLOR_BORDER)
        c.setLineWidth(1)
        c.setFillColor(HexColor(stone.color or '#4CAF50'))
        c.circle(center_x, img_y + img_size / 2, img_size / 3, fill=1, stroke=1)

    @classmethod
    def _draw_certification_text(cls, c, stone):
        """Draw the main certification text"""
        center_x = cls.PAGE_WIDTH / 2
        text_y = cls.PAGE_HEIGHT - 145 * mm

        c.setFillColor(cls.COLOR_TEXT)
        c.setFont("Helvetica", 13)
        c.drawCentredString(center_x, text_y, _("This certifies that"))

        # Username - prominent
        username = stone.FK_user.username if stone.FK_user else _("Unknown")
        c.setFillColor(cls.COLOR_PRIMARY_DARK)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(center_x, text_y - 20, username)

        c.setFillColor(cls.COLOR_TEXT)
        c.setFont("Helvetica", 13)
        c.drawCentredString(center_x, text_y - 42, _("is the creator of"))

        # Stone name - large and prominent
        c.setFillColor(cls.COLOR_PRIMARY)
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(center_x, text_y - 65, stone.PK_stone)

        # Stone number
        stone_number = stone.get_stone_number()
        if stone_number is not None:
            c.setFillColor(cls.COLOR_GOLD)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(center_x, text_y - 88, f"Stone #{stone_number}")

    @classmethod
    def _draw_stone_details(cls, c, stone):
        """Draw stone details section"""
        center_x = cls.PAGE_WIDTH / 2
        details_y = cls.PAGE_HEIGHT - 260 * mm

        # Decorative line above details
        c.setStrokeColor(cls.COLOR_BORDER)
        c.setLineWidth(0.5)
        c.line(center_x - 60 * mm, details_y + 15 * mm,
               center_x + 60 * mm, details_y + 15 * mm)

        c.setFillColor(cls.COLOR_LIGHT_TEXT)
        c.setFont("Helvetica", 11)

        # Journey start date
        if stone.created_at:
            date_str = stone.created_at.strftime('%B %d, %Y')
            c.drawCentredString(
                center_x, details_y,
                _("Journey started on %(date)s") % {'date': date_str}
            )

        # Stone type
        type_display = stone.get_stone_type_display() if hasattr(stone, 'get_stone_type_display') else stone.stone_type
        c.drawCentredString(
            center_x, details_y - 16,
            _("Type: %(type)s") % {'type': type_display}
        )

        # Description (truncated if long)
        if stone.description:
            desc = stone.description[:100]
            if len(stone.description) > 100:
                desc += "..."
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(center_x, details_y - 36, f'"{desc}"')

    @classmethod
    def _draw_qr_code(cls, c, stone):
        """Draw the stone's QR code on the certificate"""
        center_x = cls.PAGE_WIDTH / 2
        qr_size = 30 * mm
        qr_y = 55 * mm

        try:
            stone_url = stone.get_qr_url()

            # Generate QR code in memory
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=2,
            )
            qr.add_data(stone_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Convert PIL image to reportlab ImageReader
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            qr_reader = ImageReader(qr_buffer)

            c.drawImage(
                qr_reader,
                center_x - qr_size / 2,
                qr_y,
                width=qr_size,
                height=qr_size
            )

            # URL text under QR
            c.setFillColor(cls.COLOR_LIGHT_TEXT)
            c.setFont("Helvetica", 7)
            c.drawCentredString(center_x, qr_y - 4 * mm, stone_url)

        except Exception as e:
            logger.warning(f"Could not generate QR code for certificate: {e}")

    @classmethod
    def _draw_footer(cls, c):
        """Draw the footer with website URL"""
        center_x = cls.PAGE_WIDTH / 2

        # Decorative line
        c.setStrokeColor(cls.COLOR_BORDER)
        c.setLineWidth(0.5)
        c.line(center_x - 60 * mm, 40 * mm, center_x + 60 * mm, 40 * mm)

        # Website URL
        c.setFillColor(cls.COLOR_PRIMARY)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(center_x, 33 * mm, "stonewalker.org")

        # Tagline
        c.setFillColor(cls.COLOR_LIGHT_TEXT)
        c.setFont("Helvetica", 8)
        c.drawCentredString(center_x, 27 * mm, _("Track your painted stone's journey around the world"))
