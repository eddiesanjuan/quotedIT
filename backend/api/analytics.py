"""
Analytics API routes for Quoted (DISC-137, DISC-138).

Handles analytics data collection from frontend:
- Exit intent survey submissions
- Conversion funnel data (DISC-138)

P0-6 Security: Business metrics endpoints restricted to founder only.
Public endpoints: exit-survey (data collection), google-ads-webhook (secret auth)
"""

import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Depends, status
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services.exit_survey import ExitSurveyService
from ..services.funnel_analytics import FunnelAnalyticsService
from ..services.google_ads_scripts import GoogleAdsScriptsService, generate_google_ads_script
from ..services.database import async_session_factory
from ..services.logging import get_api_logger
from ..services.auth import get_current_user
from ..config import settings

logger = get_api_logger()

router = APIRouter()

# Rate limiter - prevent abuse
limiter = Limiter(key_func=get_remote_address)


# ============================================================================
# P0-6: Founder-Only Authentication
# ============================================================================

async def get_founder_user(
    user: dict = Depends(get_current_user),
) -> dict:
    """
    Dependency that ensures the current user is the founder.

    P0-6 Security: Business metrics (conversion rates, traffic data, ad spend)
    should NEVER be publicly accessible. Only the founder can view these.

    Checks if user's email matches settings.founder_email.
    """
    if user["email"] != settings.founder_email:
        logger.warning(
            f"Non-founder user {user['email']} attempted to access analytics endpoint"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is restricted to administrators"
        )
    return user


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
    utm_source: Optional[str] = None,
    founder: dict = Depends(get_founder_user),
):
    """
    Get conversion funnel data.

    Returns step-by-step funnel from landing page to signup.
    Requires PostHog read API key for full visibility.

    P0-6 Security: Restricted to founder only (business metrics).

    Args:
        days: Number of days to analyze (default: 7)
        utm_source: Optional UTM source filter (e.g., "google")
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
    days: int = 7,
    founder: dict = Depends(get_founder_user),
):
    """
    Get traffic breakdown by UTM source.

    Requires PostHog read API key.

    P0-6 Security: Restricted to founder only (business metrics).

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
async def check_traffic_anomalies(
    request: Request,
    founder: dict = Depends(get_founder_user),
):
    """
    Check for traffic anomalies (spikes and drops).

    Compares current traffic to 7-day baseline.
    Returns any detected issues that need attention.

    P0-6 Security: Restricted to founder only (business metrics).

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
async def get_google_ads_status(
    request: Request,
    founder: dict = Depends(get_founder_user),
):
    """
    Get Google Ads performance summary.

    Requires Google Ads API credentials to be configured.
    Returns metrics, anomalies, and AI recommendations.

    P0-6 Security: Restricted to founder only (ad spend/performance data).
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


# ============================================================================
# DISC-141 Phase 2B: Google Ads Scripts (Alternative to API)
# ============================================================================


class GoogleAdsWebhookRequest(BaseModel):
    """Data received from Google Ads Scripts."""
    accountId: str
    accountName: str = "Unknown"
    currency: str = "USD"
    dateRange: str = "LAST_7_DAYS"
    totalImpressions: int = 0
    totalClicks: int = 0
    totalCost: float = 0
    totalConversions: float = 0
    campaigns: List[Dict[str, Any]] = []
    timestamp: Optional[str] = None


class GoogleAdsScriptsResponse(BaseModel):
    """Google Ads Scripts status response."""
    has_data: bool
    message: str
    metrics: Optional[Dict[str, Any]] = None
    anomalies: List[Dict[str, Any]] = []
    recommendations: List[str] = []


@router.post("/google-ads-webhook")
async def google_ads_webhook(
    request: Request,
    data: GoogleAdsWebhookRequest
):
    """
    Receive campaign data from Google Ads Scripts.

    This is the webhook endpoint that receives data pushed from
    a Google Ads Script running in your Google Ads account.

    Requires X-Webhook-Secret header matching GOOGLE_ADS_WEBHOOK_SECRET.
    """
    # Verify webhook secret
    webhook_secret = request.headers.get("X-Webhook-Secret", "")
    expected_secret = getattr(settings, 'google_ads_webhook_secret', '')

    if not expected_secret:
        # No secret configured - accept for now (MVP)
        logger.warning("Google Ads webhook received but no secret configured")
    elif webhook_secret != expected_secret:
        logger.warning("Google Ads webhook received with invalid secret")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    try:
        # Store the snapshot
        snapshot = GoogleAdsScriptsService.store_snapshot(data.model_dump())

        return {
            "success": True,
            "message": f"Stored {len(snapshot.campaigns)} campaigns",
            "received_at": snapshot.received_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to process Google Ads webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process webhook data"
        )


