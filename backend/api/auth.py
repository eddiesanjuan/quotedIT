"""
Authentication API endpoints for Quoted.
Handles user registration and login.
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..services.auth import (
    UserCreate,
    UserLogin,
    Token,
    UserResponse,
    RefreshTokenRequest,
    get_db,
    register_user,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    validate_and_rotate_refresh_token,
    revoke_all_user_tokens,
    get_current_user,
    get_current_contractor,
)
from ..services.email import email_service
from ..services.analytics import analytics_service
from ..models.database import User, Contractor
from ..config import settings

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
    Creates both user and contractor profile in one step.
    Sends welcome email asynchronously.
    """
    user, contractor = await register_user(db, user_data)

    # Send welcome email (don't block on failure)
    try:
        await email_service.send_welcome_email(
            to_email=user.email,
            business_name=contractor.business_name,
            owner_name=contractor.owner_name,
        )
    except Exception as e:
        # Log the error but don't block registration
        print(f"Warning: Failed to send welcome email to {user.email}: {e}")

    # Track signup event
    try:
        analytics_service.identify_user(
            user_id=str(user.id),
            properties={
                "email": user.email,
                "business_name": contractor.business_name,
                "owner_name": contractor.owner_name,
                "primary_trade": contractor.primary_trade,
            }
        )
        analytics_service.track_event(
            user_id=str(user.id),
            event_name="signup_completed",
            properties={
                "business_name": contractor.business_name,
                "primary_trade": contractor.primary_trade,
                "referral_code": user.referral_code,
                "used_referral": bool(user.referred_by_code),
            }
        )
        # Track referral code generation
        analytics_service.track_event(
            user_id=str(user.id),
            event_name="referral_code_generated",
            properties={
                "referral_code": user.referral_code,
            }
        )
    except Exception as e:
        # Log the error but don't block registration
        print(f"Warning: Failed to track signup event for {user.email}: {e}")

    # Create access token (15 minutes - SEC-003)
    access_token = create_access_token(
        data={"sub": user.id, "contractor_id": contractor.id},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )

    # Create and store refresh token (7 days - SEC-003)
    refresh_token_value, jti = create_refresh_token()
    await store_refresh_token(
        db=db,
        user_id=user.id,
        token_value=refresh_token_value,
        jti=jti,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token_value,
        user_id=user.id,
        contractor_id=contractor.id,
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password.
    Returns JWT token for authenticated requests.
    """
    user = await authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get contractor profile
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == user.id)
    )
    contractor = result.scalar_one_or_none()

    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Contractor profile not found",
        )

    # Create access token (15 minutes - SEC-003)
    access_token = create_access_token(
        data={"sub": user.id, "contractor_id": contractor.id},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )

    # Create and store refresh token (7 days - SEC-003)
    refresh_token_value, jti = create_refresh_token()
    await store_refresh_token(
        db=db,
        user_id=user.id,
        token_value=refresh_token_value,
        jti=jti,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token_value,
        user_id=user.id,
        contractor_id=contractor.id,
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current user's profile.
    Requires authentication.
    """
    # Get full user model for onboarding_completed_at
    user_result = await db.execute(
        select(User).where(User.id == user["id"])
    )
    user_obj = user_result.scalar_one_or_none()

    # Get contractor profile
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == user["id"])
    )
    contractor = result.scalar_one_or_none()

    return UserResponse(
        id=user["id"],
        email=user["email"],
        is_active=user["is_active"],
        is_verified=user["is_verified"],
        contractor_id=contractor.id if contractor else None,
        business_name=contractor.business_name if contractor else None,
        primary_trade=contractor.primary_trade if contractor else None,
        onboarding_completed_at=user_obj.onboarding_completed_at.isoformat() if user_obj and user_obj.onboarding_completed_at else None,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh the access token using a refresh token.

    SEC-003: Uses refresh token rotation for security:
    - Each refresh token can only be used once
    - A new refresh token is issued with each request
    - Old refresh token is revoked immediately
    """
    # Validate and rotate refresh token
    user, new_refresh_token, jti = await validate_and_rotate_refresh_token(
        db=db,
        token_value=request.refresh_token,
    )

    # Get contractor profile
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == user.id)
    )
    contractor = result.scalar_one_or_none()

    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Contractor profile not found",
        )

    # Create new access token
    access_token = create_access_token(
        data={"sub": user.id, "contractor_id": contractor.id},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user_id=user.id,
        contractor_id=contractor.id,
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.post("/logout")
async def logout(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout the current user by revoking all their refresh tokens.

    SEC-003: This effectively invalidates all sessions for the user,
    ensuring they must re-authenticate to get new tokens.
    """
    revoked_count = await revoke_all_user_tokens(db, user["id"], reason="logout")

    return {
        "message": "Successfully logged out",
        "sessions_revoked": revoked_count,
    }
