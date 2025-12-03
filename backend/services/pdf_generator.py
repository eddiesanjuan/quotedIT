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
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
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
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.page_width = letter[0] - 1.5 * inch  # Account for margins

    def _setup_custom_styles(self):
        """Set up custom paragraph styles matching site branding."""

        # Main title - elegant serif style
        self.styles.add(ParagraphStyle(
            name='QuoteTitle',
            parent=self.styles['Heading1'],
            fontName='Times-Roman',
            fontSize=32,
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=0,
            textColor=BRAND_DARK,
            leading=38,
        ))

        # Quote number/date subtitle
        self.styles.add(ParagraphStyle(
            name='QuoteSubtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            alignment=TA_LEFT,
            textColor=BRAND_GRAY,
            spaceAfter=24,
        ))

        # Business name in header
        self.styles.add(ParagraphStyle(
            name='BusinessName',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            alignment=TA_RIGHT,
            textColor=BRAND_DARK,
            spaceAfter=2,
        ))

        # Contact info in header
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=BRAND_GRAY,
            leading=14,
        ))

        # Section headers
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=10,
            spaceBefore=24,
            spaceAfter=12,
            textColor=BRAND_LIGHT_GRAY,
            leading=12,
        ))

        # Body text
        self.styles.add(ParagraphStyle(
            name='QuoteBody',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=16,
            spaceAfter=8,
            textColor=BRAND_DARK,
        ))

        # Body text - light color
        self.styles.add(ParagraphStyle(
            name='QuoteBodyLight',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=16,
            spaceAfter=4,
            textColor=BRAND_GRAY,
        ))

        # Customer name
        self.styles.add(ParagraphStyle(
            name='CustomerName',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=BRAND_DARK,
            spaceAfter=4,
        ))

        # Total amount - large and bold
        self.styles.add(ParagraphStyle(
            name='TotalLabel',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=12,
            alignment=TA_RIGHT,
            textColor=BRAND_GRAY,
        ))

        self.styles.add(ParagraphStyle(
            name='TotalAmount',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=24,
            alignment=TA_RIGHT,
            textColor=BRAND_DARK,
        ))

        # Fine print / disclaimer
        self.styles.add(ParagraphStyle(
            name='FinePrint',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=BRAND_LIGHT_GRAY,
            leading=11,
        ))

        # Footer branding
        self.styles.add(ParagraphStyle(
            name='FooterBrand',
            parent=self.styles['Normal'],
            fontName='Times-Italic',
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
    ) -> bytes:
        """
        Generate a professional PDF quote document.

        Args:
            quote_data: The structured quote data
            contractor: Contractor information
            terms: Terms and conditions
            output_path: Optional file path to save PDF

        Returns:
            PDF as bytes
        """
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch,
        )

        elements = []

        # Header with logo and business info
        elements.extend(self._build_header(contractor, quote_data))

        # Divider
        elements.append(HorizontalLine(self.page_width))
        elements.append(Spacer(1, 20))

        # Title and date
        elements.extend(self._build_title_section(quote_data))

        # Customer info (if available)
        elements.extend(self._build_customer_section(quote_data))

        # Project description
        elements.extend(self._build_description_section(quote_data))

        # Line items
        elements.extend(self._build_line_items_section(quote_data))

        # Total
        elements.extend(self._build_total_section(quote_data))

        # Divider
        elements.append(HorizontalLine(self.page_width))
        elements.append(Spacer(1, 16))

        # Timeline and Terms side by side
        elements.extend(self._build_details_section(quote_data, terms))

        # Disclaimer and branding
        elements.extend(self._build_footer_section())

        doc.build(elements)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)

        return pdf_bytes

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

                # Create BytesIO object for ReportLab
                logo_buffer = io.BytesIO(logo_binary)

                # Create Image object with fixed height, preserve aspect ratio
                logo = Image(logo_buffer, width=48, height=48)
            except Exception as e:
                # If logo fails to load, fall back to placeholder
                print(f"Warning: Failed to load custom logo: {e}")
                logo = LogoPlaceholder(initial, size=48)
        else:
            # Use placeholder logo
            logo = LogoPlaceholder(initial, size=48)

        # Business info column
        business_info = []
        business_info.append(Paragraph(business_name, self.styles['BusinessName']))
        if contact_text:
            business_info.append(Paragraph(contact_text, self.styles['ContactInfo']))

        # Combine into a table for layout
        header_data = [[logo, business_info]]

        header_table = Table(
            header_data,
            colWidths=[60, self.page_width - 60],
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
        elements.append(Spacer(1, 16))

        return elements

    def _build_title_section(self, quote_data: dict) -> list:
        """Build the title and date section."""
        elements = []

        # Main title
        elements.append(Paragraph("Estimate", self.styles['QuoteTitle']))

        # Date and quote number
        quote_date = datetime.now().strftime("%B %d, %Y")
        quote_num = quote_data.get('quote_number', datetime.now().strftime("%Y%m%d%H%M"))

        elements.append(Paragraph(
            f"#{quote_num}  ·  {quote_date}",
            self.styles['QuoteSubtitle']
        ))

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
            amount = item.get('amount', 0)

            # Combine name and description
            if desc:
                item_text = f"<b>{name}</b><br/><font size='9' color='#666666'>{desc}</font>"
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
        style_commands = [
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),

            # Bottom border on each row
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

        # Total in a right-aligned table
        total_data = [
            [
                Paragraph("Estimated Total", self.styles['TotalLabel']),
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
            ('TOPPADDING', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
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

        # Build left column (Timeline + Notes)
        left_content = []

        if estimated_days or estimated_crew:
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

        elements.append(Spacer(1, 24))

        return elements

    def _build_footer_section(self) -> list:
        """Build the footer with disclaimer and branding."""
        elements = []

        # Disclaimer
        disclaimer_text = (
            "This is a preliminary budgetary estimate for planning purposes only. "
            "Final pricing may vary based on site conditions, material selections, "
            "and scope changes. This is not a binding contract."
        )

        elements.append(Paragraph(disclaimer_text, self.styles['FinePrint']))
        elements.append(Spacer(1, 16))

        # Branding
        elements.append(Paragraph(
            "Generated with quoted.it",
            self.styles['FooterBrand']
        ))

        return elements


# Singleton pattern
_pdf_service: Optional[PDFGeneratorService] = None


def get_pdf_service() -> PDFGeneratorService:
    """Get the PDF generation service singleton."""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFGeneratorService()
    return _pdf_service
