"""
Funnel Analytics Service (DISC-138).

Provides conversion funnel visibility for Google Ads campaigns:
- Landing page → Try page → Demo generation → Signup
- Uses PostHog API when available, falls back to database metrics
- Segments by UTM source, device, time period

Cost: $0 additional (uses existing PostHog)
"""

import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .logging import get_logger
from ..config import settings

logger = get_logger("quoted.funnel_analytics")


@dataclass
class FunnelStep:
    """Single step in the conversion funnel."""
    name: str
    event_name: str
    count: int = 0
    conversion_rate: float = 0.0  # Rate from previous step


@dataclass
class FunnelData:
    """Complete funnel data for a time period."""
    period_start: datetime
    period_end: datetime
    steps: List[FunnelStep] = field(default_factory=list)

    @property
    def overall_conversion_rate(self) -> float:
        """Calculate end-to-end conversion rate."""
        if not self.steps or self.steps[0].count == 0:
            return 0.0
        return (self.steps[-1].count / self.steps[0].count) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "overall_conversion_rate": round(self.overall_conversion_rate, 2),
            "steps": [
                {
                    "name": step.name,
                    "event": step.event_name,
                    "count": step.count,
                    "conversion_rate": round(step.conversion_rate, 2)
                }
                for step in self.steps
            ]
        }


