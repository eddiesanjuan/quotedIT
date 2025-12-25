"""
Follow-Up API endpoints for Quoted (INNOV-3).

Manages smart follow-up sequences for quotes:
- Create/enable follow-up sequences
- Pause/resume sequences
- Get sequence status and history
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..services.auth import get_db, get_current_user
from ..services.follow_up import FollowUpService
from ..services.logging import get_logger

router = APIRouter()
logger = get_logger("quoted.api.followup")


class FollowUpSequenceResponse(BaseModel):
    """Follow-up sequence status."""
    id: str
    status: str
    current_step: int
    max_steps: int
    next_follow_up_at: Optional[str]
    detected_signal: Optional[str]
    emails_sent: int
    events: list


class CreateSequenceRequest(BaseModel):
    """Request to create a follow-up sequence."""
    quote_id: str


class SequenceActionResponse(BaseModel):
    """Response for sequence actions."""
    success: bool
    message: str
    sequence_id: Optional[str] = None


@router.post("/create", response_model=SequenceActionResponse)
async def create_follow_up_sequence(
    request: CreateSequenceRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a smart follow-up sequence for a quote.

    The AI will automatically:
    - Analyze customer viewing patterns
    - Determine optimal follow-up timing
    - Send personalized follow-up emails
    """
    from ..models.database import Quote
    from sqlalchemy import select

    # Verify quote belongs to this contractor
    result = await db.execute(
        select(Quote).where(Quote.id == request.quote_id)
    )
    quote = result.scalar_one_or_none()

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    if str(quote.contractor_id) != str(user["contractor_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this quote"
        )

    # Check quote has customer email
    if not quote.customer_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quote must have customer email for follow-ups"
        )

    # Create sequence
    sequence_id = await FollowUpService.create_sequence(
        db=db,
        quote_id=request.quote_id,
        contractor_id=user["contractor_id"],
    )

    if not sequence_id:
        return SequenceActionResponse(
            success=False,
            message="Follow-up sequence already exists for this quote"
        )

    logger.info(f"Created follow-up sequence {sequence_id} for quote {request.quote_id}")

    return SequenceActionResponse(
        success=True,
        message="Follow-up sequence created successfully",
        sequence_id=sequence_id
    )


@router.get("/quote/{quote_id}", response_model=Optional[FollowUpSequenceResponse])
async def get_follow_up_status(
    quote_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get follow-up sequence status for a quote.

    Returns sequence details including:
    - Current step and status
    - Next follow-up time
    - Detected customer signals
    - Event history
    """
    from ..models.database import Quote
    from sqlalchemy import select

    # Verify quote belongs to this contractor
    result = await db.execute(
        select(Quote).where(Quote.id == quote_id)
    )
    quote = result.scalar_one_or_none()

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    if str(quote.contractor_id) != str(user["contractor_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this quote"
        )

    status_data = await FollowUpService.get_sequence_status(db, quote_id)
    return status_data


@router.post("/quote/{quote_id}/pause", response_model=SequenceActionResponse)
async def pause_follow_up_sequence(
    quote_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Pause follow-up sequence for a quote.

    Use this when:
    - Customer requested no more emails
    - Contractor wants to manually follow up
    - Deal is in negotiation
    """
    from ..models.database import Quote
    from sqlalchemy import select

    # Verify quote belongs to this contractor
    result = await db.execute(
        select(Quote).where(Quote.id == quote_id)
    )
    quote = result.scalar_one_or_none()

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    if str(quote.contractor_id) != str(user["contractor_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this quote"
        )

    success = await FollowUpService.pause_sequence(db, quote_id)

    if success:
        logger.info(f"Paused follow-up sequence for quote {quote_id}")
        return SequenceActionResponse(
            success=True,
            message="Follow-up sequence paused"
        )
    else:
        return SequenceActionResponse(
            success=False,
            message="No active sequence to pause"
        )


@router.post("/quote/{quote_id}/resume", response_model=SequenceActionResponse)
async def resume_follow_up_sequence(
    quote_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resume a paused follow-up sequence.

    The AI will recalculate optimal timing based on current viewing patterns.
    """
    from ..models.database import Quote
    from sqlalchemy import select

    # Verify quote belongs to this contractor
    result = await db.execute(
        select(Quote).where(Quote.id == quote_id)
    )
    quote = result.scalar_one_or_none()

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

    if str(quote.contractor_id) != str(user["contractor_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this quote"
        )

    success = await FollowUpService.resume_sequence(db, quote_id)

    if success:
        logger.info(f"Resumed follow-up sequence for quote {quote_id}")
        return SequenceActionResponse(
            success=True,
            message="Follow-up sequence resumed"
        )
    else:
        return SequenceActionResponse(
            success=False,
            message="No paused sequence to resume"
        )
