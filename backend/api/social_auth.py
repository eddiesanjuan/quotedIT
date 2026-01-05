"""
Social Authentication API endpoints for Quoted.
DISC-134: Google/Apple Sign-In for reduced signup friction.

Handles OAuth flows for:
- Google Sign-In (One Tap and redirect flow)
- Apple Sign-In (future)
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..services.logging import get_auth_logger
from ..services.rate_limiting import ip_limiter, RateLimits
from ..services.auth import (
    Token,
    get_db,
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    get_user_by_email,
    hash_password,
)
from ..services.email import email_service
from ..services.analytics import analytics_service
from ..models.database import User, Contractor, PricingModel, ContractorTerms, generate_uuid
from ..config import settings

logger = get_auth_logger()

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    """Request body for Google Sign-In."""
    credential: str  # Google ID token (JWT)
    referral_code: Optional[str] = None  # Optional referral code


class GoogleAuthResponse(Token):
    """Response for Google Sign-In, extends Token."""
    is_new_user: bool = False  # True if this was a new account creation


async def verify_google_token(credential: str) -> dict:
    """
    Verify Google ID token and extract user info.

    Uses Google's public keys to verify the JWT signature.
    Returns the decoded payload with user info.

    Raises HTTPException if token is invalid.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.google_oauth_client_id,
        )

        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid issuer')

        return {
            'email': idinfo['email'],
            'email_verified': idinfo.get('email_verified', False),
            'name': idinfo.get('name', ''),
            'given_name': idinfo.get('given_name', ''),
            'family_name': idinfo.get('family_name', ''),
            'picture': idinfo.get('picture', ''),
            'sub': idinfo['sub'],  # Google user ID
        }

    except ImportError:
        # google-auth library not installed, use manual verification
        logger.warning("google-auth not installed, using manual JWT verification")
        return await verify_google_token_manual(credential)
    except ValueError as e:
        logger.warning(f"Invalid Google token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google authentication token",
        )


async def verify_google_token_manual(credential: str) -> dict:
    """
    Manual verification of Google ID token when google-auth library is not available.

    Fetches Google's public keys and verifies the JWT signature manually.
    This is a fallback for environments where google-auth is not installed.
    """
    import httpx
    from jose import jwt, JWTError

    # Google's public key endpoint
    GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

    try:
        # Fetch Google's public keys
        async with httpx.AsyncClient() as client:
            response = await client.get(GOOGLE_CERTS_URL)
            response.raise_for_status()
            keys = response.json()

        # Decode the token header to get the key ID
        unverified_header = jwt.get_unverified_header(credential)
        kid = unverified_header.get('kid')

        # Find the matching key
        key = None
        for k in keys.get('keys', []):
            if k.get('kid') == kid:
                key = k
                break

        if not key:
            raise ValueError("Unable to find matching key")

        # Verify and decode the token
        payload = jwt.decode(
            credential,
            key,
            algorithms=['RS256'],
            audience=settings.google_oauth_client_id,
            issuer=['accounts.google.com', 'https://accounts.google.com'],
        )

        return {
            'email': payload['email'],
            'email_verified': payload.get('email_verified', False),
            'name': payload.get('name', ''),
            'given_name': payload.get('given_name', ''),
            'family_name': payload.get('family_name', ''),
            'picture': payload.get('picture', ''),
            'sub': payload['sub'],
        }

    except (JWTError, httpx.HTTPError, KeyError) as e:
        logger.warning(f"Manual Google token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google authentication token",
        )


