"""
Marketing Analytics Service (DISC-141).

Autonomous daily tracking of marketing performance:
- Signup/demo metrics from database
- Conversion funnel analysis
- Founder alerts for key events

Phase 1: Database metrics + email reports
Phase 2: PostHog API integration (requires read API key)
Phase 3: Google Ads API integration

Cost: $0 additional (uses existing infrastructure)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .logging import get_logger
from ..config import settings

logger = get_logger("quoted.marketing_analytics")


@dataclass
class DailyMetrics:
    """Daily marketing metrics snapshot."""
    date: datetime
    signups: int
    quotes_generated: int
    demos_generated: int
    conversions: int  # signups from demo visitors (if trackable)

    @property
    def conversion_rate(self) -> float:
        """Calculate demo-to-signup conversion rate."""
        if self.demos_generated == 0:
            return 0.0
        return (self.conversions / self.demos_generated) * 100


class MarketingAnalyticsService:
    """Service for tracking marketing performance metrics."""

    @staticmethod
    async def get_daily_metrics(
        db: AsyncSession,
        date: Optional[datetime] = None
    ) -> DailyMetrics:
        """
        Get marketing metrics for a specific date.

        Args:
            db: Database session
            date: Date to query (defaults to yesterday)

        Returns:
            DailyMetrics object with counts
        """
        from ..models.database import Contractor, Quote

        if date is None:
            date = datetime.utcnow() - timedelta(days=1)

        # Define date range (start of day to end of day)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Count signups
        signups_result = await db.execute(
            select(func.count(Contractor.id)).where(
                and_(
                    Contractor.created_at >= start_of_day,
                    Contractor.created_at < end_of_day
                )
            )
        )
        signups = signups_result.scalar() or 0

        # Count quotes generated (by logged-in users)
        quotes_result = await db.execute(
            select(func.count(Quote.id)).where(
                and_(
                    Quote.created_at >= start_of_day,
                    Quote.created_at < end_of_day,
                    Quote.contractor_id.isnot(None)  # Has an owner
                )
            )
        )
        quotes_generated = quotes_result.scalar() or 0

        # Count demo quotes (no contractor_id, generated via demo endpoint)
        # Note: Demo quotes don't persist to database currently, so we estimate from logs
        demos_generated = 0  # TODO: Track demo generations in database (DISC-142)

        # Conversions (users who signed up after using demo)
        # Note: Requires tracking in signup flow - utm_source or referrer
        conversions = 0  # TODO: Add conversion attribution tracking

        return DailyMetrics(
            date=start_of_day,
            signups=signups,
            quotes_generated=quotes_generated,
            demos_generated=demos_generated,
            conversions=conversions
        )

    @staticmethod
    async def get_metrics_range(
        db: AsyncSession,
        days: int = 7
    ) -> List[DailyMetrics]:
        """
        Get metrics for the last N days.

        Args:
            db: Database session
            days: Number of days to include

        Returns:
            List of DailyMetrics objects, most recent first
        """
        metrics = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i+1)
            daily = await MarketingAnalyticsService.get_daily_metrics(db, date)
            metrics.append(daily)
        return metrics

    @staticmethod
    async def get_total_counts(db: AsyncSession) -> Dict[str, int]:
        """
        Get total counts (all-time metrics).

        Args:
            db: Database session

        Returns:
            Dict with total counts
        """
        from ..models.database import Contractor, Quote

        # Total signups
        total_signups = await db.execute(
            select(func.count(Contractor.id))
        )

        # Total quotes
        total_quotes = await db.execute(
            select(func.count(Quote.id))
        )

        # Paying users (subscription_tier != 'trial')
        paying_users = await db.execute(
            select(func.count(Contractor.id)).where(
                Contractor.subscription_tier != 'trial'
            )
        )

        return {
            "total_signups": total_signups.scalar() or 0,
            "total_quotes": total_quotes.scalar() or 0,
            "paying_users": paying_users.scalar() or 0
        }

    @staticmethod
    def generate_daily_report_html(
        metrics: DailyMetrics,
        totals: Dict[str, int],
        week_metrics: List[DailyMetrics]
    ) -> str:
        """
        Generate HTML email content for daily marketing report.

        Args:
            metrics: Yesterday's metrics
            totals: All-time totals
            week_metrics: Last 7 days of metrics

        Returns:
            HTML string for email body
        """
        # Calculate week totals
        week_signups = sum(m.signups for m in week_metrics)
        week_quotes = sum(m.quotes_generated for m in week_metrics)

        # Format date
        date_str = metrics.date.strftime("%B %d, %Y")

        # Build trend indicators
        def trend_indicator(current: int, previous: int) -> str:
            if previous == 0:
                return "➡️ (new)"
            diff = current - previous
            pct = (diff / previous) * 100 if previous > 0 else 0
            if diff > 0:
                return f"📈 +{diff} ({pct:.0f}%)"
            elif diff < 0:
                return f"📉 {diff} ({pct:.0f}%)"
            return "➡️ flat"

        # Get previous day metrics for comparison
        prev_day = week_metrics[1] if len(week_metrics) > 1 else metrics
        signup_trend = trend_indicator(metrics.signups, prev_day.signups)

        # Build 7-day sparkline (text representation)
        sparkline = " ".join([
            "█" * min(m.signups, 5) if m.signups > 0 else "·"
            for m in reversed(week_metrics[-7:])
        ])

        html = f"""
        <h1>📊 Daily Marketing Report</h1>
        <p style="color: #a0a0a0; font-size: 14px;">{date_str}</p>

        <div class="stats-grid" style="margin: 24px 0;">
            <div class="stat-box">
                <div class="stat-value">{metrics.signups}</div>
                <div class="stat-label">New Signups</div>
                <div style="color: #a0a0a0; font-size: 12px; margin-top: 8px;">{signup_trend}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{metrics.quotes_generated}</div>
                <div class="stat-label">Quotes Generated</div>
            </div>
        </div>

        <div style="background-color: #1a1a1a; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 20px; margin: 24px 0;">
            <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 16px;">📅 Last 7 Days</div>
            <div style="color: #e0e0e0; font-size: 15px; line-height: 1.8;">
                <strong>Signups:</strong> {week_signups}<br>
                <strong>Quotes:</strong> {week_quotes}<br>
                <div style="font-family: monospace; font-size: 20px; margin-top: 12px; letter-spacing: 2px;">{sparkline}</div>
            </div>
        </div>

        <div style="background-color: #1a1a1a; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 20px; margin: 24px 0;">
            <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 16px;">🏆 All-Time Totals</div>
            <div style="color: #e0e0e0; font-size: 15px; line-height: 1.8;">
                <strong>Total Signups:</strong> {totals['total_signups']}<br>
                <strong>Total Quotes:</strong> {totals['total_quotes']}<br>
                <strong>Paying Users:</strong> {totals['paying_users']}
            </div>
        </div>

        <div style="background-color: #2a1a1a; border: 1px solid rgba(255, 100, 100, 0.2); border-radius: 8px; padding: 20px; margin: 24px 0;">
            <div style="color: #ff9999; font-size: 14px; font-weight: 600; margin-bottom: 12px;">⚠️ Data Limitations</div>
            <div style="color: #ccaaaa; font-size: 13px; line-height: 1.6;">
                This report shows database metrics only. For full funnel visibility (page views → demos → signups), configure PostHog read API:
                <br><br>
                <code style="background: #1a1111; padding: 4px 8px; border-radius: 4px;">POSTHOG_READ_API_KEY=phx_...</code>
                <br><br>
                Get key at: <a href="https://app.posthog.com/settings/user-api-keys" style="color: #ff9999;">PostHog Settings</a>
            </div>
        </div>

        <p class="muted" style="margin-top: 32px; font-size: 12px;">
            This report is generated automatically by DISC-141 Marketing Analytics.<br>
            To stop these emails, set MARKETING_REPORTS_ENABLED=false in Railway.
        </p>
        """

        return html

    @staticmethod
    async def send_daily_report(db: AsyncSession) -> bool:
        """
        Generate and send the daily marketing report to founder.

        Args:
            db: Database session

        Returns:
            True if sent successfully
        """
        from .email import EmailService

        logger.info("Generating daily marketing report...")

        try:
            # Get metrics
            yesterday = await MarketingAnalyticsService.get_daily_metrics(db)
            totals = await MarketingAnalyticsService.get_total_counts(db)
            week_metrics = await MarketingAnalyticsService.get_metrics_range(db, 7)

            # Generate HTML
            html_content = MarketingAnalyticsService.generate_daily_report_html(
                yesterday, totals, week_metrics
            )

            # Send email
            date_str = yesterday.date.strftime("%b %d")
            subject = f"📊 Quoted Daily: {yesterday.signups} signups, {yesterday.quotes_generated} quotes ({date_str})"

            await EmailService.send_email(
                to_email=settings.founder_email,
                subject=subject,
                body=html_content
            )

            logger.info(f"Daily marketing report sent to {settings.founder_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send daily marketing report: {e}")
            return False

    @staticmethod
    async def check_anomalies(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Check for notable anomalies that warrant immediate alerts.

        Returns:
            List of anomaly dicts with type and details
        """
        anomalies = []

        try:
            # Get today vs yesterday
            today = await MarketingAnalyticsService.get_daily_metrics(
                db, datetime.utcnow()
            )
            yesterday = await MarketingAnalyticsService.get_daily_metrics(db)

            # Check for signup spike (3x normal)
            if today.signups >= 3 and yesterday.signups > 0:
                if today.signups / yesterday.signups >= 3:
                    anomalies.append({
                        "type": "signup_spike",
                        "message": f"🚀 Signup spike! {today.signups} today vs {yesterday.signups} yesterday",
                        "severity": "high"
                    })

            # Check for zero signups when ads are running
            # (Would need Google Ads integration to detect this properly)

        except Exception as e:
            logger.error(f"Error checking anomalies: {e}")

        return anomalies


# Convenience function for scheduler
async def run_daily_marketing_report():
    """
    Scheduled job function for daily marketing report.
    Called by APScheduler.
    """
    from .database import async_session_factory

    # Check if reports are enabled
    if not getattr(settings, 'marketing_reports_enabled', True):
        logger.debug("Marketing reports disabled")
        return

    try:
        async with async_session_factory() as db:
            await MarketingAnalyticsService.send_daily_report(db)
    except Exception as e:
        logger.error(f"Error in run_daily_marketing_report: {e}")
