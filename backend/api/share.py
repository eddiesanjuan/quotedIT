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
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services.auth import get_current_user
from ..services import get_db_service, get_pdf_service
from ..services.email import email_service
from ..services.analytics import analytics_service
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


class SharedQuoteResponse(BaseModel):
    """Public quote data for shared view (limited fields)."""
    id: str
    contractor_name: str
    contractor_phone: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    job_type: Optional[str] = None
    job_description: Optional[str] = None
    line_items: list = []
    subtotal: float = 0
    total: float = 0
    estimated_days: Optional[int] = None
    created_at: Optional[str] = None


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

        # Update share tracking
        share_updates = {
            "share_count": (quote.share_count or 0) + 1,
        }
        if not quote.shared_at:
            share_updates["shared_at"] = datetime.utcnow()

        await db.update_quote(quote_id, **share_updates)

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
            raise HTTPException(status_code=404, detail="Quote not found or link expired")

        # Get contractor info (limited fields)
        contractor = await db.get_contractor_by_id(quote.contractor_id)
        if not contractor:
            raise HTTPException(status_code=404, detail="Contractor not found")

        # Track view event (anonymous)
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
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track view event: {e}")

        # Return limited public data
        return SharedQuoteResponse(
            id=quote.id,
            contractor_name=contractor.business_name or contractor.owner_name,
            contractor_phone=contractor.phone,
            customer_name=quote.customer_name,
            customer_address=quote.customer_address,
            job_type=quote.job_type,
            job_description=quote.job_description,
            line_items=quote.line_items or [],
            subtotal=quote.subtotal or 0,
            total=quote.total or 0,
            estimated_days=quote.estimated_days,
            created_at=quote.created_at.isoformat() if quote.created_at else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error viewing shared quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))
