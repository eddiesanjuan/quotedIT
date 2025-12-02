"""
Referral service for Quoted.
Handles referral code generation, application, and reward crediting.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from ..models.database import User
from ..config import settings
from .analytics import analytics_service


class ReferralService:
    """Service for managing referral operations."""

    @staticmethod
    def generate_referral_code(email: str) -> str:
        """
        Generate a unique referral code from email username.
        Format: JOHN-A3X9 (username prefix + 4 random alphanumeric chars).

        Args:
            email: User's email address

        Returns:
            str: Referral code in format USERNAME-XXXX
        """
        # Extract username from email and take first 6 chars, uppercase
        username = email.split("@")[0][:6].upper()

        # Generate 4 random alphanumeric characters
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

        return f"{username}-{random_suffix}"

    @staticmethod
    async def ensure_unique_referral_code(db: AsyncSession, email: str) -> str:
        """
        Generate a unique referral code, retrying if collision occurs.

        Args:
            db: Database session
            email: User's email address

        Returns:
            str: Unique referral code
        """
        max_attempts = 10
        for _ in range(max_attempts):
            code = ReferralService.generate_referral_code(email)

            # Check if code already exists
            result = await db.execute(
                select(User).where(User.referral_code == code)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                return code

        # Fallback: add timestamp suffix if still colliding
        username = email.split("@")[0][:4].upper()
        timestamp_suffix = str(int(datetime.utcnow().timestamp()))[-4:]
        return f"{username}-{timestamp_suffix}"

    @staticmethod
    async def apply_referral_code(
        db: AsyncSession,
        new_user: User,
        referral_code: str
    ) -> bool:
        """
        Apply a referral code during signup.
        - Validates the referral code exists
        - Prevents self-referral
        - Extends trial to 14 days (referee benefit)
        - Stores referral relationship

        Args:
            db: Database session
            new_user: The newly registered user
            referral_code: The referral code to apply

        Returns:
            bool: True if successfully applied, False if invalid

        Raises:
            HTTPException: If referral code is invalid or self-referral
        """
        # Find referrer by code
        result = await db.execute(
            select(User).where(User.referral_code == referral_code.upper())
        )
        referrer = result.scalar_one_or_none()

        if not referrer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid referral code"
            )

        # Prevent self-referral
        if referrer.id == new_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot use your own referral code"
            )

        # Apply referral
        new_user.referred_by_code = referral_code.upper()

        # Extend trial to 14 days (referee benefit)
        new_user.trial_ends_at = datetime.utcnow() + timedelta(days=14)

        await db.commit()

        # Track analytics event
        try:
            analytics_service.track_event(
                user_id=str(new_user.id),
                event_name="referral_code_applied",
                properties={
                    "referral_code": referral_code.upper(),
                    "referrer_id": str(referrer.id),
                    "extended_trial_days": 14,
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track referral_code_applied event: {e}")

        return True

    @staticmethod
    async def credit_referrer(db: AsyncSession, referee_user: User) -> None:
        """
        Credit the referrer when a referee subscribes to a paid plan.
        - Awards 1 month credit to referrer
        - Increments referrer's referral count
        - Only credits once per referee

        This should be called from the Stripe webhook when a subscription is activated.

        Args:
            db: Database session
            referee_user: The user who just subscribed (referee)
        """
        if not referee_user.referred_by_code:
            # User wasn't referred, nothing to do
            return

        # Find referrer
        result = await db.execute(
            select(User).where(User.referral_code == referee_user.referred_by_code)
        )
        referrer = result.scalar_one_or_none()

        if not referrer:
            print(f"Warning: Referrer not found for code {referee_user.referred_by_code}")
            return

        # Award credit (1 month = 1 credit)
        referrer.referral_credits += 1
        referrer.referral_count += 1

        await db.commit()

        # Track analytics event
        try:
            analytics_service.track_event(
                user_id=str(referrer.id),
                event_name="referral_credit_earned",
                properties={
                    "referee_id": str(referee_user.id),
                    "referee_email": referee_user.email,
                    "credits_earned": 1,
                    "total_referrals": referrer.referral_count,
                    "total_credits": referrer.referral_credits,
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track referral_credit_earned event: {e}")

    @staticmethod
    async def get_referral_stats(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """
        Get referral statistics for a user.
        Auto-generates referral code for existing users who don't have one.

        Args:
            db: Database session
            user_id: User's ID

        Returns:
            dict: Referral stats including code, count, credits, and shareable link
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Auto-generate referral code for existing users who don't have one
        if not user.referral_code:
            user.referral_code = await ReferralService.ensure_unique_referral_code(db, user.email)
            await db.commit()
            await db.refresh(user)

        # Construct shareable link
        base_url = settings.frontend_url.rstrip("/")
        shareable_link = f"{base_url}/signup?ref={user.referral_code}" if user.referral_code else None

        return {
            "referral_code": user.referral_code,
            "referral_count": user.referral_count or 0,
            "referral_credits": user.referral_credits or 0,
            "shareable_link": shareable_link,
        }
