"""
PDF generation service for Quoted.
Creates professional, minimalist quote documents from structured quote data.
Uses ReportLab for PDF generation with premium styling.
"""

import io
import os
import base64
from datetime import datetime, timedelta
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable,
    KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Circle, String
from reportlab.graphics import renderPDF


# Brand colors matching the website
BRAND_DARK = colors.HexColor('#0a0a0a')
BRAND_CARD = colors.HexColor('#1a1a1a')
BRAND_GRAY = colors.HexColor('#666666')
BRAND_LIGHT_GRAY = colors.HexColor('#a0a0a0')
BRAND_BORDER = colors.HexColor('#e5e5e5')
BRAND_BG_ALT = colors.HexColor('#fafafa')
BRAND_WHITE = colors.white


# ============================================================================
# PDF Template System (DISC-028)
# ============================================================================

PDF_TEMPLATES = {
    "classic": {
        "name": "Classic",
        "description": "Traditional professional look",
        "title_font": "Times-Roman",
        "body_font": "Helvetica",
        "header_color": "#000000",
        "accent_color": "#2563eb",  # Blue
        "bg_alt_color": "#f8fafc",
        "available_to": ["starter", "pro", "team"]
    },
    "modern": {
        "name": "Modern Minimal",
        "description": "Clean, contemporary design",
        "title_font": "Helvetica",
        "body_font": "Helvetica",
        "header_color": "#18181b",
        "accent_color": "#6366f1",  # Indigo
        "bg_alt_color": "#fafafa",
        "available_to": ["starter", "pro", "team"]
    },
    "bold": {
        "name": "Bold Professional",
        "description": "Strong, confident impression",
        "title_font": "Helvetica-Bold",
        "body_font": "Helvetica",
        "header_color": "#0f172a",
        "accent_color": "#dc2626",  # Red
        "bg_alt_color": "#f1f5f9",
        "available_to": ["pro", "team"]  # Pro+ only
    },
    "elegant": {
        "name": "Elegant",
        "description": "Sophisticated, premium feel",
        "title_font": "Times-Roman",
        "body_font": "Times-Roman",
        "header_color": "#1e293b",
        "accent_color": "#0d9488",  # Teal
        "bg_alt_color": "#f8fafc",
        "available_to": ["pro", "team"]  # Pro+ only
    },
    "technical": {
        "name": "Technical",
        "description": "Detailed, engineering-focused",
        "title_font": "Courier",
        "body_font": "Helvetica",
        "header_color": "#374151",
        "accent_color": "#4f46e5",  # Purple
        "bg_alt_color": "#f3f4f6",
        "available_to": ["pro", "team"]  # Pro+ only
    },
    "friendly": {
        "name": "Friendly",
        "description": "Warm, approachable style",
        "title_font": "Helvetica",
        "body_font": "Helvetica",
        "header_color": "#292524",
        "accent_color": "#f59e0b",  # Amber
        "bg_alt_color": "#fefce8",
        "available_to": ["starter", "pro", "team"]
    },
    "craftsman": {
        "name": "Craftsman",
        "description": "Rustic, handcrafted feel",
        "title_font": "Times-Bold",
        "body_font": "Times-Roman",
        "header_color": "#422006",
        "accent_color": "#92400e",  # Brown
        "bg_alt_color": "#fef3c7",
        "available_to": ["pro", "team"]  # Pro+ only
    },
    "corporate": {
        "name": "Corporate",
        "description": "Formal, business-oriented",
        "title_font": "Helvetica",
        "body_font": "Helvetica",
        "header_color": "#1e3a5f",
        "accent_color": "#1e40af",  # Dark blue
        "bg_alt_color": "#eff6ff",
        "available_to": ["team"]  # Team only
    },
    # DISC-072: New compact and detailed templates
    "compact": {
        "name": "Compact",
        "description": "Tight spacing for longer quotes",
        "title_font": "Helvetica",
        "body_font": "Helvetica",
        "header_color": "#18181b",
        "accent_color": "#475569",  # Slate
        "bg_alt_color": "#f8fafc",
        "available_to": ["starter", "pro", "team"],
        "spacing": "compact"  # Flag for reduced spacing
    },
    "detailed": {
        "name": "Detailed",
        "description": "Extra room for descriptions",
        "title_font": "Times-Roman",
        "body_font": "Helvetica",
        "header_color": "#1e293b",
        "accent_color": "#3b82f6",  # Blue
        "bg_alt_color": "#f1f5f9",
        "available_to": ["pro", "team"],
        "spacing": "detailed"  # Flag for increased spacing
    },
    "minimal": {
        "name": "Minimal",
        "description": "Ultra-clean, no distractions",
        "title_font": "Helvetica",
        "body_font": "Helvetica",
        "header_color": "#000000",
        "accent_color": "#000000",  # Black only
        "bg_alt_color": "#ffffff",
        "available_to": ["starter", "pro", "team"]
    }
}

