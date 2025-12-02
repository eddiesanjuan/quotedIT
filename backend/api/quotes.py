"""
Quote API routes for Quoted.
Handles quote generation, editing, and PDF creation.

Key flow:
1. User records voice → transcribed
2. Generate quote using contractor's pricing model from DB
3. User edits quote → corrections trigger learning
4. Learning updates pricing model in DB
5. Future quotes are more accurate
"""

import os
import tempfile
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..services import (
    get_transcription_service,
    get_quote_service,
    get_pdf_service,
    get_learning_service,
    get_db_service,
)
from ..services.auth import get_current_user


router = APIRouter()


# Request/Response models

class QuoteRequest(BaseModel):
    """Request to generate a quote from text."""
    transcription: str


class QuoteLineItem(BaseModel):
    """Line item in a quote."""
    name: str
    description: Optional[str] = None
    amount: float
    quantity: Optional[float] = 1
    unit: Optional[str] = None


class QuoteResponse(BaseModel):
    """Generated quote response."""
    id: str
    contractor_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    job_type: Optional[str] = None
    job_description: Optional[str] = None
    line_items: List[dict] = []
    subtotal: float = 0
    total: float = 0
    notes: Optional[str] = None
    estimated_days: Optional[int] = None
    estimated_crew_size: Optional[int] = None
    confidence: Optional[str] = None
    questions: List[str] = []
    transcription: Optional[str] = None
    was_edited: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class QuoteUpdateRequest(BaseModel):
    """Request to update/correct a quote."""
    line_items: Optional[List[dict]] = None
    job_description: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    estimated_days: Optional[int] = None
    estimated_crew_size: Optional[int] = None
    notes: Optional[str] = None
    correction_notes: Optional[str] = None  # Why the user made changes


def quote_to_response(quote) -> QuoteResponse:
    """Convert a Quote model to response."""
    return QuoteResponse(
        id=quote.id,
        contractor_id=quote.contractor_id,
        customer_name=quote.customer_name,
        customer_address=quote.customer_address,
        customer_phone=quote.customer_phone,
        customer_email=quote.customer_email,
        job_type=quote.job_type,
        job_description=quote.job_description,
        line_items=quote.line_items or [],
        subtotal=quote.subtotal or 0,
        total=quote.total or 0,
        notes=getattr(quote, 'notes', None),
        estimated_days=quote.estimated_days,
        estimated_crew_size=quote.estimated_crew_size,
        transcription=quote.transcription,
        was_edited=quote.was_edited or False,
        created_at=quote.created_at.isoformat() if quote.created_at else None,
        updated_at=quote.updated_at.isoformat() if quote.updated_at else None,
    )


