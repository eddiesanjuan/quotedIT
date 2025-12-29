"""
Learning Progress API for Quoted.

Shows users their AI learning progress across categories.
This makes the invisible learning system visible and builds trust.

Anthropic Showcase Principles:
- Interpretable AI: Every price traceable to its source
- Honest Uncertainty: Confidence scores reflect actual data quality
- Human-AI Collaboration: Learning improves from user corrections
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services import get_db_service
from ..services.auth import get_current_user
from ..services.pricing_confidence import (
    PricingConfidenceService,
    calculate_confidence,
)
from ..services.pricing_explanation import (
    PricingExplanationService,
    generate_pricing_explanation,
)


router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# Response Models
# ============================================================================


class CategoryProgress(BaseModel):
    """Progress data for a single category."""
    name: str
    display_name: str
    quotes: int
    corrections: int
    confidence: int  # 0-100


class LearningProgress(BaseModel):
    """Overall learning progress for a contractor."""
    total_quotes: int
    total_corrections: int
    categories_learned: int
    total_categories: int
    learning_progress_percent: int
    top_categories: List[CategoryProgress]
    learning_velocity: str  # "fast", "steady", "slow"


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/progress", response_model=LearningProgress)
async def get_learning_progress(current_user: dict = Depends(get_current_user)):
    """
    Get learning progress for the current user.

    Returns:
    - Total quotes generated
    - Total corrections made
    - Categories learned (with confidence levels)
    - Learning velocity (fast/steady/slow based on correction rate)
    - Top categories by activity
    """
    db = get_db_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        raise HTTPException(status_code=400, detail="Pricing model not found")

    # Get all quotes
    quotes = await db.get_quotes_by_contractor(contractor.id)
    total_quotes = len(quotes)

    # Count corrections (quotes that were edited)
    total_corrections = sum(1 for q in quotes if q.was_edited)

    # Get categories from pricing knowledge
    pricing_knowledge = pricing_model.pricing_knowledge or {}
    categories = pricing_knowledge.get("categories", {})

    # Count quotes per category
    quote_counts = {}
    correction_counts = {}
    for quote in quotes:
        job_type = quote.job_type
        if job_type:
            quote_counts[job_type] = quote_counts.get(job_type, 0) + 1
            if quote.was_edited:
                correction_counts[job_type] = correction_counts.get(job_type, 0) + 1

    # Build category progress list
    top_categories = []
    for category_key, category_data in categories.items():
        quotes_count = quote_counts.get(category_key, 0)
        corrections_count = correction_counts.get(category_key, 0)

        # Calculate confidence score (0-100)
        # Base confidence from stored value (0-1) -> convert to 0-100
        base_confidence = category_data.get("confidence", 0.5) * 100

        # Boost based on corrections (each correction adds ~5%, max 100%)
        corrections_boost = min(corrections_count * 5, 50)

        # Boost based on quotes (each quote adds ~2%, max 100%)
        quotes_boost = min(quotes_count * 2, 30)

        confidence = min(100, int(base_confidence + corrections_boost + quotes_boost))

        top_categories.append(CategoryProgress(
            name=category_key,
            display_name=category_data.get("display_name", category_key.replace("_", " ").title()),
            quotes=quotes_count,
            corrections=corrections_count,
            confidence=confidence,
        ))

    # Sort by activity (quotes + corrections)
    top_categories.sort(key=lambda x: (x.quotes + x.corrections * 2), reverse=True)

    # Take top 10
    top_categories = top_categories[:10]

    # Calculate categories learned (confidence > 50%)
    categories_learned = sum(1 for cat in top_categories if cat.confidence >= 50)
    total_categories = len(categories)

    # Calculate learning progress percent
    if total_categories > 0:
        learning_progress_percent = int((categories_learned / total_categories) * 100)
    else:
        learning_progress_percent = 0

    # Determine learning velocity
    if total_quotes > 0:
        correction_rate = total_corrections / total_quotes
        if correction_rate >= 0.5:
            learning_velocity = "fast"
        elif correction_rate >= 0.2:
            learning_velocity = "steady"
        else:
            learning_velocity = "slow"
    else:
        learning_velocity = "starting"

    return LearningProgress(
        total_quotes=total_quotes,
        total_corrections=total_corrections,
        categories_learned=categories_learned,
        total_categories=total_categories,
        learning_progress_percent=learning_progress_percent,
        top_categories=top_categories,
        learning_velocity=learning_velocity,
    )


# ============================================================================
# Anthropic Showcase: Confidence & Explanation Endpoints
# ============================================================================


class ConfidenceDimension(BaseModel):
    """Individual confidence dimension."""
    label: str
    value: float
    description: str


class CategoryConfidence(BaseModel):
    """Multi-dimensional confidence for a category."""
    category: str
    overall_confidence: float  # 0.0-1.0
    display_level: str  # "High", "Medium", "Low", "Learning"
    badge: str
    color: str
    message: str
    tooltip: str
    warnings: List[str]
    dimensions: Dict[str, str]  # Dimension breakdown
    quote_count: int
    acceptance_rate: float


class ExplanationComponent(BaseModel):
    """A single component of the pricing explanation."""
    type: str
    label: str
    amount: float
    source: str
    confidence: float


class PricingExplanationResponse(BaseModel):
    """Complete explanation of how a quote was priced."""
    summary: str
    overall_confidence: float
    confidence_label: str
    components: List[Dict[str, Any]]
    uncertainties: List[Dict[str, Any]]
    patterns_applied: List[Dict[str, Any]]
    learning_context: Optional[Dict[str, Any]]


class FeedbackRequest(BaseModel):
    """Structured feedback about pricing corrections."""
    line_item_id: Optional[str] = None
    original_price: float
    new_price: float
    category: str
    edit_type: str  # 'increase' or 'decrease'
    edit_percentage: float
    feedback_reason: str
    timestamp: str


@router.get("/confidence/{category}")
async def get_category_confidence(
    category: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get multi-dimensional confidence metrics for a job category.

    Anthropic Showcase Principle: Honest Uncertainty
    - Returns calibrated confidence that reflects actual data quality
    - If we claim 80% confidence, 80% of quotes should be accepted without edit

    Returns:
        CategoryConfidence with badge, message, tooltip, and dimension breakdown
    """
    db = get_db_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        # Return "learning" state for new users
        return CategoryConfidence(
            category=category,
            overall_confidence=0.35,
            display_level="Learning",
            badge="Learning",
            color="gray",
            message="Building your pricing model",
            tooltip="Each quote you send helps AI learn your preferences",
            warnings=["New user - building your pricing model"],
            dimensions={
                "Data": "0% (no quotes yet)",
                "Accuracy": "0% (no data)",
                "Recency": "100% (fresh start)",
                "Coverage": "0% (no data)",
            },
            quote_count=0,
            acceptance_rate=0.0,
        )

    # Get category data from pricing knowledge
    pricing_knowledge = pricing_model.pricing_knowledge or {}
    categories = pricing_knowledge.get("categories", {})
    cat_data = categories.get(category, {})

    if not cat_data:
        # New category - return learning state
        return CategoryConfidence(
            category=category,
            overall_confidence=0.35,
            display_level="Learning",
            badge="Learning",
            color="gray",
            message=f"First {category.replace('_', ' ').title()} quote - building patterns",
            tooltip="This quote will establish baseline pricing for future similar jobs",
            warnings=[f"No prior {category.replace('_', ' ')} quotes"],
            dimensions={
                "Data": "0% (no quotes)",
                "Accuracy": "0% (no data)",
                "Recency": "100% (fresh start)",
                "Coverage": "0% (no data)",
            },
            quote_count=0,
            acceptance_rate=0.0,
        )

    # Calculate confidence using service
    quote_count = cat_data.get("quote_count", 0)
    acceptance_count = cat_data.get("acceptance_count", 0)
    correction_count = cat_data.get("correction_count", 0)
    correction_magnitudes = cat_data.get("correction_magnitudes", [])

    # Calculate days since last quote
    last_quote_at = cat_data.get("last_quote_at")
    if last_quote_at:
        try:
            last_dt = datetime.fromisoformat(last_quote_at.replace('Z', '+00:00'))
            days_since = (datetime.utcnow() - last_dt.replace(tzinfo=None)).days
        except Exception:
            days_since = 0
    else:
        days_since = 0

    complexity_distribution = cat_data.get("complexity_counts", {})

    # Calculate confidence
    confidence = calculate_confidence(
        quote_count=quote_count,
        acceptance_count=acceptance_count,
        correction_count=correction_count,
        correction_magnitudes=correction_magnitudes,
        days_since_last_quote=days_since,
        complexity_distribution=complexity_distribution,
    )

    # Get display elements
    service = PricingConfidenceService()
    display = service.get_confidence_display(confidence)

    total_signals = acceptance_count + correction_count
    acceptance_rate = acceptance_count / total_signals if total_signals > 0 else 0.0

    logger.info(
        f"Confidence API: contractor={contractor.id}, "
        f"category={category}, confidence={confidence.overall_confidence:.2f}, "
        f"level={confidence.display_confidence}"
    )

    return CategoryConfidence(
        category=category,
        overall_confidence=confidence.overall_confidence,
        display_level=confidence.display_confidence,
        badge=display["badge"],
        color=display["color"],
        message=display["message"],
        tooltip=display["tooltip"],
        warnings=display["warnings"],
        dimensions=display["dimension_breakdown"],
        quote_count=quote_count,
        acceptance_rate=round(acceptance_rate, 2),
    )


