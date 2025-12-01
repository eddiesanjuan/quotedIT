"""
Quote API routes for Quoted.
Handles quote generation, editing, and PDF creation.
"""

import os
import tempfile
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..services import (
    get_transcription_service,
    get_quote_service,
    get_pdf_service,
    get_learning_service,
)


router = APIRouter()


# Request/Response models

class QuoteRequest(BaseModel):
    """Request to generate a quote from text."""
    transcription: str
    contractor_id: str


class QuoteResponse(BaseModel):
    """Generated quote response."""
    id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    job_type: Optional[str] = None
    job_description: Optional[str] = None
    line_items: list = []
    subtotal: float = 0
    notes: Optional[str] = None
    estimated_days: Optional[int] = None
    estimated_crew_size: Optional[int] = None
    confidence: Optional[str] = None
    questions: list = []
    transcription: Optional[str] = None
    generated_at: Optional[str] = None


class QuoteUpdateRequest(BaseModel):
    """Request to update/correct a quote."""
    line_items: Optional[list] = None
    job_description: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    estimated_days: Optional[int] = None
    estimated_crew_size: Optional[int] = None
    notes: Optional[str] = None
    correction_notes: Optional[str] = None


# Mock data for demo (replace with database queries)
DEMO_CONTRACTOR = {
    "id": "demo-contractor",
    "business_name": "Mike's Deck Pros",
    "owner_name": "Mike Johnson",
    "email": "mike@deckpros.com",
    "phone": "(555) 123-4567",
    "address": "123 Main St, Anytown, USA",
    "primary_trade": "deck_builder",
}

DEMO_PRICING_MODEL = {
    "labor_rate_hourly": 75.0,
    "helper_rate_hourly": 45.0,
    "material_markup_percent": 20.0,
    "minimum_job_amount": 1500.0,
    "pricing_knowledge": {
        "composite_deck": {
            "base_per_sqft": 58.0,
            "typical_range": [48.0, 75.0],
            "unit": "sqft",
            "notes": "Trex Select baseline",
            "confidence": 0.85,
            "samples": 23,
        },
        "wood_deck": {
            "base_per_sqft": 42.0,
            "typical_range": [35.0, 55.0],
            "unit": "sqft",
        },
        "railing": {
            "per_linear_foot": 38.0,
            "unit": "linear_ft",
            "cable_rail_multiplier": 1.8,
        },
        "demolition": {
            "base_rate": 900.0,
            "per_sqft_adder": 2.5,
            "notes": "Add 50% for second story",
        },
        "stairs": {
            "per_step": 175.0,
            "landing_flat": 400.0,
        },
    },
    "pricing_notes": "I add 10% for jobs in difficult access areas. 5% discount for repeat customers.",
}

DEMO_TERMS = {
    "deposit_percent": 50.0,
    "quote_valid_days": 30,
    "labor_warranty_years": 2,
    "accepted_payment_methods": ["check", "credit_card", "Zelle"],
}

# In-memory quote storage for demo
_quotes = {}


@router.post("/generate", response_model=QuoteResponse)
async def generate_quote(request: QuoteRequest):
    """
    Generate a quote from transcribed text.

    Takes the transcribed voice note and generates a structured quote
    using the contractor's pricing model.
    """
    try:
        quote_service = get_quote_service()

        # Generate the quote
        quote_data = await quote_service.generate_quote(
            transcription=request.transcription,
            contractor=DEMO_CONTRACTOR,  # TODO: Load from database
            pricing_model=DEMO_PRICING_MODEL,
            terms=DEMO_TERMS,
        )

        # Store for later retrieval
        quote_id = f"quote_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        quote_data["id"] = quote_id
        _quotes[quote_id] = quote_data

        return QuoteResponse(**quote_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-from-audio", response_model=QuoteResponse)
async def generate_quote_from_audio(
    audio: UploadFile = File(...),
    contractor_id: str = Form("demo-contractor"),
):
    """
    Generate a quote from audio file.

    Full pipeline: Audio → Transcription → Quote Generation
    """
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(audio.filename)[1] or ".mp3"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            quote_service = get_quote_service()
            transcription_service = get_transcription_service()

            # Generate quote from audio
            quote_data = await quote_service.generate_quote_from_audio(
                audio_file_path=tmp_path,
                contractor=DEMO_CONTRACTOR,
                pricing_model=DEMO_PRICING_MODEL,
                terms=DEMO_TERMS,
                transcription_service=transcription_service,
            )

            # Check for errors
            if quote_data.get("error"):
                raise HTTPException(status_code=400, detail=quote_data["error"])

            # Store for later
            quote_id = f"quote_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            quote_data["id"] = quote_id
            _quotes[quote_id] = quote_data

            return QuoteResponse(**quote_data)

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(quote_id: str):
    """Get a quote by ID."""
    if quote_id not in _quotes:
        raise HTTPException(status_code=404, detail="Quote not found")

    return QuoteResponse(**_quotes[quote_id])


@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(quote_id: str, update: QuoteUpdateRequest):
    """
    Update/correct a quote.

    This triggers the learning loop to improve future quotes.
    """
    if quote_id not in _quotes:
        raise HTTPException(status_code=404, detail="Quote not found")

    original_quote = _quotes[quote_id].copy()

    # Apply updates
    quote = _quotes[quote_id]

    if update.line_items is not None:
        quote["line_items"] = update.line_items
        quote["subtotal"] = sum(item.get("amount", 0) for item in update.line_items)

    if update.job_description is not None:
        quote["job_description"] = update.job_description

    if update.customer_name is not None:
        quote["customer_name"] = update.customer_name

    if update.customer_address is not None:
        quote["customer_address"] = update.customer_address

    if update.customer_phone is not None:
        quote["customer_phone"] = update.customer_phone

    if update.estimated_days is not None:
        quote["estimated_days"] = update.estimated_days

    if update.estimated_crew_size is not None:
        quote["estimated_crew_size"] = update.estimated_crew_size

    if update.notes is not None:
        quote["notes"] = update.notes

    quote["was_edited"] = True
    quote["edited_at"] = datetime.utcnow().isoformat()

    # Trigger learning
    try:
        learning_service = get_learning_service()
        learning_result = await learning_service.process_correction(
            original_quote=original_quote,
            final_quote=quote,
            contractor_notes=update.correction_notes,
        )
        quote["learning_result"] = learning_result
    except Exception as e:
        # Don't fail the update if learning fails
        print(f"Learning failed: {e}")

    _quotes[quote_id] = quote
    return QuoteResponse(**quote)


@router.post("/{quote_id}/pdf")
async def generate_pdf(quote_id: str):
    """Generate a PDF for a quote."""
    if quote_id not in _quotes:
        raise HTTPException(status_code=404, detail="Quote not found")

    quote = _quotes[quote_id]

    try:
        pdf_service = get_pdf_service()

        # Generate PDF
        output_path = f"./data/pdfs/{quote_id}.pdf"
        pdf_bytes = pdf_service.generate_quote_pdf(
            quote_data=quote,
            contractor=DEMO_CONTRACTOR,
            terms=DEMO_TERMS,
            output_path=output_path,
        )

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"quote_{quote_id}.pdf",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_quotes():
    """List all quotes (for demo purposes)."""
    return {
        "quotes": list(_quotes.values()),
        "count": len(_quotes),
    }
