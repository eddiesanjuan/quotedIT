"""
Contractor API routes for Quoted.
Handles contractor registration, profile management, and pricing models.
"""

from typing import Optional, List
from datetime import datetime
import base64
import imghdr

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, EmailStr

from ..services import get_learning_service, get_database_service
from ..services.auth import get_current_contractor
from ..models.database import Contractor
from ..config import settings


router = APIRouter()


# P0-06/P0-10 FIX: Demo endpoints are only available in non-production
# This prevents route shadowing and memory DoS attacks in production
def _is_demo_enabled():
    """Check if demo endpoints should be enabled (non-production only)."""
    return settings.environment != "production"


# Request/Response models

class ContractorCreate(BaseModel):
    """Request to create a new contractor."""
    business_name: str
    owner_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    primary_trade: str
    services: Optional[List[str]] = None


class ContractorResponse(BaseModel):
    """Contractor response."""
    id: str
    business_name: str
    owner_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    primary_trade: str
    services: Optional[List[str]] = None
    plan: str = "starter"
    created_at: Optional[str] = None


class PricingModelResponse(BaseModel):
    """Pricing model response."""
    labor_rate_hourly: Optional[float] = None
    helper_rate_hourly: Optional[float] = None
    material_markup_percent: float = 20.0
    minimum_job_amount: Optional[float] = None
    pricing_knowledge: dict = {}
    pricing_notes: Optional[str] = None
    pricing_philosophy: Optional[str] = None  # Global pricing DNA
    correction_count: int = 0
    last_learning_at: Optional[str] = None


class PricingModelUpdate(BaseModel):
    """Request to update pricing model."""
    labor_rate_hourly: Optional[float] = None
    helper_rate_hourly: Optional[float] = None
    material_markup_percent: Optional[float] = None
    minimum_job_amount: Optional[float] = None
    pricing_notes: Optional[str] = None
    pricing_philosophy: Optional[str] = None  # Global pricing DNA


class TermsResponse(BaseModel):
    """Terms response."""
    deposit_percent: float = 50.0
    deposit_description: Optional[str] = None
    final_payment_terms: str = "Balance due upon completion"
    accepted_payment_methods: List[str] = ["check", "credit_card"]
    credit_card_fee_percent: float = 3.0
    quote_valid_days: int = 30
    labor_warranty_years: int = 2
    custom_terms: Optional[str] = None
    # DISC-080: Default timeline and terms text for quotes
    default_timeline_text: Optional[str] = None
    default_terms_text: Optional[str] = None


class TermsUpdate(BaseModel):
    """Request to update terms."""
    deposit_percent: Optional[float] = None
    deposit_description: Optional[str] = None
    final_payment_terms: Optional[str] = None
    accepted_payment_methods: Optional[List[str]] = None
    credit_card_fee_percent: Optional[float] = None
    quote_valid_days: Optional[int] = None
    labor_warranty_years: Optional[int] = None
    custom_terms: Optional[str] = None
    # DISC-080: Default timeline and terms text for quotes
    default_timeline_text: Optional[str] = None
    default_terms_text: Optional[str] = None


class SetIndustryRequest(BaseModel):
    """Request to set contractor's industry/trade."""
    industry: str


class AccuracyStatsResponse(BaseModel):
    """Accuracy statistics response."""
    total_quotes: int = 0
    edited_count: int = 0
    unedited_count: int = 0
    accuracy_rate: float = 0.0
    average_adjustment_percent: float = 0.0
    within_5_percent: int = 0
    within_10_percent: int = 0


# In-memory storage for demo
_contractors = {
    "demo-contractor": {
        "id": "demo-contractor",
        "business_name": "Mike's Deck Pros",
        "owner_name": "Mike Johnson",
        "email": "mike@deckpros.com",
        "phone": "(555) 123-4567",
        "address": "123 Main St, Anytown, USA",
        "primary_trade": "deck_builder",
        "services": ["composite_decks", "wood_decks", "railings", "stairs"],
        "plan": "starter",
        "created_at": "2024-01-15T10:00:00Z",
    }
}

_pricing_models = {
    "demo-contractor": {
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
            },
            "demolition": {
                "base_rate": 900.0,
                "per_sqft_adder": 2.5,
            },
        },
        "pricing_notes": "Add 10% for difficult access. 5% discount for repeat customers.",
        "correction_count": 23,
        "last_learning_at": "2024-03-10T15:30:00Z",
    }
}

