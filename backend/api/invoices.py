"""
Invoice API routes for Quoted.
DISC-071: Quote-to-Invoice conversion feature.

Handles invoice CRUD, PDF generation, sending, and payment tracking.
Invoices can be created from quotes or standalone.
"""

import secrets
from typing import Optional, List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..services.auth import get_current_user, get_db
from ..services import get_db_service, get_pdf_service
from ..services.analytics import analytics_service
from ..models.database import Invoice, Quote, Contractor
from ..services.database import async_session_factory


router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class InvoiceLineItem(BaseModel):
    """Line item in an invoice."""
    name: str
    description: Optional[str] = None
    amount: float
    quantity: Optional[float] = 1
    unit: Optional[str] = None


class InvoiceCreateRequest(BaseModel):
    """Request to create an invoice."""
    # Source quote (optional - for quote-to-invoice conversion)
    quote_id: Optional[str] = None

    # Customer info (required if no quote_id)
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None

    # Invoice details
    description: Optional[str] = None
    line_items: Optional[List[dict]] = None
    tax_percent: float = 0

    # Dates
    due_days: int = 30  # Days until due date

    # Terms
    terms_text: Optional[str] = None
    notes: Optional[str] = None


class InvoiceUpdateRequest(BaseModel):
    """Request to update an invoice."""
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    description: Optional[str] = None
    line_items: Optional[List[dict]] = None
    tax_percent: Optional[float] = None
    due_date: Optional[datetime] = None
    terms_text: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Invoice response model."""
    id: str
    contractor_id: str
    quote_id: Optional[str] = None
    invoice_number: str

    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None

    description: Optional[str] = None
    line_items: List[dict] = []
    subtotal: float = 0
    tax_percent: float = 0
    tax_amount: float = 0
    total: float = 0

    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    terms_text: Optional[str] = None
    notes: Optional[str] = None

    status: str = "draft"
    sent_at: Optional[str] = None
    paid_at: Optional[str] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None

    share_token: Optional[str] = None
    pdf_url: Optional[str] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MarkPaidRequest(BaseModel):
    """Request to mark invoice as paid."""
    payment_method: Optional[str] = None  # check, credit_card, cash, zelle, etc.
    payment_reference: Optional[str] = None  # Check number, transaction ID


# ============================================================================
# Helper Functions
# ============================================================================

def invoice_to_response(invoice: Invoice) -> InvoiceResponse:
    """Convert Invoice model to response."""
    return InvoiceResponse(
        id=invoice.id,
        contractor_id=invoice.contractor_id,
        quote_id=invoice.quote_id,
        invoice_number=invoice.invoice_number,
        customer_name=invoice.customer_name,
        customer_email=invoice.customer_email,
        customer_phone=invoice.customer_phone,
        customer_address=invoice.customer_address,
        description=invoice.description,
        line_items=invoice.line_items or [],
        subtotal=invoice.subtotal or 0,
        tax_percent=invoice.tax_percent or 0,
        tax_amount=invoice.tax_amount or 0,
        total=invoice.total or 0,
        invoice_date=invoice.invoice_date.isoformat() if invoice.invoice_date else None,
        due_date=invoice.due_date.isoformat() if invoice.due_date else None,
        terms_text=invoice.terms_text,
        notes=invoice.notes,
        status=invoice.status or "draft",
        sent_at=invoice.sent_at.isoformat() if invoice.sent_at else None,
        paid_at=invoice.paid_at.isoformat() if invoice.paid_at else None,
        payment_method=invoice.payment_method,
        payment_reference=invoice.payment_reference,
        share_token=invoice.share_token,
        pdf_url=invoice.pdf_url,
        created_at=invoice.created_at.isoformat() if invoice.created_at else None,
        updated_at=invoice.updated_at.isoformat() if invoice.updated_at else None,
    )


async def get_next_invoice_number(session: AsyncSession, contractor_id: str) -> str:
    """Generate the next invoice number for a contractor."""
    # Get count of existing invoices for this contractor
    result = await session.execute(
        select(Invoice).where(Invoice.contractor_id == contractor_id)
    )
    count = len(result.scalars().all())

    # Format: INV-XXXX (e.g., INV-0001, INV-0042)
    return f"INV-{count + 1:04d}"


async def get_contractor_for_user(user_id: str) -> Optional[Contractor]:
    """Get contractor record for a user."""
    db = get_db_service()
    return await db.get_contractor_by_user_id(user_id)


# ============================================================================
# CRUD Endpoints
# ============================================================================

@router.post("", response_model=InvoiceResponse)
async def create_invoice(
    invoice_request: InvoiceCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new invoice.

    Can be created from scratch or from an existing quote.
    If quote_id is provided, customer info and line items are copied from quote.
    """
    contractor = await get_contractor_for_user(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Please complete onboarding first")

    # Initialize invoice data
    customer_name = invoice_request.customer_name
    customer_email = invoice_request.customer_email
    customer_phone = invoice_request.customer_phone
    customer_address = invoice_request.customer_address
    description = invoice_request.description
    line_items = invoice_request.line_items or []

    source_quote_id = None

    # If quote_id provided, copy data from quote
    if invoice_request.quote_id:
        result = await db.execute(
            select(Quote).where(Quote.id == invoice_request.quote_id)
        )
        quote = result.scalar_one_or_none()

        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")

        if quote.contractor_id != contractor.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this quote")

        # Copy from quote (allow overrides from request)
        customer_name = customer_name or quote.customer_name
        customer_email = customer_email or quote.customer_email
        customer_phone = customer_phone or quote.customer_phone
        customer_address = customer_address or quote.customer_address
        description = description or quote.job_description
        line_items = line_items if line_items else (quote.line_items or [])
        source_quote_id = quote.id

    # Calculate amounts
    subtotal = sum(item.get("amount", 0) for item in line_items)
    tax_percent = invoice_request.tax_percent
    tax_amount = subtotal * (tax_percent / 100) if tax_percent else 0
    total = subtotal + tax_amount

    # Generate invoice number
    invoice_number = await get_next_invoice_number(db, contractor.id)

    # Calculate due date
    due_date = datetime.utcnow() + timedelta(days=invoice_request.due_days)

    # Generate share token
    share_token = secrets.token_urlsafe(24)[:32]

    # Get default terms from contractor if not provided
    terms_text = invoice_request.terms_text
    if not terms_text:
        db_service = get_db_service()
        terms = await db_service.get_terms(contractor.id)
        if terms and terms.default_terms_text:
            terms_text = terms.default_terms_text

    # Create invoice
    invoice = Invoice(
        contractor_id=contractor.id,
        quote_id=source_quote_id,
        invoice_number=invoice_number,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        customer_address=customer_address,
        description=description,
        line_items=line_items,
        subtotal=subtotal,
        tax_percent=tax_percent,
        tax_amount=tax_amount,
        total=total,
        invoice_date=datetime.utcnow(),
        due_date=due_date,
        terms_text=terms_text,
        notes=invoice_request.notes,
        status="draft",
        share_token=share_token,
    )

    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)

    # Track analytics
    try:
        analytics_service.track_event(
            user_id=str(current_user["id"]),
            event_name="invoice_created",
            properties={
                "contractor_id": str(contractor.id),
                "invoice_id": str(invoice.id),
                "from_quote": source_quote_id is not None,
                "source_quote_id": source_quote_id,
                "total": total,
                "line_item_count": len(line_items),
            }
        )
    except Exception as e:
        print(f"Warning: Failed to track invoice creation: {e}")

    return invoice_to_response(invoice)