@router.get("/google-ads-scripts", response_model=GoogleAdsScriptsResponse)
async def get_google_ads_scripts_status(
    request: Request,
    founder: dict = Depends(get_founder_user),
):
    """
    Get Google Ads performance from Scripts data.

    Returns metrics, anomalies, and recommendations based on
    data pushed from Google Ads Scripts.

    P0-6 Security: Restricted to founder only (ad spend/performance data).
    """
    snapshot = GoogleAdsScriptsService.get_latest_snapshot()

    if not snapshot:
        return GoogleAdsScriptsResponse(
            has_data=False,
            message="No data yet. Run the Google Ads Script to sync data.",
            metrics=None,
            anomalies=[],
            recommendations=GoogleAdsScriptsService.generate_recommendations()
        )

    return GoogleAdsScriptsResponse(
        has_data=True,
        message=f"Data from {snapshot.received_at.strftime('%Y-%m-%d %H:%M')} UTC",
        metrics={
            "account_name": snapshot.account_name,
            "date_range": snapshot.date_range,
            "impressions": snapshot.total_impressions,
            "clicks": snapshot.total_clicks,
            "cost": round(snapshot.total_cost, 2),
            "conversions": snapshot.total_conversions,
            "ctr": round(snapshot.overall_ctr, 2),
            "cpc": round(snapshot.overall_cpc, 2),
            "cpa": round(snapshot.overall_cpa, 2) if snapshot.overall_cpa != float('inf') else None,
            "campaigns": len(snapshot.campaigns)
        },
        anomalies=GoogleAdsScriptsService.check_anomalies(),
        recommendations=GoogleAdsScriptsService.generate_recommendations()
    )


@router.get("/google-ads-script-code")
async def get_google_ads_script_code(
    request: Request,
    founder: dict = Depends(get_founder_user),
):
    """
    Get the JavaScript code to paste into Google Ads Scripts.

    This generates the script with your webhook URL and secret.
    Copy this into Google Ads → Tools & Settings → Scripts.

    P0-6 Security: Restricted to founder only (exposes webhook secret).
    """
    # Determine the webhook URL based on environment
    if settings.environment == "production":
        webhook_url = "https://quoted.it.com/api/analytics/google-ads-webhook"
    else:
        webhook_url = "http://localhost:8000/api/analytics/google-ads-webhook"

    webhook_secret = getattr(settings, 'google_ads_webhook_secret', 'dev-secret-change-me')

    script_code = generate_google_ads_script(webhook_url, webhook_secret)

    return {
        "webhook_url": webhook_url,
        "script_code": script_code,
        "instructions": [
            "1. Go to Google Ads → Tools & Settings → Scripts",
            "2. Click the + button to create a new script",
            "3. Name it 'Quoted Data Sync'",
            "4. Paste the script_code below",
            "5. Click 'Authorize' and grant permissions",
            "6. Click 'Preview' to test (check logs for success)",
            "7. Set frequency to 'Daily' and save"
        ]
    }


# ============================================================================
# User Outreach - Personal Follow-Up Emails
# ============================================================================


class UserOutreachResponse(BaseModel):
    """Response for user outreach operations."""
    total_users: int
    users_without_quotes: int
    users_with_quotes: int
    emails_sent: int
    skipped: int
    errors: List[str]


class UserListResponse(BaseModel):
    """Response listing users for outreach."""
    total_users: int
    users: List[Dict[str, Any]]


@router.get("/outreach/users", response_model=UserListResponse)
async def list_users_for_outreach(
    request: Request,
    founder: dict = Depends(get_founder_user),
):
    """
    List all users and their engagement status.

    Shows which users have created quotes and which haven't,
    to help decide who to send personal outreach to.

    P0-6 Security: Restricted to founder only.
    """
    from sqlalchemy import select, func
    from ..models.database import User, Contractor, Quote

    try:
        async with async_session_factory() as db:
            # Get all contractors with their quote counts
            result = await db.execute(
                select(
                    Contractor.id,
                    Contractor.business_name,
                    Contractor.owner_name,
                    Contractor.email,
                    Contractor.created_at,
                    User.email.label("user_email"),
                    User.plan_tier,
                    User.trial_ends_at,
                    func.count(Quote.id).label("quote_count")
                )
                .join(User, Contractor.user_id == User.id)
                .outerjoin(Quote, Quote.contractor_id == Contractor.id)
                .group_by(Contractor.id, User.id)
                .order_by(Contractor.created_at.desc())
            )
            rows = result.all()

            users = []
            for row in rows:
                users.append({
                    "contractor_id": row.id,
                    "business_name": row.business_name,
                    "owner_name": row.owner_name,
                    "email": row.email or row.user_email,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "plan_tier": row.plan_tier,
                    "trial_ends_at": row.trial_ends_at.isoformat() if row.trial_ends_at else None,
                    "quote_count": row.quote_count,
                    "has_created_quote": row.quote_count > 0
                })

            return UserListResponse(
                total_users=len(users),
                users=users
            )

    except Exception as e:
        logger.error(f"Failed to list users for outreach: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to list users"
        )