_terms = {
    "demo-contractor": {
        "deposit_percent": 50.0,
        "deposit_description": "50% deposit to schedule",
        "final_payment_terms": "Balance due upon completion",
        "accepted_payment_methods": ["check", "credit_card", "Zelle"],
        "credit_card_fee_percent": 3.0,
        "quote_valid_days": 30,
        "labor_warranty_years": 2,
        "custom_terms": None,
    }
}


@router.post("/", response_model=ContractorResponse)
async def create_contractor(contractor: ContractorCreate):
    """Create a new contractor account (demo only - disabled in production)."""
    # P0-06/P0-10: Gate demo endpoint in production
    if not _is_demo_enabled():
        raise HTTPException(status_code=404, detail="Not found")

    contractor_id = f"contractor_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    contractor_data = {
        "id": contractor_id,
        **contractor.model_dump(),
        "plan": "starter",
        "created_at": datetime.utcnow().isoformat(),
    }

    _contractors[contractor_id] = contractor_data

    # Initialize empty pricing model
    _pricing_models[contractor_id] = {
        "labor_rate_hourly": None,
        "helper_rate_hourly": None,
        "material_markup_percent": 20.0,
        "minimum_job_amount": None,
        "pricing_knowledge": {},
        "pricing_notes": None,
        "correction_count": 0,
    }

    # Initialize default terms
    _terms[contractor_id] = {
        "deposit_percent": 50.0,
        "quote_valid_days": 30,
        "labor_warranty_years": 2,
        "accepted_payment_methods": ["check", "credit_card"],
    }

    return ContractorResponse(**contractor_data)


@router.get("/demo/{contractor_id}", response_model=ContractorResponse)
async def get_contractor(contractor_id: str):
    """Get a demo contractor by ID (demo only - disabled in production).

    P0-06 FIX: Changed from /{contractor_id} to /demo/{contractor_id} to prevent
    route shadowing of static routes like /logo, /me/terms, /suggestions.
    """
    # P0-06/P0-10: Gate demo endpoint in production
    if not _is_demo_enabled():
        raise HTTPException(status_code=404, detail="Not found")

    if contractor_id not in _contractors:
        raise HTTPException(status_code=404, detail="Contractor not found")

    return ContractorResponse(**_contractors[contractor_id])


@router.get("/{contractor_id}/pricing", response_model=PricingModelResponse)
async def get_pricing_model(
    contractor_id: str,
    current_contractor: Contractor = Depends(get_current_contractor),
):
    """Get a contractor's pricing model from database."""
    # Verify ownership
    if current_contractor.id != contractor_id:
        raise HTTPException(status_code=403, detail="Access denied")

    db = get_database_service()
    pricing_model = await db.get_pricing_model(contractor_id)

    if not pricing_model:
        raise HTTPException(status_code=404, detail="Pricing model not found")

    return PricingModelResponse(
        labor_rate_hourly=pricing_model.labor_rate_hourly,
        helper_rate_hourly=pricing_model.helper_rate_hourly,
        material_markup_percent=pricing_model.material_markup_percent or 20.0,
        minimum_job_amount=pricing_model.minimum_job_amount,
        pricing_knowledge=pricing_model.pricing_knowledge or {},
        pricing_notes=pricing_model.pricing_notes,
        pricing_philosophy=pricing_model.pricing_philosophy,  # Global pricing DNA
        correction_count=0,
        last_learning_at=pricing_model.updated_at.isoformat() if pricing_model.updated_at else None,
    )


@router.put("/{contractor_id}/pricing", response_model=PricingModelResponse)
async def update_pricing_model_endpoint(
    contractor_id: str,
    update: PricingModelUpdate,
    current_contractor: Contractor = Depends(get_current_contractor),
):
    """Update a contractor's pricing model in database."""
    # Verify ownership
    if current_contractor.id != contractor_id:
        raise HTTPException(status_code=403, detail="Access denied")

    db = get_database_service()
    pricing_model = await db.get_pricing_model(contractor_id)

    if not pricing_model:
        raise HTTPException(status_code=404, detail="Pricing model not found")

    # Update using the database service
    updated = await db.update_pricing_model(
        contractor_id=contractor_id,
        labor_rate_hourly=update.labor_rate_hourly,
        helper_rate_hourly=update.helper_rate_hourly,
        material_markup_percent=update.material_markup_percent,
        minimum_job_amount=update.minimum_job_amount,
        pricing_notes=update.pricing_notes,
        pricing_philosophy=update.pricing_philosophy,  # Global pricing DNA
    )

    return PricingModelResponse(
        labor_rate_hourly=updated.labor_rate_hourly,
        helper_rate_hourly=updated.helper_rate_hourly,
        material_markup_percent=updated.material_markup_percent or 20.0,
        minimum_job_amount=updated.minimum_job_amount,
        pricing_knowledge=updated.pricing_knowledge or {},
        pricing_notes=updated.pricing_notes,
        pricing_philosophy=updated.pricing_philosophy,  # Global pricing DNA
        correction_count=0,
        last_learning_at=updated.updated_at.isoformat() if updated.updated_at else None,
    )


