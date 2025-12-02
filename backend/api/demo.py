"""
Demo API routes for Quoted.
Allows unauthenticated users to try the product without signing up.

Key features:
- No authentication required
- Rate limited per IP (3 quotes/hour)
- Uses hardcoded demo contractor profile
- Generates real quotes using existing quote generation logic
- Marks quotes as demo (not saved to user's account)
"""

import os
import tempfile
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services import get_transcription_service, get_quote_service


router = APIRouter()

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


# Demo contractor configuration (hardcoded, generic handyman profile)
DEMO_CONTRACTOR = {
    "id": "demo",
    "business_name": "Demo Handyman Services",
    "owner_name": "Demo Contractor",
    "email": "demo@quoted.it.com",
    "phone": "(555) 123-4567",
    "address": "123 Main St, Anytown, USA",
    "primary_trade": "General Contractor",
}

DEMO_PRICING_MODEL = {
    "labor_rate_hourly": 75.0,
    "helper_rate_hourly": 45.0,
    "material_markup_percent": 20.0,
    "minimum_job_amount": 150.0,
    "pricing_knowledge": {
        "categories": {
            "general_repairs": {
                "display_name": "General Repairs",
                "base_rates": {
                    "labor_rate": 75.0,
                    "typical_hours": 2,
                },
            },
            "painting": {
                "display_name": "Painting",
                "base_rates": {
                    "labor_rate": 65.0,
                    "typical_sqft_rate": 3.5,
                },
            },
            "basic_electrical": {
                "display_name": "Basic Electrical",
                "base_rates": {
                    "labor_rate": 85.0,
                    "outlet_install": 150.0,
                    "switch_install": 125.0,
                },
            },
            "basic_plumbing": {
                "display_name": "Basic Plumbing",
                "base_rates": {
                    "labor_rate": 85.0,
                    "faucet_install": 200.0,
                    "toilet_install": 250.0,
                },
            },
        }
    },
    "pricing_notes": "Demo pricing for general handyman services. Covers basic repairs, painting, electrical, and plumbing work.",
}

DEMO_TERMS = {
    "deposit_percent": 25,
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


@router.post("/quote", response_model=DemoQuoteResponse)
@limiter.limit("3/hour")
async def generate_demo_quote(
    request: Request,
    description: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
):
    """
    Generate a demo quote without authentication.

    Accepts either:
    - description (text): Text description of the job
    - audio (file): Audio file to transcribe and generate quote from

    Rate limited to 3 quotes per IP per hour.

    Returns a real quote using demo contractor profile.
    Quote is marked as is_demo=true and not saved to any account.
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

        quote_service = get_quote_service()
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

        # Detect job type
        detected_job_type = await quote_service.detect_job_type(
            transcription_text,
            pricing_knowledge=DEMO_PRICING_MODEL.get("pricing_knowledge")
        )

        # Generate quote using demo contractor profile
        # No correction examples for demo (no learning history)
        quote_data = await quote_service.generate_quote(
            transcription=transcription_text,
            contractor=DEMO_CONTRACTOR,
            pricing_model=DEMO_PRICING_MODEL,
            terms=DEMO_TERMS,
            correction_examples=None,  # No learning for demo
            detected_category=detected_job_type,
        )

        # Add demo-specific metadata
        quote_data["is_demo"] = True
        quote_data["id"] = "demo"

        # Add helpful note about demo mode
        demo_note = "\n\nThis is a DEMO quote. Sign up to save quotes, track history, and improve accuracy over time."
        if quote_data.get("notes"):
            quote_data["notes"] = quote_data["notes"] + demo_note
        else:
            quote_data["notes"] = "Demo quote using generic handyman pricing." + demo_note

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
            total=quote_data.get("subtotal", 0),  # Demo quotes have no tax
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
