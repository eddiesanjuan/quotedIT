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

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct, func, or_

from ..services import (
    get_transcription_service,
    get_quote_service,
    get_pdf_service,
    get_learning_service,
    get_db_service,
    get_sanity_check_service,
    get_onboarding_service,
)
from ..services.auth import get_current_user, get_db
from ..services.billing import BillingService
from ..services.analytics import analytics_service
from ..models.database import Quote
from ..services.database import async_session_factory


router = APIRouter()

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


# Request/Response models

class QuoteRequest(BaseModel):
    """Request to generate a quote from text."""
    transcription: str
    use_confidence_sampling: bool = False  # Enhancement 3: Multi-sample variance
    num_samples: int = 3  # Number of samples for confidence sampling


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


# Enhancement 5: Active Learning Models
class ClarifyingQuestion(BaseModel):
    """A clarifying question for the user."""
    id: str
    question: str
    type: str = "text"  # text, select, number
    options: Optional[List[str]] = None
    impact: Optional[str] = None
    default_assumption: Optional[str] = None


class ClarifyingQuestionsRequest(BaseModel):
    """Request to get clarifying questions."""
    transcription: str
    max_questions: int = 3


class ClarifyingQuestionsResponse(BaseModel):
    """Response with clarifying questions."""
    questions: List[ClarifyingQuestion]
    reasoning: Optional[str] = None
    missing_info: List[str] = []


class ClarificationAnswer(BaseModel):
    """An answer to a clarifying question."""
    question_id: str
    question: str
    answer: str


class QuoteWithClarificationsRequest(BaseModel):
    """Request to generate quote with clarification answers."""
    transcription: str
    clarifications: List[ClarificationAnswer]


# ============================================================================
# Feedback Models (Enhancement 4)
# ============================================================================

class FeedbackIssue(str):
    """Valid feedback issue types."""
    PRICE_TOO_HIGH = "price_too_high"
    PRICE_TOO_LOW = "price_too_low"
    MISSING_ITEMS = "missing_items"
    WRONG_QUANTITIES = "wrong_quantities"
    UNCLEAR_DESCRIPTION = "unclear_description"
    WRONG_JOB_TYPE = "wrong_job_type"
    TIMELINE_UNREALISTIC = "timeline_unrealistic"


class QuoteFeedbackRequest(BaseModel):
    """Request to submit feedback on a quote."""
    # Overall rating (1-5 stars)
    overall_rating: Optional[int] = None

    # Aspect ratings (1-5 each)
    pricing_accuracy: Optional[int] = None
    description_quality: Optional[int] = None
    line_item_completeness: Optional[int] = None
    timeline_accuracy: Optional[int] = None

    # Issue flags
    issues: Optional[List[str]] = None

    # Quick pricing feedback
    pricing_direction: Optional[str] = None  # "too_high", "too_low", "about_right"
    pricing_off_by_percent: Optional[float] = None

    # Actual values if known
    actual_total: Optional[float] = None
    actual_line_items: Optional[List[dict]] = None

    # Free-form feedback
    feedback_text: Optional[str] = None
    improvement_suggestions: Optional[str] = None

    # Context
    quote_was_sent: Optional[bool] = None
    quote_outcome: Optional[str] = None  # "won", "lost", "pending"

    class Config:
        schema_extra = {
            "example": {
                "overall_rating": 4,
                "pricing_direction": "about_right",
                "issues": ["missing_items"],
                "feedback_text": "Quote was good but forgot to include permits",
            }
        }


