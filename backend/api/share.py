"""
Share Quote API routes for Quoted (GROWTH-003).
Enables contractors to share quotes via email or shareable links.

Key features:
- Email quotes with PDF attachment
- Generate shareable public links
- Track share metrics (count, views)
- PostHog analytics integration
"""

import secrets
import os
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services.auth import get_current_user
from ..services import get_db_service, get_pdf_service
from ..services.email import email_service
from ..services.analytics import analytics_service
from ..services.billing import BillingService  # INNOV-2: Deposit checkout
from ..config import settings


router = APIRouter()

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


# ============================================================================
# Request/Response Models
# ============================================================================

class ShareEmailRequest(BaseModel):
    """Request to share quote via email."""
    recipient_email: EmailStr
    message: Optional[str] = None  # Optional personal message

    class Config:
        schema_extra = {
            "example": {
                "recipient_email": "customer@example.com",
                "message": "Thanks for your interest! Looking forward to working with you."
            }
        }


class ShareEmailResponse(BaseModel):
    """Response from email share."""
    success: bool
    message: str
    quote_id: str


class ShareLinkResponse(BaseModel):
    """Response from link generation."""
    share_url: str
    token: str
    quote_id: str


class ExpirationInfo(BaseModel):
    """Expiration status for quotes (Wave 2)."""
    expired: bool = False
    expires_at: Optional[str] = None
    days_remaining: Optional[int] = None


class SharedQuoteResponse(BaseModel):
    """Public quote data for shared view (limited fields)."""
    id: str
    contractor_name: str
    contractor_phone: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None  # INNOV-2: For Stripe checkout
    customer_address: Optional[str] = None
    job_type: Optional[str] = None
    job_description: Optional[str] = None
    line_items: list = []
    subtotal: float = 0
    total: float = 0
    estimated_days: Optional[int] = None
    created_at: Optional[str] = None
    # PROPOSIFY-DOMINATION: Status and signature fields for accept/reject UI
    status: Optional[str] = None
    accepted_at: Optional[str] = None
    signature_name: Optional[str] = None
    # Wave 2: Expiration info
    expiration: Optional[ExpirationInfo] = None
    # INNOV-2: Deposit and scheduling info
    deposit_info: Optional[dict] = None
    scheduled_start_date: Optional[str] = None
    deposit_paid: bool = False


# ============================================================================
# Share Via Email
# ============================================================================

