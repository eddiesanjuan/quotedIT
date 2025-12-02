"""
Contractor API routes for Quoted.
Handles contractor registration, profile management, and pricing models.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from ..services import get_learning_service, get_database_service
from ..services.auth import get_current_contractor
from ..models.database import Contractor


router = APIRouter()


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
    correction_count: int = 0
    last_learning_at: Optional[str] = None


class PricingModelUpdate(BaseModel):
    """Request to update pricing model."""
    labor_rate_hourly: Optional[float] = None
    helper_rate_hourly: Optional[float] = None
    material_markup_percent: Optional[float] = None
    minimum_job_amount: Optional[float] = None
    pricing_notes: Optional[str] = None


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
    """Create a new contractor account."""
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


@router.get("/{contractor_id}", response_model=ContractorResponse)
async def get_contractor(contractor_id: str):
    """Get a contractor by ID."""
    if contractor_id not in _contractors:
        raise HTTPException(status_code=404, detail="Contractor not found")

    return ContractorResponse(**_contractors[contractor_id])


@router.get("/{contractor_id}/pricing", response_model=PricingModelResponse)
async def get_pricing_model(contractor_id: str):
    """Get a contractor's pricing model from database."""
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
        correction_count=0,
        last_learning_at=pricing_model.updated_at.isoformat() if pricing_model.updated_at else None,
    )


@router.put("/{contractor_id}/pricing", response_model=PricingModelResponse)
async def update_pricing_model_endpoint(contractor_id: str, update: PricingModelUpdate):
    """Update a contractor's pricing model in database."""
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
    )

    return PricingModelResponse(
        labor_rate_hourly=updated.labor_rate_hourly,
        helper_rate_hourly=updated.helper_rate_hourly,
        material_markup_percent=updated.material_markup_percent or 20.0,
        minimum_job_amount=updated.minimum_job_amount,
        pricing_knowledge=updated.pricing_knowledge or {},
        pricing_notes=updated.pricing_notes,
        correction_count=0,
        last_learning_at=updated.updated_at.isoformat() if updated.updated_at else None,
    )


@router.get("/{contractor_id}/terms", response_model=TermsResponse)
async def get_terms(contractor_id: str):
    """Get a contractor's terms."""
    if contractor_id not in _terms:
        raise HTTPException(status_code=404, detail="Contractor not found")

    return TermsResponse(**_terms[contractor_id])


@router.put("/{contractor_id}/terms", response_model=TermsResponse)
async def update_terms(contractor_id: str, update: TermsUpdate):
    """Update a contractor's terms."""
    if contractor_id not in _terms:
        raise HTTPException(status_code=404, detail="Contractor not found")

    terms = _terms[contractor_id]

    for field in update.model_fields:
        value = getattr(update, field)
        if value is not None:
            terms[field] = value

    _terms[contractor_id] = terms
    return TermsResponse(**terms)


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
    """List all contractors (admin/demo only)."""
    return {
        "contractors": list(_contractors.values()),
        "count": len(_contractors),
    }