class QuoteFeedbackResponse(BaseModel):
    """Response for quote feedback."""
    id: str
    quote_id: str
    overall_rating: Optional[int] = None
    pricing_accuracy: Optional[int] = None
    description_quality: Optional[int] = None
    line_item_completeness: Optional[int] = None
    timeline_accuracy: Optional[int] = None
    issues: Optional[List[str]] = None
    pricing_direction: Optional[str] = None
    pricing_off_by_percent: Optional[float] = None
    actual_total: Optional[float] = None
    feedback_text: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    quote_was_sent: Optional[bool] = None
    quote_outcome: Optional[str] = None
    created_at: Optional[str] = None


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
@limiter.limit("30/minute")
async def generate_quote(
    request: Request,
    quote_request: QuoteRequest,
    current_user: dict = Depends(get_current_user),
    auth_db: AsyncSession = Depends(get_db),
):
    """
    Generate a quote from transcribed text.

    Uses the authenticated user's pricing model from the database.
    """
    try:
        # Check billing status first
        billing_check = await BillingService.check_quote_limit(auth_db, current_user["id"])

        if not billing_check["can_generate"]:
            if billing_check["reason"] == "trial_expired":
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "trial_expired",
                        "message": "Your trial has expired. Please upgrade to continue generating quotes.",
                        "trial_ends_at": billing_check.get("trial_ends_at"),
                    }
                )
            elif billing_check["reason"] == "trial_limit_reached":
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "trial_limit_reached",
                        "message": f"You've reached your trial limit of {billing_check.get('quotes_used', 0)} quotes. Please upgrade to continue.",
                    }
                )
            else:
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "quota_exceeded",
                        "message": "Unable to generate quote. Please check your subscription status.",
                    }
                )

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

        # LAZY GENERATION: For existing users without pricing_philosophy (grandfathering)
        # Generate one from their existing data and save it for future quotes
        pricing_philosophy = pricing_model.pricing_philosophy
        if not pricing_philosophy:
            onboarding = get_onboarding_service()
            pricing_philosophy = onboarding.generate_philosophy_from_existing_model(
                contractor_name=contractor.business_name or contractor.owner_name or "Contractor",
                primary_trade=contractor.primary_trade or "general_contractor",
                pricing_model=pricing_dict,
            )
            # Save it so we don't regenerate every time
            await db.update_pricing_model(
                contractor.id,
                pricing_philosophy=pricing_philosophy
            )
            print(f"[GRANDFATHER] Generated pricing_philosophy for existing user {contractor.id}")

        pricing_dict["pricing_philosophy"] = pricing_philosophy

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
            quote_request.transcription,
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
        # AND category-specific learned adjustments injected into the prompt
        # Enhancement 3: Optionally use confidence sampling for data-driven confidence
        if quote_request.use_confidence_sampling:
            quote_data, variance_confidence = await quote_service.generate_quote_with_confidence(
                transcription=quote_request.transcription,
                contractor=contractor_dict,
                pricing_model=pricing_dict,
                terms=terms_dict,
                correction_examples=correction_examples,
                detected_category=detected_job_type,
                num_samples=min(max(quote_request.num_samples, 2), 5),  # Clamp to 2-5
            )
        else:
            quote_data = await quote_service.generate_quote(
                transcription=quote_request.transcription,
                contractor=contractor_dict,
                pricing_model=pricing_dict,
                terms=terms_dict,
                correction_examples=correction_examples,
                detected_category=detected_job_type,  # For learned adjustments injection
            )

        # Ensure detected job_type is used if AI didn't return one
        if not quote_data.get("job_type"):
            quote_data["job_type"] = detected_job_type

        # DISC-034: Pricing sanity check to prevent catastrophic hallucinations
        sanity_check_service = get_sanity_check_service()
        sanity_result = await sanity_check_service.check_quote_sanity(
            db=auth_db,
            contractor_id=contractor.id,
            quote_total=quote_data.get("subtotal", 0),
            category=detected_job_type,
        )

        # If quote is blocked (>10x P95), return error
        if not sanity_result["is_sane"]:
            # Log the blocked quote for pattern analysis
            await sanity_check_service.log_flagged_quote(
                db=auth_db,
                contractor_id=contractor.id,
                quote_total=quote_data.get("subtotal", 0),
                category=detected_job_type,
                action="block",
                bounds=sanity_result["bounds"],
                transcription=quote_request.transcription,
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "quote_sanity_check_failed",
                    "message": sanity_result["message"],
                    "quote_total": quote_data.get("subtotal", 0),
                    "bounds": sanity_result["bounds"],
                }
            )

        # If quote is flagged with warning (>3x P95), add warning to quote
        if sanity_result["action"] == "warn":
            quote_data["sanity_warning"] = sanity_result["message"]
            # Log the warning for pattern analysis
            await sanity_check_service.log_flagged_quote(
                db=auth_db,
                contractor_id=contractor.id,
                quote_total=quote_data.get("subtotal", 0),
                category=detected_job_type,
                action="warn",
                bounds=sanity_result["bounds"],
                transcription=quote_request.transcription,
            )

        # Save to database (DISC-018: Mark grace quotes)
        quote = await db.create_quote(
            contractor_id=contractor.id,
            transcription=quote_request.transcription,
            job_type=quote_data.get("job_type"),
            job_description=quote_data.get("job_description"),
            line_items=quote_data.get("line_items", []),
            subtotal=quote_data.get("subtotal", 0),
            customer_name=quote_data.get("customer_name"),
            customer_address=quote_data.get("customer_address"),
            customer_phone=quote_data.get("customer_phone"),
            estimated_days=quote_data.get("estimated_days"),
            ai_generated_total=quote_data.get("subtotal", 0),
            is_grace_quote=billing_check.get("is_grace_quote", False),
        )

        # Register the category so future quotes can match against it
        # This ensures the category list grows with usage, not just edits
        await db.ensure_category_exists(contractor.id, detected_job_type)

        # Increment quote usage counter (DISC-018: Track grace quotes separately)
        await BillingService.increment_quote_usage(
            auth_db,
            current_user["id"],
            is_grace_quote=billing_check.get("is_grace_quote", False)
        )

        # Track quote generation event (DISC-012: Include user learning stats)
        try:
            # Get user's total quote and edit counts for edit rate tracking
            all_quotes = await db.get_quotes_by_contractor(contractor.id)
            user_quote_count = len(all_quotes)
            user_edit_count = sum(1 for q in all_quotes if q.was_edited)

            # Get category-specific stats
            category_quotes = [q for q in all_quotes if q.job_type == detected_job_type]
            category_quote_count = len(category_quotes)
            category_edit_count = sum(1 for q in category_quotes if q.was_edited)

            analytics_service.track_event(
                user_id=str(current_user["id"]),
                event_name="quote_generated",
                properties={
                    "contractor_id": str(contractor.id),
                    "quote_id": str(quote.id),
                    "job_type": detected_job_type,
                    "subtotal": quote_data.get("subtotal", 0),
                    "has_customer_info": bool(quote_data.get("customer_name")),
                    "confidence": quote_data.get("confidence"),
                    "line_item_count": len(quote_data.get("line_items", [])),
                    # DISC-011: Input method tracking (voice vs text)
                    "input_method": "text",
                    # DISC-012: User learning stats for edit rate trend analysis
                    "user_quote_count": user_quote_count,
                    "user_edit_count": user_edit_count,
                    "user_edit_rate": round(user_edit_count / user_quote_count * 100, 2) if user_quote_count > 0 else 0,
                    "category_quote_count": category_quote_count,
                    "category_edit_count": category_edit_count,
                    "category_edit_rate": round(category_edit_count / category_quote_count * 100, 2) if category_quote_count > 0 else 0,
                    # DISC-018: Trial warning tracking
                    "warning_level": billing_check.get("warning_level"),
                    "is_grace_quote": billing_check.get("is_grace_quote", False),
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track quote generation: {e}")

        # DISC-018: Add billing info to response for frontend warnings
        response = quote_to_response(quote)
        response_dict = response.dict()
        response_dict["billing_info"] = {
            "warning_level": billing_check.get("warning_level"),
            "is_grace_quote": billing_check.get("is_grace_quote", False),
            "quotes_remaining": billing_check.get("quotes_remaining", 0),
            "grace_remaining": billing_check.get("grace_remaining", 0),
        }

        return response_dict

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Enhancement 5: Active Learning Endpoints
# ============================================================================

@router.post("/clarifying-questions", response_model=ClarifyingQuestionsResponse)
@limiter.limit("30/minute")
async def get_clarifying_questions(
    request: Request,
    clarify_request: ClarifyingQuestionsRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Get clarifying questions to improve quote accuracy.

    Enhancement 5: Active Learning - When information is ambiguous or
    incomplete, generate targeted questions that would most improve
    estimate accuracy.

    Use this when:
    - Initial quote has low confidence
    - User wants more accurate estimate
    - Description is vague or missing key details
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

        contractor_dict = {
            "primary_trade": contractor.primary_trade,
            "business_name": contractor.business_name,
        }

        pricing_dict = {
            "pricing_knowledge": pricing_model.pricing_knowledge or {},
        }

        # Generate clarifying questions
        result = await quote_service.generate_clarifying_questions(
            transcription=clarify_request.transcription,
            contractor=contractor_dict,
            pricing_model=pricing_dict,
            max_questions=min(max(clarify_request.max_questions, 1), 5),  # Clamp 1-5
        )

        # Convert to response model
        questions = []
        for q in result.get("questions", []):
            questions.append(ClarifyingQuestion(
                id=q.get("id", "q1"),
                question=q.get("question", ""),
                type=q.get("type", "text"),
                options=q.get("options"),
                impact=q.get("impact"),
                default_assumption=q.get("default_assumption"),
            ))

        return ClarifyingQuestionsResponse(
            questions=questions,
            reasoning=result.get("reasoning"),
            missing_info=result.get("missing_info", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-with-clarifications", response_model=QuoteResponse)
@limiter.limit("30/minute")
async def generate_quote_with_clarifications(
    request: Request,
    clarified_request: QuoteWithClarificationsRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a quote using the original transcription plus clarification answers.

    Enhancement 5: Active Learning - After user answers clarifying questions,
    generate a more accurate quote incorporating their answers.

    Flow:
    1. User gets low-confidence quote
    2. User requests clarifying questions
    3. User answers questions
    4. This endpoint generates improved quote with that context
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

        contractor_dict = {
            "id": contractor.id,
            "business_name": contractor.business_name,
            "owner_name": contractor.owner_name,
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

        # LAZY GENERATION: For existing users without pricing_philosophy (grandfathering)
        pricing_philosophy = pricing_model.pricing_philosophy
        if not pricing_philosophy:
            onboarding = get_onboarding_service()
            pricing_philosophy = onboarding.generate_philosophy_from_existing_model(
                contractor_name=contractor.business_name or contractor.owner_name or "Contractor",
                primary_trade=contractor.primary_trade or "general_contractor",
                pricing_model=pricing_dict,
            )
            await db.update_pricing_model(contractor.id, pricing_philosophy=pricing_philosophy)
            print(f"[GRANDFATHER] Generated pricing_philosophy for existing user {contractor.id}")

        pricing_dict["pricing_philosophy"] = pricing_philosophy

        terms_dict = None
        if terms:
            terms_dict = {
                "deposit_percent": terms.deposit_percent,
                "quote_valid_days": terms.quote_valid_days,
            }

        # Convert clarifications to list of dicts
        clarification_dicts = [
            {
                "question_id": c.question_id,
                "question": c.question,
                "answer": c.answer,
            }
            for c in clarified_request.clarifications
        ]

        # Generate quote with clarifications
        quote_data = await quote_service.generate_quote_with_clarifications(
            transcription=clarified_request.transcription,
            clarifications=clarification_dicts,
            contractor=contractor_dict,
            pricing_model=pricing_dict,
            terms=terms_dict,
        )

        # Save to database
        quote = await db.create_quote(
            contractor_id=contractor.id,
            transcription=clarified_request.transcription,
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


# ============================================================================
# End Enhancement 5
# ============================================================================


class TranscriptionResponse(BaseModel):
    """Response from transcription endpoint."""
    text: str
    duration: Optional[float] = None


@router.post("/transcribe", response_model=TranscriptionResponse)
@limiter.limit("20/minute")
async def transcribe_audio(
    request: Request,
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
@limiter.limit("20/minute")
async def generate_quote_from_audio(
    request: Request,
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    auth_db: AsyncSession = Depends(get_db),
):
    """
    Generate a quote from audio file.

    Full pipeline: Audio → Transcription → Quote Generation
    """
    try:
        # Check billing status first
        billing_check = await BillingService.check_quote_limit(auth_db, current_user["id"])

        if not billing_check["can_generate"]:
            if billing_check["reason"] == "trial_expired":
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "trial_expired",
                        "message": "Your trial has expired. Please upgrade to continue generating quotes.",
                        "trial_ends_at": billing_check.get("trial_ends_at"),
                    }
                )
            elif billing_check["reason"] == "trial_limit_reached":
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "trial_limit_reached",
                        "message": f"You've reached your trial limit. Please upgrade to continue.",
                    }
                )
            else:
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "quota_exceeded",
                        "message": "Unable to generate quote. Please check your subscription status.",
                    }
                )

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

            # LAZY GENERATION: For existing users without pricing_philosophy (grandfathering)
            pricing_philosophy = pricing_model.pricing_philosophy
            if not pricing_philosophy:
                onboarding = get_onboarding_service()
                pricing_philosophy = onboarding.generate_philosophy_from_existing_model(
                    contractor_name=contractor.business_name or contractor.owner_name or "Contractor",
                    primary_trade=contractor.primary_trade or "general_contractor",
                    pricing_model=pricing_dict,
                )
                await db.update_pricing_model(contractor.id, pricing_philosophy=pricing_philosophy)
                print(f"[GRANDFATHER] Generated pricing_philosophy for existing user {contractor.id}")

            pricing_dict["pricing_philosophy"] = pricing_philosophy

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
            # AND category-specific learned adjustments injected into the prompt
            quote_data = await quote_service.generate_quote(
                transcription=transcription_text,
                contractor=contractor_dict,
                pricing_model=pricing_dict,
                terms=terms_dict,
                correction_examples=correction_examples,
                detected_category=detected_job_type,  # For learned adjustments injection
            )

            # Add audio metadata
            quote_data["audio_duration"] = transcription_result.get("duration", 0)
            quote_data["transcription_confidence"] = transcription_result.get("confidence")

            # Ensure detected job_type is used if AI didn't return one
            if not quote_data.get("job_type"):
                quote_data["job_type"] = detected_job_type

            # DISC-034: Pricing sanity check to prevent catastrophic hallucinations
            sanity_check_service = get_sanity_check_service()
            sanity_result = await sanity_check_service.check_quote_sanity(
                db=auth_db,
                contractor_id=contractor.id,
                quote_total=quote_data.get("subtotal", 0),
                category=detected_job_type,
            )

            # If quote is blocked (>10x P95), return error
            if not sanity_result["is_sane"]:
                # Log the blocked quote for pattern analysis
                await sanity_check_service.log_flagged_quote(
                    db=auth_db,
                    contractor_id=contractor.id,
                    quote_total=quote_data.get("subtotal", 0),
                    category=detected_job_type,
                    action="block",
                    bounds=sanity_result["bounds"],
                    transcription=transcription_text,
                )
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "quote_sanity_check_failed",
                        "message": sanity_result["message"],
                        "quote_total": quote_data.get("subtotal", 0),
                        "bounds": sanity_result["bounds"],
                    }
                )

            # If quote is flagged with warning (>3x P95), add warning to quote
            if sanity_result["action"] == "warn":
                quote_data["sanity_warning"] = sanity_result["message"]
                # Log the warning for pattern analysis
                await sanity_check_service.log_flagged_quote(
                    db=auth_db,
                    contractor_id=contractor.id,
                    quote_total=quote_data.get("subtotal", 0),
                    category=detected_job_type,
                    action="warn",
                    bounds=sanity_result["bounds"],
                    transcription=transcription_text,
                )

            # Save to database (DISC-018: Mark grace quotes)
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
                is_grace_quote=billing_check.get("is_grace_quote", False),
            )

            # Register the category so future quotes can match against it
            # This ensures the category list grows with usage, not just edits
            await db.ensure_category_exists(contractor.id, detected_job_type)

            # Increment quote usage counter (DISC-018: Track grace quotes separately)
            await BillingService.increment_quote_usage(
                auth_db,
                current_user["id"],
                is_grace_quote=billing_check.get("is_grace_quote", False)
            )

            # Track quote generation event (DISC-012: Include user learning stats)
            try:
                # Get user's total quote and edit counts for edit rate tracking
                all_quotes = await db.get_quotes_by_contractor(contractor.id)
                user_quote_count = len(all_quotes)
                user_edit_count = sum(1 for q in all_quotes if q.was_edited)

                # Get category-specific stats
                category_quotes = [q for q in all_quotes if q.job_type == detected_job_type]
                category_quote_count = len(category_quotes)
                category_edit_count = sum(1 for q in category_quotes if q.was_edited)

                analytics_service.track_event(
                    user_id=str(current_user["id"]),
                    event_name="quote_generated",
                    properties={
                        "contractor_id": str(contractor.id),
                        "quote_id": str(quote.id),
                        "job_type": detected_job_type,
                        "subtotal": quote_data.get("subtotal", 0),
                        "has_customer_info": bool(quote_data.get("customer_name")),
                        "confidence": quote_data.get("confidence"),
                        "line_item_count": len(quote_data.get("line_items", [])),
                        # DISC-011: Input method tracking (voice vs text)
                        "input_method": "voice",
                        # DISC-012: User learning stats for edit rate trend analysis
                        "user_quote_count": user_quote_count,
                        "user_edit_count": user_edit_count,
                        "user_edit_rate": round(user_edit_count / user_quote_count * 100, 2) if user_quote_count > 0 else 0,
                        "category_quote_count": category_quote_count,
                        "category_edit_count": category_edit_count,
                        "category_edit_rate": round(category_edit_count / category_quote_count * 100, 2) if category_quote_count > 0 else 0,
                        # DISC-018: Trial warning tracking
                        "warning_level": billing_check.get("warning_level"),
                        "is_grace_quote": billing_check.get("is_grace_quote", False),
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to track quote generation: {e}")

            # DISC-018: Add billing info to response for frontend warnings
            response = quote_to_response(quote)
            response_dict = response.dict()
            response_dict["billing_info"] = {
                "warning_level": billing_check.get("warning_level"),
                "is_grace_quote": billing_check.get("is_grace_quote", False),
                "quotes_remaining": billing_check.get("quotes_remaining", 0),
                "grace_remaining": billing_check.get("grace_remaining", 0),
            }

            return response_dict

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


class CustomerUpdateRequest(BaseModel):
    """Request to update customer information on a quote."""
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None


@router.put("/{quote_id}/customer", response_model=QuoteResponse)
async def update_quote_customer(
    quote_id: str,
    update: CustomerUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update customer information on a quote.

    This is a simple update endpoint that only modifies customer fields.
    Does not trigger learning since customer info changes are not pricing-related.
    """
    db = get_db_service()

    # Get the quote
    quote = await db.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Build update dict - only customer fields
    update_data = {}
    if update.customer_name is not None:
        update_data["customer_name"] = update.customer_name
    if update.customer_address is not None:
        update_data["customer_address"] = update.customer_address
    if update.customer_phone is not None:
        update_data["customer_phone"] = update.customer_phone

    # Update the quote in database
    updated_quote = await db.update_quote(quote_id, **update_data)

    return quote_to_response(updated_quote)


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

        # Get category-specific correction stats for analytics
        all_quotes = await db.get_quotes_by_contractor(contractor.id)
        category_quotes = [q for q in all_quotes if q.job_type == quote.job_type]
        corrections_for_category = sum(1 for q in category_quotes if q.was_edited)
        user_total_corrections = sum(1 for q in all_quotes if q.was_edited)

        # Fetch existing context for THREE-LAYER learning
        existing_learnings = []
        existing_tailored_prompt = None
        existing_philosophy = None

        pricing_model = await db.get_pricing_model(contractor.id)
        if pricing_model:
            # Layer 1 & 2: Category-specific context
            if pricing_model.pricing_knowledge:
                categories = pricing_model.pricing_knowledge.get("categories", {})
                if quote.job_type and quote.job_type in categories:
                    cat_data = categories[quote.job_type]
                    existing_learnings = cat_data.get("learned_adjustments", [])
                    existing_tailored_prompt = cat_data.get("tailored_prompt")

            # Layer 3: Global pricing philosophy
            existing_philosophy = pricing_model.pricing_philosophy

        # Process the correction - Claude sees THREE-LAYER context
        learning_result = await learning_service.process_correction(
            original_quote=original_quote,
            final_quote=final_quote,
            contractor_notes=update.correction_notes,
            contractor_id=str(contractor.id),
            category=quote.job_type,
            user_id=str(current_user["id"]),
            existing_learnings=existing_learnings,
            existing_tailored_prompt=existing_tailored_prompt,
            existing_philosophy=existing_philosophy,
        )

        # If there were learnings, apply them to the pricing model
        # Learnings are stored per-category for targeted prompt injection
        if learning_result.get("has_changes") and learning_result.get("learnings"):
            await db.apply_learnings_to_pricing_model(
                contractor_id=contractor.id,
                learnings=learning_result["learnings"],
                category=quote.job_type,  # Store learnings under this category
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

    # Track quote edit event (DISC-012: Enhanced with learning context)
    try:
        # Calculate edit metrics
        subtotal_change = (updated_quote.subtotal or 0) - original_subtotal if update.line_items else 0
        subtotal_change_percent = abs(subtotal_change / original_subtotal * 100) if original_subtotal > 0 else 0

        # Get updated quote counts for edit rate tracking
        all_quotes_updated = await db.get_quotes_by_contractor(contractor.id)
        user_quote_count = len(all_quotes_updated)
        user_edit_count = sum(1 for q in all_quotes_updated if q.was_edited)

        analytics_service.track_event(
            user_id=str(current_user["id"]),
            event_name="quote_edited",
            properties={
                "contractor_id": str(contractor.id),
                "quote_id": quote_id,
                "job_type": quote.job_type,
                "had_line_item_changes": update.line_items is not None,
                "had_customer_changes": any([
                    update.customer_name is not None,
                    update.customer_address is not None,
                    update.customer_phone is not None,
                    update.customer_email is not None,
                ]),
                "subtotal_change": round(subtotal_change, 2),
                "subtotal_change_percent": round(subtotal_change_percent, 2),
                # DISC-012: Learning system validation metrics
                "user_quote_count": user_quote_count,
                "user_edit_count": user_edit_count,
                "user_edit_rate": round(user_edit_count / user_quote_count * 100, 2) if user_quote_count > 0 else 0,
                "corrections_for_category": corrections_for_category,
                "user_total_corrections": user_total_corrections,
            }
        )
    except Exception as e:
        print(f"Warning: Failed to track quote edit: {e}")

    # Refresh the quote
    updated_quote = await db.get_quote(quote_id)
    return quote_to_response(updated_quote)


@router.post("/{quote_id}/pdf")
@limiter.limit("30/minute")
async def generate_pdf(request: Request, quote_id: str, current_user: dict = Depends(get_current_user)):
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
            "logo_data": contractor.logo_data,  # Include logo for PDF
        }

        terms_dict = {}
        if terms:
            terms_dict = {
                "deposit_percent": terms.deposit_percent,
                "quote_valid_days": terms.quote_valid_days,
                "labor_warranty_years": terms.labor_warranty_years,
            }

        # DISC-028: Get contractor's template preferences
        template = contractor.pdf_template or "modern"
        accent_color = contractor.pdf_accent_color

        # DISC-066: Generate PDF in memory to avoid filesystem issues on Railway
        pdf_bytes = pdf_service.generate_quote_pdf(
            quote_data=quote_dict,
            contractor=contractor_dict,
            terms=terms_dict,
            watermark=quote.is_grace_quote,  # Add watermark if this is a grace quote
            template=template,  # DISC-028: Use contractor's template
            accent_color=accent_color,  # DISC-028: Use contractor's accent color
        )

        # Return PDF directly from memory
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="quote_{quote_id}.pdf"'
            }
        )

    except Exception as e:
        import traceback
        print(f"PDF generation error for quote {quote_id}: {e}")
        print(f"Quote data: {quote_dict}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF error: {str(e)}")


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


# ============================================================================
# Feedback Endpoints (Enhancement 4)
# ============================================================================

def feedback_to_response(feedback) -> QuoteFeedbackResponse:
    """Convert a QuoteFeedback model to response."""
    return QuoteFeedbackResponse(
        id=feedback.id,
        quote_id=feedback.quote_id,
        overall_rating=feedback.overall_rating,
        pricing_accuracy=feedback.pricing_accuracy,
        description_quality=feedback.description_quality,
        line_item_completeness=feedback.line_item_completeness,
        timeline_accuracy=feedback.timeline_accuracy,
        issues=feedback.issues or [],
        pricing_direction=feedback.pricing_direction,
        pricing_off_by_percent=feedback.pricing_off_by_percent,
        actual_total=feedback.actual_total,
        feedback_text=feedback.feedback_text,
        improvement_suggestions=feedback.improvement_suggestions,
        quote_was_sent=feedback.quote_was_sent,
        quote_outcome=feedback.quote_outcome,
        created_at=feedback.created_at.isoformat() if feedback.created_at else None,
    )


@router.post("/{quote_id}/feedback", response_model=QuoteFeedbackResponse)
async def submit_feedback(
    quote_id: str,
    feedback: QuoteFeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit feedback on a generated quote.

    This is a non-destructive way to provide feedback without editing the quote.
    Feedback is used to improve future quote generation.
    """
    db = get_db_service()

    # Get the quote
    quote = await db.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if feedback already exists
    existing_feedback = await db.get_quote_feedback(quote_id)
    if existing_feedback:
        raise HTTPException(
            status_code=400,
            detail="Feedback already exists for this quote. Use PUT to update."
        )

    # Create feedback
    feedback_data = feedback.dict(exclude_none=True)
    new_feedback = await db.create_quote_feedback(
        quote_id=quote_id,
        **feedback_data
    )

    # Trigger learning from feedback if pricing direction or actual values provided
    if feedback.pricing_direction or feedback.actual_total or feedback.actual_line_items:
        try:
            learning_service = get_learning_service()
            await learning_service.process_feedback(
                quote_id=quote_id,
                feedback_data=feedback_data,
                original_quote={
                    "line_items": quote.line_items,
                    "subtotal": quote.subtotal,
                    "job_type": quote.job_type,
                },
            )
            # Mark as processed for learning
            await db.update_quote_feedback(
                new_feedback.id,
                processed_for_learning=True,
                processed_at=datetime.utcnow()
            )
        except Exception as e:
            # Don't fail feedback submission if learning fails
            print(f"[FEEDBACK LEARNING ERROR] {e}")

    return feedback_to_response(new_feedback)


@router.put("/{quote_id}/feedback", response_model=QuoteFeedbackResponse)
async def update_feedback(
    quote_id: str,
    feedback: QuoteFeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update existing feedback on a quote."""
    db = get_db_service()

    # Get the quote
    quote = await db.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get existing feedback
    existing_feedback = await db.get_quote_feedback(quote_id)
    if not existing_feedback:
        raise HTTPException(status_code=404, detail="No feedback exists for this quote")

    # Update feedback
    feedback_data = feedback.dict(exclude_none=True)
    updated_feedback = await db.update_quote_feedback(
        existing_feedback.id,
        **feedback_data
    )

    return feedback_to_response(updated_feedback)


@router.get("/{quote_id}/feedback", response_model=QuoteFeedbackResponse)
async def get_feedback(
    quote_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get feedback for a specific quote."""
    db = get_db_service()

    # Get the quote
    quote = await db.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get feedback
    feedback = await db.get_quote_feedback(quote_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="No feedback for this quote")

    return feedback_to_response(feedback)


@router.get("/feedback/stats")
async def get_feedback_stats(current_user: dict = Depends(get_current_user)):
    """Get aggregated feedback statistics for the current user."""
    db = get_db_service()

    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    stats = await db.get_feedback_stats(contractor.id)

    return stats


# ============================================================================
# Customer Autocomplete Endpoint (DISC-022)
# ============================================================================

class CustomerResponse(BaseModel):
    """Customer data for autocomplete."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    q: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Get unique customers from user's quote history for autocomplete.

    DISC-022: Customer Memory - Returns list of past customers to enable
    autocomplete when entering customer details on new quotes.

    Args:
        q: Optional search query to filter customers by name/email/phone
        current_user: Authenticated user from JWT

    Returns:
        List of unique customers (deduplicated by email or name)
    """
    db = get_db_service()

    # Get contractor for current user
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        return []

    # Query quotes for this contractor and extract unique customers
    async with async_session_factory() as session:
        # Build query to get distinct customers
        query = select(
            Quote.customer_name,
            Quote.customer_email,
            Quote.customer_phone
        ).where(
            Quote.contractor_id == contractor.id
        ).where(
            # Only include quotes that have at least a name or email
            or_(
                Quote.customer_name.isnot(None),
                Quote.customer_email.isnot(None)
            )
        )

        # Apply search filter if provided
        if q:
            search_term = f"%{q.lower()}%"
            query = query.where(
                or_(
                    func.lower(Quote.customer_name).like(search_term),
                    func.lower(Quote.customer_email).like(search_term),
                    func.lower(Quote.customer_phone).like(search_term)
                )
            )

        # Order by most recent
        query = query.order_by(Quote.created_at.desc())

        result = await session.execute(query)
        rows = result.all()

        # Deduplicate customers (prefer by email, fallback to name)
        seen_emails = set()
        seen_names = set()
        unique_customers = []

        for row in rows:
            name, email, phone = row

            # Skip if we've seen this customer already
            if email and email.lower() in seen_emails:
                continue
            if not email and name and name.lower() in seen_names:
                continue

            # Track this customer
            if email:
                seen_emails.add(email.lower())
            if name:
                seen_names.add(name.lower())

            unique_customers.append(
                CustomerResponse(
                    name=name,
                    email=email,
                    phone=phone
                )
            )

        return unique_customers


# ============================================================================
# PDF Template Endpoints (DISC-028)
# ============================================================================

class TemplateInfo(BaseModel):
    """Template information."""
    key: str
    name: str
    description: str
    available_to: List[str]


class TemplatesResponse(BaseModel):
    """Response with available templates."""
    templates: List[TemplateInfo]
    accent_colors: dict
    current_template: Optional[str] = None
    current_accent_color: Optional[str] = None


@router.get("/pdf/templates", response_model=TemplatesResponse)
async def get_pdf_templates(
    current_user: dict = Depends(get_current_user),
    auth_db: AsyncSession = Depends(get_db)
):
    """
    Get available PDF templates for the current user's plan tier.

    DISC-028: Template library - returns templates user can access based on
    their subscription tier (starter, pro, team).
    """
    from ..services.pdf_generator import PDF_TEMPLATES, ACCENT_COLORS
    from ..models.database import User

    db = get_db_service()

    # Get contractor to determine plan tier
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get user's plan tier from database
    result = await auth_db.execute(
        select(User).where(User.id == current_user["id"])
    )
    user = result.scalar_one_or_none()
    user_tier = user.plan_tier if user else contractor.plan or "starter"

    # Filter templates by tier
    available_templates = []
    for key, template in PDF_TEMPLATES.items():
        if user_tier in template["available_to"]:
            available_templates.append(
                TemplateInfo(
                    key=key,
                    name=template["name"],
                    description=template["description"],
                    available_to=template["available_to"]
                )
            )

    return TemplatesResponse(
        templates=available_templates,
        accent_colors=ACCENT_COLORS,
        current_template=contractor.pdf_template or "modern",
        current_accent_color=contractor.pdf_accent_color,
    )


# ============================================================================
# Quote Duplication Endpoint (DISC-038)
# ============================================================================

@router.post("/{quote_id}/duplicate", response_model=QuoteResponse)
async def duplicate_quote(
    quote_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Duplicate an existing quote.

    DISC-038: Quote Template Feature - Creates a new quote with copied data
    from an existing quote. User can then edit and regenerate.

    Flow:
    1. Copy customer info, transcription, and line items from source quote
    2. Create new quote in draft state (status = 'draft')
    3. Track source quote for analytics
    4. Return new quote for editing
    """
    db = get_db_service()

    # Get the source quote
    source_quote = await db.get_quote(quote_id)
    if not source_quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or source_quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Create new quote with copied data
    new_quote = await db.create_quote(
        contractor_id=contractor.id,
        transcription=source_quote.transcription,
        job_type=source_quote.job_type,
        job_description=source_quote.job_description,
        line_items=source_quote.line_items,
        subtotal=source_quote.subtotal,
        customer_name=source_quote.customer_name,
        customer_address=source_quote.customer_address,
        customer_phone=source_quote.customer_phone,
        estimated_days=source_quote.estimated_days,
        ai_generated_total=source_quote.ai_generated_total,
        duplicate_source_quote_id=quote_id,  # Track the source
        status="draft",  # Mark as draft for editing
    )

    # Track duplication event
    try:
        analytics_service.track_event(
            user_id=str(current_user["id"]),
            event_name="quote_duplicate_created",
            properties={
                "contractor_id": str(contractor.id),
                "source_quote_id": quote_id,
                "new_quote_id": str(new_quote.id),
                "job_type": source_quote.job_type,
                "subtotal": source_quote.subtotal,
            }
        )
    except Exception as e:
        print(f"Warning: Failed to track quote duplication: {e}")

    return quote_to_response(new_quote)