@router.get("/explanation/{quote_id}")
async def get_quote_explanation(
    quote_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get pricing explanation for a specific quote.

    Anthropic Showcase Principle: Interpretable AI
    - Shows the chain of reasoning from learned patterns → voice signals → final price
    - Every pricing component is traceable to its source

    Returns:
        PricingExplanationResponse with components, patterns, uncertainties
    """
    db = get_db_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get quote
    quote = await db.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Verify ownership
    if quote.contractor_id != contractor.id:
        raise HTTPException(status_code=403, detail="Not your quote")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        # Return minimal explanation for users without pricing model
        return PricingExplanationResponse(
            summary="Pricing based on market averages (no prior data)",
            overall_confidence=0.35,
            confidence_label="Learning",
            components=[{
                "type": "base_rate",
                "label": "Market average pricing",
                "amount": float(quote.subtotal or quote.total or 0),
                "source": "default",
                "confidence": 0.30,
            }],
            uncertainties=[{
                "area": "First quote",
                "reason": "No prior pricing data - using market averages",
                "suggestion": "This quote will help AI learn your pricing preferences",
            }],
            patterns_applied=[],
            learning_context=None,
        )

    # Get category data
    pricing_knowledge = pricing_model.pricing_knowledge or {}
    categories = pricing_knowledge.get("categories", {})
    detected_category = quote.job_type or "general"
    cat_data = categories.get(detected_category, {})

    # Calculate confidence for context
    confidence = calculate_confidence(
        quote_count=cat_data.get("quote_count", 0),
        acceptance_count=cat_data.get("acceptance_count", 0),
        correction_count=cat_data.get("correction_count", 0),
        correction_magnitudes=cat_data.get("correction_magnitudes", []),
        days_since_last_quote=0,
        complexity_distribution=cat_data.get("complexity_counts", {}),
    )

    # Get contractor DNA (for pattern transfer explanations)
    contractor_dna = pricing_knowledge.get("contractor_dna", {})

    # Get learned adjustments from quote metadata
    quote_metadata = quote.metadata or {}
    learned_adjustments = quote_metadata.get("learned_adjustments", [])
    voice_signals = quote_metadata.get("voice_signals", {})

    # Generate explanation
    explanation_service = PricingExplanationService()
    explanation = explanation_service.generate_explanation(
        quote=quote,
        learned_adjustments=learned_adjustments,
        contractor_dna=contractor_dna,
        voice_signals=voice_signals,
        confidence=confidence,
        pricing_model=pricing_model.pricing_knowledge or {},
        detected_category=detected_category,
    )

    logger.info(
        f"Explanation API: contractor={contractor.id}, "
        f"quote={quote_id}, category={detected_category}, "
        f"confidence={explanation.overall_confidence:.2f}"
    )

    return PricingExplanationResponse(
        summary=explanation.summary,
        overall_confidence=explanation.overall_confidence,
        confidence_label=explanation.confidence_label,
        components=[c.to_dict() for c in explanation.components],
        uncertainties=[u.to_dict() for u in explanation.uncertainties],
        patterns_applied=[p.to_dict() for p in explanation.patterns_applied],
        learning_context=explanation.learning_context.to_dict() if explanation.learning_context else None,
    )


@router.post("/feedback")
async def submit_edit_feedback(
    feedback: FeedbackRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Record structured feedback about pricing corrections.

    Anthropic Showcase Principle: Human-AI Collaboration
    - Captures structured feedback when users correct AI pricing
    - Feeds into learning system for continuous improvement

    Returns:
        Acknowledgment that feedback was recorded
    """
    db = get_db_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Log for learning system
    logger.info(
        f"Edit feedback: contractor={contractor.id}, "
        f"category={feedback.category}, "
        f"type={feedback.edit_type}, "
        f"percentage={feedback.edit_percentage:.1f}%, "
        f"reason={feedback.feedback_reason}"
    )

    # Track in PostHog for analysis (if available)
    try:
        from ..config import settings
        if settings.posthog_api_key:
            import posthog
            posthog.capture(
                distinct_id=str(contractor.id),
                event="pricing_feedback_submitted",
                properties={
                    "category": feedback.category,
                    "edit_type": feedback.edit_type,
                    "edit_percentage": feedback.edit_percentage,
                    "feedback_reason": feedback.feedback_reason,
                    "original_price": feedback.original_price,
                    "new_price": feedback.new_price,
                }
            )
    except Exception as e:
        logger.warning(f"PostHog tracking failed: {e}")

    # TODO: In future, feed this into the learning system for model improvement
    # This creates a correction signal (opposite of acceptance)

    return {"status": "recorded", "message": "Thank you for your feedback - this helps improve AI pricing"}