@router.post("/generate", response_model=QuoteResponse)
async def generate_quote(request: QuoteRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate a quote from transcribed text.

    Uses the authenticated user's pricing model from the database.
    """
    try:
        db = get_db_service()
        quote_service = get_quote_service()

        # Get contractor for this user
        contractor = await db.get_contractor_by_user_id(current_user["id"])
        if not contractor:
            raise HTTPException(status_code=400, detail="Please complete onboarding first")

        # Get their pricing model
        pricing_model = await db.get_pricing_model(contractor.id)
        if not pricing_model:
            raise HTTPException(status_code=400, detail="Please complete onboarding first")

        # Get their terms
        terms = await db.get_terms(contractor.id)

        # Convert models to dicts for the quote generator
        contractor_dict = {
            "id": contractor.id,
            "business_name": contractor.business_name,
            "owner_name": contractor.owner_name,
            "email": contractor.email,
            "phone": contractor.phone,
            "address": contractor.address,
            "primary_trade": contractor.primary_trade,
        }

        pricing_dict = {
            "labor_rate_hourly": pricing_model.labor_rate_hourly,
            "helper_rate_hourly": pricing_model.helper_rate_hourly,
            "material_markup_percent": pricing_model.material_markup_percent,
            "minimum_job_amount": pricing_model.minimum_job_amount,
            "pricing_knowledge": pricing_model.pricing_knowledge or {},
            "pricing_notes": pricing_model.pricing_notes,
        }

        terms_dict = None
        if terms:
            terms_dict = {
                "deposit_percent": terms.deposit_percent,
                "quote_valid_days": terms.quote_valid_days,
                "labor_warranty_years": terms.labor_warranty_years,
                "accepted_payment_methods": terms.accepted_payment_methods,
            }

        # PASS 1: Detect category from transcription (fast, cheap call)
        # Uses user's existing categories for fuzzy matching, or creates new ones
        detected_job_type = await quote_service.detect_job_type(
            request.transcription,
            pricing_knowledge=pricing_dict.get("pricing_knowledge")
        )

        # PASS 2: Fetch type-specific correction examples for few-shot learning
        # First try to get examples for this specific job type
        correction_examples = await db.get_correction_examples(
            contractor.id,
            job_type=detected_job_type
        )

        # If no type-specific corrections, fall back to general corrections
        if not correction_examples:
            correction_examples = await db.get_correction_examples(contractor.id)

        # PASS 3: Generate quote with type-filtered context
        quote_data = await quote_service.generate_quote(
            transcription=request.transcription,
            contractor=contractor_dict,
            pricing_model=pricing_dict,
            terms=terms_dict,
            correction_examples=correction_examples,
        )

        # Ensure detected job_type is used if AI didn't return one
        if not quote_data.get("job_type"):
            quote_data["job_type"] = detected_job_type

        # Save to database
        quote = await db.create_quote(
            contractor_id=contractor.id,
            transcription=request.transcription,
            job_type=quote_data.get("job_type"),
            job_description=quote_data.get("job_description"),
            line_items=quote_data.get("line_items", []),
            subtotal=quote_data.get("subtotal", 0),
            customer_name=quote_data.get("customer_name"),
            customer_address=quote_data.get("customer_address"),
            customer_phone=quote_data.get("customer_phone"),
            estimated_days=quote_data.get("estimated_days"),
            ai_generated_total=quote_data.get("subtotal", 0),
        )

        return quote_to_response(quote)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TranscriptionResponse(BaseModel):
    """Response from transcription endpoint."""
    text: str
    duration: Optional[float] = None


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Transcribe audio to text without generating a quote.
    Useful for interview/chat voice messages.
    """
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(audio.filename)[1] or ".webm"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            transcription_service = get_transcription_service()
            result = await transcription_service.transcribe(tmp_path)

            if not result.get("text"):
                raise HTTPException(status_code=400, detail="No speech detected in audio")

            return TranscriptionResponse(
                text=result["text"],
                duration=result.get("duration"),
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-from-audio", response_model=QuoteResponse)
async def generate_quote_from_audio(
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a quote from audio file.

    Full pipeline: Audio → Transcription → Quote Generation
    """
    try:
        db = get_db_service()

        # Get contractor for this user
        contractor = await db.get_contractor_by_user_id(current_user["id"])
        if not contractor:
            raise HTTPException(status_code=400, detail="Please complete onboarding first")

        # Get their pricing model
        pricing_model = await db.get_pricing_model(contractor.id)
        if not pricing_model:
            raise HTTPException(status_code=400, detail="Please complete onboarding first")

        # Get their terms
        terms = await db.get_terms(contractor.id)

        # Save uploaded file temporarily
        suffix = os.path.splitext(audio.filename)[1] or ".mp3"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            quote_service = get_quote_service()
            transcription_service = get_transcription_service()

            # Convert models to dicts
            contractor_dict = {
                "id": contractor.id,
                "business_name": contractor.business_name,
                "owner_name": contractor.owner_name,
                "email": contractor.email,
                "phone": contractor.phone,
                "address": contractor.address,
                "primary_trade": contractor.primary_trade,
            }

            pricing_dict = {
                "labor_rate_hourly": pricing_model.labor_rate_hourly,
                "helper_rate_hourly": pricing_model.helper_rate_hourly,
                "material_markup_percent": pricing_model.material_markup_percent,
                "minimum_job_amount": pricing_model.minimum_job_amount,
                "pricing_knowledge": pricing_model.pricing_knowledge or {},
                "pricing_notes": pricing_model.pricing_notes,
            }

            terms_dict = None
            if terms:
                terms_dict = {
                    "deposit_percent": terms.deposit_percent,
                    "quote_valid_days": terms.quote_valid_days,
                    "labor_warranty_years": terms.labor_warranty_years,
                    "accepted_payment_methods": terms.accepted_payment_methods,
                }

            # STEP 1: Transcribe the audio first
            transcription_result = await transcription_service.transcribe(tmp_path)
            transcription_text = transcription_result.get("text", "")

            if not transcription_text.strip():
                raise HTTPException(status_code=400, detail="No speech detected in audio")

            # STEP 2: Detect category from transcription (fast, cheap call)
            # Uses user's existing categories for fuzzy matching, or creates new ones
            detected_job_type = await quote_service.detect_job_type(
                transcription_text,
                pricing_knowledge=pricing_dict.get("pricing_knowledge")
            )

            # STEP 3: Fetch type-specific correction examples for few-shot learning
            correction_examples = await db.get_correction_examples(
                contractor.id,
                job_type=detected_job_type
            )

            # Fall back to general corrections if no type-specific ones
            if not correction_examples:
                correction_examples = await db.get_correction_examples(contractor.id)

            # STEP 4: Generate quote with type-filtered context
            quote_data = await quote_service.generate_quote(
                transcription=transcription_text,
                contractor=contractor_dict,
                pricing_model=pricing_dict,
                terms=terms_dict,
                correction_examples=correction_examples,
            )

            # Add audio metadata
            quote_data["audio_duration"] = transcription_result.get("duration", 0)
            quote_data["transcription_confidence"] = transcription_result.get("confidence")

            # Ensure detected job_type is used if AI didn't return one
            if not quote_data.get("job_type"):
                quote_data["job_type"] = detected_job_type

            # Save to database
            quote = await db.create_quote(
                contractor_id=contractor.id,
                transcription=quote_data.get("transcription", ""),
                job_type=quote_data.get("job_type"),
                job_description=quote_data.get("job_description"),
                line_items=quote_data.get("line_items", []),
                subtotal=quote_data.get("subtotal", 0),
                customer_name=quote_data.get("customer_name"),
                customer_address=quote_data.get("customer_address"),
                customer_phone=quote_data.get("customer_phone"),
                estimated_days=quote_data.get("estimated_days"),
                ai_generated_total=quote_data.get("subtotal", 0),
            )

            return quote_to_response(quote)

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(quote_id: str, current_user: dict = Depends(get_current_user)):
    """Get a quote by ID."""
    db = get_db_service()
    quote = await db.get_quote(quote_id)

    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return quote_to_response(quote)


@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: str,
    update: QuoteUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update/correct a quote.

    THIS IS THE LEARNING TRIGGER.
    When a user corrects a quote, we:
    1. Save the correction
    2. Analyze what changed
    3. Update their pricing model
    """
    db = get_db_service()

    # Get the original quote
    quote = await db.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Store original state for learning (this is critical for the learning loop)
    original_line_items = quote.line_items or []
    original_subtotal = quote.subtotal or 0
    original_quote = {
        "line_items": original_line_items,
        "subtotal": original_subtotal,
        "job_description": quote.job_description,
        "estimated_days": quote.estimated_days,
    }

    # Build update dict
    update_data = {}
    if update.line_items is not None:
        update_data["line_items"] = update.line_items
        update_data["subtotal"] = sum(item.get("amount", 0) for item in update.line_items)
        update_data["total"] = update_data["subtotal"]
    if update.job_description is not None:
        update_data["job_description"] = update.job_description
    if update.customer_name is not None:
        update_data["customer_name"] = update.customer_name
    if update.customer_address is not None:
        update_data["customer_address"] = update.customer_address
    if update.customer_phone is not None:
        update_data["customer_phone"] = update.customer_phone
    if update.customer_email is not None:
        update_data["customer_email"] = update.customer_email
    if update.estimated_days is not None:
        update_data["estimated_days"] = update.estimated_days
    if update.estimated_crew_size is not None:
        update_data["estimated_crew_size"] = update.estimated_crew_size
    if update.notes is not None:
        # Store notes as part of job_description for now
        pass

    # Mark as edited
    update_data["was_edited"] = True

    # Update the quote in database
    updated_quote = await db.update_quote(quote_id, **update_data)

    # ==========================================
    # THE LEARNING LOOP - This is the magic
    # ==========================================
    try:
        learning_service = get_learning_service()

        # Build the final quote state
        final_quote = {
            "line_items": updated_quote.line_items,
            "subtotal": updated_quote.subtotal,
            "job_description": updated_quote.job_description,
            "estimated_days": updated_quote.estimated_days,
        }

        # Process the correction
        learning_result = await learning_service.process_correction(
            original_quote=original_quote,
            final_quote=final_quote,
            contractor_notes=update.correction_notes,
        )

        # If there were learnings, apply them to the pricing model
        if learning_result.get("has_changes") and learning_result.get("learnings"):
            await db.apply_learnings_to_pricing_model(
                contractor_id=contractor.id,
                learnings=learning_result["learnings"],
            )

            # Store edit details on the quote for history and future learning
            await db.update_quote(
                quote_id,
                edit_details={
                    "original_line_items": original_line_items,
                    "original_subtotal": original_subtotal,
                    "corrections": learning_result.get("corrections"),
                    "learning_note": update.correction_notes,
                    "learnings_applied": True,
                    "processed_at": datetime.utcnow().isoformat(),
                }
            )

            print(f"[LEARNING] Applied learnings for contractor {contractor.id}")

    except Exception as e:
        # Don't fail the update if learning fails
        print(f"[LEARNING ERROR] {e}")

    # Refresh the quote
    updated_quote = await db.get_quote(quote_id)
    return quote_to_response(updated_quote)


@router.post("/{quote_id}/pdf")
async def generate_pdf(quote_id: str, current_user: dict = Depends(get_current_user)):
    """Generate a PDF for a quote."""
    db = get_db_service()

    quote = await db.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get terms
    terms = await db.get_terms(contractor.id)

    try:
        pdf_service = get_pdf_service()

        # Convert to dicts
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

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"quote_{quote_id}.pdf",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_quotes(current_user: dict = Depends(get_current_user)):
    """List all quotes for the current user."""
    db = get_db_service()

    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        return {"quotes": [], "count": 0}

    quotes = await db.get_quotes_by_contractor(contractor.id)

    return {
        "quotes": [quote_to_response(q) for q in quotes],
        "count": len(quotes),
    }


@router.get("/{quote_id}/learning-stats")
async def get_learning_stats(quote_id: str, current_user: dict = Depends(get_current_user)):
    """Get learning statistics for a contractor based on their quote history."""
    db = get_db_service()

    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get quote history
    quote_history = await db.get_quote_history_for_learning(contractor.id)

    # Calculate stats
    learning_service = get_learning_service()
    stats = learning_service.calculate_accuracy_stats(quote_history)

    return stats
