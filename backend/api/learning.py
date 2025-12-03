"""
Learning Progress API for Quoted.

Shows users their AI learning progress across categories.
This makes the invisible learning system visible and builds trust.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services import get_db_service
from ..services.auth import get_current_user


router = APIRouter()


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
