"""
Customer API endpoints for Quoted CRM (DISC-088).
Handles customer CRUD, search, and management operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

from ..services.auth import get_db, get_current_user
from ..services.customer_service import CustomerService
from ..models.database import Contractor
from sqlalchemy import select

router = APIRouter()


# Response/Request Models

class CustomerBase(BaseModel):
    """Base customer fields."""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = "active"
    notes: Optional[str] = None
    tags: Optional[List[str]] = []
    source: Optional[str] = None


class CustomerResponse(BaseModel):
    """Customer response model."""
    id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    status: str
    notes: Optional[str]
    tags: List[str]
    source: Optional[str]
    total_quoted: float
    total_won: float
    quote_count: int
    first_quote_at: Optional[datetime]
    last_quote_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """Paginated customer list response."""
    customers: List[CustomerResponse]
    total: int
    limit: int
    offset: int


class CustomerCreateRequest(BaseModel):
    """Create customer request."""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = "lead"
    source: Optional[str] = None


class CustomerUpdateRequest(BaseModel):
    """Update customer request."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None


class AddNoteRequest(BaseModel):
    """Add note request."""
    note: str


class AddTagRequest(BaseModel):
    """Add tag request."""
    tag: str


class CustomerSummaryResponse(BaseModel):
    """Customer summary stats response."""
    total_customers: int
    by_status: dict
    total_quoted: float
    total_won: float


class QuoteInCustomer(BaseModel):
    """Quote info for customer detail view."""
    id: str
    job_type: Optional[str]
    job_description: Optional[str]
    total: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerDetailResponse(CustomerResponse):
    """Customer detail with quotes."""
    quotes: List[QuoteInCustomer] = []


# Helper to get contractor

async def get_contractor(user: dict, db: AsyncSession) -> Contractor:
    """Get contractor for current user."""
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == user["id"])
    )
    contractor = result.scalar_one_or_none()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    return contractor


# Endpoints