@router.get("/{contractor_id}/terms", response_model=TermsResponse)
async def get_terms(
    contractor_id: str,
    current_contractor: Contractor = Depends(get_current_contractor),
):
    """Get a contractor's terms."""
    # Verify ownership
    if current_contractor.id != contractor_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if contractor_id not in _terms:
        raise HTTPException(status_code=404, detail="Contractor not found")

    return TermsResponse(**_terms[contractor_id])


@router.put("/{contractor_id}/terms", response_model=TermsResponse)
async def update_terms(
    contractor_id: str,
    update: TermsUpdate,
    current_contractor: Contractor = Depends(get_current_contractor),
):
    """Update a contractor's terms."""
    # Verify ownership
    if current_contractor.id != contractor_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if contractor_id not in _terms:
        raise HTTPException(status_code=404, detail="Contractor not found")

    terms = _terms[contractor_id]

    for field in update.model_fields:
        value = getattr(update, field)
        if value is not None:
            terms[field] = value

    _terms[contractor_id] = terms
    return TermsResponse(**terms)


@router.get("/me/terms", response_model=TermsResponse)
async def get_my_terms(contractor: Contractor = Depends(get_current_contractor)):
    """Get the current contractor's default quote terms."""
    db = get_database_service()
    terms = await db.get_terms(contractor.id)

    if not terms:
        # Return defaults if no terms exist
        return TermsResponse()

    return TermsResponse(
        deposit_percent=terms.deposit_percent,
        final_payment_terms=terms.final_payment_terms,
        quote_valid_days=terms.quote_valid_days,
        labor_warranty_years=terms.labor_warranty_years,
        accepted_payment_methods=terms.accepted_payment_methods,
        custom_terms=terms.custom_terms,
        # DISC-080: Default timeline and terms text
        default_timeline_text=terms.default_timeline_text,
        default_terms_text=terms.default_terms_text,
    )


@router.put("/me/terms", response_model=TermsResponse)
async def update_my_terms(update: TermsUpdate, contractor: Contractor = Depends(get_current_contractor)):
    """Update the current contractor's default quote terms."""
    db = get_database_service()

    # Build update dict
    update_data = {}
    if update.deposit_percent is not None:
        update_data["deposit_percent"] = update.deposit_percent
    if update.quote_valid_days is not None:
        update_data["quote_valid_days"] = update.quote_valid_days
    if update.labor_warranty_years is not None:
        update_data["labor_warranty_years"] = update.labor_warranty_years
    if update.final_payment_terms is not None:
        update_data["final_payment_terms"] = update.final_payment_terms
    if update.accepted_payment_methods is not None:
        update_data["accepted_payment_methods"] = update.accepted_payment_methods
    if update.custom_terms is not None:
        update_data["custom_terms"] = update.custom_terms
    # DISC-080: Default timeline and terms text
    if update.default_timeline_text is not None:
        update_data["default_timeline_text"] = update.default_timeline_text
    if update.default_terms_text is not None:
        update_data["default_terms_text"] = update.default_terms_text

    terms = await db.update_terms(contractor.id, **update_data)

    if not terms:
        raise HTTPException(status_code=404, detail="Terms not found")

    return TermsResponse(
        deposit_percent=terms.deposit_percent,
        final_payment_terms=terms.final_payment_terms,
        quote_valid_days=terms.quote_valid_days,
        labor_warranty_years=terms.labor_warranty_years,
        accepted_payment_methods=terms.accepted_payment_methods,
        custom_terms=terms.custom_terms,
        # DISC-080: Default timeline and terms text
        default_timeline_text=terms.default_timeline_text,
        default_terms_text=terms.default_terms_text,
    )


