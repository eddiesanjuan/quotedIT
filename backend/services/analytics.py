"""
PostHog Analytics Service for Quoted.

Tracks user events for product analytics.
Gracefully handles missing API key (logs warning but doesn't crash).
"""

import os
from typing import Optional, Dict, Any
import logging

# Configure logger
logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    PostHog analytics tracking service.

    Tracks user events for product analytics. If PostHog API key is not configured,
    logs events to console but doesn't fail.
    """

    def __init__(self):
        """Initialize PostHog client if API key is available."""
        self.enabled = False
        self.client = None

        api_key = os.getenv("POSTHOG_API_KEY")

        if not api_key:
            logger.warning(
                "PostHog API key not configured (POSTHOG_API_KEY). "
                "Analytics will be logged but not sent to PostHog."
            )
            return

        try:
            import posthog
            posthog.api_key = api_key
            posthog.host = "https://us.i.posthog.com"  # US region
            self.client = posthog
            self.enabled = True
            logger.info("PostHog analytics initialized successfully")
        except ImportError:
            logger.warning(
                "PostHog library not installed. "
                "Run: pip install posthog. "
                "Analytics will be logged but not sent."
            )
        except Exception as e:
            logger.error(f"Failed to initialize PostHog: {e}")

    def track_event(
        self,
        user_id: str,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track an analytics event.

        Args:
            user_id: Unique user identifier
            event_name: Name of the event (e.g., "signup_completed")
            properties: Optional dictionary of event properties
        """
        if properties is None:
            properties = {}

        # Always log the event
        logger.info(
            f"Analytics event: {event_name} | User: {user_id} | Props: {properties}"
        )

        # Send to PostHog if enabled
        if self.enabled and self.client:
            try:
                self.client.capture(
                    distinct_id=user_id,
                    event=event_name,
                    properties=properties
                )
            except Exception as e:
                logger.error(f"Failed to send event to PostHog: {e}")

    def identify_user(
        self,
        user_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Identify a user and set properties.

        Args:
            user_id: Unique user identifier
            properties: User properties (email, business_name, etc.)
        """
        if properties is None:
            properties = {}

        logger.info(f"Analytics identify: User {user_id} | Props: {properties}")

        if self.enabled and self.client:
            try:
                self.client.identify(
                    distinct_id=user_id,
                    properties=properties
                )
            except Exception as e:
                logger.error(f"Failed to identify user in PostHog: {e}")


# Global singleton instance
analytics_service = AnalyticsService()
