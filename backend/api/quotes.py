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
    # DISC-067: Free-form timeline and terms fields
    timeline_text: Optional[str] = None
    terms_text: Optional[str] = None
    # Track if quote has been converted to invoice
    has_invoice: bool = False
    # Wave 2: View tracking for shared quotes
    view_count: int = 0
    status: Optional[str] = None


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
    # DISC-067: Free-form timeline and terms fields
    timeline_text: Optional[str] = None
    terms_text: Optional[str] = None


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


# ============================================================================
# INNOV-7: Confidence Explainer Models
# ============================================================================

class ConfidenceDimension(BaseModel):
    """Individual dimension of pricing confidence."""
    dimension: str  # data, accuracy, recency, coverage
    score: float  # 0.0-1.0
    weight: float  # How much this dimension contributes
    description: str  # Human-readable explanation


class PricingConfidenceResponse(BaseModel):
    """Multi-dimensional pricing confidence breakdown."""
    quote_id: str
    job_type: str
    overall_confidence: float  # 0.0-1.0
    display_confidence: str  # "High", "Medium", "Low", "Learning"
    dimensions: List[ConfidenceDimension]
    # Statistics
    quote_count: int
    acceptance_count: int
    correction_count: int
    acceptance_rate: float
    avg_correction_magnitude: float
    days_since_last_quote: int
    # Warnings and context
    warnings: List[str] = []
    last_updated: Optional[str] = None


class PricingComponentResponse(BaseModel):
    """A component of the pricing breakdown."""
    type: str  # base_rate, modifier, adjustment, voice_signal
    label: str  # Human-readable label
    amount: float  # Dollar amount
    source: str  # learned, default, dna_transfer, voice_detected
    confidence: float  # 0.0-1.0
    learning_ref: Optional[str] = None
    pattern_id: Optional[str] = None
    validation_count: Optional[int] = None


class AppliedPatternResponse(BaseModel):
    """A pricing pattern that was applied."""
    pattern: str
    source_category: str
    times_validated: int
    confidence: float


class UncertaintyNoteResponse(BaseModel):
    """An area of uncertainty in pricing."""
    area: str
    reason: str
    suggestion: Optional[str] = None


class DNATransferResponse(BaseModel):
    """Information about a DNA pattern transfer."""
    pattern: str
    from_category: str
    inherited_confidence: float
    reason: str


class LearningContextResponse(BaseModel):
    """Context about learning state."""
    category: str
    quote_count: int
    correction_count: int
    acceptance_rate: float
    avg_adjustment: float


class PricingExplanationResponse(BaseModel):
    """Complete explanation of how a quote was priced."""
    quote_id: str
    summary: str
    overall_confidence: float
    confidence_label: str  # "High", "Medium", "Low"
    components: List[PricingComponentResponse] = []
    patterns_applied: List[AppliedPatternResponse] = []
    uncertainties: List[UncertaintyNoteResponse] = []
    dna_transfers: List[DNATransferResponse] = []
    learning_context: Optional[LearningContextResponse] = None