@router.get("/{contractor_id}/accuracy", response_model=AccuracyStatsResponse)
async def get_accuracy_stats(contractor_id: str):
    """Get accuracy statistics for a contractor."""
    if contractor_id not in _contractors:
        raise HTTPException(status_code=404, detail="Contractor not found")

    # TODO: Calculate from actual quote history
    # For demo, return mock stats based on pricing model data
    model = _pricing_models.get(contractor_id, {})

    return AccuracyStatsResponse(
        total_quotes=model.get("correction_count", 0) + 5,
        edited_count=model.get("correction_count", 0),
        unedited_count=5,
        accuracy_rate=82.5 if model.get("correction_count", 0) > 10 else 65.0,
        average_adjustment_percent=3.2 if model.get("correction_count", 0) > 10 else 8.5,
        within_5_percent=model.get("correction_count", 0) - 2,
        within_10_percent=model.get("correction_count", 0),
    )


@router.post("/industry", response_model=ContractorResponse)
async def set_industry(
    request: SetIndustryRequest,
    contractor: Contractor = Depends(get_current_contractor),
):
    """
    Set the contractor's industry/trade.
    Used during onboarding to specify what type of work they do.
    """
    db = get_database_service()

    # Validate industry is not empty and has reasonable length
    if not request.industry or len(request.industry) > 100:
        raise HTTPException(
            status_code=400,
            detail="Industry must be between 1 and 100 characters"
        )

    # Update the contractor's primary_trade field
    updated = await db.update_contractor(
        contractor_id=contractor.id,
        primary_trade=request.industry
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Contractor not found")

    return ContractorResponse(
        id=updated.id,
        business_name=updated.business_name,
        owner_name=updated.owner_name,
        email=updated.email,
        phone=updated.phone,
        address=updated.address,
        primary_trade=updated.primary_trade,
        services=updated.services,
        plan=updated.plan,
        created_at=updated.created_at.isoformat() if updated.created_at else None,
    )


@router.get("/")
async def list_contractors():
    """List all contractors (demo only - disabled in production)."""
    # P0-06/P0-10: Gate demo endpoint in production
    if not _is_demo_enabled():
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "contractors": list(_contractors.values()),
        "count": len(_contractors),
    }


# ========================================
# Logo Management (DISC-016)
# ========================================

class LogoUploadResponse(BaseModel):
    """Response for logo upload."""
    success: bool
    message: str
    logo_data: Optional[str] = None


@router.post("/logo", response_model=LogoUploadResponse)
async def upload_logo(
    file: UploadFile = File(...),
    contractor: Contractor = Depends(get_current_contractor),
):
    """
    Upload a business logo (PNG or JPG, max 2MB).
    Stores as base64-encoded string in database.
    """
    # Validate file size (2MB max)
    MAX_SIZE = 2 * 1024 * 1024  # 2MB in bytes

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is 2MB, got {file_size / 1024 / 1024:.2f}MB"
        )

    # Validate file type (PNG or JPG)
    file_type = imghdr.what(None, h=file_content)
    if file_type not in ['png', 'jpeg']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PNG and JPG are allowed, got {file_type or 'unknown'}"
        )

    # Convert to base64
    base64_data = base64.b64encode(file_content).decode('utf-8')

    # Create data URI with proper MIME type
    mime_type = "image/png" if file_type == "png" else "image/jpeg"
    data_uri = f"data:{mime_type};base64,{base64_data}"

    # Update contractor in database
    db = get_database_service()
    updated = await db.update_contractor(
        contractor_id=contractor.id,
        logo_data=data_uri
    )

    if not updated:
        raise HTTPException(status_code=500, detail="Failed to save logo")

    return LogoUploadResponse(
        success=True,
        message="Logo uploaded successfully",
        logo_data=data_uri
    )


@router.get("/logo")
async def get_logo(
    contractor: Contractor = Depends(get_current_contractor),
):
    """Get the current contractor's logo."""
    db = get_database_service()
    contractor_data = await db.get_contractor(contractor.id)

    if not contractor_data:
        raise HTTPException(status_code=404, detail="Contractor not found")

    return {
        "logo_data": contractor_data.logo_data,
        "has_logo": contractor_data.logo_data is not None
    }


@router.delete("/logo")
async def delete_logo(
    contractor: Contractor = Depends(get_current_contractor),
):
    """Remove the contractor's logo."""
    db = get_database_service()

    updated = await db.update_contractor(
        contractor_id=contractor.id,
        logo_data=None
    )

    if not updated:
        raise HTTPException(status_code=500, detail="Failed to delete logo")

    return {
        "success": True,
        "message": "Logo deleted successfully"
    }


# ============================================================================
# PDF Template Settings (DISC-028)
# ============================================================================

class TemplateSettingsUpdate(BaseModel):
    """Request to update PDF template settings."""
    pdf_template: Optional[str] = None
    pdf_accent_color: Optional[str] = None


