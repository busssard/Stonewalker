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

    # Fixed label size: each QR label (QR + link + stone number) prints at
    # 30mm wide x 35mm tall. As many as fit are tiled per A4 page, paginating
    # across pages for larger packs.
    LABEL_W = 30 * mm
    LABEL_H = 35 * mm

    # Margins (in mm, converted to points)
    MARGIN_TOP = 22 * mm
    MARGIN_BOTTOM = 16 * mm
    MARGIN_LEFT = 15 * mm
    MARGIN_RIGHT = 15 * mm

    # Colors — black & white only for toner-friendly output
    COLOR_BLACK = HexColor('#000000')
    COLOR_DARK_GRAY = HexColor('#333333')
    COLOR_MID_GRAY = HexColor('#999999')
    COLOR_LIGHT_GRAY = HexColor('#CCCCCC')
    COLOR_CUT_LINE = HexColor('#BBBBBB')

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
        # Fixed 30x35mm labels tiled across the usable area.
        usable_width = cls.PAGE_WIDTH - cls.MARGIN_LEFT - cls.MARGIN_RIGHT
        usable_height = cls.PAGE_HEIGHT - cls.MARGIN_TOP - cls.MARGIN_BOTTOM
        cols = max(1, int(usable_width // cls.LABEL_W))
        rows = max(1, int(usable_height // cls.LABEL_H))
        per_page = cols * rows
        # Centre the grid horizontally within the usable width.
        x_offset = cls.MARGIN_LEFT + (usable_width - cols * cls.LABEL_W) / 2

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
            x = x_offset + (col * cls.LABEL_W)
            y = cls.PAGE_HEIGHT - cls.MARGIN_TOP - ((row + 1) * cls.LABEL_H)
            cls._add_qr_cell(c, stone, x, y, cls.LABEL_W, cls.LABEL_H)

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
    def _add_header(cls, c):
        """Add minimal black & white header."""
        # "STONEWALKER" title in bold black
        c.setFillColor(cls.COLOR_BLACK)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(cls.PAGE_WIDTH / 2, cls.PAGE_HEIGHT - 14 * mm, "STONEWALKER.org")

        # Thin separator line
        line_y = cls.PAGE_HEIGHT - 17.5 * mm
        c.setStrokeColor(cls.COLOR_LIGHT_GRAY)
        c.setLineWidth(0.5)
        c.line(cls.MARGIN_LEFT, line_y, cls.PAGE_WIDTH - cls.MARGIN_RIGHT, line_y)

    # Height of the text strip beneath the QR (the "5mm" under a 30x30 QR).
    TEXT_STRIP = 5 * mm

    @classmethod
    def _add_qr_cell(cls, c, stone, x, y, cell_width, cell_height):
        """
        Draw a 30x35mm label: a 30x30mm QR square on top, and the link + stone
        number in the 5mm strip beneath it.
        """
        import qrcode
        from qrcode.constants import ERROR_CORRECT_H

        # Light dashed cut border around the label.
        c.saveState()
        c.setDash(2, 3)
        c.setStrokeColor(cls.COLOR_CUT_LINE)
        c.setLineWidth(0.4)
        c.rect(x, y, cell_width, cell_height)
        c.restoreState()

        qr_area = cell_height - cls.TEXT_STRIP  # 30mm for a 30x35 cell
        qr_side = min(cell_width, qr_area)       # 30mm square

        # Build a plain, high-error-correction QR (its own quiet-zone border
        # keeps it scannable even flush to the cut line).
        try:
            qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=2)
            qr.add_data(stone.get_qr_url())
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            qr_x = x + (cell_width - qr_side) / 2
            qr_y = y + cls.TEXT_STRIP + (qr_area - qr_side) / 2
            c.drawImage(ImageReader(buf), qr_x, qr_y, width=qr_side, height=qr_side)
        except Exception as e:
            logger.warning(f"Could not render QR for {stone.PK_stone}: {e}")
            cls._draw_qr_placeholder(c, x + 1 * mm, y + cls.TEXT_STRIP, qr_area - 2 * mm)

        # Text strip beneath the QR: the link, then the stone number.
        cx = x + cell_width / 2
        c.setFillColor(cls.COLOR_BLACK)
        c.setFont("Helvetica", 5)
        c.drawCentredString(cx, y + 2.9 * mm, f"stonewalker.org/stone-link/{stone.stone_number}")
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(cx, y + 0.8 * mm, f"Stone #{stone.stone_number}")

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
        """Add minimal footer."""
        footer_y = 8 * mm

        # Thin separator line
        c.setStrokeColor(cls.COLOR_LIGHT_GRAY)
        c.setLineWidth(0.5)
        c.line(cls.MARGIN_LEFT, footer_y + 5 * mm, cls.PAGE_WIDTH - cls.MARGIN_RIGHT, footer_y + 5 * mm)

        # Instruction text
        c.setFillColor(cls.COLOR_DARK_GRAY)
        c.setFont("Helvetica", 8)
        c.drawCentredString(
            cls.PAGE_WIDTH / 2,
            footer_y + 1 * mm,
            "Cut out each QR code and attach to your painted stone  |  stonewalker.org"
        )

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