def quote_to_response(quote, has_invoice: bool = False) -> QuoteResponse:
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
        # DISC-067: Free-form timeline and terms fields
        timeline_text=getattr(quote, 'timeline_text', None),
        terms_text=getattr(quote, 'terms_text', None),
        has_invoice=has_invoice,
        # Wave 2: View tracking for shared quotes
        view_count=quote.view_count or 0,
        status=quote.status,
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
        # DISC-068: Now returns full category info including confidence
        category_detection = await quote_service.detect_or_create_category(
            quote_request.transcription,
            pricing_knowledge=pricing_dict.get("pricing_knowledge")
        )
        detected_job_type = category_detection["category"]
        category_confidence = category_detection.get("category_confidence", 100)
        suggested_new_category = category_detection.get("suggested_new_category")

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

        # ALWAYS use detected_job_type for consistency with category keys
        # Claude's generated job_type might not match the normalized snake_case category key
        # This ensures quote.job_type matches pricing_knowledge["categories"][key] for counting
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

        # DISC-091: Link quote to customer record (auto-creates if needed)
        if quote.customer_name:
            try:
                from ..services.customer_service import CustomerService
                await CustomerService.link_quote_to_customer(auth_db, quote)
                await auth_db.commit()
            except Exception as e:
                print(f"Warning: Failed to link quote to customer: {e}")

        # Register the category so future quotes can match against it
        # This ensures the category list grows with usage, not just edits
        await db.ensure_category_exists(contractor.id, detected_job_type)

        # Increment category-level quote count for Pricing Brain tracking
        await db.increment_category_quote_count(contractor.id, detected_job_type)

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

        # DISC-068: Add category confidence info for frontend notification
        response_dict["category_info"] = {
            "category": detected_job_type,
            "confidence": category_confidence,
            "suggested_new_category": suggested_new_category,
            "needs_review": category_confidence < 70 or suggested_new_category is not None,
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
    auth_db: AsyncSession = Depends(get_db),
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

        # DISC-091: Link quote to customer record (auto-creates if needed)
        if quote.customer_name:
            try:
                from ..services.customer_service import CustomerService
                await CustomerService.link_quote_to_customer(auth_db, quote)
                await auth_db.commit()
            except Exception as e:
                print(f"Warning: Failed to link quote to customer: {e}")

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
            # DISC-068: Now returns full category info including confidence
            category_detection = await quote_service.detect_or_create_category(
                transcription_text,
                pricing_knowledge=pricing_dict.get("pricing_knowledge")
            )
            detected_job_type = category_detection["category"]
            category_confidence = category_detection.get("category_confidence", 100)
            suggested_new_category = category_detection.get("suggested_new_category")

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

            # ALWAYS use detected_job_type for consistency with category keys
            # Claude's generated job_type might not match the normalized snake_case category key
            # This ensures quote.job_type matches pricing_knowledge["categories"][key] for counting
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

            # DISC-091: Link quote to customer record (auto-creates if needed)
            if quote.customer_name:
                try:
                    from ..services.customer_service import CustomerService
                    await CustomerService.link_quote_to_customer(auth_db, quote)
                    await auth_db.commit()
                except Exception as e:
                    print(f"Warning: Failed to link quote to customer: {e}")

            # Register the category so future quotes can match against it
            # This ensures the category list grows with usage, not just edits
            await db.ensure_category_exists(contractor.id, detected_job_type)

            # Increment category-level quote count for Pricing Brain tracking
            await db.increment_category_quote_count(contractor.id, detected_job_type)

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

            # DISC-068: Add category confidence info for frontend notification
            response_dict["category_info"] = {
                "category": detected_job_type,
                "confidence": category_confidence,
                "suggested_new_category": suggested_new_category,
                "needs_review": category_confidence < 70 or suggested_new_category is not None,
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


# ============================================================================
# INNOV-7: Confidence Explainer Endpoints
# ============================================================================

CONFIDENCE_DIMENSION_DESCRIPTIONS = {
    "data": "Based on volume of quotes in this category",
    "accuracy": "Based on acceptance rate and correction magnitude",
    "recency": "Based on how recent the data is",
    "coverage": "Based on job complexity variety",
}

CONFIDENCE_DIMENSION_WEIGHTS = {
    "data": 0.20,
    "accuracy": 0.40,
    "recency": 0.25,
    "coverage": 0.15,
}


@router.get("/{quote_id}/confidence", response_model=PricingConfidenceResponse)
async def get_quote_confidence(
    quote_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    INNOV-7: Get multi-dimensional pricing confidence for a quote.

    Returns detailed confidence breakdown across 4 dimensions:
    - Data (20%): Volume of quotes in this category
    - Accuracy (40%): Acceptance rate and correction patterns
    - Recency (25%): Freshness of learning data
    - Coverage (15%): Job complexity variety
    """
    from ..services.pricing_confidence import PricingConfidenceService

    db = get_db_service()
    quote = await db.get_quote(quote_id)

    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get pricing model for confidence calculation
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        # Return minimal confidence for new users
        return PricingConfidenceResponse(
            quote_id=str(quote.id),
            job_type=quote.job_type or "unknown",
            overall_confidence=0.3,
            display_confidence="Learning",
            dimensions=[
                ConfidenceDimension(
                    dimension=dim,
                    score=0.3,
                    weight=CONFIDENCE_DIMENSION_WEIGHTS[dim],
                    description=CONFIDENCE_DIMENSION_DESCRIPTIONS[dim]
                )
                for dim in ["data", "accuracy", "recency", "coverage"]
            ],
            quote_count=0,
            acceptance_count=0,
            correction_count=0,
            acceptance_rate=0.0,
            avg_correction_magnitude=0.0,
            days_since_last_quote=0,
            warnings=["New category - learning in progress"],
            last_updated=datetime.utcnow().isoformat(),
        )

    # Get all quotes for this category to calculate confidence
    quotes = await db.get_quotes_by_contractor(contractor.id)
    category_quotes = [q for q in quotes if q.job_type == quote.job_type]

    # Calculate statistics
    quote_count = len(category_quotes)
    acceptance_count = sum(1 for q in category_quotes if q.status == "won")
    correction_count = sum(1 for q in category_quotes if q.was_edited)

    # Calculate correction magnitudes
    correction_magnitudes = []
    for q in category_quotes:
        if q.was_edited and hasattr(q, 'correction_percent'):
            correction_magnitudes.append(abs(q.correction_percent or 0))

    # Days since last quote
    days_since_last = 0
    if category_quotes:
        most_recent = max(q.created_at for q in category_quotes if q.created_at)
        days_since_last = (datetime.utcnow() - most_recent).days

    # Calculate complexity distribution from quote amounts
    complexity_dist = {"simple": 0, "medium": 0, "complex": 0}
    for q in category_quotes:
        if q.total:
            if q.total < 500:
                complexity_dist["simple"] += 1
            elif q.total < 2000:
                complexity_dist["medium"] += 1
            else:
                complexity_dist["complex"] += 1

    # Use PricingConfidenceService for proper calculation
    service = PricingConfidenceService()
    confidence = service.calculate(
        quote_count=quote_count,
        acceptance_count=acceptance_count,
        correction_count=correction_count,
        correction_magnitudes=correction_magnitudes,
        days_since_last_quote=days_since_last,
        complexity_distribution=complexity_dist,
    )

    # Build dimension responses
    dimensions = [
        ConfidenceDimension(
            dimension="data",
            score=confidence.data_confidence,
            weight=CONFIDENCE_DIMENSION_WEIGHTS["data"],
            description=CONFIDENCE_DIMENSION_DESCRIPTIONS["data"],
        ),
        ConfidenceDimension(
            dimension="accuracy",
            score=confidence.accuracy_confidence,
            weight=CONFIDENCE_DIMENSION_WEIGHTS["accuracy"],
            description=CONFIDENCE_DIMENSION_DESCRIPTIONS["accuracy"],
        ),
        ConfidenceDimension(
            dimension="recency",
            score=confidence.recency_confidence,
            weight=CONFIDENCE_DIMENSION_WEIGHTS["recency"],
            description=CONFIDENCE_DIMENSION_DESCRIPTIONS["recency"],
        ),
        ConfidenceDimension(
            dimension="coverage",
            score=confidence.coverage_confidence,
            weight=CONFIDENCE_DIMENSION_WEIGHTS["coverage"],
            description=CONFIDENCE_DIMENSION_DESCRIPTIONS["coverage"],
        ),
    ]

    return PricingConfidenceResponse(
        quote_id=str(quote.id),
        job_type=quote.job_type or "unknown",
        overall_confidence=confidence.overall_confidence,
        display_confidence=confidence.display_confidence,
        dimensions=dimensions,
        quote_count=confidence.quote_count,
        acceptance_count=confidence.acceptance_count,
        correction_count=confidence.correction_count,
        acceptance_rate=confidence.acceptance_rate,
        avg_correction_magnitude=confidence.avg_correction_magnitude,
        days_since_last_quote=confidence.days_since_last_quote,
        warnings=confidence.warnings,
        last_updated=confidence.last_updated,
    )


@router.get("/{quote_id}/explanation", response_model=PricingExplanationResponse)
async def get_quote_explanation(
    quote_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    INNOV-7: Get detailed pricing explanation for a quote.

    Shows exactly WHY the quote was priced the way it was:
    - Component breakdown (base rate, modifiers, voice signals)
    - Patterns applied (which learnings were used)
    - Uncertainties (what we don't know)
    - DNA transfers (patterns borrowed from related categories)
    """
    from ..services.pricing_explanation import PricingExplanationService
    from ..services.pricing_confidence import PricingConfidenceService

    db = get_db_service()
    quote = await db.get_quote(quote_id)

    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)

    # Get quotes for learning context
    quotes = await db.get_quotes_by_contractor(contractor.id)
    category_quotes = [q for q in quotes if q.job_type == quote.job_type]

    # Calculate learning context
    quote_count = len(category_quotes)
    correction_count = sum(1 for q in category_quotes if q.was_edited)
    acceptance_count = sum(1 for q in category_quotes if q.status == "won")
    acceptance_rate = acceptance_count / quote_count if quote_count > 0 else 0.0

    # Calculate average adjustment
    adjustments = []
    for q in category_quotes:
        if q.was_edited and hasattr(q, 'correction_percent'):
            adjustments.append(q.correction_percent or 0)
    avg_adjustment = sum(adjustments) / len(adjustments) if adjustments else 0.0

    # Get pricing knowledge for this category
    pricing_knowledge = pricing_model.pricing_knowledge if pricing_model else {}
    category_knowledge = pricing_knowledge.get("categories", {}).get(quote.job_type, {})
    learned_adjustments = category_knowledge.get("learned_adjustments", [])

    # Build voice signals from transcription
    voice_signals = {}
    if quote.transcription:
        transcription_lower = quote.transcription.lower()
        if "rush" in transcription_lower or "asap" in transcription_lower:
            voice_signals["rush"] = True
        if "weekend" in transcription_lower:
            voice_signals["weekend"] = True
        if "difficult" in transcription_lower or "complex" in transcription_lower:
            voice_signals["complexity"] = "high"

    # Get contractor DNA patterns
    contractor_dna = pricing_model.contractor_dna if pricing_model else {}

    # Calculate confidence for context
    service = PricingConfidenceService()
    confidence = service.calculate(
        quote_count=quote_count,
        acceptance_count=acceptance_count,
        correction_count=correction_count,
        correction_magnitudes=[],
        days_since_last_quote=0,
        complexity_distribution={},
    )

    # Generate explanation
    explanation_service = PricingExplanationService()
    explanation = explanation_service.generate_explanation(
        quote={
            "total": quote.total or 0,
            "subtotal": quote.subtotal or 0,
            "line_items": quote.line_items or [],
            "job_type": quote.job_type,
            "job_description": quote.job_description,
        },
        learned_adjustments=learned_adjustments,
        contractor_dna=contractor_dna,
        voice_signals=voice_signals,
        confidence=confidence,
        pricing_model=pricing_model.__dict__ if pricing_model else {},
        detected_category=quote.job_type,
    )

    # Convert to response format
    components = [
        PricingComponentResponse(
            type=c.type,
            label=c.label,
            amount=c.amount,
            source=c.source,
            confidence=c.confidence,
            learning_ref=c.learning_ref,
            pattern_id=c.pattern_id,
            validation_count=c.validation_count,
        )
        for c in explanation.components
    ]

    patterns_applied = [
        AppliedPatternResponse(
            pattern=p.pattern,
            source_category=p.source_category,
            times_validated=p.times_validated,
            confidence=p.confidence,
        )
        for p in explanation.patterns_applied
    ]

    uncertainties = [
        UncertaintyNoteResponse(
            area=u.area,
            reason=u.reason,
            suggestion=u.suggestion,
        )
        for u in explanation.uncertainties
    ]

    dna_transfers = [
        DNATransferResponse(
            pattern=d.pattern,
            from_category=d.from_category,
            inherited_confidence=d.inherited_confidence,
            reason=d.reason,
        )
        for d in explanation.dna_transfers
    ]

    learning_context = None
    if explanation.learning_context:
        learning_context = LearningContextResponse(
            category=explanation.learning_context.category,
            quote_count=explanation.learning_context.quote_count,
            correction_count=explanation.learning_context.correction_count,
            acceptance_rate=explanation.learning_context.acceptance_rate,
            avg_adjustment=explanation.learning_context.avg_adjustment,
        )

    return PricingExplanationResponse(
        quote_id=str(quote.id),
        summary=explanation.summary,
        overall_confidence=explanation.overall_confidence,
        confidence_label=explanation.confidence_label,
        components=components,
        patterns_applied=patterns_applied,
        uncertainties=uncertainties,
        dna_transfers=dna_transfers,
        learning_context=learning_context,
    )


# ============================================================================
# Wave 2: Quote Analytics Endpoint (Proposify Domination)
# ============================================================================

class QuoteAnalyticsResponse(BaseModel):
    """Analytics data for a quote."""
    quote_id: str
    view_count: int
    first_viewed_at: Optional[str] = None
    last_viewed_at: Optional[str] = None
    status: Optional[str] = None
    sent_at: Optional[str] = None
    accepted_at: Optional[str] = None
    rejected_at: Optional[str] = None
    # Expiration info
    expires_at: Optional[str] = None
    is_expired: bool = False
    days_remaining: Optional[int] = None


@router.get("/{quote_id}/analytics", response_model=QuoteAnalyticsResponse)
async def get_quote_analytics(
    quote_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get analytics for a specific quote.

    Wave 2: Proposify Domination - Provides view tracking, status history,
    and expiration information for contractor visibility.
    """
    from datetime import timedelta

    db = get_db_service()
    quote = await db.get_quote(quote_id)

    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get terms for expiration calculation
    terms = await db.get_terms(contractor.id)
    quote_valid_days = terms.quote_valid_days if terms else None

    # Calculate expiration
    expires_at = None
    is_expired = False
    days_remaining = None

    if quote_valid_days and quote.created_at:
        expires_at_dt = quote.created_at + timedelta(days=quote_valid_days)
        expires_at = expires_at_dt.isoformat()
        is_expired = datetime.utcnow() > expires_at_dt
        if not is_expired:
            days_remaining = max(0, (expires_at_dt - datetime.utcnow()).days)

    return QuoteAnalyticsResponse(
        quote_id=str(quote.id),
        view_count=quote.view_count or 0,
        first_viewed_at=quote.first_viewed_at.isoformat() if quote.first_viewed_at else None,
        last_viewed_at=quote.last_viewed_at.isoformat() if quote.last_viewed_at else None,
        status=quote.status,
        sent_at=quote.sent_at.isoformat() if quote.sent_at else None,
        accepted_at=quote.accepted_at.isoformat() if quote.accepted_at else None,
        rejected_at=quote.rejected_at.isoformat() if quote.rejected_at else None,
        expires_at=expires_at,
        is_expired=is_expired,
        days_remaining=days_remaining,
    )


@router.delete("/{quote_id}")
async def delete_quote(quote_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a quote by ID."""
    db = get_db_service()
    quote = await db.get_quote(quote_id)

    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    success = await db.delete_quote(quote_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete quote")

    return {"message": "Quote deleted successfully", "quote_id": quote_id}


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
    # DISC-067: Free-form timeline and terms fields
    if update.timeline_text is not None:
        update_data["timeline_text"] = update.timeline_text
    if update.terms_text is not None:
        update_data["terms_text"] = update.terms_text

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

    # DISC-091: Re-link quote to customer if customer info was updated
    if any([update.customer_name, update.customer_phone, update.customer_email]):
        try:
            from ..services.customer_service import CustomerService
            from ..services.auth import get_db
            async for auth_db in get_db():
                await CustomerService.link_quote_to_customer(auth_db, updated_quote)
                await auth_db.commit()
                break
        except Exception as e:
            print(f"Warning: Failed to re-link quote to customer: {e}")

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

        # Build terms dict from contractor defaults
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
    from ..models.database import Invoice

    db = get_db_service()

    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        return {"quotes": [], "count": 0}

    quotes = await db.get_quotes_by_contractor(contractor.id)

    # Get quote IDs that have invoices created from them
    quote_ids = [q.id for q in quotes]
    if quote_ids:
        async with db.async_session_maker() as session:
            result = await session.execute(
                select(Invoice.quote_id).where(
                    Invoice.quote_id.in_(quote_ids),
                    Invoice.quote_id.isnot(None)
                )
            )
            quotes_with_invoices = set(row[0] for row in result.fetchall())
    else:
        quotes_with_invoices = set()

    return {
        "quotes": [quote_to_response(q, has_invoice=(q.id in quotes_with_invoices)) for q in quotes],
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
    accent_color: Optional[str] = None  # For visual preview
    header_color: Optional[str] = None  # For visual preview
    title_font: Optional[str] = None  # For font preview (Times-Roman, Helvetica, Courier)
    body_font: Optional[str] = None  # For font preview


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

    # Trial users get access to ALL templates to experience full product
    is_trial = user_tier == "trial"

    # Filter templates by tier (trial users see all)
    available_templates = []
    for key, template in PDF_TEMPLATES.items():
        if is_trial or user_tier in template["available_to"]:
            available_templates.append(
                TemplateInfo(
                    key=key,
                    name=template["name"],
                    description=template["description"],
                    available_to=template["available_to"],
                    accent_color=template.get("accent_color"),
                    header_color=template.get("header_color"),
                    title_font=template.get("title_font"),
                    body_font=template.get("body_font")
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


# ============================================================================
# INNOV-1: Outcome Intelligence Engine
# ============================================================================

# Structured loss reasons for pattern analysis
LOSS_REASONS = {
    "price_too_high": "Price was too high",
    "went_with_competitor": "Went with a competitor",
    "project_cancelled": "Project was cancelled/postponed",
    "no_response": "Customer never responded",
    "scope_changed": "Job scope changed significantly",
    "timing_issue": "Timing/scheduling didn't work",
    "budget_constraint": "Customer budget constraints",
    "quality_concerns": "Concerns about quality/experience",
    "other": "Other reason",
}

# Structured win factors for learning what works
WIN_FACTORS = {
    "best_price": "Had the best price",
    "best_value": "Best overall value",
    "reputation": "Reputation/reviews",
    "quick_response": "Fast response time",
    "relationship": "Existing relationship",
    "referral": "Referral from past customer",
    "availability": "Best availability/timing",
    "other": "Other factor",
}


class MarkOutcomeRequest(BaseModel):
    """Request to mark a quote outcome (win/loss)."""
    outcome: str  # "won" or "lost"
    reason: Optional[str] = None  # Key from LOSS_REASONS or WIN_FACTORS
    notes: Optional[str] = None  # Free-form notes
    final_price: Optional[float] = None  # Actual price if different from quote


class MarkOutcomeResponse(BaseModel):
    """Response from marking outcome."""
    success: bool
    quote_id: str
    outcome: str
    message: str


class OutcomeStatsResponse(BaseModel):
    """Outcome statistics for a contractor."""
    total_quotes: int
    quotes_with_outcome: int
    won_count: int
    lost_count: int
    pending_count: int
    overall_win_rate: Optional[float] = None
    by_category: dict = {}
    by_price_range: dict = {}
    top_loss_reasons: list = []
    top_win_factors: list = []
    average_winning_price: Optional[float] = None
    average_losing_price: Optional[float] = None


class CategoryOutcomeInsight(BaseModel):
    """Pricing intelligence for a specific category."""
    category: str
    total_quotes: int
    won_count: int
    lost_count: int
    win_rate: Optional[float] = None
    avg_won_price: Optional[float] = None
    avg_lost_price: Optional[float] = None
    price_sweet_spot: Optional[dict] = None  # {min: X, max: Y, optimal: Z}
    confidence: str = "low"  # low, medium, high based on sample size


@router.post("/{quote_id}/outcome", response_model=MarkOutcomeResponse)
async def mark_quote_outcome(
    quote_id: str,
    outcome_request: MarkOutcomeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a quote as won or lost (contractor-side).

    INNOV-1: Outcome Intelligence Engine - Enables contractors to record
    outcomes when customers respond outside the app (phone, in-person, etc.).

    This data feeds into the learning system to:
    1. Track win/loss rates by category
    2. Identify optimal price points
    3. Learn what factors lead to success
    """
    if outcome_request.outcome not in ["won", "lost"]:
        raise HTTPException(
            status_code=400,
            detail="Outcome must be 'won' or 'lost'"
        )

    db = get_db_service()

    # Get the quote
    quote = await db.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor or quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if already has outcome
    if quote.outcome in ["won", "lost"]:
        return MarkOutcomeResponse(
            success=False,
            quote_id=quote_id,
            outcome=quote.outcome,
            message=f"Quote already marked as {quote.outcome}"
        )

    # Build update fields
    now = datetime.utcnow()
    update_fields = {
        "outcome": outcome_request.outcome,
        "status": outcome_request.outcome,
    }

    if outcome_request.outcome == "won":
        update_fields["accepted_at"] = now
    else:
        update_fields["rejected_at"] = now

    # Build outcome notes with structured reason
    notes_parts = []
    if outcome_request.reason:
        if outcome_request.outcome == "lost":
            reason_text = LOSS_REASONS.get(outcome_request.reason, outcome_request.reason)
        else:
            reason_text = WIN_FACTORS.get(outcome_request.reason, outcome_request.reason)
        notes_parts.append(f"Reason: {reason_text}")
        update_fields["rejection_reason"] = outcome_request.reason  # Store structured key

    if outcome_request.notes:
        notes_parts.append(outcome_request.notes)

    if notes_parts:
        update_fields["outcome_notes"] = " | ".join(notes_parts)

    # Store final price if provided (for learning actual vs quoted)
    if outcome_request.final_price:
        current_notes = quote.outcome_notes or ""
        price_note = f"Final price: ${outcome_request.final_price:,.2f} (quoted: ${quote.subtotal:,.2f})"
        update_fields["outcome_notes"] = f"{current_notes} | {price_note}" if current_notes else price_note

    # Update the quote
    await db.update_quote(quote_id, **update_fields)

    # Process outcome for learning
    if quote.job_type:
        try:
            if outcome_request.outcome == "won":
                # Successful quote - boost confidence in pricing
                await db.apply_acceptance_to_pricing_model(
                    contractor_id=str(contractor.id),
                    category=quote.job_type,
                    signal_type="won",
                )
            # For losses, we track the data but don't immediately adjust pricing
            # The aggregated stats will inform future pricing decisions
        except Exception as e:
            print(f"Warning: Failed to process outcome learning: {e}")

    # Track analytics
    try:
        analytics_service.track_event(
            user_id=str(current_user["id"]),
            event_name="quote_outcome_marked",
            properties={
                "contractor_id": str(contractor.id),
                "quote_id": quote_id,
                "outcome": outcome_request.outcome,
                "reason": outcome_request.reason,
                "job_type": quote.job_type,
                "quote_total": quote.subtotal,
                "final_price": outcome_request.final_price,
                "price_difference": (
                    outcome_request.final_price - quote.subtotal
                    if outcome_request.final_price else None
                ),
            }
        )
    except Exception as e:
        print(f"Warning: Failed to track outcome event: {e}")

    return MarkOutcomeResponse(
        success=True,
        quote_id=quote_id,
        outcome=outcome_request.outcome,
        message=f"Quote marked as {outcome_request.outcome}"
    )


@router.get("/outcome/stats", response_model=OutcomeStatsResponse)
async def get_outcome_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get aggregated outcome statistics for the contractor.

    INNOV-1: Outcome Intelligence Engine - Provides insights into:
    - Overall win/loss rates
    - Win rates by job category
    - Win rates by price range
    - Top reasons for wins and losses
    - Optimal price points
    """
    db = get_db_service()

    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get all quotes for this contractor
    quotes = await db.get_quotes_by_contractor(contractor.id)

    if not quotes:
        return OutcomeStatsResponse(
            total_quotes=0,
            quotes_with_outcome=0,
            won_count=0,
            lost_count=0,
            pending_count=0,
        )

    # Calculate overall stats
    total_quotes = len(quotes)
    won_quotes = [q for q in quotes if q.outcome == "won"]
    lost_quotes = [q for q in quotes if q.outcome == "lost"]
    pending_quotes = [q for q in quotes if q.outcome not in ["won", "lost"]]

    won_count = len(won_quotes)
    lost_count = len(lost_quotes)
    pending_count = len(pending_quotes)
    quotes_with_outcome = won_count + lost_count

    overall_win_rate = None
    if quotes_with_outcome > 0:
        overall_win_rate = round(won_count / quotes_with_outcome * 100, 1)

    # Calculate by category
    by_category = {}
    for q in quotes:
        if q.job_type:
            if q.job_type not in by_category:
                by_category[q.job_type] = {
                    "total": 0, "won": 0, "lost": 0, "pending": 0,
                    "won_total": 0, "lost_total": 0
                }
            by_category[q.job_type]["total"] += 1
            if q.outcome == "won":
                by_category[q.job_type]["won"] += 1
                by_category[q.job_type]["won_total"] += q.subtotal or 0
            elif q.outcome == "lost":
                by_category[q.job_type]["lost"] += 1
                by_category[q.job_type]["lost_total"] += q.subtotal or 0
            else:
                by_category[q.job_type]["pending"] += 1

    # Calculate win rates and averages per category
    for cat_name, cat_data in by_category.items():
        decided = cat_data["won"] + cat_data["lost"]
        if decided > 0:
            cat_data["win_rate"] = round(cat_data["won"] / decided * 100, 1)
            if cat_data["won"] > 0:
                cat_data["avg_won_price"] = round(cat_data["won_total"] / cat_data["won"], 2)
            if cat_data["lost"] > 0:
                cat_data["avg_lost_price"] = round(cat_data["lost_total"] / cat_data["lost"], 2)

    # Calculate by price range
    price_ranges = [
        (0, 500, "Under $500"),
        (500, 1000, "$500-$1,000"),
        (1000, 2500, "$1,000-$2,500"),
        (2500, 5000, "$2,500-$5,000"),
        (5000, 10000, "$5,000-$10,000"),
        (10000, float('inf'), "$10,000+"),
    ]

    by_price_range = {}
    for min_price, max_price, label in price_ranges:
        range_quotes = [
            q for q in quotes
            if q.subtotal and min_price <= q.subtotal < max_price
        ]
        if range_quotes:
            won_in_range = len([q for q in range_quotes if q.outcome == "won"])
            lost_in_range = len([q for q in range_quotes if q.outcome == "lost"])
            decided_in_range = won_in_range + lost_in_range
            by_price_range[label] = {
                "total": len(range_quotes),
                "won": won_in_range,
                "lost": lost_in_range,
                "win_rate": round(won_in_range / decided_in_range * 100, 1) if decided_in_range > 0 else None,
            }

    # Top loss reasons
    loss_reason_counts = {}
    for q in lost_quotes:
        reason = q.rejection_reason or "unknown"
        loss_reason_counts[reason] = loss_reason_counts.get(reason, 0) + 1

    top_loss_reasons = sorted(
        [{"reason": k, "count": v, "label": LOSS_REASONS.get(k, k)}
         for k, v in loss_reason_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]

    # Average prices
    avg_winning_price = None
    if won_quotes:
        won_totals = [q.subtotal for q in won_quotes if q.subtotal]
        if won_totals:
            avg_winning_price = round(sum(won_totals) / len(won_totals), 2)

    avg_losing_price = None
    if lost_quotes:
        lost_totals = [q.subtotal for q in lost_quotes if q.subtotal]
        if lost_totals:
            avg_losing_price = round(sum(lost_totals) / len(lost_totals), 2)

    return OutcomeStatsResponse(
        total_quotes=total_quotes,
        quotes_with_outcome=quotes_with_outcome,
        won_count=won_count,
        lost_count=lost_count,
        pending_count=pending_count,
        overall_win_rate=overall_win_rate,
        by_category=by_category,
        by_price_range=by_price_range,
        top_loss_reasons=top_loss_reasons,
        top_win_factors=[],  # TODO: Track win factors
        average_winning_price=avg_winning_price,
        average_losing_price=avg_losing_price,
    )


@router.get("/outcome/category/{category}", response_model=CategoryOutcomeInsight)
async def get_category_outcome_insight(
    category: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get pricing intelligence for a specific job category.

    INNOV-1: Outcome Intelligence Engine - Returns:
    - Win rate for this category
    - Average prices for won vs lost quotes
    - Price sweet spot (optimal pricing range)
    - Confidence level based on sample size
    """
    db = get_db_service()

    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get quotes for this category
    all_quotes = await db.get_quotes_by_contractor(contractor.id)
    category_quotes = [q for q in all_quotes if q.job_type == category]

    if not category_quotes:
        return CategoryOutcomeInsight(
            category=category,
            total_quotes=0,
            won_count=0,
            lost_count=0,
        )

    total_quotes = len(category_quotes)
    won_quotes = [q for q in category_quotes if q.outcome == "won"]
    lost_quotes = [q for q in category_quotes if q.outcome == "lost"]

    won_count = len(won_quotes)
    lost_count = len(lost_quotes)
    decided = won_count + lost_count

    win_rate = None
    if decided > 0:
        win_rate = round(won_count / decided * 100, 1)

    # Calculate average prices
    avg_won_price = None
    if won_quotes:
        won_totals = [q.subtotal for q in won_quotes if q.subtotal]
        if won_totals:
            avg_won_price = round(sum(won_totals) / len(won_totals), 2)

    avg_lost_price = None
    if lost_quotes:
        lost_totals = [q.subtotal for q in lost_quotes if q.subtotal]
        if lost_totals:
            avg_lost_price = round(sum(lost_totals) / len(lost_totals), 2)

    # Calculate price sweet spot
    price_sweet_spot = None
    if won_count >= 3:  # Need at least 3 won quotes to calculate
        won_prices = sorted([q.subtotal for q in won_quotes if q.subtotal])
        if won_prices:
            price_sweet_spot = {
                "min": round(won_prices[0], 2),
                "max": round(won_prices[-1], 2),
                "optimal": round(sum(won_prices) / len(won_prices), 2),  # Average of wins
            }
            # If we have lost quotes that were higher, cap the max
            if lost_quotes:
                lost_prices = [q.subtotal for q in lost_quotes if q.subtotal]
                avg_loss = sum(lost_prices) / len(lost_prices) if lost_prices else 0
                if avg_loss > price_sweet_spot["optimal"]:
                    price_sweet_spot["ceiling_warning"] = round(avg_loss, 2)

    # Determine confidence level
    if decided >= 20:
        confidence = "high"
    elif decided >= 10:
        confidence = "medium"
    else:
        confidence = "low"

    return CategoryOutcomeInsight(
        category=category,
        total_quotes=total_quotes,
        won_count=won_count,
        lost_count=lost_count,
        win_rate=win_rate,
        avg_won_price=avg_won_price,
        avg_lost_price=avg_lost_price,
        price_sweet_spot=price_sweet_spot,
        confidence=confidence,
    )


@router.get("/outcome/reasons")
async def get_outcome_reasons():
    """
    Get available outcome reason options.

    Returns structured lists of loss reasons and win factors
    for frontend dropdown population.
    """
    return {
        "loss_reasons": [
            {"key": k, "label": v} for k, v in LOSS_REASONS.items()
        ],
        "win_factors": [
            {"key": k, "label": v} for k, v in WIN_FACTORS.items()
        ],
    }


# ============================================================================
# INNOV-5: Win/Loss Dashboard
# ============================================================================

@router.get("/analytics/dashboard")
async def get_win_loss_dashboard(
    period: str = "this_month",
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive win/loss dashboard data.

    Returns:
    - Overview stats (win rate, totals, averages)
    - Trend comparison vs previous period
    - Loss reason analysis
    - Performance by job type
    - Recent wins/losses
    - Monthly trend for charting
    """
    from ..services.win_loss_analytics import WinLossAnalyticsService, TimePeriod

    db = get_db_service()
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Parse period
    try:
        time_period = TimePeriod(period)
    except ValueError:
        time_period = TimePeriod.THIS_MONTH

    async with db.async_session_maker() as session:
        dashboard = await WinLossAnalyticsService.get_full_dashboard(
            db=session,
            contractor_id=contractor.id,
            period=time_period
        )

    return dashboard


@router.get("/analytics/stats")
async def get_win_loss_stats(
    period: str = "this_month",
    current_user: dict = Depends(get_current_user)
):
    """
    Get win/loss statistics for a specific period.

    Lighter-weight endpoint for quick stats without full dashboard data.
    """
    from ..services.win_loss_analytics import WinLossAnalyticsService, TimePeriod
    from dataclasses import asdict

    db = get_db_service()
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    try:
        time_period = TimePeriod(period)
    except ValueError:
        time_period = TimePeriod.THIS_MONTH

    async with db.async_session_maker() as session:
        stats = await WinLossAnalyticsService.get_win_loss_stats(
            db=session,
            contractor_id=contractor.id,
            period=time_period
        )

    return asdict(stats)


@router.get("/analytics/loss-reasons")
async def get_loss_reasons_analysis(
    period: str = "this_year",
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed loss reason analysis.

    Analyzes patterns in lost quotes to help improve win rate.
    """
    from ..services.win_loss_analytics import WinLossAnalyticsService, TimePeriod
    from dataclasses import asdict

    db = get_db_service()
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    try:
        time_period = TimePeriod(period)
    except ValueError:
        time_period = TimePeriod.THIS_YEAR

    async with db.async_session_maker() as session:
        analysis = await WinLossAnalyticsService.get_loss_reason_analysis(
            db=session,
            contractor_id=contractor.id,
            period=time_period
        )

    return {"loss_reasons": [asdict(lr) for lr in analysis]}


@router.get("/analytics/trend")
async def get_monthly_trend(
    months: int = 6,
    current_user: dict = Depends(get_current_user)
):
    """
    Get monthly trend data for charting.

    Returns win rate, quote count, and revenue by month.
    """
    from ..services.win_loss_analytics import WinLossAnalyticsService

    db = get_db_service()
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Cap at 12 months
    months = min(max(1, months), 12)

    async with db.async_session_maker() as session:
        trend = await WinLossAnalyticsService.get_monthly_trend(
            db=session,
            contractor_id=contractor.id,
            months=months
        )

    return {"monthly_trend": trend}


@router.get("/analytics/by-job-type")
async def get_performance_by_job_type(
    period: str = "this_year",
    current_user: dict = Depends(get_current_user)
):
    """
    Get win/loss performance breakdown by job type.

    Helps identify which job types have best conversion rates.
    """
    from ..services.win_loss_analytics import WinLossAnalyticsService, TimePeriod

    db = get_db_service()
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    try:
        time_period = TimePeriod(period)
    except ValueError:
        time_period = TimePeriod.THIS_YEAR

    async with db.async_session_maker() as session:
        performance = await WinLossAnalyticsService.get_performance_by_job_type(
            db=session,
            contractor_id=contractor.id,
            period=time_period
        )

    return {"by_job_type": performance}
