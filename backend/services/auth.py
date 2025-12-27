"""
Authentication service for Quoted.
Handles user registration, login, and JWT token management.

SEC-003: Implements short-lived access tokens (15 min) + refresh tokens (7 days)
for improved security while maintaining good UX.
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.database import User, Contractor, PricingModel, ContractorTerms, RefreshToken, Base, generate_uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token
security = HTTPBearer()


# Pydantic models for auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    business_name: str
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    referral_code: Optional[str] = None  # Optional referral code to apply during signup


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str  # SEC-003: Add refresh token to response
    token_type: str = "bearer"
    user_id: str
    contractor_id: str
    expires_in: int = 900  # Access token expiry in seconds (15 min)


class RefreshTokenRequest(BaseModel):
    """Request body for token refresh endpoint."""
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    is_verified: bool
    contractor_id: Optional[str] = None
    business_name: Optional[str] = None
    primary_trade: Optional[str] = None  # For onboarding industry check
    onboarding_completed_at: Optional[str] = None  # ISO datetime string for onboarding check


# Database session
_engine = None
_async_session_maker = None


async def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.async_database_url)
    return _engine


async def get_db() -> AsyncSession:
    global _async_session_maker
    if _async_session_maker is None:
        engine = await get_engine()
        _async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with _async_session_maker() as session:
        yield session


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


# SEC-003: Refresh Token Management Functions

def create_refresh_token() -> tuple[str, str]:
    """
    Create a new refresh token.
    Returns (token_value, jti) where:
    - token_value: The actual token to send to client (64 bytes, URL-safe)
    - jti: The JWT ID for tracking/revocation
    """
    token_value = secrets.token_urlsafe(64)
    jti = generate_uuid()
    return token_value, jti


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token for secure storage."""
    return pwd_context.hash(token)


def verify_refresh_token(plain_token: str, hashed_token: str) -> bool:
    """Verify a refresh token against its hash."""
    return pwd_context.verify(plain_token, hashed_token)


async def store_refresh_token(
    db: AsyncSession,
    user_id: str,
    token_value: str,
    jti: str,
    family_id: Optional[str] = None,
    device_info: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> RefreshToken:
    """
    Store a new refresh token in the database.

    Args:
        db: Database session
        user_id: User ID this token belongs to
        token_value: The actual token value (will be hashed)
        jti: JWT ID for this token
        family_id: Token family ID for rotation tracking
        device_info: Optional device/browser info
        ip_address: Optional client IP address
    """
    expires_at = datetime.utcnow() + timedelta(days=settings.jwt_refresh_expire_days)

    refresh_token = RefreshToken(
        id=generate_uuid(),
        user_id=user_id,
        jti=jti,
        token_hash=hash_refresh_token(token_value),
        family_id=family_id or generate_uuid(),
        expires_at=expires_at,
        device_info=device_info,
        ip_address=ip_address,
    )
    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)
    return refresh_token


