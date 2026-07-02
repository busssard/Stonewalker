"""
PDF Service for generating QR code pack sheets.
Creates printable PDF with multiple QR codes in a grid layout.
Designed to match the single QR download style: black & white, toner-friendly.
"""
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from django.conf import settings
from django.http import FileResponse
import logging

logger = logging.getLogger(__name__)


class PDFService:
    """Generate printable PDF sheets with QR codes for stone packs."""

    # A4 page dimensions in points (1 point = 1/72 inch)
    PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 x 841.89 points

    # Each label's printed content (QR + text) is 30mm x 35mm: a 30x30mm QR with
    # the link + stone number in the 5mm strip beneath it.
    LABEL_W = 30 * mm
    LABEL_H = 35 * mm
    TEXT_STRIP = 5 * mm
    # A rounded cutting guide is drawn this far out from the label content.
    CUT_MARGIN = 3 * mm
    # Minimum gap between adjacent cut boxes; any leftover space is distributed
    # evenly so labels sit evenly spaced across the page.
    MIN_GUTTER = 2.5 * mm

    # Margins (in mm, converted to points). Top leaves room for the logo header
    # and the application instructions.
    MARGIN_TOP = 32 * mm
    MARGIN_BOTTOM = 12 * mm
    MARGIN_LEFT = 12 * mm
    MARGIN_RIGHT = 12 * mm

    # Colors — black & white only for toner-friendly output
    COLOR_BLACK = HexColor('#000000')
    COLOR_DARK_GRAY = HexColor('#333333')
    COLOR_MID_GRAY = HexColor('#999999')
    COLOR_LIGHT_GRAY = HexColor('#CCCCCC')
    COLOR_CUT_LINE = HexColor('#9A9A9A')

    # Cached PNG of the "StoneWalker" wordmark in the MainLogo (GiantBoom) font.
    _title_png = None

    @classmethod
    def generate_pack_pdf(cls, pack, stones):
        """
        Generate a PDF with all QR codes for a pack.

        Args:
            pack: QRPack instance
            stones: List of Stone instances with QR codes

        Returns:
            str: Path to the generated PDF file
        """
        # Each label gets a rounded cut box 3mm out from its content, and the
        # boxes are spread with even gutters across the usable area.
        cut_w = cls.LABEL_W + 2 * cls.CUT_MARGIN
        cut_h = cls.LABEL_H + 2 * cls.CUT_MARGIN
        usable_width = cls.PAGE_WIDTH - cls.MARGIN_LEFT - cls.MARGIN_RIGHT
        usable_height = cls.PAGE_HEIGHT - cls.MARGIN_TOP - cls.MARGIN_BOTTOM
        cols = max(1, int((usable_width + cls.MIN_GUTTER) / (cut_w + cls.MIN_GUTTER)))
        rows = max(1, int((usable_height + cls.MIN_GUTTER) / (cut_h + cls.MIN_GUTTER)))
        per_page = cols * rows
        # Distribute leftover space as equal gutters (including the outer edges),
        # so columns and rows are evenly spaced.
        gutter_x = (usable_width - cols * cut_w) / (cols + 1)
        gutter_y = (usable_height - rows * cut_h) / (rows + 1)

        # Create PDF buffer
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        cls._add_header(c)

        for idx, stone in enumerate(stones):
            # New page when the current one is full.
            if idx > 0 and idx % per_page == 0:
                cls._add_footer(c)
                c.showPage()
                cls._add_header(c)

            pos = idx % per_page
            row = pos // cols
            col = pos % cols
            cut_x = cls.MARGIN_LEFT + gutter_x * (col + 1) + cut_w * col
            cut_y = cls.PAGE_HEIGHT - cls.MARGIN_TOP - gutter_y * (row + 1) - cut_h * (row + 1)
            cls._add_qr_label(c, stone, cut_x, cut_y, cut_w, cut_h)

        # Add footer
        cls._add_footer(c)

        c.save()

        # Ensure output directory exists
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'qr_packs')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f'{pack.id}.pdf')

        # Write to file
        with open(pdf_path, 'wb') as f:
            f.write(buffer.getvalue())

        logger.info(f"Generated PDF for pack {pack.id}: {pdf_path}")
        return pdf_path

    @classmethod
    def _title_image(cls):
        """Rasterise the 'StoneWalker' wordmark in the MainLogo (GiantBoom) font
        to a transparent PNG (cached). reportlab can't embed the CFF/OTF font
        directly, so we render it with PIL/FreeType and place it as an image."""
        if cls._title_png is not None:
            return cls._title_png
        cls._title_png = b''
        try:
            from PIL import Image, ImageDraw, ImageFont
            candidates = [
                os.path.join(str(d), 'fonts/GiantBoomDEMO/GiantBoomFont.otf')
                for d in getattr(settings, 'STATICFILES_DIRS', [])
            ]
            candidates.append(os.path.join(
                str(getattr(settings, 'BASE_DIR', '')),
                'content/assets/fonts/GiantBoomDEMO/GiantBoomFont.otf'))
            font_path = next((p for p in candidates if p and os.path.exists(p)), None)
            if not font_path:
                logger.warning("GiantBoom font not found; using text fallback for PDF header")
                return cls._title_png
            font = ImageFont.truetype(font_path, 160)
            text = "StoneWalker"
            bbox = ImageDraw.Draw(Image.new('RGBA', (10, 10))).textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            pad = 24
            img = Image.new('RGBA', (tw + 2 * pad, th + 2 * pad), (255, 255, 255, 0))
            ImageDraw.Draw(img).text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=(20, 20, 20, 255))
            buf = BytesIO()
            img.save(buf, format='PNG')
            cls._title_png = buf.getvalue()
        except Exception as e:
            logger.warning(f"Could not render GiantBoom title image: {e}")
        return cls._title_png

    @classmethod
    def _add_header(cls, c):
        """Logo wordmark + application instructions at the top of each page."""
        top = cls.PAGE_HEIGHT - 5 * mm
        title = cls._title_image()
        if title:
            reader = ImageReader(BytesIO(title))
            iw, ih = reader.getSize()
            target_h = 13 * mm
            target_w = target_h * iw / ih
            max_w = 70 * mm
            if target_w > max_w:
                target_w = max_w
                target_h = target_w * ih / iw
            c.drawImage(reader, (cls.PAGE_WIDTH - target_w) / 2, top - target_h,
                        width=target_w, height=target_h, mask='auto')
            text_bottom = top - target_h
        else:
            c.setFillColor(cls.COLOR_BLACK)
            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(cls.PAGE_WIDTH / 2, top - 8 * mm, "StoneWalker")
            text_bottom = top - 12 * mm

        # Application instructions.
        c.setFillColor(cls.COLOR_DARK_GRAY)
        c.setFont("Helvetica", 8.5)
        c.drawCentredString(
            cls.PAGE_WIDTH / 2, text_bottom - 4.5 * mm,
            "1) Cut out — rounded corners work better   2) Glue on (Gorilla Glue works well)   3) Coat to weatherproof")
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(
            cls.PAGE_WIDTH / 2, text_bottom - 8.5 * mm,
            "Weatherproofing: epoxy, clear nail polish, or varnish.")

        # Thin separator line above the label grid.
        line_y = cls.PAGE_HEIGHT - cls.MARGIN_TOP + 2 * mm
        c.setStrokeColor(cls.COLOR_LIGHT_GRAY)
        c.setLineWidth(0.5)
        c.line(cls.MARGIN_LEFT, line_y, cls.PAGE_WIDTH - cls.MARGIN_RIGHT, line_y)

    @classmethod
    def _add_qr_label(cls, c, stone, cut_x, cut_y, cut_w, cut_h):
        """
        Draw one label inside its rounded cut box: a 30x30mm QR with the link +
        stone number in the 5mm strip beneath, and a rounded dashed cutting guide
        3mm out from the content.
        """
        import qrcode
        from qrcode.constants import ERROR_CORRECT_H

        # Rounded dashed cutting guide.
        c.saveState()
        c.setDash(2, 2)
        c.setStrokeColor(cls.COLOR_CUT_LINE)
        c.setLineWidth(0.5)
        c.roundRect(cut_x, cut_y, cut_w, cut_h, cls.CUT_MARGIN)
        c.restoreState()

        content_x = cut_x + cls.CUT_MARGIN
        content_y = cut_y + cls.CUT_MARGIN
        qr_side = cls.LABEL_W  # 30mm square, filling the content width
        qr_x = content_x
        qr_y = content_y + cls.TEXT_STRIP

        # Plain high-error-correction QR (its own quiet-zone border keeps it
        # scannable).
        try:
            qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=2)
            qr.add_data(stone.get_qr_url())
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            c.drawImage(ImageReader(buf), qr_x, qr_y, width=qr_side, height=qr_side)
        except Exception as e:
            logger.warning(f"Could not render QR for {stone.PK_stone}: {e}")
            cls._draw_qr_placeholder(c, qr_x, qr_y, qr_side)

        # Text strip beneath the QR: the link, then the stone number.
        cx = content_x + cls.LABEL_W / 2
        c.setFillColor(cls.COLOR_BLACK)
        c.setFont("Helvetica", 5)
        c.drawCentredString(cx, content_y + 2.9 * mm, f"stonewalker.org/stone-link/{stone.stone_number}")
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(cx, content_y + 0.8 * mm, f"Stone #{stone.stone_number}")

    @classmethod
    def _draw_qr_placeholder(cls, c, x, y, size):
        """Draw a placeholder box when QR image is missing."""
        c.saveState()
        c.setStrokeColor(cls.COLOR_LIGHT_GRAY)
        c.setLineWidth(0.5)
        c.rect(x, y, size, size)
        c.setFillColor(cls.COLOR_MID_GRAY)
        c.setFont("Helvetica", 9)
        c.drawCentredString(x + size / 2, y + size / 2 - 4, "QR Code")
        c.restoreState()

    @classmethod
    def _add_footer(cls, c):
        """Add a minimal footer."""
        c.setFillColor(cls.COLOR_MID_GRAY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cls.PAGE_WIDTH / 2, 6 * mm, "stonewalker.org")

    @classmethod
    def get_download_response(cls, pack):
        """
        Create HTTP response for downloading pack PDF.

        Args:
            pack: QRPack instance

        Returns:
            FileResponse or None if PDF doesn't exist
        """
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'qr_packs', f'{pack.id}.pdf')

        if not os.path.exists(pdf_path):
            logger.warning(f"PDF not found for pack {pack.id}")
            return None

        try:
            return FileResponse(
                open(pdf_path, 'rb'),
                as_attachment=True,
                filename=f'stonewalker_qr_pack_{pack.id}.pdf',
                content_type='application/pdf'
            )
        except Exception as e:
            logger.error(f"Failed to create download response for pack {pack.id}: {e}")
            return None

    @classmethod
    def pdf_exists(cls, pack):
        """
        Check if PDF exists for a pack.

        Args:
            pack: QRPack instance

        Returns:
            bool: True if PDF file exists
        """
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'qr_packs', f'{pack.id}.pdf')
        return os.path.exists(pdf_path)
