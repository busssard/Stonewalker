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

    # Grid layout: 2 columns x 5 rows = 10 QR codes
    COLS = 2
    ROWS = 5

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
        # Calculate cell dimensions
        usable_width = cls.PAGE_WIDTH - cls.MARGIN_LEFT - cls.MARGIN_RIGHT
        usable_height = cls.PAGE_HEIGHT - cls.MARGIN_TOP - cls.MARGIN_BOTTOM
        cell_width = usable_width / cls.COLS
        cell_height = usable_height / cls.ROWS

        # Create PDF buffer
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        # Add header
        cls._add_header(c)

        # Add QR codes in grid
        for idx, stone in enumerate(stones[:10]):  # Max 10 per page
            row = idx // cls.COLS
            col = idx % cls.COLS
            cls._add_qr_cell(c, stone, row, col, idx + 1, cell_width, cell_height)

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

    @classmethod
    def _add_qr_cell(cls, c, stone, row, col, number, cell_width, cell_height):
        """
        Add a single QR code cell using the same enhanced QR image
        as the single-stone download (via QRCodeService).
        """
        from .qr_service import QRCodeService

        # Calculate cell position (from top-left)
        x = cls.MARGIN_LEFT + (col * cell_width)
        y = cls.PAGE_HEIGHT - cls.MARGIN_TOP - ((row + 1) * cell_height)

        # Draw light dashed border for cutting guide
        c.saveState()
        c.setDash(3, 5)
        c.setStrokeColor(cls.COLOR_CUT_LINE)
        c.setLineWidth(0.4)
        c.rect(x, y, cell_width, cell_height)
        c.restoreState()

        # Scissors icon hint at top-left corner
        c.setFillColor(cls.COLOR_CUT_LINE)
        c.setFont("Helvetica", 7)
        c.drawString(x + 1.5 * mm, y + cell_height - 4 * mm, "- - -")

        # Generate the enhanced QR image (same as single download)
        result = QRCodeService.generate_enhanced_qr_for_download(stone)

        if result['success']:
            try:
                qr_img = ImageReader(BytesIO(result['image_data']))

                # The enhanced image is 200x250 (3:4-ish with branding text).
                # Fit it within the cell with padding.
                side_padding = 6 * mm
                top_padding = 5 * mm
                bottom_padding = 3 * mm
                available_width = cell_width - (2 * side_padding)
                available_height = cell_height - top_padding - bottom_padding

                # Get the actual image aspect ratio (width:height)
                img_width, img_height = qr_img.getSize()
                aspect = img_width / img_height

                # Scale to fit within available space, preserving aspect ratio
                if available_width / available_height > aspect:
                    # Height-constrained
                    draw_height = available_height
                    draw_width = draw_height * aspect
                else:
                    # Width-constrained
                    draw_width = available_width
                    draw_height = draw_width / aspect

                # Center within cell
                qr_x = x + (cell_width - draw_width) / 2
                qr_y = y + bottom_padding + (available_height - draw_height) / 2

                c.drawImage(qr_img, qr_x, qr_y, width=draw_width, height=draw_height)
            except Exception as e:
                logger.warning(f"Could not render enhanced QR for {stone.PK_stone}: {e}")
                cls._draw_qr_placeholder(c, x + 6 * mm, y + 3 * mm, cell_width - 12 * mm)
        else:
            logger.warning(f"Failed to generate enhanced QR for {stone.PK_stone}: {result.get('error')}")
            cls._draw_qr_placeholder(c, x + 6 * mm, y + 3 * mm, cell_width - 12 * mm)

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