@router.post("/google", response_model=GoogleAuthResponse)
@ip_limiter.limit(RateLimits.AUTH_LOGIN)
async def google_auth(
    request: Request,
    response: Response,
    auth_request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Google Sign-In.

    Flow:
    1. Verify Google ID token with Google's servers
    2. Extract email, name from token
    3. Find existing user OR create new user
    4. Return JWT tokens for our app

    Success Metric: 30%+ of new signups use social login within 30 days
    """
    # Verify Google token and get user info
    google_user = await verify_google_token(auth_request.credential)

    if not google_user.get('email_verified', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google email is not verified",
        )

    email = google_user['email'].lower()
    is_new_user = False

    # Check if user exists
    user = await get_user_by_email(db, email)

    if user:
        # Existing user - log them in
        logger.info(f"Google login for existing user: {email}")

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

        # Track login event
        try:
            analytics_service.track_event(
                user_id=str(user.id),
                event_name="google_login_completed",
                properties={
                    "email": email,
                    "auth_provider": "google",
                }
            )
        except Exception as e:
            logger.warning(f"Failed to track Google login event: {e}")

    else:
        # New user - create account
        is_new_user = True
        logger.info(f"Creating new user via Google Sign-In: {email}")

        # Use Google name or default
        owner_name = google_user.get('name', '') or google_user.get('given_name', '')
        business_name = f"{owner_name}'s Business" if owner_name else "My Business"

        # Generate unique referral code
        from ..services.referral import ReferralService
        referral_code = await ReferralService.ensure_unique_referral_code(db, email)

        # Create user (no password for social auth - use random secure hash)
        import secrets
        random_password = secrets.token_urlsafe(32)

        from ..utils.email import normalize_email
        normalized = normalize_email(email)

        user = User(
            id=generate_uuid(),
            email=email,
            normalized_email=normalized,
            hashed_password=hash_password(random_password),  # Random, user uses Google to login
            is_active=True,
            is_verified=True,  # Google verified the email
            referral_code=referral_code,
        )
        db.add(user)

        # Create contractor profile
        contractor = Contractor(
            id=generate_uuid(),
            user_id=user.id,
            email=email,
            business_name=business_name,
            owner_name=owner_name,
            is_active=True,
            primary_trade="general",
        )
        db.add(contractor)

        # Create default pricing model
        pricing_model = PricingModel(
            id=generate_uuid(),
            contractor_id=contractor.id,
            labor_rate_hourly=65.0,
            helper_rate_hourly=35.0,
            material_markup_percent=20.0,
            minimum_job_amount=500.0,
            pricing_knowledge={},
            pricing_notes=None,
        )
        db.add(pricing_model)

        # Create default terms
        terms = ContractorTerms(
            id=generate_uuid(),
            contractor_id=contractor.id,
            deposit_percent=50.0,
            quote_valid_days=30,
            labor_warranty_years=2,
            accepted_payment_methods=["Check", "Credit Card", "Cash"],
        )
        db.add(terms)

        await db.commit()
        await db.refresh(user)
        await db.refresh(contractor)

        # Initialize trial period
        from ..services.billing import BillingService
        await BillingService.initialize_trial(db, user.id)

        # Apply referral code if provided
        if auth_request.referral_code:
            try:
                await ReferralService.apply_referral_code(db, user, auth_request.referral_code)
            except HTTPException as e:
                logger.warning(f"Failed to apply referral code: {e.detail}")

        # Send welcome email (don't block)
        try:
            await email_service.send_welcome_email(
                to_email=user.email,
                business_name=contractor.business_name,
                owner_name=contractor.owner_name,
            )
        except Exception as e:
            logger.warning(f"Failed to send welcome email to {email}: {e}")

        # Send founder notification (don't block)
        try:
            await email_service.send_founder_signup_notification(
                user_email=user.email,
                business_name=contractor.business_name,
                owner_name=contractor.owner_name,
                primary_trade=contractor.primary_trade,
                referral_code=user.referral_code,
                used_referral=user.referred_by_code,
            )
        except Exception as e:
            logger.warning(f"Failed to send founder notification: {e}")

        # Track signup event
        try:
            analytics_service.identify_user(
                user_id=str(user.id),
                properties={
                    "email": user.email,
                    "business_name": contractor.business_name,
                    "owner_name": contractor.owner_name,
                    "primary_trade": contractor.primary_trade,
                    "signup_provider": "google",
                }
            )
            analytics_service.track_event(
                user_id=str(user.id),
                event_name="google_signup_completed",
                properties={
                    "business_name": contractor.business_name,
                    "primary_trade": contractor.primary_trade,
                    "referral_code": user.referral_code,
                    "used_referral": bool(user.referred_by_code),
                    "auth_provider": "google",
                }
            )
        except Exception as e:
            logger.warning(f"Failed to track Google signup event: {e}")

    # Create access token (15 minutes)
    access_token = create_access_token(
        data={"sub": user.id, "contractor_id": contractor.id},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )

    # Create and store refresh token (7 days)
    refresh_token_value, jti = create_refresh_token()
    await store_refresh_token(
        db=db,
        user_id=user.id,
        token_value=refresh_token_value,
        jti=jti,
    )

    return GoogleAuthResponse(
        access_token=access_token,
        refresh_token=refresh_token_value,
        user_id=user.id,
        contractor_id=contractor.id,
        expires_in=settings.jwt_expire_minutes * 60,
        is_new_user=is_new_user,
    )


# Future: Apple Sign-In endpoint
# @router.post("/apple", response_model=GoogleAuthResponse)
# async def apple_auth(...)
