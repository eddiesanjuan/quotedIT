"""
Enhanced Rate Limiting Service for Quoted (SEC-004).

Provides tiered rate limiting with:
- IP-based limiting for unauthenticated requests
- User-based limiting for authenticated requests
- Separate limits for different endpoint categories
- Custom error responses with retry-after headers
"""

import logging
from typing import Optional, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger("quoted.rate_limiting")


# =============================================================================
# Rate Limit Tiers (requests per period)
# =============================================================================

class RateLimits:
    """Centralized rate limit definitions."""

    # Authentication - strict limits to prevent brute force
    AUTH_LOGIN = "5/minute"
    AUTH_REGISTER = "3/minute"
    AUTH_PASSWORD_RESET = "3/minute"

    # Quote operations - moderate limits
    QUOTE_CREATE = "30/minute"  # Creating new quotes
    QUOTE_READ = "60/minute"  # Reading quotes
    QUOTE_UPDATE = "30/minute"  # Updating quotes
    QUOTE_SHARE = "10/minute"  # Sharing quotes

    # Demo - strict limits for unauthenticated users
    DEMO_QUOTE = "5/hour"  # Demo quote generation
    DEMO_PREVIEW = "10/hour"  # Demo PDF previews

    # API operations - generous for authenticated users
    API_READ = "120/minute"  # General read operations
    API_WRITE = "60/minute"  # General write operations

    # Billing - moderate limits
    BILLING_READ = "30/minute"
    BILLING_WRITE = "10/minute"

    # Heavy operations - strict limits
    PDF_GENERATE = "20/minute"
    TRANSCRIPTION = "30/minute"


def get_user_id_or_ip(request: Request) -> str:
    """
    Get rate limit key - user ID for authenticated requests, IP for others.

    This provides per-user rate limiting for logged-in users while still
    protecting against IP-based abuse from unauthenticated users.
    """
    # Check for user info in request state (set by auth middleware)
    if hasattr(request.state, "user") and request.state.user:
        user_id = request.state.user.get("id")
        if user_id:
            return f"user:{user_id}"

    # Fall back to IP address
    return get_remote_address(request)


def get_contractor_or_ip(request: Request) -> str:
    """
    Get rate limit key - contractor ID for authenticated requests, IP for others.

    Uses contractor ID for business-specific rate limiting.
    """
    if hasattr(request.state, "contractor") and request.state.contractor:
        contractor_id = request.state.contractor.get("id")
        if contractor_id:
            return f"contractor:{contractor_id}"

    return get_remote_address(request)


# =============================================================================
# Custom Rate Limit Exceeded Handler
# =============================================================================

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.

    Returns a JSON response with:
    - Clear error message
    - Rate limit details
    - Retry-After header
    """
    # Parse the rate limit info from the exception
    limit = str(exc.detail) if exc.detail else "Rate limit exceeded"

    # Try to extract retry-after from the exception or headers
    retry_after = 60  # Default to 60 seconds

    # Log the rate limit hit
    client_ip = get_remote_address(request)
    endpoint = request.url.path
    logger.warning(
        f"Rate limit exceeded",
        extra={
            "client_ip": client_ip,
            "endpoint": endpoint,
            "limit": limit,
        }
    )

    response = JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down.",
            "detail": limit,
            "retry_after": retry_after,
        },
    )

    # Add standard rate limit headers
    response.headers["Retry-After"] = str(retry_after)
    response.headers["X-RateLimit-Limit"] = limit
    response.headers["X-RateLimit-Remaining"] = "0"

    return response


# =============================================================================
# Limiter Instance Configuration
# =============================================================================

def create_limiter(
    key_func: Callable = get_remote_address,
    default_limits: list = None,
) -> Limiter:
    """
    Create a configured limiter instance.

    Args:
        key_func: Function to extract rate limit key from request
        default_limits: Default rate limits applied to all endpoints
    """
    return Limiter(
        key_func=key_func,
        default_limits=default_limits or [],
        headers_enabled=True,  # Add rate limit headers to responses
        retry_after="http-date",  # Use HTTP-date format for Retry-After
    )


# Pre-configured limiters for different use cases
ip_limiter = create_limiter(key_func=get_remote_address)
user_limiter = create_limiter(key_func=get_user_id_or_ip)
contractor_limiter = create_limiter(key_func=get_contractor_or_ip)


# =============================================================================
# Rate Limiting Middleware Helpers
# =============================================================================

def add_rate_limit_headers(response: Response, limit: str, remaining: int, reset: int):
    """Add rate limit headers to a response."""
    response.headers["X-RateLimit-Limit"] = limit
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset)
    return response