# Accent color presets for Pro tier
ACCENT_COLORS = {
    "blue": "#2563eb",
    "indigo": "#6366f1",
    "purple": "#9333ea",
    "red": "#dc2626",
    "orange": "#ea580c",
    "amber": "#d97706",
    "green": "#16a34a",
    "teal": "#0d9488",
}


# DISC-066: Font name mapping for variants
# ReportLab uses specific names for font variants
FONT_BOLD_MAP = {
    "Helvetica": "Helvetica-Bold",
    "Times-Roman": "Times-Bold",
    "Courier": "Courier-Bold",
}

FONT_ITALIC_MAP = {
    "Helvetica": "Helvetica-Oblique",
    "Times-Roman": "Times-Italic",
    "Courier": "Courier-Oblique",
}


def get_bold_font(font_name: str) -> str:
    """Get the correct bold variant for a font name."""
    if "Bold" in font_name:
        return font_name
    return FONT_BOLD_MAP.get(font_name, font_name + "-Bold")


def get_italic_font(font_name: str) -> str:
    """Get the correct italic variant for a font name."""
    if "Italic" in font_name or "Oblique" in font_name:
        return font_name
    return FONT_ITALIC_MAP.get(font_name, font_name)


class LogoPlaceholder(Flowable):
    """
    A circular logo placeholder with the business initial.
    Clean, minimalist design for businesses without custom logos.
    """

    def __init__(self, initial: str, size: float = 48):
        Flowable.__init__(self)
        self.initial = initial.upper() if initial else "Q"
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        # Draw circle
        self.canv.setFillColor(BRAND_DARK)
        self.canv.circle(
            self.size / 2,
            self.size / 2,
            self.size / 2,
            fill=1,
            stroke=0
        )

        # Draw initial
        self.canv.setFillColor(BRAND_WHITE)
        self.canv.setFont('Helvetica', self.size * 0.45)

        # Center the text
        text_width = self.canv.stringWidth(self.initial, 'Helvetica', self.size * 0.45)
        x = (self.size - text_width) / 2
        y = self.size / 2 - self.size * 0.16  # Vertical centering adjustment

        self.canv.drawString(x, y, self.initial)


class HorizontalLine(Flowable):
    """A thin horizontal divider line."""

    def __init__(self, width: float, color=BRAND_BORDER, thickness: float = 0.5):
        Flowable.__init__(self)
        self.width = width
        self.line_color = color
        self.thickness = thickness
        self.height = thickness + 4  # Small padding

    def draw(self):
        self.canv.setStrokeColor(self.line_color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.height / 2, self.width, self.height / 2)


