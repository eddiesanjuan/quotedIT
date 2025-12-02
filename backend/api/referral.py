"""
Referral API endpoints for Quoted.
Handles referral code sharing, stats, and application.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from ..services.auth import get_db, get_current_user
from ..services.referral import ReferralService

router = APIRouter()


class ReferralCodeResponse(BaseModel):
    """Response model for referral code."""
    referral_code: str
    shareable_link: str


class ReferralStatsResponse(BaseModel):
    """Response model for referral statistics."""
    referral_code: Optional[str]
    referral_count: int
    referral_credits: int
    shareable_link: Optional[str]


class ApplyReferralRequest(BaseModel):
    """Request model for applying a referral code."""
    referral_code: str


@router.get("/code", response_model=ReferralCodeResponse)
async def get_referral_code(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current user's referral code and shareable link.
    Returns the code they can share with others.
    """
    stats = await ReferralService.get_referral_stats(db, user["id"])

    if not stats["referral_code"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral code not found. This may indicate an old account. Contact support."
        )

    return ReferralCodeResponse(
        referral_code=stats["referral_code"],
        shareable_link=stats["shareable_link"],
    )


@router.get("/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get referral statistics for the current user.
    Shows how many people they've referred and how many credits they've earned.
    """
    stats = await ReferralService.get_referral_stats(db, user["id"])

    return ReferralStatsResponse(
        referral_code=stats["referral_code"],
        referral_count=stats["referral_count"],
        referral_credits=stats["referral_credits"],
        shareable_link=stats["shareable_link"],
    )


@router.get("/link", response_model=ReferralCodeResponse)
async def get_referral_link(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the full shareable referral link.
    Convenience endpoint that returns the same as /code.
    """
    stats = await ReferralService.get_referral_stats(db, user["id"])

    if not stats["referral_code"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral code not found"
        )

    return ReferralCodeResponse(
        referral_code=stats["referral_code"],
        shareable_link=stats["shareable_link"],
    )