@router.get("", response_model=List[InvoiceResponse])
async def list_invoices(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all invoices for the current contractor."""
    contractor = await get_contractor_for_user(current_user["id"])
    if not contractor:
        return []

    query = select(Invoice).where(Invoice.contractor_id == contractor.id)

    if status:
        query = query.where(Invoice.status == status)

    query = query.order_by(Invoice.created_at.desc())

    result = await db.execute(query)
    invoices = result.scalars().all()

    return [invoice_to_response(inv) for inv in invoices]


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific invoice by ID."""
    contractor = await get_contractor_for_user(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return invoice_to_response(invoice)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    update: InvoiceUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an invoice."""
    contractor = await get_contractor_for_user(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Don't allow editing paid invoices
    if invoice.status == "paid":
        raise HTTPException(status_code=400, detail="Cannot edit a paid invoice")

    # Update fields
    if update.customer_name is not None:
        invoice.customer_name = update.customer_name
    if update.customer_email is not None:
        invoice.customer_email = update.customer_email
    if update.customer_phone is not None:
        invoice.customer_phone = update.customer_phone
    if update.customer_address is not None:
        invoice.customer_address = update.customer_address
    if update.description is not None:
        invoice.description = update.description
    if update.line_items is not None:
        invoice.line_items = update.line_items
        # Recalculate totals
        invoice.subtotal = sum(item.get("amount", 0) for item in update.line_items)
        tax_pct = update.tax_percent if update.tax_percent is not None else invoice.tax_percent
        invoice.tax_amount = invoice.subtotal * (tax_pct / 100) if tax_pct else 0
        invoice.total = invoice.subtotal + invoice.tax_amount
    if update.tax_percent is not None:
        invoice.tax_percent = update.tax_percent
        invoice.tax_amount = invoice.subtotal * (update.tax_percent / 100) if update.tax_percent else 0
        invoice.total = invoice.subtotal + invoice.tax_amount
    if update.due_date is not None:
        invoice.due_date = update.due_date
    if update.terms_text is not None:
        invoice.terms_text = update.terms_text
    if update.notes is not None:
        invoice.notes = update.notes
    if update.status is not None:
        invoice.status = update.status

    invoice.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(invoice)

    return invoice_to_response(invoice)


@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an invoice."""
    contractor = await get_contractor_for_user(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Don't allow deleting paid invoices
    if invoice.status == "paid":
        raise HTTPException(status_code=400, detail="Cannot delete a paid invoice")

    await db.delete(invoice)
    await db.commit()

    return {"message": "Invoice deleted successfully", "invoice_id": invoice_id}


# ============================================================================
# Actions
# ============================================================================

@router.post("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: str,
    payment: MarkPaidRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark an invoice as paid."""
    contractor = await get_contractor_for_user(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if invoice.status == "paid":
        raise HTTPException(status_code=400, detail="Invoice is already paid")

    invoice.status = "paid"
    invoice.paid_at = datetime.utcnow()
    invoice.payment_method = payment.payment_method
    invoice.payment_reference = payment.payment_reference
    invoice.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(invoice)

    # Track analytics
    try:
        analytics_service.track_event(
            user_id=str(current_user["id"]),
            event_name="invoice_marked_paid",
            properties={
                "contractor_id": str(contractor.id),
                "invoice_id": str(invoice.id),
                "total": invoice.total,
                "payment_method": payment.payment_method,
            }
        )
    except Exception as e:
        print(f"Warning: Failed to track payment: {e}")

    return invoice_to_response(invoice)


@router.post("/{invoice_id}/pdf")
async def generate_invoice_pdf(
    request: Request,
    invoice_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate PDF for an invoice."""
    contractor = await get_contractor_for_user(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get terms
    db_service = get_db_service()
    terms = await db_service.get_terms(contractor.id)

    try:
        pdf_service = get_pdf_service()

        # Build invoice data dict
        invoice_dict = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "customer_name": invoice.customer_name,
            "customer_address": invoice.customer_address,
            "customer_phone": invoice.customer_phone,
            "customer_email": invoice.customer_email,
            "job_description": invoice.description,
            "line_items": invoice.line_items,
            "subtotal": invoice.subtotal,
            "tax_percent": invoice.tax_percent,
            "tax_amount": invoice.tax_amount,
            "total": invoice.total,
            "invoice_date": invoice.invoice_date.strftime("%B %d, %Y") if invoice.invoice_date else None,
            "due_date": invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else None,
            "terms_text": invoice.terms_text,
            "notes": invoice.notes,
            "status": invoice.status,
        }

        contractor_dict = {
            "business_name": contractor.business_name,
            "owner_name": contractor.owner_name,
            "email": contractor.email,
            "phone": contractor.phone,
            "address": contractor.address,
            "logo_data": contractor.logo_data,
        }

        terms_dict = {}
        if terms:
            terms_dict = {
                "deposit_percent": terms.deposit_percent,
                "quote_valid_days": terms.quote_valid_days,
                "labor_warranty_years": terms.labor_warranty_years,
            }

        # Get contractor's template preferences
        template = contractor.pdf_template or "modern"
        accent_color = contractor.pdf_accent_color

        # Generate PDF (reuse quote PDF generator with invoice flag)
        pdf_bytes = pdf_service.generate_quote_pdf(
            quote_data=invoice_dict,
            contractor=contractor_dict,
            terms=terms_dict,
            template=template,
            accent_color=accent_color,
            is_invoice=True,  # This tells the generator to use "INVOICE" instead of "QUOTE"
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            }
        )

    except Exception as e:
        import traceback
        print(f"Invoice PDF generation error for {invoice_id}: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF error: {str(e)}")


class SendInvoiceRequest(BaseModel):
    """Request to send invoice via email."""
    recipient_email: str
    message: Optional[str] = None


@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
async def send_invoice(
    invoice_id: str,
    send_request: SendInvoiceRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send an invoice via email to the customer.

    Updates invoice status to 'sent' and records sent_at timestamp.
    """
    from ..services.email_service import email_service

    contractor = await get_contractor_for_user(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Build share URL
    base_url = "https://quoted.it.com"
    share_url = f"{base_url}/invoice/{invoice.share_token}"

    # Send email
    try:
        subject = f"Invoice {invoice.invoice_number} from {contractor.business_name}"

        # Build email body
        body_parts = []
        if send_request.message:
            body_parts.append(send_request.message)
            body_parts.append("")

        body_parts.append(f"You have received an invoice from {contractor.business_name}.")
        body_parts.append("")
        body_parts.append(f"Invoice #: {invoice.invoice_number}")
        body_parts.append(f"Amount Due: ${invoice.total:,.2f}")
        if invoice.due_date:
            body_parts.append(f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}")
        body_parts.append("")
        body_parts.append(f"View your invoice: {share_url}")
        body_parts.append("")
        body_parts.append("Thank you for your business!")
        body_parts.append("")
        body_parts.append(f"— {contractor.business_name}")

        body = "\n".join(body_parts)

        await email_service.send_email(
            to_email=send_request.recipient_email,
            subject=subject,
            body=body,
        )

        # Update invoice status
        invoice.status = "sent"
        invoice.sent_at = datetime.utcnow()
        invoice.customer_email = send_request.recipient_email  # Update if different
        invoice.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(invoice)

        # Track analytics
        try:
            analytics_service.track_event(
                user_id=str(current_user["id"]),
                event_name="invoice_sent",
                properties={
                    "contractor_id": str(contractor.id),
                    "invoice_id": str(invoice.id),
                    "total": invoice.total,
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track invoice send: {e}")

        return invoice_to_response(invoice)

    except Exception as e:
        print(f"Error sending invoice email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


# ============================================================================
# Quote-to-Invoice Conversion (Convenience endpoint on quotes router)
# ============================================================================

@router.post("/from-quote/{quote_id}", response_model=InvoiceResponse)
async def create_invoice_from_quote(
    quote_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an invoice directly from a quote.

    This is a convenience endpoint that copies all quote data to a new invoice.
    Same as calling POST /invoices with quote_id.
    """
    # Just delegate to create_invoice with quote_id
    request = InvoiceCreateRequest(quote_id=quote_id)
    return await create_invoice(request, current_user, db)
