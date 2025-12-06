"""
Pricing Brain API routes for Quoted.

Allows users to view and edit what the AI has learned about their pricing.
This is the "show your work" feature that builds trust in the learning system.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services import get_pricing_brain_service, get_db_service
from ..services.auth import get_current_user


router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================


class CategorySummary(BaseModel):
    """Summary of a pricing category."""
    category: str
    display_name: str
    quotes_count: int
    confidence: float
    samples: int
    learned_adjustments_count: int


class CategoryDetail(BaseModel):
    """Detailed view of a pricing category."""
    category: str
    display_name: str
    learned_adjustments: List[str]
    samples: int
    confidence: float
    correction_count: int  # DISC-035


class UpdateCategoryRequest(BaseModel):
    """Request to update a category."""
    display_name: Optional[str] = None
    learned_adjustments: Optional[List[str]] = None


class CategoryAnalysis(BaseModel):
    """AI analysis of a category."""
    category: str
    analysis: str
    analyzed_at: str
    model: str
    error: Optional[bool] = False


class GlobalSettings(BaseModel):
    """Global pricing settings."""
    labor_rate_hourly: Optional[float]
    helper_rate_hourly: Optional[float]
    material_markup_percent: Optional[float]
    minimum_job_amount: Optional[float]
    pricing_notes: Optional[str]


class ConfidenceInfo(BaseModel):
    """Confidence information for a category (DISC-035)."""
    category: str
    correction_count: int
    confidence_level: str  # "low", "medium", "good", "high"
    confidence_label: str  # Human-readable label with count
    description: str  # Description of what this means


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("", response_model=List[CategorySummary])
async def get_all_categories(current_user: dict = Depends(get_current_user)):
    """
    Get all pricing categories with statistics.

    Returns a list of categories sorted by quote count (most used first).
    Shows learned adjustments count, confidence, and samples for each.
    """
    db = get_db_service()
    pricing_brain = get_pricing_brain_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        raise HTTPException(status_code=400, detail="Pricing model not found")

    # Debug logging
    pk = pricing_model.pricing_knowledge or {}
    print(f"[GET DEBUG] pricing_knowledge keys: {list(pk.keys())}")
    print(f"[GET DEBUG] categories: {list(pk.get('categories', {}).keys())}")

    # Get quotes for statistics
    quotes = await db.get_quotes_by_contractor(contractor.id)

    # Get categories with stats
    categories = pricing_brain.get_all_categories(
        pricing_knowledge=pricing_model.pricing_knowledge or {},
        quotes=quotes,
    )

    return categories


@router.get("/{category}", response_model=CategoryDetail)
async def get_category(category: str, current_user: dict = Depends(get_current_user)):
    """
    Get detailed information for a specific category.

    Returns the category's learned adjustments, samples, and confidence.
    """
    db = get_db_service()
    pricing_brain = get_pricing_brain_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        raise HTTPException(status_code=400, detail="Pricing model not found")

    # Get category detail
    category_detail = pricing_brain.get_category_detail(
        pricing_knowledge=pricing_model.pricing_knowledge or {},
        category=category,
    )

    if not category_detail:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")

    return category_detail


@router.put("/{category}", response_model=CategoryDetail)
async def update_category(
    category: str,
    update: UpdateCategoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a category's data.

    Allows editing display name and learned adjustments.
    Learned adjustments are the pricing rules the AI has learned for this category.
    """
    db = get_db_service()
    pricing_brain = get_pricing_brain_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        raise HTTPException(status_code=400, detail="Pricing model not found")

    try:
        # Update category
        updated_pricing_knowledge = pricing_brain.update_category(
            pricing_knowledge=pricing_model.pricing_knowledge or {},
            category=category,
            display_name=update.display_name,
            learned_adjustments=update.learned_adjustments,
        )

        # Save to database
        await db.update_pricing_model(
            contractor_id=contractor.id,
            pricing_knowledge=updated_pricing_knowledge,
        )

        # Return updated category detail
        category_detail = pricing_brain.get_category_detail(
            pricing_knowledge=updated_pricing_knowledge,
            category=category,
        )

        return category_detail

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{category}")
async def delete_category(category: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a category from pricing knowledge.

    This removes all learned adjustments for this category.
    Use with caution - this cannot be undone.
    """
    db = get_db_service()
    pricing_brain = get_pricing_brain_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        raise HTTPException(status_code=400, detail="Pricing model not found")

    try:
        # Delete category
        updated_pricing_knowledge = pricing_brain.delete_category(
            pricing_knowledge=pricing_model.pricing_knowledge or {},
            category=category,
        )

        # Save to database
        await db.update_pricing_model(
            contractor_id=contractor.id,
            pricing_knowledge=updated_pricing_knowledge,
        )

        return {"success": True, "message": f"Category '{category}' deleted"}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{category}/analyze", response_model=CategoryAnalysis)
async def analyze_category(category: str, current_user: dict = Depends(get_current_user)):
    """
    Get AI analysis for a specific category.

    Uses Claude Haiku (~$0.001/call) to analyze learned patterns
    and provide actionable insights.

    This is an on-demand feature - not run automatically to save costs.
    """
    db = get_db_service()
    pricing_brain = get_pricing_brain_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        raise HTTPException(status_code=400, detail="Pricing model not found")

    # Get category detail
    category_data = pricing_brain.get_category_detail(
        pricing_knowledge=pricing_model.pricing_knowledge or {},
        category=category,
    )

    if not category_data:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")

    # Get recent quotes for context
    quotes = await db.get_quotes_by_contractor(contractor.id)
    recent_quotes = [
        {
            "subtotal": q.subtotal,
            "job_description": q.job_description,
        }
        for q in quotes
        if q.job_type == category
    ][:5]  # Last 5 quotes

    # Run analysis
    analysis = await pricing_brain.analyze_category(
        category=category,
        category_data=category_data,
        recent_quotes=recent_quotes,
        contractor_name=contractor.business_name,
    )

    return analysis


class SyncResult(BaseModel):
    """Result of syncing categories from quotes."""
    categories_added: int
    categories_found: List[str]
    message: str


@router.post("/sync", response_model=SyncResult)
async def sync_categories_from_quotes(current_user: dict = Depends(get_current_user)):
    """
    Sync categories from existing quotes to the Pricing Brain.

    This is useful for accounts created before category registration was added.
    Scans all quotes and ensures each job_type is registered as a category.
    """
    db = get_db_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get all quotes
    quotes = await db.get_quotes_by_contractor(contractor.id)

    # Collect unique job types
    job_types = set()
    for quote in quotes:
        if quote.job_type:
            job_types.add(quote.job_type)

    # Register each category
    added_count = 0
    for job_type in job_types:
        was_added = await db.ensure_category_exists(
            contractor_id=contractor.id,
            category=job_type,
        )
        if was_added:
            added_count += 1

    return SyncResult(
        categories_added=added_count,
        categories_found=list(job_types),
        message=f"Synced {added_count} new categories from {len(quotes)} quotes"
    )


@router.get("/settings/global", response_model=GlobalSettings)
async def get_global_settings(current_user: dict = Depends(get_current_user)):
    """
    Get global pricing settings.

    Returns base rates, material markup, and minimum job amount.
    These apply across all categories.
    """
    db = get_db_service()
    pricing_brain = get_pricing_brain_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        raise HTTPException(status_code=400, detail="Pricing model not found")

    # Get global settings
    settings = pricing_brain.get_global_settings(pricing_model)

    return settings


@router.put("/settings/global", response_model=GlobalSettings)
async def update_global_settings(
    settings: GlobalSettings,
    current_user: dict = Depends(get_current_user)
):
    """
    Update global pricing settings.

    Allows editing base rates, material markup, minimum job amount, and pricing notes.
    These settings apply across all categories.
    """
    db = get_db_service()
    pricing_brain = get_pricing_brain_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Validate inputs
    if settings.labor_rate_hourly is not None and settings.labor_rate_hourly < 0:
        raise HTTPException(status_code=400, detail="Labor rate must be positive")

    if settings.helper_rate_hourly is not None and settings.helper_rate_hourly < 0:
        raise HTTPException(status_code=400, detail="Helper rate must be positive")

    if settings.material_markup_percent is not None:
        if settings.material_markup_percent < 0 or settings.material_markup_percent > 100:
            raise HTTPException(status_code=400, detail="Material markup must be between 0 and 100")

    if settings.minimum_job_amount is not None and settings.minimum_job_amount < 0:
        raise HTTPException(status_code=400, detail="Minimum job amount must be positive")

    # Update pricing model
    updated_model = await db.update_pricing_model(
        contractor_id=contractor.id,
        labor_rate_hourly=settings.labor_rate_hourly,
        helper_rate_hourly=settings.helper_rate_hourly,
        material_markup_percent=settings.material_markup_percent,
        minimum_job_amount=settings.minimum_job_amount,
        pricing_notes=settings.pricing_notes,
    )

    if not updated_model:
        raise HTTPException(status_code=400, detail="Failed to update pricing model")

    # Return updated settings
    updated_settings = pricing_brain.get_global_settings(updated_model)
    return updated_settings


@router.get("/{category}/confidence", response_model=ConfidenceInfo)
async def get_category_confidence(
    category: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get confidence information for a specific category.

    DISC-035: Learning System Trust Indicators
    Returns correction count and confidence label to show learning progress.
    """
    db = get_db_service()
    pricing_brain = get_pricing_brain_service()

    # Get contractor
    contractor = await db.get_contractor_by_user_id(current_user["id"])
    if not contractor:
        raise HTTPException(status_code=400, detail="Contractor not found")

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor.id)
    if not pricing_model:
        raise HTTPException(status_code=400, detail="Pricing model not found")

    # Get category detail
    category_data = pricing_brain.get_category_detail(
        pricing_knowledge=pricing_model.pricing_knowledge or {},
        category=category,
    )

    if not category_data:
        # Category doesn't exist yet, return low confidence
        confidence_info = pricing_brain.get_confidence_label(0, 0)
        return ConfidenceInfo(
            category=category,
            correction_count=0,
            **confidence_info
        )

    # Get confidence label
    correction_count = category_data.get("correction_count", 0)
    samples = category_data.get("samples", 0)
    confidence_info = pricing_brain.get_confidence_label(correction_count, samples)

    return ConfidenceInfo(
        category=category,
        correction_count=correction_count,
        **confidence_info
    )
