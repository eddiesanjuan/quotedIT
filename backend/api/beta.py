"""
Beta spots API for social proof scarcity.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..services.auth import get_db
from ..models.database import User

router = APIRouter()

# Configuration
BETA_TOTAL_SPOTS = 100
BETA_OFFSET = 64  # Adjusted down to account for test accounts (targeting ~16 spots remaining)

@router.get("/spots")
async def get_beta_spots(db: AsyncSession = Depends(get_db)):
    """
    Get beta spots status.
    Returns total spots, claimed count (real + offset), and remaining.
    """
    # Count real users
    result = await db.execute(select(func.count(User.id)))
    real_users = result.scalar() or 0

    # Calculate claimed (offset + real users)
    claimed = BETA_OFFSET + real_users

    # Calculate remaining (can't go negative)
    remaining = max(0, BETA_TOTAL_SPOTS - claimed)

    return {
        "total": BETA_TOTAL_SPOTS,
        "claimed": claimed,
        "remaining": remaining,
        "is_full": remaining == 0
    }