class PDFGeneratorService:
    """
    Generates professional PDF quotes with minimalist, premium styling.
    Matches the quoted.it website aesthetic.

    DISC-028: Now supports multiple template styles with accent color customization.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.page_width = letter[0] - 1.5 * inch  # Account for margins
        # Template-specific colors (set in _setup_custom_styles)
        self.template_colors = {}
        self._setup_custom_styles()  # Uses default template initially

    def _setup_custom_styles(self, template_key: str = "modern", accent_color: Optional[str] = None, prefer_one_page: bool = False):
        """
        Set up custom paragraph styles based on selected template.

        DISC-028: Template system - styles adapt to template selection.
        DISC-072: Added spacing support for compact/detailed templates.

        Args:
            template_key: Template identifier (e.g., "modern", "classic")
            accent_color: Optional hex color override for accent color
            prefer_one_page: If True, use aggressive compact styling for single-page output
        """
        # Get template config or fall back to modern
        template = PDF_TEMPLATES.get(template_key, PDF_TEMPLATES["modern"])

        # DISC-072: Get spacing mode (normal, compact, detailed)
        self.spacing_mode = template.get("spacing", "normal")

        # Apply accent color override if provided (Pro feature)
        if accent_color:
            # Check if it's a preset name or hex color
            if accent_color.startswith("#"):
                template["accent_color"] = accent_color
            elif accent_color in ACCENT_COLORS:
                template["accent_color"] = ACCENT_COLORS[accent_color]

        # Convert template colors to ReportLab color objects
        self.template_colors = {
            "header": colors.HexColor(template["header_color"]),
            "accent": colors.HexColor(template["accent_color"]),
            "bg_alt": colors.HexColor(template["bg_alt_color"]),
        }

        # DISC-066: Create fresh stylesheet each time to avoid deletion issues
        # StyleSheet1 doesn't support item deletion, so we recreate it
        self.styles = getSampleStyleSheet()

        # DISC-072: Spacing multipliers for different modes
        # prefer_one_page forces the most aggressive compaction
        if prefer_one_page:
            space_mult = 0.4  # 40% of normal spacing - very tight
            font_adj = -2  # Smaller fonts for one-page preference
        elif self.spacing_mode == "compact":
            space_mult = 0.6  # 60% of normal spacing
            font_adj = -1  # Slightly smaller fonts
        elif self.spacing_mode == "detailed":
            space_mult = 1.3  # 130% of normal spacing
            font_adj = 0
        else:
            space_mult = 1.0
            font_adj = 0

        # Store for use in line items table
        self._space_mult = space_mult
        self._font_adj = font_adj

        # Main title - uses template title font
        self.styles.add(ParagraphStyle(
            name='QuoteTitle',
            parent=self.styles['Heading1'],
            fontName=template["title_font"],
            fontSize=32 + font_adj,
            alignment=TA_LEFT,
            spaceAfter=int(8 * space_mult),
            spaceBefore=0,
            textColor=self.template_colors["header"],
            leading=38,
        ))

        # Quote number/date subtitle
        self.styles.add(ParagraphStyle(
            name='QuoteSubtitle',
            parent=self.styles['Normal'],
            fontName=template["body_font"],
            fontSize=11,
            alignment=TA_LEFT,
            textColor=BRAND_GRAY,
            spaceAfter=24,
        ))

        # Business name in header
        self.styles.add(ParagraphStyle(
            name='BusinessName',
            parent=self.styles['Normal'],
            fontName=get_bold_font(template["body_font"]),
            fontSize=14,
            alignment=TA_RIGHT,
            textColor=self.template_colors["header"],
            spaceAfter=2,
        ))

        # Contact info in header
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontName=template["body_font"],
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=BRAND_GRAY,
            leading=14,
        ))

        # Section headers - use accent color
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontName=get_bold_font(template["body_font"]),
            fontSize=10 + font_adj,
            spaceBefore=int(24 * space_mult),
            spaceAfter=int(12 * space_mult),
            textColor=self.template_colors["accent"],
            leading=12,
        ))

        # Body text (leading increased from 16 to 18 for better paragraph readability)
        self.styles.add(ParagraphStyle(
            name='QuoteBody',
            parent=self.styles['Normal'],
            fontName=template["body_font"],
            fontSize=11 + font_adj,
            leading=int(18 * space_mult) if space_mult != 0.6 else 15,
            spaceAfter=int(8 * space_mult),
            textColor=self.template_colors["header"],
        ))

        # Body text - light color (leading increased from 16 to 18 for better paragraph readability)
        self.styles.add(ParagraphStyle(
            name='QuoteBodyLight',
            parent=self.styles['Normal'],
            fontName=template["body_font"],
            fontSize=11 + font_adj,
            leading=int(18 * space_mult) if space_mult != 0.6 else 15,
            spaceAfter=int(4 * space_mult),
            textColor=BRAND_GRAY,
        ))

        # Customer name
        self.styles.add(ParagraphStyle(
            name='CustomerName',
            parent=self.styles['Normal'],
            fontName=get_bold_font(template["body_font"]),
            fontSize=12,
            textColor=self.template_colors["header"],
            spaceAfter=4,
        ))

        # Total amount - large and bold
        self.styles.add(ParagraphStyle(
            name='TotalLabel',
            parent=self.styles['Normal'],
            fontName=template["body_font"],
            fontSize=12,
            alignment=TA_RIGHT,
            textColor=BRAND_GRAY,
        ))

        self.styles.add(ParagraphStyle(
            name='TotalAmount',
            parent=self.styles['Normal'],
            fontName=get_bold_font(template["body_font"]),
            fontSize=24,
            alignment=TA_RIGHT,
            textColor=self.template_colors["accent"],  # Use accent color for total
        ))

        # Fine print / disclaimer
        self.styles.add(ParagraphStyle(
            name='FinePrint',
            parent=self.styles['Normal'],
            fontName=template["body_font"],
            fontSize=8,
            textColor=BRAND_LIGHT_GRAY,
            leading=11,
        ))

        # Footer branding
        self.styles.add(ParagraphStyle(
            name='FooterBrand',
            parent=self.styles['Normal'],
            fontName=get_italic_font(template["title_font"]) if template["title_font"] == 'Times-Roman' else template["body_font"],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=BRAND_LIGHT_GRAY,
        ))

    def generate_quote_pdf(
        self,
        quote_data: dict,
        contractor: dict,
        terms: Optional[dict] = None,
        output_path: Optional[str] = None,
        watermark: bool = False,
        watermark_text: Optional[str] = None,
        template: str = "modern",
        accent_color: Optional[str] = None,
        is_invoice: bool = False,
        prefer_one_page: bool = True,
    ) -> bytes:
        """
        Generate a professional PDF quote or invoice document.

        Args:
            quote_data: The structured quote data
            contractor: Contractor information
            terms: Terms and conditions
            output_path: Optional file path to save PDF
            watermark: If True, add watermark to PDF
            watermark_text: Custom watermark text (default: "TRIAL EXPIRED" for grace period, "DEMO" for demo)
            template: Template style key (DISC-028)
            accent_color: Optional accent color override (hex or preset name) (DISC-028)
            is_invoice: If True, generate as invoice instead of estimate (DISC-071)
            prefer_one_page: If True, aggressively optimize for single-page output

        Returns:
            PDF as bytes
        """
        # DISC-071: Store invoice mode for use in section builders
        self._is_invoice = is_invoice
        # Store one-page preference for use in section builders
        self._prefer_one_page = prefer_one_page
        # Store watermark text for use in callback
        self._watermark_text = watermark_text or "TRIAL EXPIRED"
        # DISC-028: Apply template styles before generating PDF
        self._setup_custom_styles(template_key=template, accent_color=accent_color, prefer_one_page=prefer_one_page)

        buffer = io.BytesIO()

        # Tighter margins when preferring one page
        if prefer_one_page:
            margins = {
                'rightMargin': 0.5 * inch,
                'leftMargin': 0.5 * inch,
                'topMargin': 0.4 * inch,
                'bottomMargin': 0.4 * inch,
            }
            # Update page_width to account for tighter margins
            self.page_width = letter[0] - 1.0 * inch
        else:
            margins = {
                'rightMargin': 0.75 * inch,
                'leftMargin': 0.75 * inch,
                'topMargin': 0.6 * inch,
                'bottomMargin': 0.6 * inch,
            }
            self.page_width = letter[0] - 1.5 * inch

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            **margins,
        )

        elements = []

        # Get spacing multiplier for one-page optimization
        space_mult = getattr(self, '_space_mult', 1.0)

        # DISC-066: Wrap each section with error handling for debugging
        try:
            # Header with logo and business info
            elements.extend(self._build_header(contractor, quote_data))
        except Exception as e:
            print(f"PDF error in _build_header: {e}")
            raise

        # Divider - reduced spacing for one-page preference
        elements.append(HorizontalLine(self.page_width))
        elements.append(Spacer(1, max(8, int(20 * space_mult))))

        try:
            # Title and date
            elements.extend(self._build_title_section(quote_data))
        except Exception as e:
            print(f"PDF error in _build_title_section: {e}")
            raise

        try:
            # Customer info (if available)
            elements.extend(self._build_customer_section(quote_data))
        except Exception as e:
            print(f"PDF error in _build_customer_section: {e}")
            raise

        try:
            # Project description
            elements.extend(self._build_description_section(quote_data))
        except Exception as e:
            print(f"PDF error in _build_description_section: {e}")
            raise

        try:
            # Line items
            elements.extend(self._build_line_items_section(quote_data))
        except Exception as e:
            print(f"PDF error in _build_line_items_section: {e}")
            raise

        try:
            # DISC-072: Keep total, details and footer together to prevent awkward page breaks
            # Build these sections but wrap them in KeepTogether
            total_elements = self._build_total_section(quote_data)
            divider_elements = [HorizontalLine(self.page_width), Spacer(1, max(6, int(16 * space_mult)))]
            details_elements = self._build_details_section(quote_data, terms)
            footer_elements = self._build_footer_section()

            # Combine total + divider + details + footer and keep together
            # This prevents the total from being separated from the summary
            summary_block = total_elements + divider_elements + details_elements + footer_elements
            elements.append(KeepTogether(summary_block))
        except Exception as e:
            print(f"PDF error in summary section: {e}")
            raise

        # DISC-018: Add watermark callback for grace quotes
        try:
            if watermark:
                doc.build(elements, onFirstPage=self._add_watermark, onLaterPages=self._add_watermark)
            else:
                doc.build(elements)
        except Exception as e:
            print(f"PDF error in doc.build: {e}")
            raise

        pdf_bytes = buffer.getvalue()
        buffer.close()

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)

        return pdf_bytes

    def _add_watermark(self, canvas, doc):
        """
        Add watermark to PDF page.

        DISC-018: For grace period quotes, add semi-transparent diagonal watermark.
        For demo quotes, shows "DEMO" watermark.
        """
        canvas.saveState()

        # Get watermark text (set in generate_quote_pdf)
        watermark_text = getattr(self, '_watermark_text', 'TRIAL EXPIRED')
        is_demo = watermark_text.upper() == "DEMO"

        # Semi-transparent color (blue for demo, red for trial)
        if is_demo:
            canvas.setFillColorRGB(0.3, 0.4, 0.9, alpha=0.12)
            canvas.setStrokeColorRGB(0.3, 0.4, 0.9, alpha=0.25)
        else:
            canvas.setFillColorRGB(0.9, 0.3, 0.3, alpha=0.15)
            canvas.setStrokeColorRGB(0.9, 0.3, 0.3, alpha=0.3)
        canvas.setLineWidth(2)

        # Center of page
        page_width = letter[0]
        page_height = letter[1]

        # Rotate and position text
        canvas.translate(page_width / 2, page_height / 2)
        canvas.rotate(45)

        # Large text
        canvas.setFont('Helvetica-Bold', 72)
        text_width = canvas.stringWidth(watermark_text, 'Helvetica-Bold', 72)

        # Draw text centered
        canvas.drawString(-text_width / 2, -36, watermark_text)

        # Add smaller subtitle
        canvas.setFont('Helvetica', 24)
        subtitle = "Sign up for your own pricing" if is_demo else "Upgrade to remove watermark"
        subtitle_width = canvas.stringWidth(subtitle, 'Helvetica', 24)
        canvas.drawString(-subtitle_width / 2, -70, subtitle)

        canvas.restoreState()

    def _build_header(self, contractor: dict, quote_data: dict) -> list:
        """Build the header with logo (custom or placeholder) and business info."""
        elements = []

        business_name = contractor.get('business_name', 'Your Business')
        initial = business_name[0] if business_name else 'Q'

        # Build contact info
        contact_lines = []
        if contractor.get('phone'):
            contact_lines.append(contractor['phone'])
        if contractor.get('email'):
            contact_lines.append(contractor['email'])
        if contractor.get('address'):
            contact_lines.append(contractor['address'])

        contact_text = '<br/>'.join(contact_lines) if contact_lines else ''

        # Create logo - use custom logo if available, otherwise placeholder
        logo_data = contractor.get('logo_data')
        logo = None
        if logo_data:
            # Custom logo from base64 data URI
            try:
                # Extract base64 data from data URI
                if logo_data.startswith('data:'):
                    # Format: data:image/png;base64,<base64_data>
                    base64_str = logo_data.split(',', 1)[1]
                else:
                    base64_str = logo_data

                # Decode base64 to binary
                logo_binary = base64.b64decode(base64_str)

                # DISC-066: Validate image before using (if PIL available)
                try:
                    from PIL import Image as PILImage
                    pil_img = PILImage.open(io.BytesIO(logo_binary))
                    pil_img.verify()  # Verify it's a valid image
                except ImportError:
                    pass  # PIL not installed, skip validation
                except Exception as pil_e:
                    print(f"Warning: Logo image validation failed: {pil_e}")
                    logo = LogoPlaceholder(initial, size=48)

                if logo is None:
                    # Create BytesIO object for ReportLab
                    logo_buffer = io.BytesIO(logo_binary)
                    # DISC-127: Preserve aspect ratio - calculate dimensions from actual image
                    max_height = 48
                    max_width = 120  # Allow wider logos
                    try:
                        from PIL import Image as PILImage
                        # Re-open image to get dimensions (verify() closes it)
                        logo_buffer.seek(0)
                        pil_img = PILImage.open(io.BytesIO(logo_binary))
                        orig_width, orig_height = pil_img.size
                        # Calculate scale to fit within max dimensions while preserving aspect ratio
                        scale = min(max_width / orig_width, max_height / orig_height)
                        scaled_width = orig_width * scale
                        scaled_height = orig_height * scale
                        logo_buffer.seek(0)
                        logo = Image(logo_buffer, width=scaled_width, height=scaled_height)
                    except ImportError:
                        # PIL not available - use fixed height, let ReportLab handle width
                        logo_buffer.seek(0)
                        logo = Image(logo_buffer, height=max_height)
            except Exception as e:
                # If logo fails to load, fall back to placeholder
                print(f"Warning: Failed to load custom logo: {e}")
                logo = LogoPlaceholder(initial, size=48)

        if logo is None:
            # Use placeholder logo
            logo = LogoPlaceholder(initial, size=48)

        # Business info column
        business_info = []
        business_info.append(Paragraph(business_name, self.styles['BusinessName']))
        if contact_text:
            business_info.append(Paragraph(contact_text, self.styles['ContactInfo']))

        # Combine into a table for layout
        header_data = [[logo, business_info]]

        # DISC-127: Increased first column to 130px to accommodate wider logos
        header_table = Table(
            header_data,
            colWidths=[130, self.page_width - 130],
            hAlign='LEFT',
        )

        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        elements.append(header_table)
        # Reduced spacer for one-page preference
        space_mult = getattr(self, '_space_mult', 1.0)
        elements.append(Spacer(1, max(6, int(16 * space_mult))))

        return elements

    def _build_title_section(self, quote_data: dict) -> list:
        """Build the title and date section."""
        elements = []

        # DISC-071: Use "Invoice" title for invoices, "Estimate" for quotes
        is_invoice = getattr(self, '_is_invoice', False)
        title = "Invoice" if is_invoice else "Estimate"
        elements.append(Paragraph(title, self.styles['QuoteTitle']))

        # Date and quote/invoice number
        if is_invoice:
            # For invoices, use invoice_date and invoice_number from data
            doc_date = quote_data.get('invoice_date', datetime.now().strftime("%B %d, %Y"))
            doc_num = quote_data.get('invoice_number', datetime.now().strftime("INV-%Y%m%d"))
            due_date = quote_data.get('due_date')
            subtitle = f"#{doc_num}  ·  {doc_date}"
            if due_date:
                subtitle += f"  ·  Due: {due_date}"
        else:
            doc_date = datetime.now().strftime("%B %d, %Y")
            doc_num = quote_data.get('quote_number', datetime.now().strftime("%Y%m%d%H%M"))
            subtitle = f"#{doc_num}  ·  {doc_date}"

        elements.append(Paragraph(subtitle, self.styles['QuoteSubtitle']))

        return elements

    def _build_customer_section(self, quote_data: dict) -> list:
        """Build the customer information section."""
        elements = []

        customer_name = quote_data.get('customer_name')
        customer_address = quote_data.get('customer_address')
        customer_phone = quote_data.get('customer_phone')

        if customer_name or customer_address:
            elements.append(Paragraph("PREPARED FOR", self.styles['SectionHeader']))

            if customer_name:
                elements.append(Paragraph(customer_name, self.styles['CustomerName']))

            if customer_address:
                elements.append(Paragraph(customer_address, self.styles['QuoteBodyLight']))

            if customer_phone:
                elements.append(Paragraph(customer_phone, self.styles['QuoteBodyLight']))

            elements.append(Spacer(1, 8))

        return elements

    def _build_description_section(self, quote_data: dict) -> list:
        """Build the project description section."""
        elements = []

        elements.append(Paragraph("PROJECT DESCRIPTION", self.styles['SectionHeader']))

        job_description = quote_data.get('job_description', 'No description provided.')
        elements.append(Paragraph(job_description, self.styles['QuoteBody']))

        return elements

    def _build_line_items_section(self, quote_data: dict) -> list:
        """Build the itemized pricing table with clean, minimal styling."""
        elements = []

        elements.append(Paragraph("LINE ITEMS", self.styles['SectionHeader']))

        line_items = quote_data.get('line_items', [])

        if not line_items:
            elements.append(Paragraph(
                "No line items specified.",
                self.styles['QuoteBodyLight']
            ))
            return elements

        # Build table data - simpler structure
        table_data = []

        for item in line_items:
            name = item.get('name', '')
            desc = item.get('description', '')
            # DISC-066: Force numeric types to prevent format string errors
            try:
                amount = float(item.get('amount', 0) or 0)
            except (ValueError, TypeError):
                amount = 0.0
            try:
                qty = float(item.get('quantity') or 1)
            except (ValueError, TypeError):
                qty = 1.0
            if qty <= 0:
                qty = 1.0
            unit = item.get('unit', '') or ''

            # Build quantity display when qty > 1 OR unit is specified
            qty_display = ""
            has_unit = bool(unit and unit.strip())
            if qty > 1 or has_unit:
                unit_price = amount / qty
                qty_display = f"<br/><font size='9' color='#666666'>Qty: {qty:g}"
                if has_unit:
                    qty_display += f" {unit}"
                qty_display += f" × ${unit_price:,.2f} = ${amount:,.2f}</font>"

            # Combine name, description, and quantity
            if desc and qty_display:
                item_text = f"<b>{name}</b><br/><font size='9' color='#666666'>{desc}</font>{qty_display}"
            elif desc:
                item_text = f"<b>{name}</b><br/><font size='9' color='#666666'>{desc}</font>"
            elif qty_display:
                item_text = f"<b>{name}</b>{qty_display}"
            else:
                item_text = f"<b>{name}</b>"

            table_data.append([
                Paragraph(item_text, ParagraphStyle(
                    name='ItemCell',
                    parent=self.styles['Normal'],
                    fontName='Helvetica',
                    fontSize=10,
                    leading=14,
                    textColor=BRAND_DARK,
                )),
                Paragraph(f"${amount:,.2f}", ParagraphStyle(
                    name='AmountCell',
                    parent=self.styles['Normal'],
                    fontName='Helvetica',
                    fontSize=11,
                    alignment=TA_RIGHT,
                    textColor=BRAND_DARK,
                )),
            ])

        # Create table with clean styling
        table = Table(
            table_data,
            colWidths=[self.page_width - 1.25 * inch, 1.25 * inch],
        )

        # Build row styles - alternating backgrounds
        # DISC-028: Use template accent color for borders
        border_color = self.template_colors.get("accent", BRAND_BORDER)

        # Apply spacing multiplier to row padding for one-page optimization
        space_mult = getattr(self, '_space_mult', 1.0)
        row_padding = max(4, int(12 * space_mult))  # Min 4pt padding

        style_commands = [
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),

            # Padding - scaled by space multiplier
            ('TOPPADDING', (0, 0), (-1, -1), row_padding),
            ('BOTTOMPADDING', (0, 0), (-1, -1), row_padding),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),

            # Bottom border on each row - use template accent color at low opacity
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, BRAND_BORDER),
        ]

        table.setStyle(TableStyle(style_commands))

        elements.append(table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_total_section(self, quote_data: dict) -> list:
        """Build the total section with prominent styling."""
        elements = []

        subtotal = quote_data.get('subtotal', 0)
        is_invoice = getattr(self, '_is_invoice', False)

        # DISC-071: For invoices, include tax breakdown if present
        if is_invoice and quote_data.get('tax_percent'):
            tax_percent = quote_data.get('tax_percent', 0)
            tax_amount = quote_data.get('tax_amount', 0)
            total = quote_data.get('total', subtotal + tax_amount)

            # Show subtotal, tax, and total
            total_data = [
                [
                    Paragraph("Subtotal", self.styles['TotalLabel']),
                    Paragraph(f"${subtotal:,.2f}", ParagraphStyle(
                        name='SubtotalAmount',
                        parent=self.styles['Normal'],
                        fontName='Helvetica',
                        fontSize=12,
                        alignment=TA_RIGHT,
                        textColor=BRAND_GRAY,
                    )),
                ],
                [
                    Paragraph(f"Tax ({tax_percent:.1f}%)", self.styles['TotalLabel']),
                    Paragraph(f"${tax_amount:,.2f}", ParagraphStyle(
                        name='TaxAmount',
                        parent=self.styles['Normal'],
                        fontName='Helvetica',
                        fontSize=12,
                        alignment=TA_RIGHT,
                        textColor=BRAND_GRAY,
                    )),
                ],
                [
                    Paragraph("Total Due", self.styles['TotalLabel']),
                    Paragraph(f"${total:,.2f}", self.styles['TotalAmount']),
                ],
            ]
        else:
            # Quote mode or invoice without tax - simple total
            label = "Total Due" if is_invoice else "Estimated Total"
            total_data = [
                [
                    Paragraph(label, self.styles['TotalLabel']),
                    Paragraph(f"${subtotal:,.2f}", self.styles['TotalAmount']),
                ],
            ]

        total_table = Table(
            total_data,
            colWidths=[self.page_width - 2 * inch, 2 * inch],
        )

        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        elements.append(total_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_details_section(self, quote_data: dict, terms: Optional[dict]) -> list:
        """Build timeline and terms in a clean two-column layout."""
        elements = []

        if not terms:
            terms = {
                'deposit_percent': 50,
                'quote_valid_days': 30,
                'labor_warranty_years': 2,
            }

        estimated_days = quote_data.get('estimated_days')
        estimated_crew = quote_data.get('estimated_crew_size')
        notes = quote_data.get('notes')

        # DISC-067: Check for custom timeline/terms text
        custom_timeline = quote_data.get('timeline_text')
        custom_terms = quote_data.get('terms_text')

        # Build left column (Timeline + Notes)
        left_content = []

        # DISC-067: Use custom timeline text if provided, otherwise use generated
        if custom_timeline:
            left_content.append(Paragraph("TIMELINE", self.styles['SectionHeader']))
            left_content.append(Paragraph(custom_timeline, self.styles['QuoteBodyLight']))
        elif estimated_days or estimated_crew:
            left_content.append(Paragraph("TIMELINE", self.styles['SectionHeader']))
            if estimated_days:
                left_content.append(Paragraph(
                    f"Duration: ~{estimated_days} day(s)",
                    self.styles['QuoteBodyLight']
                ))
            if estimated_crew:
                left_content.append(Paragraph(
                    f"Crew: {estimated_crew} person(s)",
                    self.styles['QuoteBodyLight']
                ))

        if notes:
            left_content.append(Spacer(1, 8))
            left_content.append(Paragraph("NOTES", self.styles['SectionHeader']))
            left_content.append(Paragraph(notes, self.styles['QuoteBodyLight']))

        # Build right column (Terms)
        right_content = []
        right_content.append(Paragraph("TERMS", self.styles['SectionHeader']))

        # DISC-067: Use custom terms text if provided, otherwise use generated
        if custom_terms:
            right_content.append(Paragraph(custom_terms, self.styles['QuoteBodyLight']))
        else:
            valid_days = terms.get('quote_valid_days', 30)
            right_content.append(Paragraph(
                f"Valid for {valid_days} days",
                self.styles['QuoteBodyLight']
            ))

            deposit = terms.get('deposit_percent', 50)
            right_content.append(Paragraph(
                f"{deposit}% deposit to schedule",
                self.styles['QuoteBodyLight']
            ))

            warranty = terms.get('labor_warranty_years')
            if warranty:
                right_content.append(Paragraph(
                    f"{warranty} year warranty on labor",
                    self.styles['QuoteBodyLight']
                ))

        # Create two-column table if we have content for both
        if left_content and right_content:
            details_table = Table(
                [[left_content, right_content]],
                colWidths=[self.page_width * 0.55, self.page_width * 0.45],
            )

            details_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))

            elements.append(details_table)
        elif right_content:
            # Just terms
            elements.extend(right_content)
        elif left_content:
            # Just timeline/notes
            elements.extend(left_content)

        # Reduced spacer for one-page preference
        space_mult = getattr(self, '_space_mult', 1.0)
        elements.append(Spacer(1, max(8, int(24 * space_mult))))

        return elements

    def _build_footer_section(self) -> list:
        """
        Build the footer with disclaimer and branding.

        DISC-072: Improved footer spacing to prevent cramped look.
        DISC-071: Different disclaimer text for invoices vs estimates.
        """
        elements = []

        # Get spacing multiplier for one-page preference
        space_mult = getattr(self, '_space_mult', 1.0)

        # DISC-072: Add more top spacing before footer for breathing room (scaled)
        elements.append(Spacer(1, max(8, int(24 * space_mult))))

        # DISC-071: Different disclaimer for invoices
        is_invoice = getattr(self, '_is_invoice', False)
        if is_invoice:
            disclaimer_text = (
                "Payment is due by the date shown above. "
                "Please reference the invoice number when making payment. "
                "Thank you for your business."
            )
        else:
            disclaimer_text = (
                "This is a preliminary budgetary estimate for planning purposes only. "
                "Final pricing may vary based on site conditions, material selections, "
                "and scope changes. This is not a binding contract."
            )

        elements.append(Paragraph(disclaimer_text, self.styles['FinePrint']))
        elements.append(Spacer(1, max(6, int(20 * space_mult))))

        # Branding - with more bottom padding
        elements.append(Paragraph(
            "Generated with quoted.it",
            self.styles['FooterBrand']
        ))
        elements.append(Spacer(1, max(4, int(8 * space_mult))))  # Bottom padding

        return elements


# Singleton pattern
_pdf_service: Optional[PDFGeneratorService] = None


def get_pdf_service() -> PDFGeneratorService:
    """Get the PDF generation service singleton."""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFGeneratorService()
    return _pdf_service
