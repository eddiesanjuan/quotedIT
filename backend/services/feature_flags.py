"""
Feature Flag Service for Quoted (DISC-078)

Provides server-side feature flag checks using PostHog.
For gradual rollouts and instant rollback capability.

Standard Flag Names:
  - invoicing_enabled: DISC-071 quote-to-invoice
  - new_pdf_templates: DISC-072 PDF polish
  - voice_template_customization: DISC-070 voice PDF

Usage:
    from backend.services.feature_flags import is_feature_enabled

    if is_feature_enabled("invoicing_enabled", user_id=contractor_id):
        # Show invoicing feature
        pass
"""

import logging
from typing import Optional

from backend.config import settings

logger = logging.getLogger(__name__)

# PostHog client - lazily initialized
_posthog_client = None


def _get_posthog():
    """Get or initialize PostHog client."""
    global _posthog_client

    if _posthog_client is not None:
        return _posthog_client

    if not settings.posthog_api_key:
        logger.debug("PostHog API key not configured - feature flags will use defaults")
        return None

    try:
        import posthog
        posthog.project_api_key = settings.posthog_api_key
        posthog.host = "https://us.i.posthog.com"
        _posthog_client = posthog
        logger.info("PostHog feature flags initialized")
        return posthog
    except ImportError:
        logger.warning("PostHog package not installed - feature flags will use defaults")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize PostHog: {e}")
        return None


def is_feature_enabled(
    flag_key: str,
    user_id: Optional[str] = None,
    default: bool = False
) -> bool:
    """
    Check if a feature flag is enabled for a user.

    Args:
        flag_key: The feature flag key (e.g., 'invoicing_enabled')
        user_id: The user ID for targeted rollouts. If None, uses 'anonymous'.
        default: Value to return if PostHog unavailable or flag not found.

    Returns:
        True if the feature is enabled, False otherwise.

    Example:
        # Check if invoicing is enabled for this contractor
        if is_feature_enabled("invoicing_enabled", user_id=contractor.id):
            return {"invoicing_available": True}
    """
    posthog = _get_posthog()

    if posthog is None:
        return default

    try:
        distinct_id = str(user_id) if user_id else "anonymous"
        result = posthog.feature_enabled(flag_key, distinct_id)

        # Log for debugging (only in development)
        if settings.environment != "production":
            logger.debug(f"Feature flag '{flag_key}' for user '{distinct_id}': {result}")

        return result if result is not None else default
    except Exception as e:
        logger.warning(f"Feature flag check failed for '{flag_key}': {e}")
        return default


def get_feature_flag_payload(
    flag_key: str,
    user_id: Optional[str] = None,
    default: any = None
) -> any:
    """
    Get the payload associated with a feature flag.

    Useful for A/B tests where flags carry configuration data.

    Args:
        flag_key: The feature flag key
        user_id: The user ID for targeted payloads
        default: Value to return if no payload exists

    Returns:
        The flag payload, or default if not found.
    """
    posthog = _get_posthog()

    if posthog is None:
        return default

    try:
        distinct_id = str(user_id) if user_id else "anonymous"
        payload = posthog.get_feature_flag_payload(flag_key, distinct_id)
        return payload if payload is not None else default
    except Exception as e:
        logger.warning(f"Feature flag payload fetch failed for '{flag_key}': {e}")
        return default


# Convenience functions for common flags

def is_invoicing_enabled(user_id: Optional[str] = None) -> bool:
    """Check if quote-to-invoice feature is enabled (DISC-071)."""
    return is_feature_enabled("invoicing_enabled", user_id, default=False)


def is_new_pdf_templates_enabled(user_id: Optional[str] = None) -> bool:
    """Check if new PDF templates are enabled (DISC-072)."""
    return is_feature_enabled("new_pdf_templates", user_id, default=False)


def is_voice_template_customization_enabled(user_id: Optional[str] = None) -> bool:
    """Check if voice-driven PDF customization is enabled (DISC-070)."""
    return is_feature_enabled("voice_template_customization", user_id, default=False)
