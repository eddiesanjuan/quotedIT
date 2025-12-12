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
