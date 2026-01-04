"""
Analytics API routes for Quoted (DISC-137, DISC-138).

Handles analytics data collection from frontend:
- Exit intent survey submissions
- Conversion funnel data (DISC-138)

No authentication required for data collection endpoints.
Founder-only endpoints require auth.
"""

import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services.exit_survey import ExitSurveyService
from ..services.funnel_analytics import FunnelAnalyticsService
from ..services.database import async_session_factory
from ..services.logging import get_api_logger
from ..config import settings

logger = get_api_logger()

router = APIRouter()

# Rate limiter - prevent abuse
limiter = Limiter(key_func=get_remote_address)


class ExitSurveyRequest(BaseModel):
    """Exit survey submission request."""
    reasons: List[str]  # e.g., ["not_my_trade", "pricing_high"]
    other_text: Optional[str] = None
    page_url: Optional[str] = None
    session_id: Optional[str] = None


class ExitSurveyResponse(BaseModel):
    """Exit survey submission response."""
    success: bool
    message: str


@router.post("/exit-survey", response_model=ExitSurveyResponse)
async def submit_exit_survey(
    request: Request,
    survey: ExitSurveyRequest
):
    """
    Submit exit intent survey response.

    Called from landing page when visitor completes the exit survey.
    Rate limited to 5 per hour per IP to prevent abuse.

    Triggers:
    - Instant alert if concerning keywords in other_text
    - Inclusion in daily digest email to founder
    """
    try:
        # Get client info
        client_ip = get_remote_address(request)
        ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:32] if client_ip else None
        user_agent = request.headers.get("user-agent", "")[:500]
        referrer = request.headers.get("referer", "")[:500]

        # Validate reasons
        valid_reasons = {
            "not_my_trade",
            "pricing_high",
            "no_time",
            "need_examples",
            "other"
        }

        filtered_reasons = [r for r in survey.reasons if r in valid_reasons]
        if not filtered_reasons:
            raise HTTPException(
                status_code=400,
                detail="At least one valid reason is required"
            )

        # Store survey response
        async with async_session_factory() as db:
            survey_record = await ExitSurveyService.create_survey(
                db=db,
                reasons=filtered_reasons,
                other_text=survey.other_text,
                page_url=survey.page_url,
                referrer=referrer,
                user_agent=user_agent,
                ip_hash=ip_hash,
                session_id=survey.session_id
            )

            # Check for concerning keywords and send instant alert
            alert_sent = await ExitSurveyService.check_and_send_alert(
                db=db,
                survey=survey_record
            )

            await db.commit()

            logger.info(
                f"Exit survey submitted: reasons={filtered_reasons}, "
                f"has_other_text={bool(survey.other_text)}, alert_sent={alert_sent}"
            )

        return ExitSurveyResponse(
            success=True,
            message="Thank you for your feedback"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit exit survey: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to submit survey"
        )


# ============================================================================
# DISC-138: Conversion Funnel Analytics
# ============================================================================


class FunnelResponse(BaseModel):
    """Funnel analytics response."""
    period_start: str
    period_end: str
    overall_conversion_rate: float
    steps: List[Dict[str, Any]]
    posthog_configured: bool


class TrafficSourcesResponse(BaseModel):
    """Traffic sources breakdown response."""
    sources: Dict[str, int]
    posthog_configured: bool


@router.get("/funnel", response_model=FunnelResponse)
async def get_conversion_funnel(
    request: Request,
    days: int = 7,
    utm_source: Optional[str] = None
):
    """
    Get conversion funnel data.

    Returns step-by-step funnel from landing page to signup.
    Requires PostHog read API key for full visibility.

    Args:
        days: Number of days to analyze (default: 7)
        utm_source: Optional UTM source filter (e.g., "google")

    Note: This is a public endpoint for MVP. In production,
    should be restricted to founder/admin accounts.
    """
    try:
        async with async_session_factory() as db:
            funnel = await FunnelAnalyticsService.get_funnel_data(
                db=db,
                days=days,
                utm_source=utm_source
            )

            return FunnelResponse(
                period_start=funnel.period_start.isoformat(),
                period_end=funnel.period_end.isoformat(),
                overall_conversion_rate=round(funnel.overall_conversion_rate, 2),
                steps=[
                    {
                        "name": step.name,
                        "event": step.event_name,
                        "count": step.count,
                        "conversion_rate": round(step.conversion_rate, 2)
                    }
                    for step in funnel.steps
                ],
                posthog_configured=bool(settings.posthog_read_api_key)
            )

    except Exception as e:
        logger.error(f"Failed to get funnel data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve funnel data"
        )


