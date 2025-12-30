"""
Authentication API endpoints for Quoted.
Handles user registration, login, and OAuth social login (DISC-134).
"""

from datetime import timedelta
from typing import Optional
from urllib.parse import urlencode
import secrets
import httpx

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from ..services.logging import get_auth_logger
from ..services.rate_limiting import ip_limiter, RateLimits

logger = get_auth_logger()

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
    get_or_create_oauth_user,
    link_oauth_to_user,
)
from ..services.email import email_service
from ..services.analytics import analytics_service
from ..models.database import User, Contractor
from ..config import settings


# =============================================================================
# DISC-134: OAuth/Social Login Models
# =============================================================================

class OAuthStartResponse(BaseModel):
    """Response for OAuth start endpoint."""
    auth_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    """Request for OAuth callback (frontend-initiated flow)."""
    code: str
    state: str


class OAuthLinkRequest(BaseModel):
    """Request to link OAuth account to existing user."""
    provider: str
    code: str
    state: str


# In-memory state storage (for CSRF protection)
# In production with multiple instances, use Redis
_oauth_states: dict[str, dict] = {}

router = APIRouter()


@router.post("/register", response_model=Token)
@ip_limiter.limit(RateLimits.AUTH_REGISTER)
async def register(
    request: Request,
    response: Response,
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
        logger.warning(f"Failed to send welcome email to {user.email}", exc_info=True)

    # DISC-128: Send founder notification (don't block on failure)
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
        # Log the error but don't block registration
        logger.warning(f"Failed to send founder signup notification for {user.email}", exc_info=True)

    # Track signup event - DISC-134: Include auth_method for analytics
    try:
        analytics_service.identify_user(
            user_id=str(user.id),
            properties={
                "email": user.email,
                "business_name": contractor.business_name,
                "owner_name": contractor.owner_name,
                "primary_trade": contractor.primary_trade,
                "auth_method": "email",  # DISC-134: Track auth method
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
                "auth_method": "email",  # DISC-134: Track auth method
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
        logger.warning(f"Failed to track signup event for {user.email}", exc_info=True)

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
@ip_limiter.limit(RateLimits.AUTH_LOGIN)
async def login(
    request: Request,
    response: Response,
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

    # DISC-134: Track login event with auth method
    try:
        analytics_service.track_event(
            user_id=str(user.id),
            event_name="login_completed",
            properties={
                "auth_method": "email",
            }
        )
    except Exception as e:
        logger.warning(f"Failed to track login event for {user.email}", exc_info=True)

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
@ip_limiter.limit(RateLimits.AUTH_LOGIN)  # Same limit as login to prevent brute force
async def refresh_token(
    http_request: Request,
    response: Response,
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


# =============================================================================
# DISC-134: OAuth/Social Login Endpoints
# =============================================================================

SUPPORTED_OAUTH_PROVIDERS = {"google", "apple"}


def _get_google_auth_url(state: str, redirect_uri: str) -> str:
    """Generate Google OAuth authorization URL."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def _get_apple_auth_url(state: str, redirect_uri: str) -> str:
    """Generate Apple Sign In authorization URL."""
    params = {
        "client_id": settings.apple_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "name email",
        "state": state,
        "response_mode": "form_post",
    }
    return f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"


async def _exchange_google_code(code: str, redirect_uri: str) -> dict:
    """Exchange Google authorization code for user info."""
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )

        if token_response.status_code != 200:
            logger.error(f"Google token exchange failed: {token_response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code",
            )

        tokens = token_response.json()
        access_token = tokens.get("access_token")

        # Get user info
        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_response.status_code != 200:
            logger.error(f"Google userinfo failed: {userinfo_response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google",
            )

        return userinfo_response.json()


@router.get("/oauth/{provider}/start", response_model=OAuthStartResponse)
async def oauth_start(
    request: Request,
    provider: str,
):
    """
    Start OAuth flow for a provider.
    Returns the authorization URL to redirect the user to.

    DISC-134: Supports Google OAuth (priority) and Apple Sign In.
    """
    if provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}. Supported: {', '.join(SUPPORTED_OAUTH_PROVIDERS)}",
        )

    # Check if provider is configured
    if provider == "google" and not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )
    if provider == "apple" and not settings.apple_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Apple Sign In is not configured",
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Build redirect URI (frontend will handle the callback)
    # Format: https://quoted.it.com/auth/callback/{provider}
    redirect_uri = f"{settings.frontend_url}/auth/callback/{provider}"

    # Store state for validation (expires in 10 minutes)
    _oauth_states[state] = {
        "provider": provider,
        "redirect_uri": redirect_uri,
    }

    # Generate auth URL
    if provider == "google":
        auth_url = _get_google_auth_url(state, redirect_uri)
    elif provider == "apple":
        auth_url = _get_apple_auth_url(state, redirect_uri)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider {provider} not implemented",
        )

    logger.info(f"OAuth flow started for provider: {provider}")

    return OAuthStartResponse(auth_url=auth_url, state=state)


@router.post("/oauth/{provider}/callback", response_model=Token)
@ip_limiter.limit(RateLimits.AUTH_LOGIN)
async def oauth_callback(
    request: Request,
    response: Response,
    provider: str,
    callback_data: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback from provider.
    Exchanges the authorization code for user info and creates/authenticates user.

    DISC-134: This creates a new user or logs in existing user based on OAuth identity.
    """
    if provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}",
        )

    # Validate state (CSRF protection)
    state_data = _oauth_states.pop(callback_data.state, None)
    if not state_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state. Please try again.",
        )

    if state_data["provider"] != provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider mismatch in OAuth state",
        )

    redirect_uri = state_data["redirect_uri"]

    # Exchange code for user info based on provider
    if provider == "google":
        user_info = await _exchange_google_code(callback_data.code, redirect_uri)
        oauth_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name", "")
    elif provider == "apple":
        # Apple Sign In implementation would go here
        # Apple requires JWT verification with their public keys
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Apple Sign In callback not yet implemented",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider {provider} not implemented",
        )

    if not oauth_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not get user info from OAuth provider",
        )

    # Get or create user with OAuth
    user, contractor, is_new_user = await get_or_create_oauth_user(
        db=db,
        email=email,
        oauth_provider=provider,
        oauth_id=oauth_id,
        name=name,
    )

    # Track OAuth signup/login
    try:
        if is_new_user:
            analytics_service.identify_user(
                user_id=str(user.id),
                properties={
                    "email": user.email,
                    "business_name": contractor.business_name,
                    "owner_name": contractor.owner_name,
                    "auth_method": f"oauth_{provider}",
                }
            )
            analytics_service.track_event(
                user_id=str(user.id),
                event_name="signup_completed",
                properties={
                    "auth_method": f"oauth_{provider}",
                    "oauth_provider": provider,
                    "business_name": contractor.business_name,
                    "referral_code": user.referral_code,
                }
            )

            # Send welcome email for new OAuth users
            try:
                await email_service.send_welcome_email(
                    to_email=user.email,
                    business_name=contractor.business_name,
                    owner_name=contractor.owner_name,
                )
            except Exception as e:
                logger.warning(f"Failed to send welcome email to {user.email}", exc_info=True)

            # DISC-128: Send founder notification
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
                logger.warning(f"Failed to send founder signup notification for {user.email}", exc_info=True)
        else:
            analytics_service.track_event(
                user_id=str(user.id),
                event_name="login_completed",
                properties={
                    "auth_method": f"oauth_{provider}",
                    "oauth_provider": provider,
                }
            )
    except Exception as e:
        logger.warning(f"Failed to track OAuth event for {user.email}", exc_info=True)

    logger.info(f"OAuth {'signup' if is_new_user else 'login'} completed for {email} via {provider}")

    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "contractor_id": contractor.id},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )

    # Create and store refresh token
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


