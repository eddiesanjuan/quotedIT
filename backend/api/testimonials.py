"""
Testimonial API endpoints for Quoted.
Handles collecting and retrieving user testimonials.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..services.auth import get_db, get_current_user
from ..models.database import Testimonial

router = APIRouter()


class SubmitTestimonialRequest(BaseModel):
    """Request model for submitting a testimonial."""
    rating: int  # 1-5
    quote_text: str
    name: Optional[str] = None
    company: Optional[str] = None


class TestimonialResponse(BaseModel):
    """Response model for a testimonial."""
    id: str
    rating: int
    quote_text: str
    name: Optional[str]
    company: Optional[str]
    created_at: datetime
    approved: bool


@router.post("/", status_code=status.HTTP_201_CREATED)
async def submit_testimonial(
    request: SubmitTestimonialRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a testimonial from a user.
    Triggered after user generates their 3rd quote.
    Initially marked as pending (approved=False).
    """
    # Validate rating
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )

    # Check if user already submitted a testimonial
    query = select(Testimonial).where(Testimonial.user_id == user["id"])
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a testimonial"
        )

    # Create testimonial
    testimonial = Testimonial(
        user_id=user["id"],
        rating=request.rating,
        quote_text=request.quote_text.strip(),
        name=request.name.strip() if request.name else None,
        company=request.company.strip() if request.company else None,
        approved=False,
    )

    db.add(testimonial)
    await db.commit()
    await db.refresh(testimonial)

    return {
        "id": testimonial.id,
        "message": "Thank you for your feedback! Your testimonial has been submitted for review."
    }


@router.get("/", response_model=List[TestimonialResponse])
async def get_testimonials(
    approved_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    Get testimonials for display on landing page.
    By default, only returns approved testimonials.
    Set approved_only=false to get all testimonials (for admin review).
    """
    query = select(Testimonial)

    if approved_only:
        query = query.where(Testimonial.approved == True)

    query = query.order_by(Testimonial.created_at.desc())

    result = await db.execute(query)
    testimonials = result.scalars().all()

    return [
        TestimonialResponse(
            id=t.id,
            rating=t.rating,
            quote_text=t.quote_text,
            name=t.name,
            company=t.company,
            created_at=t.created_at,
            approved=t.approved,
        )
        for t in testimonials
    ]


@router.get("/check-submitted")
async def check_testimonial_submitted(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if the current user has already submitted a testimonial.
    Used to prevent showing the collection modal multiple times.
    """
    query = select(Testimonial).where(Testimonial.user_id == user["id"])
    result = await db.execute(query)
    testimonial = result.scalar_one_or_none()

    return {
        "has_submitted": testimonial is not None
    }