class TemplateSettingsResponse(BaseModel):
    """PDF template settings response."""
    pdf_template: str
    pdf_accent_color: Optional[str] = None


@router.put("/template-settings", response_model=TemplateSettingsResponse)
async def update_template_settings(
    settings: TemplateSettingsUpdate,
    contractor: Contractor = Depends(get_current_contractor),
):
    """
    Update PDF template settings for contractor.

    DISC-028: Allows Pro/Team users to customize their PDF quote appearance.
    """
    from ..services.pdf_generator import PDF_TEMPLATES

    db = get_database_service()

    # Validate template exists
    if settings.pdf_template and settings.pdf_template not in PDF_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid template. Available: {', '.join(PDF_TEMPLATES.keys())}"
        )

    # Build update dict
    update_data = {}
    if settings.pdf_template is not None:
        update_data["pdf_template"] = settings.pdf_template
    if settings.pdf_accent_color is not None:
        update_data["pdf_accent_color"] = settings.pdf_accent_color

    # Update contractor
    updated = await db.update_contractor(
        contractor_id=contractor.id,
        **update_data
    )

    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update template settings")

    return TemplateSettingsResponse(
        pdf_template=updated.pdf_template or "modern",
        pdf_accent_color=updated.pdf_accent_color,
    )


@router.get("/template-settings", response_model=TemplateSettingsResponse)
async def get_template_settings(
    contractor: Contractor = Depends(get_current_contractor),
):
    """Get current PDF template settings."""
    return TemplateSettingsResponse(
        pdf_template=contractor.pdf_template or "modern",
        pdf_accent_color=contractor.pdf_accent_color,
    )


# ============================================================================
# INNOV-9: Proactive Suggestions
# ============================================================================

class SuggestionData(BaseModel):
    """Dynamic data associated with a suggestion."""
    pass

    class Config:
        extra = "allow"  # Allow any additional fields


class SuggestionResponse(BaseModel):
    """A single proactive suggestion."""
    id: str
    type: str  # re_engagement, pricing_hint, follow_up, revenue_alert, etc.
    priority: str  # high, medium, low
    title: str
    message: str
    action_label: Optional[str] = None
    action_url: Optional[str] = None
    data: dict = {}
    dismissible: bool = True
    expires_at: Optional[str] = None


class SuggestionsListResponse(BaseModel):
    """Response containing proactive suggestions."""
    suggestions: List[SuggestionResponse]
    generated_at: str
    count: int


@router.get("/suggestions", response_model=SuggestionsListResponse)
async def get_proactive_suggestions(
    max_suggestions: int = 5,
    contractor: Contractor = Depends(get_current_contractor),
):
    """
    INNOV-9: Get proactive suggestions for the contractor.

    Returns personalized, actionable suggestions based on:
    - Dormant customers (re-engagement opportunities)
    - Stale quotes (follow-up reminders)
    - Pricing patterns (win rate analysis)
    - Revenue trends (alerts on changes)
    - Learning milestones (system achievements)
    - Efficiency tips (logo, settings optimization)
    """
    from ..services.proactive_suggestions import proactive_suggestions
    from ..database import get_db_session
    from datetime import datetime

    async with get_db_session() as db:
        suggestions = await proactive_suggestions.get_suggestions(
            db=db,
            contractor_id=contractor.id,
            max_suggestions=max_suggestions,
        )

        return SuggestionsListResponse(
            suggestions=[
                SuggestionResponse(
                    id=s.id,
                    type=s.type,
                    priority=s.priority,
                    title=s.title,
                    message=s.message,
                    action_label=s.action_label,
                    action_url=s.action_url,
                    data=s.data,
                    dismissible=s.dismissible,
                    expires_at=s.expires_at,
                )
                for s in suggestions
            ],
            generated_at=datetime.utcnow().isoformat(),
            count=len(suggestions),
        )


@router.post("/suggestions/{suggestion_id}/dismiss")
async def dismiss_suggestion(
    suggestion_id: str,
    contractor: Contractor = Depends(get_current_contractor),
):
    """
    INNOV-9: Dismiss a suggestion so it doesn't appear again.

    In the future, this could track dismissals in the database.
    For now, the frontend can manage this locally.
    """
    # TODO: Store dismissal in database for persistence
    # For now, just acknowledge the dismissal
    return {
        "success": True,
        "message": f"Suggestion {suggestion_id} dismissed",
        "suggestion_id": suggestion_id,
    }