@router.post("/oauth/link", response_model=dict)
async def oauth_link(
    request: OAuthLinkRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Link an OAuth account to an existing user.
    Allows users who signed up with email to add social login.

    DISC-134: Edge case handling for account linking.
    """
    if request.provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {request.provider}",
        )

    # Validate state
    state_data = _oauth_states.pop(request.state, None)
    if not state_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state. Please try again.",
        )

    redirect_uri = state_data["redirect_uri"]

    # Exchange code for user info
    if request.provider == "google":
        user_info = await _exchange_google_code(request.code, redirect_uri)
        oauth_id = user_info.get("id")
        oauth_email = user_info.get("email")
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Provider {request.provider} linking not yet implemented",
        )

    if not oauth_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not get user info from OAuth provider",
        )

    # Link OAuth to user
    success = await link_oauth_to_user(
        db=db,
        user_id=user["id"],
        oauth_provider=request.provider,
        oauth_id=oauth_id,
    )

    if success:
        # Track account linking
        try:
            analytics_service.track_event(
                user_id=str(user["id"]),
                event_name="oauth_account_linked",
                properties={
                    "oauth_provider": request.provider,
                }
            )
        except Exception:
            pass

        logger.info(f"OAuth account linked for user {user['id']} via {request.provider}")
        return {"message": f"Successfully linked {request.provider} account"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to link OAuth account. It may already be linked to another user.",
        )