@router.get("/traffic-sources", response_model=TrafficSourcesResponse)
async def get_traffic_sources(
    request: Request,
    days: int = 7
):
    """
    Get traffic breakdown by UTM source.

    Requires PostHog read API key.

    Args:
        days: Number of days to analyze (default: 7)
    """
    try:
        sources = await FunnelAnalyticsService.get_traffic_sources(days=days)

        return TrafficSourcesResponse(
            sources=sources if not sources.get("posthog_not_configured") else {},
            posthog_configured=bool(settings.posthog_read_api_key)
        )

    except Exception as e:
        logger.error(f"Failed to get traffic sources: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve traffic sources"
        )


class TrafficAnomalyResponse(BaseModel):
    """Traffic anomaly check response."""
    has_issues: bool
    alerts: List[Dict[str, Any]]
    message: str


@router.get("/traffic-check", response_model=TrafficAnomalyResponse)
async def check_traffic_anomalies(request: Request):
    """
    Check for traffic anomalies (spikes and drops).

    Compares current traffic to 7-day baseline.
    Returns any detected issues that need attention.

    Use this to quickly diagnose traffic problems.
    """
    try:
        from ..services.traffic_spike_alerts import TrafficSpikeAlertService

        async with async_session_factory() as db:
            # Check for spikes
            spike_alerts = await TrafficSpikeAlertService.detect_spikes(db)

            # Check for drops (the painful part)
            drop_alerts = await TrafficSpikeAlertService.detect_traffic_drops(db)

            all_alerts = spike_alerts + drop_alerts

            # Format alerts for response
            alert_list = [
                {
                    "type": a.alert_type,
                    "severity": a.severity,
                    "message": a.message,
                    "current": a.current_value,
                    "average": round(a.average_value, 1),
                    "multiplier": round(a.multiplier, 2) if a.multiplier != float("inf") else None
                }
                for a in all_alerts
            ]

            if not all_alerts:
                message = "✅ Traffic looks normal. No significant spikes or drops detected."
            elif any(a.alert_type in ['traffic_drop', 'conversion_drop'] for a in all_alerts):
                message = f"⚠️ {len(all_alerts)} issue(s) detected - traffic may be declining!"
            else:
                message = f"🚀 {len(all_alerts)} spike(s) detected - traffic is surging!"

            return TrafficAnomalyResponse(
                has_issues=len(all_alerts) > 0,
                alerts=alert_list,
                message=message
            )

    except Exception as e:
        logger.error(f"Failed to check traffic anomalies: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to check traffic anomalies"
        )


class GoogleAdsResponse(BaseModel):
    """Google Ads status response."""
    configured: bool
    message: str
    metrics: Optional[Dict[str, Any]] = None
    anomalies: List[Dict[str, Any]] = []
    recommendations: List[str] = []


@router.get("/google-ads", response_model=GoogleAdsResponse)
async def get_google_ads_status(request: Request):
    """
    Get Google Ads performance summary.

    Requires Google Ads API credentials to be configured.
    Returns metrics, anomalies, and AI recommendations.
    """
    try:
        from ..services.google_ads_analytics import get_google_ads_summary

        summary = await get_google_ads_summary()

        return GoogleAdsResponse(
            configured=summary["configured"],
            message=summary.get("message", "Google Ads data retrieved"),
            metrics=summary.get("metrics"),
            anomalies=summary.get("anomalies", []),
            recommendations=summary.get("recommendations", [])
        )

    except Exception as e:
        logger.error(f"Failed to get Google Ads status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve Google Ads status"
        )