class FunnelAnalyticsService:
    """
    Service for tracking conversion funnel performance.

    Primary: PostHog API (requires POSTHOG_READ_API_KEY)
    Fallback: Database metrics (less granular but always available)
    """

    # Funnel steps in order (event names from frontend tracking)
    FUNNEL_STEPS = [
        ("Landing Page Views", "landing_page_view"),
        ("CTA Clicks", "cta_clicked"),
        ("Try Page Views", "try_page_viewed"),
        ("Demo Input Started", "demo_input_started"),
        ("Demo Quote Generated", "demo_quote_generated"),
        ("Signup Attempts", "start_signup_submitted"),
        ("Signups Complete", "account_created"),
    ]

    @staticmethod
    def _posthog_available() -> bool:
        """Check if PostHog read API is configured."""
        return bool(settings.posthog_read_api_key)

    @staticmethod
    async def _query_posthog(
        event_name: str,
        date_from: str,
        date_to: str,
        filter_property: Optional[str] = None,
        filter_value: Optional[str] = None
    ) -> int:
        """
        Query PostHog API for event count.

        Args:
            event_name: PostHog event name
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            filter_property: Optional property to filter by (e.g., "utm_source")
            filter_value: Value to filter for

        Returns:
            Event count for the period
        """
        if not settings.posthog_read_api_key:
            return 0

        url = "https://app.posthog.com/api/projects/@current/insights/trend/"
        headers = {
            "Authorization": f"Bearer {settings.posthog_read_api_key}",
            "Content-Type": "application/json"
        }

        # Build filters
        properties = []
        if filter_property and filter_value:
            properties.append({
                "key": filter_property,
                "value": filter_value,
                "operator": "exact",
                "type": "event"
            })

        payload = {
            "events": [{"id": event_name, "name": event_name, "type": "events"}],
            "date_from": date_from,
            "date_to": date_to,
            "display": "ActionsLineGraph",
            "properties": properties if properties else None,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    # Sum all data points in the result
                    if "result" in data and data["result"]:
                        return sum(data["result"][0].get("data", []))
                else:
                    logger.warning(f"PostHog API returned {response.status_code}: {response.text}")

        except Exception as e:
            logger.error(f"PostHog API error: {e}")

        return 0

    @staticmethod
    async def get_funnel_data(
        db: AsyncSession,
        days: int = 7,
        utm_source: Optional[str] = None
    ) -> FunnelData:
        """
        Get conversion funnel data for the specified period.

        Args:
            db: Database session (for fallback metrics)
            days: Number of days to analyze
            utm_source: Optional UTM source filter (e.g., "google", "reddit")

        Returns:
            FunnelData with step counts and conversion rates
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        date_from = start_date.strftime("%Y-%m-%d")
        date_to = end_date.strftime("%Y-%m-%d")

        funnel_data = FunnelData(
            period_start=start_date,
            period_end=end_date,
            steps=[]
        )

        if FunnelAnalyticsService._posthog_available():
            # Use PostHog API for full funnel visibility
            logger.info(f"Querying PostHog funnel: {date_from} to {date_to}")

            previous_count = 0
            for step_name, event_name in FunnelAnalyticsService.FUNNEL_STEPS:
                count = await FunnelAnalyticsService._query_posthog(
                    event_name=event_name,
                    date_from=date_from,
                    date_to=date_to,
                    filter_property="utm_source" if utm_source else None,
                    filter_value=utm_source
                )

                # Calculate conversion rate from previous step
                if previous_count > 0:
                    rate = (count / previous_count) * 100
                elif len(funnel_data.steps) == 0:
                    rate = 100.0  # First step is always 100%
                else:
                    rate = 0.0

                funnel_data.steps.append(FunnelStep(
                    name=step_name,
                    event_name=event_name,
                    count=count,
                    conversion_rate=rate
                ))
                previous_count = count
        else:
            # Fallback: Use database for signup metrics only
            logger.info("PostHog API not configured - using database fallback")
            funnel_data.steps = await FunnelAnalyticsService._get_db_funnel(
                db, start_date, end_date
            )

        return funnel_data

    @staticmethod
    async def _get_db_funnel(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> List[FunnelStep]:
        """
        Fallback funnel using database metrics.

        Only has visibility into signups and quotes, not page views.
        """
        from ..models.database import Contractor, Quote

        # Get signup count
        signups_result = await db.execute(
            select(func.count(Contractor.id)).where(
                and_(
                    Contractor.created_at >= start_date,
                    Contractor.created_at < end_date
                )
            )
        )
        signups = signups_result.scalar() or 0

        # Get quote count (as proxy for demo completions)
        quotes_result = await db.execute(
            select(func.count(Quote.id)).where(
                and_(
                    Quote.created_at >= start_date,
                    Quote.created_at < end_date
                )
            )
        )
        quotes = quotes_result.scalar() or 0

        # Build limited funnel
        return [
            FunnelStep(
                name="Landing Page Views",
                event_name="landing_page_view",
                count=0,  # Unknown without PostHog
                conversion_rate=0.0
            ),
            FunnelStep(
                name="Quotes Generated",
                event_name="quote_generated",
                count=quotes,
                conversion_rate=0.0
            ),
            FunnelStep(
                name="Signups Complete",
                event_name="account_created",
                count=signups,
                conversion_rate=(signups / quotes * 100) if quotes > 0 else 0.0
            ),
        ]

    @staticmethod
    async def get_traffic_sources(
        days: int = 7
    ) -> Dict[str, int]:
        """
        Get breakdown of traffic by UTM source.

        Requires PostHog API.
        """
        if not FunnelAnalyticsService._posthog_available():
            return {"posthog_not_configured": True}

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        date_from = start_date.strftime("%Y-%m-%d")
        date_to = end_date.strftime("%Y-%m-%d")

        url = "https://app.posthog.com/api/projects/@current/insights/trend/"
        headers = {
            "Authorization": f"Bearer {settings.posthog_read_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "events": [{"id": "landing_page_view", "name": "landing_page_view", "type": "events"}],
            "date_from": date_from,
            "date_to": date_to,
            "display": "ActionsTable",
            "breakdown": "utm_source",
            "breakdown_type": "event"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    sources = {}
                    for result in data.get("result", []):
                        source = result.get("breakdown_value", "direct")
                        count = sum(result.get("data", []))
                        sources[source or "direct"] = count
                    return sources

        except Exception as e:
            logger.error(f"PostHog breakdown query error: {e}")

        return {}

    @staticmethod
    def generate_funnel_report_html(funnel: FunnelData) -> str:
        """
        Generate HTML section for funnel data (for email reports).

        Args:
            funnel: FunnelData object

        Returns:
            HTML string for inclusion in email
        """
        if not funnel.steps:
            return """
            <div style="background-color: #2a1a1a; border: 1px solid rgba(255, 100, 100, 0.2);
                        border-radius: 8px; padding: 20px; margin: 24px 0;">
                <div style="color: #ff9999; font-size: 14px; font-weight: 600; margin-bottom: 12px;">
                    📊 Funnel Data Unavailable
                </div>
                <div style="color: #ccaaaa; font-size: 13px; line-height: 1.6;">
                    Configure POSTHOG_READ_API_KEY for full funnel visibility.
                </div>
            </div>
            """

        # Build step-by-step visualization
        steps_html = ""
        for i, step in enumerate(funnel.steps):
            # Calculate bar width (relative to first step)
            max_count = funnel.steps[0].count if funnel.steps[0].count > 0 else 1
            bar_width = int((step.count / max_count) * 100) if step.count > 0 else 0

            # Color based on conversion rate
            if step.conversion_rate >= 50:
                bar_color = "#4CAF50"  # Green
            elif step.conversion_rate >= 25:
                bar_color = "#FFC107"  # Yellow
            else:
                bar_color = "#F44336"  # Red

            conversion_badge = ""
            if i > 0:
                conversion_badge = f"""
                <span style="color: {bar_color}; font-size: 12px; margin-left: 8px;">
                    ({step.conversion_rate:.0f}% from previous)
                </span>
                """

            steps_html += f"""
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="color: #ffffff; font-size: 13px;">{step.name}</span>
                    <span style="color: #a0a0a0; font-size: 13px;">
                        {step.count:,}{conversion_badge}
                    </span>
                </div>
                <div style="background-color: #333; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background-color: {bar_color}; width: {bar_width}%; height: 100%;"></div>
                </div>
            </div>
            """

        # Overall summary
        overall_rate = funnel.overall_conversion_rate
        rate_color = "#4CAF50" if overall_rate >= 5 else "#FFC107" if overall_rate >= 1 else "#F44336"

        return f"""
        <div style="background-color: #1a1a1a; border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px; padding: 20px; margin: 24px 0;">
            <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 16px;">
                📈 Conversion Funnel (Last {(funnel.period_end - funnel.period_start).days} Days)
            </div>

            {steps_html}

            <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #a0a0a0; font-size: 14px;">Overall Conversion Rate</span>
                    <span style="color: {rate_color}; font-size: 18px; font-weight: 600;">
                        {overall_rate:.2f}%
                    </span>
                </div>
                <div style="color: #666; font-size: 12px; margin-top: 8px;">
                    (Landing → Signup)
                </div>
            </div>
        </div>
        """

    @staticmethod
    async def check_funnel_anomalies(
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Check for concerning funnel patterns.

        Returns list of anomaly alerts.
        """
        anomalies = []

        try:
            # Get 7-day funnel
            funnel = await FunnelAnalyticsService.get_funnel_data(db, days=7)

            if funnel.steps and len(funnel.steps) >= 3:
                # Check for severe drop-off at specific steps
                for i in range(1, len(funnel.steps)):
                    step = funnel.steps[i]
                    if step.conversion_rate < 10 and funnel.steps[i-1].count > 20:
                        # Severe drop-off with significant traffic
                        anomalies.append({
                            "type": "funnel_dropoff",
                            "message": f"⚠️ Severe drop-off at {step.name}: only {step.conversion_rate:.0f}% conversion",
                            "severity": "high",
                            "step": step.name,
                            "rate": step.conversion_rate
                        })

                # Check for zero signups with traffic
                if funnel.steps[0].count > 50 and funnel.steps[-1].count == 0:
                    anomalies.append({
                        "type": "zero_conversions",
                        "message": f"🚨 {funnel.steps[0].count} visitors but 0 signups this week!",
                        "severity": "critical"
                    })

        except Exception as e:
            logger.error(f"Error checking funnel anomalies: {e}")

        return anomalies