@router.post("/{quote_id}/share/email", response_model=ShareEmailResponse)
@limiter.limit("10/minute")
async def share_quote_via_email(
    request: Request,
    quote_id: str,
    share_request: ShareEmailRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Share quote via email with PDF attachment.

    Sends professional email to customer with quote details and PDF.
    Tracks share in database and PostHog analytics.
    """
    try:
        db = get_db_service()

        # Get the quote
        quote = await db.get_quote(quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")

        # Verify ownership
        contractor = await db.get_contractor_by_user_id(current_user["id"])
        if not contractor or quote.contractor_id != contractor.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Generate PDF if not exists
        pdf_service = get_pdf_service()
        if not quote.pdf_url or not os.path.exists(quote.pdf_url):
            # Get terms for PDF generation
            terms = await db.get_terms(contractor.id)

            quote_dict = {
                "id": quote.id,
                "customer_name": quote.customer_name,
                "customer_address": quote.customer_address,
                "customer_phone": quote.customer_phone,
                "job_description": quote.job_description,
                "line_items": quote.line_items,
                "subtotal": quote.subtotal,
                "total": quote.total,
                "estimated_days": quote.estimated_days,
            }

            contractor_dict = {
                "business_name": contractor.business_name,
                "owner_name": contractor.owner_name,
                "email": contractor.email,
                "phone": contractor.phone,
                "address": contractor.address,
            }

            terms_dict = {}
            if terms:
                terms_dict = {
                    "deposit_percent": terms.deposit_percent,
                    "quote_valid_days": terms.quote_valid_days,
                    "labor_warranty_years": terms.labor_warranty_years,
                }

            # Generate PDF
            os.makedirs("./data/pdfs", exist_ok=True)
            output_path = f"./data/pdfs/{quote_id}.pdf"

            pdf_service.generate_quote_pdf(
                quote_data=quote_dict,
                contractor=contractor_dict,
                terms=terms_dict,
                output_path=output_path,
            )

            # Update quote with PDF URL
            await db.update_quote(quote_id, pdf_url=output_path)
            quote.pdf_url = output_path

        # Send email
        print(f"Attempting to send quote email to {share_request.recipient_email} for quote {quote_id}")
        try:
            email_response = await email_service.send_quote_email(
                to_email=share_request.recipient_email,
                contractor_name=contractor.business_name or contractor.owner_name,
                contractor_phone=contractor.phone or "N/A",
                customer_name=quote.customer_name,
                job_description=quote.job_description or "Project",
                total=quote.total or quote.subtotal or 0,
                message=share_request.message,
                pdf_path=quote.pdf_url,
            )
            print(f"Email sent successfully. Response: {email_response}")
        except Exception as email_error:
            print(f"CRITICAL: Email failed to send for quote {quote_id}: {email_error}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email: {str(email_error)}"
            )

        # Update share tracking (KI-012 FIX: Also set sent_at and status)
        share_updates = {
            "share_count": (quote.share_count or 0) + 1,
        }
        if not quote.shared_at:
            share_updates["shared_at"] = datetime.utcnow()

        # KI-012 FIX: Set sent_at timestamp and status when emailing
        if not quote.sent_at:
            share_updates["sent_at"] = datetime.utcnow()
        if quote.status == "draft":
            share_updates["status"] = "sent"

        await db.update_quote(quote_id, **share_updates)

        # Learning Excellence: Process acceptance signal if quote was NOT edited
        # Acceptance learning boosts confidence without creating new statements
        if not quote.was_edited and quote.job_type:
            try:
                acceptance_result = await db.apply_acceptance_to_pricing_model(
                    contractor_id=str(contractor.id),
                    category=quote.job_type,
                    signal_type="sent",
                )
                if acceptance_result:
                    print(f"[ACCEPTANCE] Quote {quote_id} sent without edit: {acceptance_result}")
            except Exception as e:
                print(f"Warning: Failed to process acceptance learning: {e}")

        # Track analytics event
        try:
            analytics_service.track_event(
                user_id=str(current_user["id"]),
                event_name="quote_shared",
                properties={
                    "method": "email",
                    "quote_id": quote_id,
                    "contractor_id": str(contractor.id),
                    "recipient_email": share_request.recipient_email,
                    "has_message": bool(share_request.message),
                    "job_type": quote.job_type,
                    "total": quote.total or quote.subtotal or 0,
                    "was_edited": quote.was_edited,  # Learning Excellence: track for analytics
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track share event: {e}")

        return ShareEmailResponse(
            success=True,
            message=f"Quote sent to {share_request.recipient_email}",
            quote_id=quote_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sharing quote via email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Generate Shareable Link
# ============================================================================

@router.post("/{quote_id}/share", response_model=ShareLinkResponse)
@limiter.limit("30/minute")
async def generate_share_link(
    request: Request,
    quote_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a shareable public link for the quote.

    Creates a unique token that allows public access to view the quote
    without authentication. Token is permanent (doesn't expire).
    """
    try:
        db = get_db_service()

        # Get the quote
        quote = await db.get_quote(quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")

        # Verify ownership
        contractor = await db.get_contractor_by_user_id(current_user["id"])
        if not contractor or quote.contractor_id != contractor.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Generate token if not exists
        if not quote.share_token:
            share_token = secrets.token_urlsafe(16)

            # Update quote with token
            update_data = {
                "share_token": share_token,
                "share_count": (quote.share_count or 0) + 1,
            }
            if not quote.shared_at:
                update_data["shared_at"] = datetime.utcnow()

            await db.update_quote(quote_id, **update_data)
        else:
            share_token = quote.share_token

        # Construct shareable URL
        share_url = f"{settings.frontend_url}/shared/{share_token}"

        # Track analytics event
        try:
            analytics_service.track_event(
                user_id=str(current_user["id"]),
                event_name="quote_shared",
                properties={
                    "method": "link",
                    "quote_id": quote_id,
                    "contractor_id": str(contractor.id),
                    "share_token": share_token,
                    "job_type": quote.job_type,
                    "total": quote.total or quote.subtotal or 0,
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track share event: {e}")

        return ShareLinkResponse(
            share_url=share_url,
            token=share_token,
            quote_id=quote_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating share link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Public Shared Quote View
# ============================================================================

@router.get("/shared/{token}", response_model=SharedQuoteResponse)
@limiter.limit("60/minute")
async def view_shared_quote(
    request: Request,
    token: str,
):
    """
    View a publicly shared quote (no authentication required).

    Returns limited quote data for public viewing. Does not expose
    sensitive contractor information beyond name and phone.
    """
    try:
        db = get_db_service()

        # Find quote by share token
        quote = await db.get_quote_by_share_token(token)
        if not quote:
            # KI-008 FIX: Clear error message (links never expire)
            raise HTTPException(status_code=404, detail="Quote not found")

        # Get contractor info (limited fields)
        contractor = await db.get_contractor_by_id(quote.contractor_id)
        if not contractor:
            raise HTTPException(status_code=404, detail="Contractor not found")

        # KI-004 FIX: Track view count in database (not just PostHog)
        is_first_view = (quote.view_count or 0) == 0
        new_view_count = (quote.view_count or 0) + 1
        now = datetime.utcnow()

        # Build update fields
        update_fields = {
            "view_count": new_view_count,
            "last_viewed_at": now,
        }
        if is_first_view:
            update_fields["first_viewed_at"] = now
            # Update status to "viewed" if currently "sent"
            if quote.status == "sent":
                update_fields["status"] = "viewed"

        # Update quote in database
        quote = await db.update_quote(str(quote.id), **update_fields)

        # Wave 3: Send first-view notification email to contractor
        if is_first_view:
            try:
                await email_service.send_quote_first_view_email(
                    to_email=contractor.email,
                    contractor_name=contractor.business_name or contractor.owner_name or "there",
                    customer_name=quote.customer_name,
                    quote_total=quote.total or quote.subtotal or 0,
                    quote_token=token,
                )
            except Exception as e:
                print(f"Warning: Failed to send first-view notification email: {e}")

        # Track view event in PostHog (for detailed analytics)
        try:
            analytics_service.track_event(
                user_id=f"shared_{token[:8]}",  # Anonymous ID based on token
                event_name="shared_quote_viewed",
                properties={
                    "token": token,
                    "quote_id": str(quote.id),
                    "contractor_id": str(contractor.id),
                    "job_type": quote.job_type,
                    "total": quote.total or quote.subtotal or 0,
                    "view_count": quote.view_count,
                    "is_first_view": is_first_view,
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track view event: {e}")

        # Wave 2: Calculate expiration
        expiration_info = None
        terms = await db.get_terms(contractor.id)
        if terms and terms.quote_valid_days and quote.created_at:
            expires_at_dt = quote.created_at + timedelta(days=terms.quote_valid_days)
            is_expired = datetime.utcnow() > expires_at_dt
            days_remaining = None
            if not is_expired:
                days_remaining = max(0, (expires_at_dt - datetime.utcnow()).days)
            expiration_info = ExpirationInfo(
                expired=is_expired,
                expires_at=expires_at_dt.isoformat(),
                days_remaining=days_remaining,
            )

        # INNOV-2: Build deposit info from contractor terms
        deposit_info = None
        if terms:
            deposit_percent = terms.deposit_percent or 50.0
            quote_total = quote.total or quote.subtotal or 0
            deposit_amount = (quote_total * deposit_percent) / 100
            deposit_info = {
                "deposit_enabled": deposit_percent > 0,
                "deposit_percent": deposit_percent,
                "deposit_amount": round(deposit_amount, 2),
                "deposit_description": terms.deposit_description or f"{int(deposit_percent)}% deposit to schedule",
            }

        # Return limited public data (PROPOSIFY-DOMINATION: include status/signature)
        return SharedQuoteResponse(
            id=quote.id,
            contractor_name=contractor.business_name or contractor.owner_name,
            contractor_phone=contractor.phone,
            customer_name=quote.customer_name,
            customer_email=quote.customer_email,  # INNOV-2: For Stripe checkout
            customer_address=quote.customer_address,
            job_type=quote.job_type,
            job_description=quote.job_description,
            line_items=quote.line_items or [],
            subtotal=quote.subtotal or 0,
            total=quote.total or 0,
            estimated_days=quote.estimated_days,
            created_at=quote.created_at.isoformat() if quote.created_at else None,
            # PROPOSIFY-DOMINATION: Status and signature for UI
            status=quote.status,
            accepted_at=quote.accepted_at.isoformat() if quote.accepted_at else None,
            signature_name=quote.signature_name,
            # Wave 2: Expiration info
            expiration=expiration_info,
            # INNOV-2: Deposit and scheduling info
            deposit_info=deposit_info,
            scheduled_start_date=quote.scheduled_start_date.isoformat() if hasattr(quote, 'scheduled_start_date') and quote.scheduled_start_date else None,
            deposit_paid=quote.deposit_paid if hasattr(quote, 'deposit_paid') else False,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error viewing shared quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Quote Accept/Reject (Public Endpoints - PROPOSIFY-DOMINATION)
# ============================================================================

class AcceptQuoteRequest(BaseModel):
    """Request to accept a quote."""
    signature_name: str  # Customer types their name to sign
    message: Optional[str] = None  # Optional note to contractor


class RejectQuoteRequest(BaseModel):
    """Request to reject a quote."""
    reason: Optional[str] = None  # Optional reason for rejection


# INNOV-2: One-Click Acceptance Flow Models
class AcceptWithDepositRequest(BaseModel):
    """Request to accept a quote with optional deposit payment and scheduling."""
    signature_name: str  # Customer types their name to sign
    scheduled_date: Optional[str] = None  # ISO date string for scheduled start
    pay_deposit: bool = False  # Whether to pay deposit now
    message: Optional[str] = None  # Optional note to contractor


class DepositCheckoutResponse(BaseModel):
    """Response with Stripe checkout URL for deposit payment."""
    checkout_url: str
    session_id: str
    deposit_amount: float
    deposit_percent: float


class QuoteDepositInfo(BaseModel):
    """Deposit configuration for a quote."""
    deposit_enabled: bool = True
    deposit_percent: float = 50.0
    deposit_amount: float = 0
    deposit_description: str = "50% deposit to schedule"


@router.post("/shared/{token}/accept")
@limiter.limit("10/minute")
async def accept_quote(
    request: Request,
    token: str,
    accept_request: AcceptQuoteRequest,
):
    """
    Customer accepts a quote (public endpoint, no authentication).

    Captures typed-name e-signature and updates quote status.
    Notifies contractor via email.
    """
    try:
        db = get_db_service()

        # Find quote by share token
        quote = await db.get_quote_by_share_token(token)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")

        # Check if already accepted/rejected
        if quote.status in ["won", "lost"]:
            return {
                "success": False,
                "message": f"Quote has already been {quote.status}",
                "status": quote.status
            }

        # Get contractor for notification
        contractor = await db.get_contractor_by_id(quote.contractor_id)
        if not contractor:
            raise HTTPException(status_code=404, detail="Contractor not found")

        # Update quote with acceptance
        now = datetime.utcnow()
        update_fields = {
            "status": "won",
            "outcome": "won",
            "signature_name": accept_request.signature_name,
            "signature_ip": request.client.host if request.client else None,
            "signature_at": now,
            "accepted_at": now,
        }
        if accept_request.message:
            update_fields["outcome_notes"] = f"Customer message: {accept_request.message}"

        quote = await db.update_quote(str(quote.id), **update_fields)

        # Learning Excellence: Process acceptance signal when customer accepts
        # This is a STRONG signal that AI pricing was correct
        if quote.job_type:
            try:
                acceptance_result = await db.apply_acceptance_to_pricing_model(
                    contractor_id=str(quote.contractor_id),
                    category=quote.job_type,
                    signal_type="accepted",
                )
                if acceptance_result:
                    print(f"[ACCEPTANCE] Quote {quote.id} accepted by customer: {acceptance_result}")
            except Exception as e:
                print(f"Warning: Failed to process acceptance learning on accept: {e}")

        # INNOV-6: Auto-generate invoice when quote is accepted
        try:
            from ..services.invoice_automation import InvoiceAutomationService
            from ..services.database import async_session_factory

            async with async_session_factory() as invoice_db:
                # Check if contractor has auto-invoicing enabled
                settings = await InvoiceAutomationService.get_contractor_invoice_settings(
                    invoice_db, str(quote.contractor_id)
                )
                if settings.get("auto_generate_invoices", False):
                    result = await InvoiceAutomationService.auto_generate_from_quote(
                        db=invoice_db,
                        quote_id=str(quote.id),
                        send_to_customer=settings.get("auto_send_invoices", False),
                        due_days=settings.get("default_due_days", 30),
                    )
                    if result.success:
                        print(f"[INVOICE-AUTO] Generated invoice {result.invoice_number} from accepted quote {quote.id}")
                    else:
                        print(f"[INVOICE-AUTO] Could not generate invoice: {result.message}")
        except Exception as e:
            print(f"Warning: Failed to auto-generate invoice: {e}")

        # Send notification email to contractor
        try:
            await email_service.send_email(
                to_email=contractor.email,
                subject=f"Great news! {quote.customer_name} accepted your quote",
                body=(
                    f"Your quote has been accepted!\n\n"
                    f"Customer: {quote.customer_name}\n"
                    f"Job: {quote.job_description or quote.job_type}\n"
                    f"Total: ${quote.total:,.2f}\n\n"
                    f"Signed by: {accept_request.signature_name}\n"
                    f"Date: {datetime.utcnow().strftime('%B %d, %Y')}\n"
                    + (f"\nCustomer message: {accept_request.message}\n" if accept_request.message else "")
                    + f"\nNext steps: Contact the customer to schedule the work.\n"
                    f"You can convert this quote to an invoice in Quoted.\n\n"
                    f"View in Quoted: {settings.app_url}/app"
                )
            )
        except Exception as e:
            print(f"Warning: Failed to send acceptance email: {e}")

        # Track analytics
        try:
            analytics_service.track_event(
                user_id=f"shared_{token[:8]}",
                event_name="quote_accepted",
                properties={
                    "token": token,
                    "quote_id": str(quote.id),
                    "contractor_id": str(quote.contractor_id),
                    "signature_name": accept_request.signature_name,
                    "total": quote.total or 0,
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track acceptance event: {e}")

        return {
            "success": True,
            "message": "Quote accepted successfully",
            "status": "won"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error accepting quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shared/{token}/reject")
@limiter.limit("10/minute")
async def reject_quote(
    request: Request,
    token: str,
    reject_request: RejectQuoteRequest,
):
    """
    Customer rejects a quote (public endpoint, no authentication).

    Updates quote status and optionally captures reason.
    """
    try:
        db = get_db_service()

        # Find quote by share token
        quote = await db.get_quote_by_share_token(token)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")

        # Check if already accepted/rejected
        if quote.status in ["won", "lost"]:
            return {
                "success": False,
                "message": f"Quote has already been {quote.status}",
                "status": quote.status
            }

        # Get contractor for potential notification
        contractor = await db.get_contractor_by_id(quote.contractor_id)

        # Update quote with rejection
        now = datetime.utcnow()
        update_fields = {
            "status": "lost",
            "outcome": "lost",
            "rejected_at": now,
        }
        if reject_request.reason:
            update_fields["outcome_notes"] = reject_request.reason
            update_fields["rejection_reason"] = reject_request.reason

        quote = await db.update_quote(str(quote.id), **update_fields)

        # Optionally notify contractor (only if reason provided)
        if reject_request.reason and contractor:
            try:
                await email_service.send_email(
                    to_email=contractor.email,
                    subject=f"Quote update: {quote.customer_name} declined",
                    body=(
                        f"Unfortunately, your quote was declined.\n\n"
                        f"Customer: {quote.customer_name}\n"
                        f"Job: {quote.job_description or quote.job_type}\n"
                        f"Total: ${quote.total:,.2f}\n\n"
                        f"Reason: {reject_request.reason}\n\n"
                        f"This feedback can help you improve future quotes.\n\n"
                        f"View in Quoted: {settings.app_url}/app"
                    )
                )
            except Exception as e:
                print(f"Warning: Failed to send rejection email: {e}")

        # Track analytics
        try:
            analytics_service.track_event(
                user_id=f"shared_{token[:8]}",
                event_name="quote_rejected",
                properties={
                    "token": token,
                    "quote_id": str(quote.id),
                    "contractor_id": str(quote.contractor_id),
                    "has_reason": bool(reject_request.reason),
                    "total": quote.total or 0,
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track rejection event: {e}")

        return {
            "success": True,
            "message": "Quote declined",
            "status": "lost"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error rejecting quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# INNOV-2: Deposit Checkout Endpoint
@router.post("/shared/{token}/deposit-checkout", response_model=DepositCheckoutResponse)
async def create_deposit_checkout(
    token: str,
    request: AcceptWithDepositRequest,
    db: DatabaseService = Depends(get_db_service),
):
    """
    Create a Stripe checkout session for deposit payment.

    INNOV-2: One-Click Acceptance Flow
    - Customer accepts quote with signature
    - Optionally schedules a start date
    - Redirected to Stripe for deposit payment
    - On success, quote is marked as accepted + deposit paid + scheduled
    """
    try:
        # Validate share token
        quote = await db.get_quote_by_share_token(token)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")

        # Get contractor info
        contractor = await db.get_contractor(str(quote.contractor_id))
        if not contractor:
            raise HTTPException(status_code=404, detail="Contractor not found")

        # Get contractor terms for deposit info
        terms = await db.get_contractor_terms(str(contractor.id))
        deposit_percent = 50.0  # Default
        if terms and terms.deposit_percent:
            deposit_percent = terms.deposit_percent

        # Calculate deposit amount
        quote_total = quote.total or quote.subtotal or 0
        deposit_amount = (quote_total * deposit_percent) / 100
        deposit_cents = int(deposit_amount * 100)

        if deposit_cents < 50:  # Stripe minimum is $0.50
            raise HTTPException(
                status_code=400,
                detail="Deposit amount too small for payment processing"
            )

        # Get customer email (required for Stripe checkout)
        customer_email = quote.customer_email
        if not customer_email:
            raise HTTPException(
                status_code=400,
                detail="Customer email required for payment"
            )

        # Store the acceptance info first (signature, scheduled date)
        update_fields = {
            "status": "pending_payment",  # Intermediate status
            "signature_name": request.signature_name,
        }
        if request.scheduled_date:
            from datetime import datetime
            try:
                scheduled_dt = datetime.fromisoformat(request.scheduled_date.replace('Z', '+00:00'))
                update_fields["scheduled_start_date"] = scheduled_dt
            except ValueError:
                pass  # Invalid date format, skip

        await db.update_quote(str(quote.id), **update_fields)

        # Build success/cancel URLs
        base_url = settings.app_url.rstrip("/")
        success_url = f"{base_url}/quote/{token}?payment=success"
        cancel_url = f"{base_url}/quote/{token}?payment=cancelled"

        # Create Stripe checkout session
        checkout_result = await BillingService.create_deposit_checkout_session(
            quote_id=str(quote.id),
            amount_cents=deposit_cents,
            contractor_name=contractor.business_name or contractor.name,
            customer_email=customer_email,
            customer_name=quote.customer_name or "Customer",
            job_description=quote.job_description or quote.job_type or "Project",
            success_url=success_url,
            cancel_url=cancel_url,
            scheduled_date=request.scheduled_date,
        )

        # Track analytics
        try:
            analytics_service.track_event(
                user_id=f"shared_{token[:8]}",
                event_name="deposit_checkout_started",
                properties={
                    "token": token,
                    "quote_id": str(quote.id),
                    "contractor_id": str(quote.contractor_id),
                    "deposit_amount": deposit_amount,
                    "deposit_percent": deposit_percent,
                    "has_scheduled_date": bool(request.scheduled_date),
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track deposit_checkout_started: {e}")

        return DepositCheckoutResponse(
            checkout_url=checkout_result["checkout_url"],
            session_id=checkout_result["session_id"],
            deposit_amount=round(deposit_amount, 2),
            deposit_percent=deposit_percent,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating deposit checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))
