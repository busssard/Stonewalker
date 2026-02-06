"""
PDF Service for generating QR code pack sheets.
Creates printable PDF with multiple QR codes in a grid layout.
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
    MARGIN_TOP = 25 * mm
    MARGIN_BOTTOM = 20 * mm
    MARGIN_LEFT = 15 * mm
    MARGIN_RIGHT = 15 * mm

    # Colors
    COLOR_PRIMARY = HexColor('#4CAF50')
    COLOR_TEXT = HexColor('#333333')
    COLOR_LIGHT_GRAY = HexColor('#CCCCCC')
    COLOR_LIGHT_BG = HexColor('#F5F5F5')

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

        # Add header with branding
        cls._add_header(c)

        # Add QR codes in grid
        for idx, stone in enumerate(stones[:10]):  # Max 10 per page
            row = idx // cls.COLS
            col = idx % cls.COLS
            cls._add_qr_cell(c, stone, row, col, idx + 1, cell_width, cell_height)

        # Add footer with instructions
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
        """Add StoneWalker header to the PDF."""
        # Logo/title area
        c.setFillColor(cls.COLOR_PRIMARY)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(cls.PAGE_WIDTH / 2, cls.PAGE_HEIGHT - 18 * mm, "StoneWalker")

        # Subtitle
        c.setFillColor(cls.COLOR_TEXT)
        c.setFont("Helvetica", 11)
        c.drawCentredString(
            cls.PAGE_WIDTH / 2,
            cls.PAGE_HEIGHT - 24 * mm,
            "QR Code Pack - Cut out each code and attach to your painted stone"
        )

    @classmethod
    def _add_qr_cell(cls, c, stone, row, col, number, cell_width, cell_height):
        """Add a single QR code cell to the PDF."""
        # Calculate cell position (from top-left)
        x = cls.MARGIN_LEFT + (col * cell_width)
        y = cls.PAGE_HEIGHT - cls.MARGIN_TOP - ((row + 1) * cell_height)

        # Draw dashed border for cutting guide
        c.saveState()
        c.setDash(4, 4)
        c.setStrokeColor(cls.COLOR_LIGHT_GRAY)
        c.setLineWidth(0.5)
        c.rect(x, y, cell_width, cell_height)
        c.restoreState()

        # QR code sizing - leave space for number and name field
        qr_size = min(cell_width, cell_height) * 0.65
        qr_x = x + (cell_width - qr_size) / 2
        qr_y = y + cell_height - qr_size - 12 * mm  # Space from top for number

        # Draw stone number in corner
        c.setFillColor(cls.COLOR_PRIMARY)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 3 * mm, y + cell_height - 8 * mm, f"#{number}")

        # Load and draw QR code image
        qr_path = os.path.join(
            settings.MEDIA_ROOT,
            'qr_codes',
            f'{stone.PK_stone}_{stone.uuid}.png'
        )

        if os.path.exists(qr_path):
            try:
                qr_img = ImageReader(qr_path)
                c.drawImage(qr_img, qr_x, qr_y, width=qr_size, height=qr_size)
            except Exception as e:
                logger.warning(f"Could not load QR image for {stone.PK_stone}: {e}")
                # Draw placeholder
                c.setStrokeColor(cls.COLOR_LIGHT_GRAY)
                c.rect(qr_x, qr_y, qr_size, qr_size)
                c.setFillColor(cls.COLOR_TEXT)
                c.setFont("Helvetica", 10)
                c.drawCentredString(
                    qr_x + qr_size / 2,
                    qr_y + qr_size / 2,
                    "QR Code"
                )
        else:
            # Draw placeholder if QR not found
            c.setStrokeColor(cls.COLOR_LIGHT_GRAY)
            c.rect(qr_x, qr_y, qr_size, qr_size)
            c.setFillColor(cls.COLOR_TEXT)
            c.setFont("Helvetica", 10)
            c.drawCentredString(
                qr_x + qr_size / 2,
                qr_y + qr_size / 2,
                "QR Code"
            )

        # Add "Stone name:" line at the bottom of the cell
        line_y = y + 8 * mm
        c.setFillColor(cls.COLOR_TEXT)
        c.setFont("Helvetica", 9)
        c.drawString(x + 8 * mm, line_y, "Stone name:")

        # Draw underline for writing
        line_start_x = x + 30 * mm
        line_end_x = x + cell_width - 8 * mm
        c.setStrokeColor(cls.COLOR_LIGHT_GRAY)
        c.setLineWidth(0.5)
        c.line(line_start_x, line_y - 1, line_end_x, line_y - 1)

    @classmethod
    def _add_footer(cls, c):
        """Add footer with instructions."""
        footer_y = 10 * mm

        # Instructions
        c.setFillColor(cls.COLOR_TEXT)
        c.setFont("Helvetica", 9)
        c.drawCentredString(
            cls.PAGE_WIDTH / 2,
            footer_y + 3 * mm,
            "Scan any QR code to claim and name your stone at stonewalker.org"
        )

        # Copyright/branding
        c.setFont("Helvetica", 7)
        c.setFillColor(cls.COLOR_LIGHT_GRAY)
        c.drawCentredString(
            cls.PAGE_WIDTH / 2,
            footer_y - 2 * mm,
            "stonewalker.org"
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