class SendOutreachRequest(BaseModel):
    """Request to send outreach emails."""
    send_to_all: bool = False  # If true, send to all users without quotes
    user_emails: Optional[List[str]] = None  # Specific emails to send to
    dry_run: bool = True  # Preview without sending


@router.post("/outreach/send", response_model=UserOutreachResponse)
async def send_personal_outreach(
    request: Request,
    outreach_request: SendOutreachRequest,
    founder: dict = Depends(get_founder_user),
):
    """
    Send personal check-in emails to users.

    By default (dry_run=True), this shows who would receive emails.
    Set dry_run=False to actually send emails.

    Options:
    - send_to_all=True: Send to all users who haven't created a quote
    - user_emails=[...]: Send to specific email addresses

    P0-6 Security: Restricted to founder only.

    Emails:
    - Come from "Eddie from Quoted <hello@quoted.it.com>"
    - Reply-to: eddie@granular.tools
    - Include offer to extend trial
    """
    import asyncio
    from sqlalchemy import select, func
    from ..models.database import User, Contractor, Quote
    from ..services.email import EmailService

    errors = []
    emails_sent = 0
    skipped = 0

    try:
        async with async_session_factory() as db:
            # Build query for users
            query = (
                select(
                    Contractor.id,
                    Contractor.business_name,
                    Contractor.owner_name,
                    Contractor.email,
                    User.email.label("user_email"),
                    func.count(Quote.id).label("quote_count")
                )
                .join(User, Contractor.user_id == User.id)
                .outerjoin(Quote, Quote.contractor_id == Contractor.id)
                .group_by(Contractor.id, User.id)
            )

            result = await db.execute(query)
            rows = result.all()

            users_without_quotes = []
            users_with_quotes = []

            for row in rows:
                user_data = {
                    "business_name": row.business_name,
                    "owner_name": row.owner_name,
                    "email": row.email or row.user_email,
                    "quote_count": row.quote_count
                }
                if row.quote_count == 0:
                    users_without_quotes.append(user_data)
                else:
                    users_with_quotes.append(user_data)

            # Determine who to send to
            targets = []

            if outreach_request.send_to_all:
                targets = users_without_quotes
            elif outreach_request.user_emails:
                all_users = users_without_quotes + users_with_quotes
                for email in outreach_request.user_emails:
                    user = next((u for u in all_users if u["email"] == email), None)
                    if user:
                        targets.append(user)
                    else:
                        errors.append(f"User not found: {email}")

            if outreach_request.dry_run:
                # Just report what would happen
                return UserOutreachResponse(
                    total_users=len(rows),
                    users_without_quotes=len(users_without_quotes),
                    users_with_quotes=len(users_with_quotes),
                    emails_sent=0,
                    skipped=len(targets),  # In dry run, show who would be sent
                    errors=[f"DRY RUN - Would send to {len(targets)} users: {[t['email'] for t in targets]}"]
                )

            # Actually send emails
            email_service = EmailService()

            for user in targets:
                try:
                    if not user["email"]:
                        skipped += 1
                        continue

                    await email_service.send_personal_checkin_email(
                        to_email=user["email"],
                        owner_name=user["owner_name"],
                        business_name=user["business_name"],
                        has_created_quote=user["quote_count"] > 0,
                        offer_extended_trial=True
                    )
                    emails_sent += 1

                    # Rate limit: Resend allows 2 req/sec
                    await asyncio.sleep(0.6)

                except Exception as e:
                    errors.append(f"Failed to send to {user['email']}: {str(e)}")

            return UserOutreachResponse(
                total_users=len(rows),
                users_without_quotes=len(users_without_quotes),
                users_with_quotes=len(users_with_quotes),
                emails_sent=emails_sent,
                skipped=skipped,
                errors=errors
            )

    except Exception as e:
        logger.error(f"Failed to send outreach emails: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send outreach emails: {str(e)}"
        )
