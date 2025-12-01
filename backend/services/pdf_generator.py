"""
PDF generation service for Quoted.
Creates professional quote documents from structured quote data.
Uses ReportLab for PDF generation.
"""

import io
import os
from datetime import datetime, timedelta
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


class PDFGeneratorService:
    """
    Generates professional PDF quotes from structured quote data.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the quote."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='QuoteTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#1a1a2e'),
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='QuoteSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666'),
            spaceAfter=30,
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#1a1a2e'),
        ))

        # Body text (QuoteBody to avoid conflict with existing BodyText)
        self.styles.add(ParagraphStyle(
            name='QuoteBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=10,
        ))

        # Fine print
        self.styles.add(ParagraphStyle(
            name='FinePrint',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#888888'),
            leading=11,
        ))

        # Total amount style
        self.styles.add(ParagraphStyle(
            name='TotalAmount',
            parent=self.styles['Normal'],
            fontSize=16,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
        ))

    def generate_quote_pdf(
        self,
        quote_data: dict,
        contractor: dict,
        terms: Optional[dict] = None,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Generate a PDF quote document.

        Args:
            quote_data: The structured quote data
            contractor: Contractor information
            terms: Terms and conditions
            output_path: Optional file path to save PDF

        Returns:
            PDF as bytes
        """
        # Create buffer
        buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        # Build content
        elements = []

        # Header with contractor info
        elements.extend(self._build_header(contractor))

        # Title
        elements.append(Paragraph("BUDGETARY ESTIMATE", self.styles['QuoteTitle']))

        # Subtitle with date
        quote_date = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(
            f"Prepared on {quote_date}",
            self.styles['QuoteSubtitle']
        ))

        # Customer info (if available)
        elements.extend(self._build_customer_section(quote_data))

        # Job description
        elements.extend(self._build_description_section(quote_data))

        # Line items table
        elements.extend(self._build_line_items_section(quote_data))

        # Total
        elements.extend(self._build_total_section(quote_data))

        # Timeline
        elements.extend(self._build_timeline_section(quote_data))

        # Notes and disclaimers
        elements.extend(self._build_notes_section(quote_data))

        # Terms and conditions
        elements.extend(self._build_terms_section(terms))

        # Budgetary disclaimer
        elements.extend(self._build_budgetary_disclaimer())

        # Build PDF
        doc.build(elements)

        # Get bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)

        return pdf_bytes

    def _build_header(self, contractor: dict) -> list:
        """Build the header with contractor information."""
        elements = []

        # Contractor name
        name = contractor.get('business_name', 'Contractor')
        elements.append(Paragraph(
            f"<b>{name}</b>",
            ParagraphStyle(
                name='ContractorName',
                parent=self.styles['Normal'],
                fontSize=18,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
            )
        ))

        # Contact info
        contact_parts = []
        if contractor.get('phone'):
            contact_parts.append(contractor['phone'])
        if contractor.get('email'):
            contact_parts.append(contractor['email'])
        if contact_parts:
            elements.append(Paragraph(
                " | ".join(contact_parts),
                self.styles['QuoteBody']
            ))

        if contractor.get('address'):
            elements.append(Paragraph(
                contractor['address'],
                self.styles['QuoteBody']
            ))

        elements.append(Spacer(1, 20))

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
                elements.append(Paragraph(
                    f"<b>{customer_name}</b>",
                    self.styles['QuoteBody']
                ))

            if customer_address:
                elements.append(Paragraph(
                    customer_address,
                    self.styles['QuoteBody']
                ))

            if customer_phone:
                elements.append(Paragraph(
                    customer_phone,
                    self.styles['QuoteBody']
                ))

            elements.append(Spacer(1, 10))

        return elements

    def _build_description_section(self, quote_data: dict) -> list:
        """Build the job description section."""
        elements = []

        elements.append(Paragraph("PROJECT DESCRIPTION", self.styles['SectionHeader']))

        job_description = quote_data.get('job_description', 'No description provided.')
        elements.append(Paragraph(job_description, self.styles['QuoteBody']))

        elements.append(Spacer(1, 10))

        return elements

    def _build_line_items_section(self, quote_data: dict) -> list:
        """Build the itemized pricing table."""
        elements = []

        elements.append(Paragraph("ESTIMATED PRICING", self.styles['SectionHeader']))

        line_items = quote_data.get('line_items', [])

        if not line_items:
            elements.append(Paragraph(
                "No line items specified.",
                self.styles['QuoteBody']
            ))
            return elements

        # Build table data
        table_data = [['Item', 'Description', 'Amount']]

        for item in line_items:
            table_data.append([
                item.get('name', ''),
                item.get('description', ''),
                f"${item.get('amount', 0):,.2f}",
            ])

        # Create table
        table = Table(
            table_data,
            colWidths=[1.5 * inch, 3.5 * inch, 1.25 * inch],
        )

        # Style the table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),

            # Alignment
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 10))

        return elements

    def _build_total_section(self, quote_data: dict) -> list:
        """Build the total section."""
        elements = []

        subtotal = quote_data.get('subtotal', 0)

        # Total table (right-aligned)
        total_data = [
            ['Estimated Total:', f"${subtotal:,.2f}"],
        ]

        total_table = Table(
            total_data,
            colWidths=[5 * inch, 1.25 * inch],
        )

        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(total_table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_timeline_section(self, quote_data: dict) -> list:
        """Build the timeline estimate section."""
        elements = []

        estimated_days = quote_data.get('estimated_days')
        estimated_crew = quote_data.get('estimated_crew_size')

        if estimated_days or estimated_crew:
            elements.append(Paragraph("ESTIMATED TIMELINE", self.styles['SectionHeader']))

            if estimated_days:
                elements.append(Paragraph(
                    f"<b>Duration:</b> Approximately {estimated_days} day(s)",
                    self.styles['QuoteBody']
                ))

            if estimated_crew:
                elements.append(Paragraph(
                    f"<b>Crew Size:</b> {estimated_crew} person(s)",
                    self.styles['QuoteBody']
                ))

            elements.append(Spacer(1, 10))

        return elements

    def _build_notes_section(self, quote_data: dict) -> list:
        """Build the notes section."""
        elements = []

        notes = quote_data.get('notes')
        if notes:
            elements.append(Paragraph("NOTES", self.styles['SectionHeader']))
            elements.append(Paragraph(notes, self.styles['QuoteBody']))
            elements.append(Spacer(1, 10))

        return elements

    def _build_terms_section(self, terms: Optional[dict]) -> list:
        """Build the terms and conditions section."""
        elements = []

        if not terms:
            # Default terms
            terms = {
                'deposit_percent': 50,
                'quote_valid_days': 30,
                'labor_warranty_years': 2,
            }

        elements.append(Paragraph("TERMS", self.styles['SectionHeader']))

        terms_text = []

        # Deposit
        deposit = terms.get('deposit_percent', 50)
        terms_text.append(f"<b>Deposit:</b> {deposit}% required to schedule work")

        # Quote validity
        valid_days = terms.get('quote_valid_days', 30)
        elements.append(Paragraph(
            f"<b>Quote Valid For:</b> {valid_days} days",
            self.styles['QuoteBody']
        ))

        # Warranty
        warranty = terms.get('labor_warranty_years')
        if warranty:
            terms_text.append(f"<b>Warranty:</b> {warranty} year(s) on labor")

        # Payment methods
        methods = terms.get('accepted_payment_methods')
        if methods:
            methods_str = ", ".join(methods)
            terms_text.append(f"<b>Payment Methods:</b> {methods_str}")

        for text in terms_text:
            elements.append(Paragraph(text, self.styles['QuoteBody']))

        elements.append(Spacer(1, 10))

        return elements

    def _build_budgetary_disclaimer(self) -> list:
        """Build the budgetary estimate disclaimer."""
        elements = []

        disclaimer_text = """
        <b>BUDGETARY ESTIMATE NOTICE:</b> This is a preliminary budgetary estimate
        provided for planning purposes only. Final pricing may vary based on actual
        site conditions, material selections, and scope changes discovered during
        detailed assessment. This estimate is not a binding contract. A formal
        proposal will be provided upon request.
        """

        elements.append(Spacer(1, 20))
        elements.append(Paragraph(disclaimer_text.strip(), self.styles['FinePrint']))

        # Generated by notice
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            "Quote generated by Quoted — quoted.you",
            ParagraphStyle(
                name='Generated',
                parent=self.styles['FinePrint'],
                alignment=TA_CENTER,
                textColor=colors.HexColor('#aaaaaa'),
            )
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
