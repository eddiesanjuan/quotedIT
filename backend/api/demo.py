"""
Demo API routes for Quoted.
Allows unauthenticated users to try the product without signing up.

Key features:
- No authentication required
- Rate limited per IP (3 quotes/hour)
- Uses UNIVERSAL demo prompt that works for ANY industry
- Generates real quotes using AI (no personalized learning)
- Marks quotes as demo (not saved to user's account)
- Includes PDF generation with demo watermark
"""

import os
import io
import base64
import tempfile
from typing import Optional
from datetime import datetime

import anthropic
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import Response
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services import get_transcription_service, get_sanity_check_service, get_pdf_service
from ..services.quote_generator import QUOTE_GENERATION_TOOL
from ..prompts import get_demo_quote_prompt
from ..config import settings


router = APIRouter()

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


# Demo profile for PDF generation (generic, professional appearance)
DEMO_CONTRACTOR = {
    "id": "demo",
    "business_name": "Your Business Name",
    "owner_name": "Your Name",
    "email": "you@example.com",
    "phone": "(555) 123-4567",
    "address": "Your Address",
    "primary_trade": "Professional Services",
}

DEMO_TERMS = {
    "deposit_percent": 50,
    "quote_valid_days": 30,
    "labor_warranty_years": 1,
    "accepted_payment_methods": ["Cash", "Check", "Credit Card"],
}


# Request/Response models

class DemoQuoteRequest(BaseModel):
    """Request to generate a demo quote from text."""
    description: str


class DemoQuoteResponse(BaseModel):
    """Generated demo quote response."""
    id: str = "demo"
    is_demo: bool = True
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    job_type: Optional[str] = None
    job_description: Optional[str] = None
    line_items: list = []
    subtotal: float = 0
    total: float = 0
    notes: Optional[str] = None
    estimated_days: Optional[int] = None
    estimated_crew_size: Optional[int] = None
    confidence: Optional[str] = None
    questions: list = []
    transcription: Optional[str] = None
    # Learning system messaging
    learning_disclaimer: str = "This quote was generated without personalized learning. With Quoted, the AI learns YOUR pricing over time - getting more accurate with every quote you correct."


class DemoPDFRequest(BaseModel):
    """Request to generate a demo PDF."""
    quote_data: dict
    contractor_name: Optional[str] = None