async def validate_and_rotate_refresh_token(
    db: AsyncSession,
    token_value: str,
    device_info: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> tuple[User, str, str]:
    """
    Validate a refresh token and rotate it (issue new one, revoke old).

    This implements token rotation for security:
    - Each refresh token can only be used once
    - If an old token is reused, the entire token family is revoked (potential theft)

    Args:
        db: Database session
        token_value: The refresh token from client
        device_info: Optional device/browser info
        ip_address: Optional client IP address

    Returns:
        (user, new_token_value, new_jti) tuple

    Raises:
        HTTPException: If token is invalid, expired, or revoked
    """
    # Find all non-expired tokens for iteration
    # We need to check each one since we can't query by token value directly (it's hashed)
    result = await db.execute(
        select(RefreshToken).where(
            and_(
                RefreshToken.expires_at > datetime.utcnow(),
            )
        ).order_by(RefreshToken.created_at.desc())
    )
    tokens = result.scalars().all()

    # Find the matching token
    matching_token = None
    for token in tokens:
        if verify_refresh_token(token_value, token.token_hash):
            matching_token = token
            break

    if not matching_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token is revoked
    if matching_token.revoked:
        # Token was already used - potential theft! Revoke entire family
        await revoke_token_family(db, matching_token.family_id, "security")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get the user
    user = await get_user_by_id(db, matching_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Revoke the old token (rotation)
    matching_token.revoked = True
    matching_token.revoked_at = datetime.utcnow()
    matching_token.revoked_reason = "token_rotation"

    # Create new token in the same family
    new_token_value, new_jti = create_refresh_token()
    await store_refresh_token(
        db=db,
        user_id=user.id,
        token_value=new_token_value,
        jti=new_jti,
        family_id=matching_token.family_id,  # Same family
        device_info=device_info,
        ip_address=ip_address,
    )

    return user, new_token_value, new_jti


async def revoke_token_family(db: AsyncSession, family_id: str, reason: str = "logout"):
    """
    Revoke all tokens in a token family.
    Used on logout or when suspicious activity is detected.
    """
    result = await db.execute(
        select(RefreshToken).where(
            and_(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked == False,
            )
        )
    )
    tokens = result.scalars().all()

    for token in tokens:
        token.revoked = True
        token.revoked_at = datetime.utcnow()
        token.revoked_reason = reason

    await db.commit()


async def revoke_all_user_tokens(db: AsyncSession, user_id: str, reason: str = "logout"):
    """
    Revoke all refresh tokens for a user.
    Used for "logout everywhere" functionality.
    """
    result = await db.execute(
        select(RefreshToken).where(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
            )
        )
    )
    tokens = result.scalars().all()

    for token in tokens:
        token.revoked = True
        token.revoked_at = datetime.utcnow()
        token.revoked_reason = reason

    await db.commit()
    return len(tokens)


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    """
    Delete expired refresh tokens from database.
    Should be run periodically (e.g., daily cron job).
    """
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow())
    )
    expired_tokens = result.scalars().all()

    count = len(expired_tokens)
    for token in expired_tokens:
        await db.delete(token)

    await db.commit()
    return count


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, user_data: UserCreate) -> tuple[User, Contractor]:
    """
    Register a new user and create their contractor profile.
    Also creates default pricing model and terms so they can start quoting immediately.
    Generates referral code and applies referral if provided.

    Trial abuse prevention (DISC-017):
    - Blocks disposable email domains
    - Normalizes email to detect duplicate accounts (Gmail dot/plus aliases)

    Returns (user, contractor) tuple.
    """
    from ..utils.email import normalize_email, validate_email_for_registration

    # Validate email (block disposable domains) - DISC-017
    is_valid, error_message = validate_email_for_registration(user_data.email)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Normalize email for duplicate detection - DISC-017
    normalized = normalize_email(user_data.email)

    # Check if email already exists (original)
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Check if normalized email already exists (prevents Gmail aliases) - DISC-017
    result = await db.execute(
        select(User).where(User.normalized_email == normalized)
    )
    existing_normalized = result.scalar_one_or_none()
    if existing_normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Generate unique referral code for this user
    from .referral import ReferralService
    referral_code = await ReferralService.ensure_unique_referral_code(db, user_data.email)

    # Create user
    user = User(
        id=generate_uuid(),
        email=user_data.email,
        normalized_email=normalized,  # DISC-017: Store normalized email for duplicate detection
        hashed_password=hash_password(user_data.password),
        is_active=True,
        is_verified=False,  # Could add email verification later
        referral_code=referral_code,  # Assign generated referral code
    )
    db.add(user)

    # Create contractor profile linked to user
    contractor = Contractor(
        id=generate_uuid(),
        user_id=user.id,
        email=user_data.email,
        business_name=user_data.business_name,
        owner_name=user_data.owner_name,
        phone=user_data.phone,
        is_active=True,
        primary_trade="general",  # Default, can be updated later
    )
    db.add(contractor)

    # Create default pricing model so user can start quoting immediately
    # These are sensible defaults that the AI will learn from and adjust
    pricing_model = PricingModel(
        id=generate_uuid(),
        contractor_id=contractor.id,
        labor_rate_hourly=65.0,  # Industry average
        helper_rate_hourly=35.0,
        material_markup_percent=20.0,
        minimum_job_amount=500.0,
        pricing_knowledge={},  # Starts empty, builds from corrections
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

    # Initialize trial period for new user
    from .billing import BillingService
    await BillingService.initialize_trial(db, user.id)

    # Apply referral code if provided (extends trial to 14 days)
    if user_data.referral_code:
        try:
            await ReferralService.apply_referral_code(db, user, user_data.referral_code)
        except HTTPException as e:
            # Log but don't block registration if referral code is invalid
            print(f"Warning: Failed to apply referral code {user_data.referral_code}: {e.detail}")

    return user, contractor


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Dependency to get the current authenticated user from JWT token.
    Use this to protect endpoints.
    Returns a dict with user info for easy access in endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Also fetch contractor_id for endpoints that need it (P0-05 fix)
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == user.id)
    )
    contractor = result.scalar_one_or_none()
    contractor_id = str(contractor.id) if contractor else None

    # Return as dict for easier access in endpoints
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "contractor_id": contractor_id,  # P0-05: Include for follow-up and other endpoints
    }


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> Optional[dict]:
    """
    Optional version of get_current_user.
    Returns None if no valid token, instead of raising an exception.
    Use this for endpoints that work for both authenticated and anonymous users.
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id: str = payload.get("sub")
    if user_id is None:
        return None

    user = await get_user_by_id(db, user_id)
    if user is None:
        return None

    if not user.is_active:
        return None

    # Also fetch contractor_id for consistency with get_current_user (P0-05 fix)
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == user.id)
    )
    contractor = result.scalar_one_or_none()
    contractor_id = str(contractor.id) if contractor else None

    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "contractor_id": contractor_id,
    }


async def get_current_contractor(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Contractor:
    """
    Dependency to get the current user's contractor profile.
    Use this for contractor-specific endpoints.
    """
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == current_user["id"])
    )
    contractor = result.scalar_one_or_none()

    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )

    return contractor