@router.get("", response_model=CustomerListResponse)
async def list_customers(
    search: Optional[str] = Query(None, description="Search by name, phone, email"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    sort_by: str = Query("last_quote_at", description="Sort field"),
    sort_desc: bool = Query(True, description="Sort descending"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of customers.

    Supports search, filtering by status, and sorting.
    """
    contractor = await get_contractor(user, db)

    customers, total = await CustomerService.get_customers(
        db=db,
        contractor_id=contractor.id,
        search=search,
        status_filter=status_filter,
        sort_by=sort_by,
        sort_desc=sort_desc,
        limit=limit,
        offset=offset
    )

    return CustomerListResponse(
        customers=[CustomerResponse.model_validate(c) for c in customers],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/summary", response_model=CustomerSummaryResponse)
async def get_customer_summary(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get summary statistics for all customers."""
    contractor = await get_contractor(user, db)

    summary = await CustomerService.get_customer_summary(db, contractor.id)

    return CustomerSummaryResponse(**summary)


@router.get("/search")
async def search_customers(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick search for customers.
    Used for voice command lookups and autocomplete.
    """
    contractor = await get_contractor(user, db)

    customers = await CustomerService.search_customers(
        db=db,
        contractor_id=contractor.id,
        query=q,
        limit=limit
    )

    return [CustomerResponse.model_validate(c) for c in customers]


@router.get("/dormant")
async def get_dormant_customers(
    days: int = Query(90, ge=1, description="Days since last quote"),
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get customers who haven't had a quote in X days."""
    contractor = await get_contractor(user, db)

    customers = await CustomerService.get_dormant_customers(
        db=db,
        contractor_id=contractor.id,
        days=days,
        limit=limit
    )

    return [CustomerResponse.model_validate(c) for c in customers]


@router.get("/top")
async def get_top_customers(
    by: str = Query("total_quoted", description="Metric to sort by"),
    limit: int = Query(10, ge=1, le=50),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get top customers by revenue or quote count."""
    contractor = await get_contractor(user, db)

    if by not in ["total_quoted", "total_won", "quote_count"]:
        by = "total_quoted"

    customers = await CustomerService.get_top_customers(
        db=db,
        contractor_id=contractor.id,
        by=by,
        limit=limit
    )

    return [CustomerResponse.model_validate(c) for c in customers]


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single customer with quote history."""
    contractor = await get_contractor(user, db)

    customer = await CustomerService.get_customer_by_id(
        db=db,
        contractor_id=contractor.id,
        customer_id=customer_id,
        include_quotes=True
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Build response with quotes
    response_data = CustomerResponse.model_validate(customer).model_dump()
    response_data["quotes"] = [
        QuoteInCustomer.model_validate(q) for q in (customer.quotes or [])
    ]

    return CustomerDetailResponse(**response_data)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    request: CustomerCreateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new customer (lead).
    Used for manually adding potential customers.
    """
    contractor = await get_contractor(user, db)

    customer = await CustomerService.find_or_create_customer(
        db=db,
        contractor_id=contractor.id,
        name=request.name,
        phone=request.phone,
        email=request.email,
        address=request.address
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create customer. Name is required."
        )

    # Set additional fields
    if request.status:
        customer.status = request.status
    if request.source:
        customer.source = request.source

    await db.commit()
    await db.refresh(customer)

    return CustomerResponse.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    request: CustomerUpdateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a customer record."""
    contractor = await get_contractor(user, db)

    # Filter out None values
    updates = {k: v for k, v in request.model_dump().items() if v is not None}

    customer = await CustomerService.update_customer(
        db=db,
        contractor_id=contractor.id,
        customer_id=customer_id,
        updates=updates
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    await db.commit()
    await db.refresh(customer)

    return CustomerResponse.model_validate(customer)


@router.post("/{customer_id}/notes", response_model=CustomerResponse)
async def add_customer_note(
    customer_id: str,
    request: AddNoteRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a note to a customer."""
    contractor = await get_contractor(user, db)

    customer = await CustomerService.add_note(
        db=db,
        contractor_id=contractor.id,
        customer_id=customer_id,
        note=request.note
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    await db.commit()
    await db.refresh(customer)

    return CustomerResponse.model_validate(customer)


@router.post("/{customer_id}/tags", response_model=CustomerResponse)
async def add_customer_tag(
    customer_id: str,
    request: AddTagRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a tag to a customer."""
    contractor = await get_contractor(user, db)

    customer = await CustomerService.add_tag(
        db=db,
        contractor_id=contractor.id,
        customer_id=customer_id,
        tag=request.tag
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    await db.commit()
    await db.refresh(customer)

    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}/tags/{tag}", response_model=CustomerResponse)
async def remove_customer_tag(
    customer_id: str,
    tag: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a tag from a customer."""
    contractor = await get_contractor(user, db)

    customer = await CustomerService.remove_tag(
        db=db,
        contractor_id=contractor.id,
        customer_id=customer_id,
        tag=tag
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    await db.commit()
    await db.refresh(customer)

    return CustomerResponse.model_validate(customer)


# ================================================================
# INNOV-4: Enhanced Voice Commands (unified from DISC-090)
# ================================================================

class VoiceCommandRequest(BaseModel):
    """Voice command request."""
    transcription: str


class VoiceCommandResponse(BaseModel):
    """Voice command response (INNOV-4 enhanced)."""
    command_type: str  # Full command type (e.g., quote_win, task_create)
    success: bool
    spoken_response: str  # What to say back to user (optimized for voice)
    data: Optional[dict] = None
    action_taken: Optional[str] = None
    is_quote_creation: bool = False  # True if user wants to create a new quote


@router.post("/voice-command", response_model=VoiceCommandResponse)
async def process_voice_command(
    request: VoiceCommandRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    INNOV-4: Enhanced unified voice command processing.

    Handles all voice commands:
    - Quote management: "Mark Johnson quote as won", "Duplicate last quote"
    - Task management: "Remind me to call Sarah tomorrow", "What's on my list?"
    - Follow-up control: "Pause follow-ups for Smith quote", "What needs follow-up?"
    - Dashboard queries: "What's my win rate this month?", "Revenue last week?"
    - CRM operations: "Show me John Smith", "Tag Baker's as VIP"

    Returns is_quote_creation=True if user wants to CREATE a new quote
    (frontend should route to quote generation flow).
    """
    from ..services.voice_commands import voice_command_service

    contractor = await get_contractor(user, db)

    # Detect command type and extract parameters
    command_data = await voice_command_service.detect_command(request.transcription)

    # Check if this is a quote creation request (not a command)
    if command_data.get("is_quote_creation", False):
        return VoiceCommandResponse(
            command_type="create_quote",
            success=True,
            spoken_response="I'll help you create that quote.",
            is_quote_creation=True
        )

    # Execute the voice command
    result = await voice_command_service.execute(
        db=db,
        contractor_id=contractor.id,
        user_id=user["id"],
        command_data=command_data
    )

    return VoiceCommandResponse(
        command_type=result.command_type.value,
        success=result.success,
        spoken_response=result.spoken_response,
        data=result.data,
        action_taken=result.action_taken,
        is_quote_creation=False
    )


# ================================================================
# DISC-091: Backfill Existing Quotes to Customers
# ================================================================

class BackfillResponse(BaseModel):
    """Backfill operation response."""
    success: bool
    quotes_processed: int
    customers_created: int
    customers_linked: int
    errors: int


@router.post("/backfill", response_model=BackfillResponse)
async def backfill_quotes_to_customers(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Backfill existing quotes to customer records.

    Processes all quotes with customer data and creates/links
    Customer records using the deduplication service.

    Safe to run multiple times - idempotent operation.
    """
    from ..scripts.backfill_customers import backfill_customers_for_contractor

    contractor = await get_contractor(user, db)

    stats = await backfill_customers_for_contractor(
        db=db,
        contractor_id=contractor.id,
        verbose=False
    )

    return BackfillResponse(
        success=stats["errors"] == 0,
        quotes_processed=stats["quotes_processed"],
        customers_created=stats["customers_created"],
        customers_linked=stats["customers_linked"],
        errors=stats["errors"]
    )


# ================================================================
# INNOV-8: Repeat Customer Auto-Quotes
# ================================================================

class RecentQuoteInfo(BaseModel):
    """Recent quote info for auto-quote suggestions."""
    id: str
    job_type: Optional[str]
    job_description: Optional[str]
    total: Optional[float]
    status: Optional[str]
    created_at: Optional[str]


class CustomerInfo(BaseModel):
    """Customer info for auto-quote suggestions."""
    id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    status: str
    quote_count: int
    total_won: float


class PrefillData(BaseModel):
    """Pre-fill data for auto-quote."""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None


class JobTypeCount(BaseModel):
    """Job type count for pricing suggestions."""
    job_type: str
    count: int


class PricingSuggestions(BaseModel):
    """Pricing suggestions based on customer history."""
    job_type: Optional[str] = None
    previous_quotes_count: Optional[int] = None
    avg_quote_amount: Optional[float] = None
    min_quote_amount: Optional[float] = None
    max_quote_amount: Optional[float] = None
    last_quote_amount: Optional[float] = None
    last_quote_date: Optional[str] = None
    suggestion: Optional[str] = None
    most_common_job_types: Optional[List[JobTypeCount]] = None


class LoyaltyInfo(BaseModel):
    """Customer loyalty information."""
    is_repeat: bool = False
    is_vip: bool = False
    total_quotes: int = 0
    total_won: int = 0
    total_spent: float = 0
    win_rate: float = 0
    first_quote_date: Optional[str] = None
    last_quote_date: Optional[str] = None
    customer_since_months: int = 0
    tier: str = "new"
    tier_label: str = "New Customer"


class AutoQuoteSuggestionsResponse(BaseModel):
    """
    INNOV-8: Response with auto-quote suggestions for repeat customers.

    Returns customer recognition, pre-fill data, pricing suggestions,
    and loyalty tier information.
    """
    recognized: bool
    customer: Optional[CustomerInfo] = None
    prefill: PrefillData = PrefillData()
    pricing_suggestions: PricingSuggestions = PricingSuggestions()
    loyalty_info: LoyaltyInfo = LoyaltyInfo()
    recent_quotes: List[RecentQuoteInfo] = []


@router.get("/auto-quote/suggestions")
async def get_auto_quote_suggestions(
    customer: str = Query(..., min_length=1, description="Customer name, phone, or email"),
    job_type: Optional[str] = Query(None, description="Optional job type for filtering"),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AutoQuoteSuggestionsResponse:
    """
    INNOV-8: Get auto-quote suggestions for a customer.

    Recognizes repeat customers and returns:
    - Pre-fill data (name, phone, email, address from history)
    - Pricing suggestions (avg, min, max from similar jobs)
    - Loyalty tier (new, bronze, silver, gold, platinum)
    - Recent quote history for context

    Example:
        GET /customers/auto-quote/suggestions?customer=John+Smith
        GET /customers/auto-quote/suggestions?customer=555-1234&job_type=deck
    """
    contractor = await get_contractor(user, db)

    suggestions = await CustomerService.get_auto_quote_suggestions(
        db=db,
        contractor_id=contractor.id,
        customer_identifier=customer,
        job_type=job_type
    )

    # Convert to response model
    customer_info = None
    if suggestions.get("customer"):
        c = suggestions["customer"]
        customer_info = CustomerInfo(
            id=str(c["id"]),
            name=c["name"],
            phone=c.get("phone"),
            email=c.get("email"),
            address=c.get("address"),
            status=c.get("status", "active"),
            quote_count=c.get("quote_count", 0),
            total_won=c.get("total_won", 0),
        )

    prefill = PrefillData(**(suggestions.get("prefill", {})))

    # Build pricing suggestions
    ps = suggestions.get("pricing_suggestions", {})
    common_types = None
    if ps.get("most_common_job_types"):
        common_types = [
            JobTypeCount(job_type=jt["job_type"], count=jt["count"])
            for jt in ps["most_common_job_types"]
        ]
    pricing_suggestions = PricingSuggestions(
        job_type=ps.get("job_type"),
        previous_quotes_count=ps.get("previous_quotes_count"),
        avg_quote_amount=ps.get("avg_quote_amount"),
        min_quote_amount=ps.get("min_quote_amount"),
        max_quote_amount=ps.get("max_quote_amount"),
        last_quote_amount=ps.get("last_quote_amount"),
        last_quote_date=ps.get("last_quote_date"),
        suggestion=ps.get("suggestion"),
        most_common_job_types=common_types,
    )

    loyalty = LoyaltyInfo(**(suggestions.get("loyalty_info", {})))

    recent_quotes = [
        RecentQuoteInfo(
            id=str(q["id"]),
            job_type=q.get("job_type"),
            job_description=q.get("job_description"),
            total=q.get("total"),
            status=q.get("status"),
            created_at=q.get("created_at"),
        )
        for q in suggestions.get("recent_quotes", [])
    ]

    return AutoQuoteSuggestionsResponse(
        recognized=suggestions["recognized"],
        customer=customer_info,
        prefill=prefill,
        pricing_suggestions=pricing_suggestions,
        loyalty_info=loyalty,
        recent_quotes=recent_quotes,
    )


@router.get("/auto-quote/recognize")
async def recognize_customer(
    text: str = Query(..., min_length=1, description="Text to search for customer"),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    INNOV-8: Quick check if customer is recognized (for real-time autocomplete).

    Returns minimal data for fast response during voice recording.
    """
    contractor = await get_contractor(user, db)

    customers = await CustomerService.search_customers(
        db=db,
        contractor_id=contractor.id,
        query=text,
        limit=3
    )

    if not customers:
        return {
            "recognized": False,
            "suggestions": []
        }

    return {
        "recognized": True,
        "suggestions": [
            {
                "id": str(c.id),
                "name": c.name,
                "phone": c.phone,
                "email": c.email,
                "quote_count": c.quote_count or 0,
                "is_vip": c.status == "vip",
                "tier": "vip" if c.status == "vip" else (
                    "repeat" if (c.quote_count or 0) > 1 else "new"
                ),
            }
            for c in customers
        ]
    }


# =========================================================================
# DISC-126: Bulletproof Customer Identification Endpoints
# =========================================================================


class CustomerMatchRequest(BaseModel):
    """Request to find customer matches."""
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerMatchResponse(BaseModel):
    """Customer match result."""
    customer_id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    confidence: float
    match_reasons: List[str]
    quote_count: int
    total_quoted: float
    last_quote_at: Optional[str]


class CustomerMatchResultResponse(BaseModel):
    """Full customer matching result."""
    matches: List[CustomerMatchResponse]
    exact_match: Optional[CustomerMatchResponse]
    recommendation: str
    message: str
    input: dict


@router.post("/match", response_model=CustomerMatchResultResponse)
async def find_customer_matches(
    request: CustomerMatchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Find potential customer matches with confidence scores.

    DISC-126: Bulletproof customer identification.

    Confidence thresholds:
    - >= 0.95: auto_link (phone match or exact name)
    - >= 0.70: confirm_needed (likely match, ask user)
    - >= 0.50: confirm_needed (weak match, ask user)
    - < 0.50: create_new (no match found)

    Returns matches sorted by confidence with recommendation.
    """
    # Get contractor
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == current_user["sub"])
    )
    contractor = result.scalar_one_or_none()
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")

    # Find matches
    match_result = await CustomerService.find_customer_matches(
        db=db,
        contractor_id=contractor.id,
        name=request.name,
        phone=request.phone,
        address=request.address
    )

    return match_result


class RecentCustomersResponse(BaseModel):
    """Recent customers for picker."""
    customers: List[dict]


@router.get("/recent", response_model=RecentCustomersResponse)
async def get_recent_customers(
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most recently quoted customers for quick picker.

    DISC-126: For "repeat customer" voice signal - show recent customers.
    """
    # Get contractor
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == current_user["sub"])
    )
    contractor = result.scalar_one_or_none()
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")

    customers = await CustomerService.get_recent_customers(
        db=db,
        contractor_id=contractor.id,
        limit=limit
    )

    return {"customers": customers}