async def _generate_demo_quote_with_universal_prompt(transcription: str) -> dict:
    """
    Generate a quote using the universal demo prompt.

    This uses Claude directly with a specialized demo prompt that:
    - Detects the industry from the description
    - Uses Claude's world knowledge for reasonable pricing
    - Works for ANY type of work (contractors, designers, consultants, etc.)
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Get the universal demo prompt
    prompt = get_demo_quote_prompt(transcription)

    try:
        message = client.messages.create(
            model=settings.claude_model,
            max_tokens=settings.claude_max_tokens,
            tools=[QUOTE_GENERATION_TOOL],
            tool_choice={"type": "tool", "name": "generate_quote"},
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract the tool call result
        for block in message.content:
            if block.type == "tool_use" and block.name == "generate_quote":
                quote_data = block.input

                # Validate and normalize
                quote_data["transcription"] = transcription
                quote_data["generated_at"] = datetime.utcnow().isoformat()

                # Ensure subtotal matches line items
                if quote_data.get("line_items"):
                    calculated_subtotal = sum(
                        item.get("amount", 0) for item in quote_data["line_items"]
                    )
                    quote_data["subtotal"] = round(calculated_subtotal)

                return quote_data

        raise ValueError("No tool call found in response")

    except Exception as e:
        raise Exception(f"Error generating demo quote: {str(e)}")


@router.post("/quote", response_model=DemoQuoteResponse)
@limiter.limit("5/hour")
async def generate_demo_quote(
    request: Request,
    description: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
):
    """
    Generate a demo quote without authentication.

    UNIVERSAL DEMO: Works for ANY industry - contractors, designers,
    consultants, event planners, freelancers, and more.

    Accepts either:
    - description (text): Text description of the job/project
    - audio (file): Audio file to transcribe and generate quote from

    Rate limited to 5 quotes per IP per hour.

    Returns a real AI-generated quote. Quote is marked as is_demo=true
    and not saved to any account.
    """
    try:
        # Validate input - need either description or audio
        if not description and not audio:
            raise HTTPException(
                status_code=400,
                detail="Either 'description' (text) or 'audio' (file) is required"
            )

        if description and audio:
            raise HTTPException(
                status_code=400,
                detail="Provide either 'description' or 'audio', not both"
            )

        transcription_text = None

        # Handle audio upload
        if audio:
            # Save uploaded file temporarily
            suffix = os.path.splitext(audio.filename)[1] or ".webm"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                content = await audio.read()
                tmp.write(content)
                tmp_path = tmp.name

            try:
                # Transcribe the audio
                transcription_service = get_transcription_service()
                transcription_result = await transcription_service.transcribe(tmp_path)
                transcription_text = transcription_result.get("text", "")

                if not transcription_text.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="No speech detected in audio. Please try recording again."
                    )
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        else:
            # Use text description directly
            transcription_text = description.strip()

            if not transcription_text:
                raise HTTPException(
                    status_code=400,
                    detail="Description cannot be empty"
                )

        # Generate quote using UNIVERSAL demo prompt (works for any industry)
        quote_data = await _generate_demo_quote_with_universal_prompt(transcription_text)

        # Sanity check for demo quotes
        sanity_check_service = get_sanity_check_service()
        quote_total = quote_data.get("subtotal", 0)

        # Check against global bounds
        if quote_total > sanity_check_service.GLOBAL_MAX_QUOTE:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "quote_sanity_check_failed",
                    "message": f"This quote amount (${quote_total:,.0f}) exceeds reasonable bounds. Please try describing your project with more specific details.",
                    "quote_total": quote_total,
                }
            )

        # Add demo-specific metadata
        quote_data["is_demo"] = True
        quote_data["id"] = "demo"

        # Add learning system note to existing notes
        learning_note = "\n\n💡 This is a demo estimate using industry-standard pricing. With Quoted, the AI learns YOUR specific pricing - getting more accurate with every correction you make."
        if quote_data.get("notes"):
            quote_data["notes"] = quote_data["notes"] + learning_note
        else:
            quote_data["notes"] = "Demo estimate based on industry-standard pricing." + learning_note

        # Build response
        return DemoQuoteResponse(
            id="demo",
            is_demo=True,
            customer_name=quote_data.get("customer_name"),
            customer_address=quote_data.get("customer_address"),
            customer_phone=quote_data.get("customer_phone"),
            job_type=quote_data.get("job_type"),
            job_description=quote_data.get("job_description"),
            line_items=quote_data.get("line_items", []),
            subtotal=quote_data.get("subtotal", 0),
            total=quote_data.get("subtotal", 0),
            notes=quote_data.get("notes"),
            estimated_days=quote_data.get("estimated_days"),
            estimated_crew_size=quote_data.get("estimated_crew_size"),
            confidence=quote_data.get("confidence"),
            questions=quote_data.get("questions", []),
            transcription=transcription_text,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating demo quote: {str(e)}")


@router.post("/pdf")
@limiter.limit("5/hour")
async def generate_demo_pdf(
    request: Request,
    body: DemoPDFRequest,
):
    """
    Generate a demo PDF with watermark.

    The PDF includes a "DEMO" watermark to distinguish from real quotes.
    Uses the generic demo contractor profile unless overridden.
    """
    try:
        pdf_service = get_pdf_service()

        # Use provided contractor name or default
        demo_contractor = DEMO_CONTRACTOR.copy()
        if body.contractor_name:
            demo_contractor["business_name"] = body.contractor_name

        # Extract quote data from request body
        quote_data = body.quote_data.copy()

        # Add quote number for PDF
        quote_data["quote_number"] = f"DEMO-{datetime.now().strftime('%Y%m%d%H%M')}"

        # Generate PDF with demo watermark
        pdf_bytes = pdf_service.generate_quote_pdf(
            quote_data=quote_data,
            contractor=demo_contractor,
            terms=DEMO_TERMS,
            watermark=True,
            watermark_text="DEMO",  # Demo-specific watermark text
            template="modern",
        )

        # Return as base64 for easy frontend handling
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return {
            "pdf_base64": pdf_base64,
            "filename": f"demo-quote-{datetime.now().strftime('%Y%m%d')}.pdf",
            "is_demo": True,
            "watermarked": True,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating demo PDF: {str(e)}")


@router.get("/pdf/{quote_id}")
@limiter.limit("10/hour")
async def download_demo_pdf(
    request: Request,
    quote_id: str,
):
    """
    Alternative endpoint: Download demo PDF directly as file.

    For demo, always generates a sample PDF since we don't persist demo quotes.
    """
    try:
        pdf_service = get_pdf_service()

        # Create a sample quote for download
        sample_quote = {
            "quote_number": f"DEMO-{datetime.now().strftime('%Y%m%d%H%M')}",
            "customer_name": "Sample Customer",
            "customer_address": "123 Demo Street",
            "job_type": "demo_sample",
            "job_description": "This is a sample demo quote to show how Quoted generates professional PDF documents. Sign up to create real quotes with your own branding and pricing!",
            "line_items": [
                {"name": "Sample Service", "description": "Example line item", "amount": 500},
                {"name": "Materials", "description": "Example materials", "amount": 200},
            ],
            "subtotal": 700,
            "estimated_days": 2,
            "notes": "💡 This is a demo PDF. With Quoted, you get your logo, contact info, and AI that learns your pricing.",
        }

        pdf_bytes = pdf_service.generate_quote_pdf(
            quote_data=sample_quote,
            contractor=DEMO_CONTRACTOR,
            terms=DEMO_TERMS,
            watermark=True,
            watermark_text="DEMO",
            template="modern",
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=quoted-demo-{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating demo PDF: {str(e)}")
