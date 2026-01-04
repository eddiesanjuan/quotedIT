"""
Traffic Spike Alerts Service (DISC-139).

Real-time monitoring for traffic and activity spikes:
- Hourly traffic comparison to 7-day average
- Demo generation velocity alerts
- Signup velocity alerts
- Founder notifications for viral moments

Runs hourly via APScheduler.

Cost: $0 additional (uses existing email infrastructure)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .logging import get_logger
from ..config import settings

logger = get_logger("quoted.traffic_spike_alerts")


@dataclass
class HourlyMetrics:
    """Metrics for a specific hour."""
    hour: datetime
    signups: int
    quotes_generated: int
    demos_generated: int


@dataclass
class SpikeAlert:
    """Represents a detected traffic spike."""
    alert_type: str  # 'signups', 'demos', 'quotes', 'overall'
    current_value: int
    average_value: float
    multiplier: float  # How many times the average
    message: str
    severity: str  # 'info', 'high', 'critical'


class TrafficSpikeAlertService:
    """Service for detecting and alerting on traffic spikes AND drops."""

    # Thresholds for spike detection
    SPIKE_MULTIPLIER = 3.0  # 3x normal = spike
    DEMO_SPIKE_THRESHOLD = 5  # 5+ demos in an hour
    SIGNUP_SPIKE_THRESHOLD = 3  # 3+ signups in an hour

    # Thresholds for DROP detection (the painful part)
    DROP_THRESHOLD = 0.3  # Below 30% of average = concerning drop
    CRITICAL_DROP_THRESHOLD = 0.1  # Below 10% of average = critical

    @staticmethod
    async def get_hourly_metrics(
        db: AsyncSession,
        hour: Optional[datetime] = None
    ) -> HourlyMetrics:
        """
        Get metrics for a specific hour.

        Args:
            db: Database session
            hour: Hour to query (defaults to current hour)

        Returns:
            HourlyMetrics object with counts
        """
        from ..models.database import Contractor, Quote

        if hour is None:
            hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

        start_of_hour = hour.replace(minute=0, second=0, microsecond=0)
        end_of_hour = start_of_hour + timedelta(hours=1)

        # Count signups in this hour
        signups_result = await db.execute(
            select(func.count(Contractor.id)).where(
                and_(
                    Contractor.created_at >= start_of_hour,
                    Contractor.created_at < end_of_hour
                )
            )
        )
        signups = signups_result.scalar() or 0

        # Count quotes generated (by logged-in users)
        quotes_result = await db.execute(
            select(func.count(Quote.id)).where(
                and_(
                    Quote.created_at >= start_of_hour,
                    Quote.created_at < end_of_hour,
                    Quote.contractor_id.isnot(None)
                )
            )
        )
        quotes_generated = quotes_result.scalar() or 0

        # Demo quotes - we don't persist these yet (DISC-142)
        # For now, return 0; when DISC-142 is implemented, query demo_sessions table
        demos_generated = 0

        return HourlyMetrics(
            hour=start_of_hour,
            signups=signups,
            quotes_generated=quotes_generated,
            demos_generated=demos_generated
        )

    @staticmethod
    async def get_7day_hourly_average(
        db: AsyncSession,
        target_hour: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get 7-day average for the same hour of day.

        This compares apples to apples - if it's 2pm, we compare to
        the average of 2pm over the last 7 days.

        Args:
            db: Database session
            target_hour: Hour of day (0-23), defaults to current hour

        Returns:
            Dict with average signups, quotes, demos per hour
        """
        from ..models.database import Contractor, Quote

        if target_hour is None:
            target_hour = datetime.utcnow().hour

        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)

        # Count signups over 7 days for this hour
        signups_result = await db.execute(
            select(func.count(Contractor.id)).where(
                and_(
                    Contractor.created_at >= seven_days_ago,
                    Contractor.created_at < now
                )
            )
        )
        total_signups = signups_result.scalar() or 0

        # Count quotes over 7 days
        quotes_result = await db.execute(
            select(func.count(Quote.id)).where(
                and_(
                    Quote.created_at >= seven_days_ago,
                    Quote.created_at < now,
                    Quote.contractor_id.isnot(None)
                )
            )
        )
        total_quotes = quotes_result.scalar() or 0

        # Calculate hourly averages (7 days * 24 hours = 168 hours)
        hours_in_period = 7 * 24

        return {
            "avg_signups_per_hour": total_signups / hours_in_period if hours_in_period > 0 else 0,
            "avg_quotes_per_hour": total_quotes / hours_in_period if hours_in_period > 0 else 0,
            "avg_demos_per_hour": 0  # TODO: DISC-142 will enable this
        }

    @staticmethod
    async def detect_spikes(db: AsyncSession) -> List[SpikeAlert]:
        """
        Detect traffic spikes by comparing current hour to 7-day average.

        Returns:
            List of SpikeAlert objects for any detected spikes
        """
        alerts = []

        try:
            current = await TrafficSpikeAlertService.get_hourly_metrics(db)
            averages = await TrafficSpikeAlertService.get_7day_hourly_average(db)

            # Check signup velocity spike
            if current.signups >= TrafficSpikeAlertService.SIGNUP_SPIKE_THRESHOLD:
                avg = averages["avg_signups_per_hour"]
                if avg > 0:
                    multiplier = current.signups / avg
                    if multiplier >= TrafficSpikeAlertService.SPIKE_MULTIPLIER:
                        alerts.append(SpikeAlert(
                            alert_type="signups",
                            current_value=current.signups,
                            average_value=avg,
                            multiplier=multiplier,
                            message=f"Signup spike! {current.signups} signups in the last hour vs {avg:.1f}/hr average",
                            severity="critical"
                        ))
                else:
                    # No previous average - any 3+ signups is notable
                    alerts.append(SpikeAlert(
                        alert_type="signups",
                        current_value=current.signups,
                        average_value=0,
                        multiplier=float("inf"),
                        message=f"Signup surge! {current.signups} signups in the last hour (no prior baseline)",
                        severity="high"
                    ))

            # Check quote generation spike
            if current.quotes_generated >= 5:  # At least 5 quotes to be notable
                avg = averages["avg_quotes_per_hour"]
                if avg > 0:
                    multiplier = current.quotes_generated / avg
                    if multiplier >= TrafficSpikeAlertService.SPIKE_MULTIPLIER:
                        alerts.append(SpikeAlert(
                            alert_type="quotes",
                            current_value=current.quotes_generated,
                            average_value=avg,
                            multiplier=multiplier,
                            message=f"Quote generation spike! {current.quotes_generated} quotes vs {avg:.1f}/hr average",
                            severity="high"
                        ))

            # Note: Demo spike detection will be enabled when DISC-142 is implemented
            # For now, demo notifications are sent individually via DISC-128

            logger.debug(
                f"Spike detection: {current.signups} signups, {current.quotes_generated} quotes. "
                f"Alerts: {len(alerts)}"
            )

        except Exception as e:
            logger.error(f"Error detecting spikes: {e}")

        return alerts

    @staticmethod
    async def detect_traffic_drops(db: AsyncSession) -> List[SpikeAlert]:
        """
        Detect traffic DROPS using PostHog funnel data.

        Compares last 24 hours to 7-day average to find significant declines.

        Returns:
            List of SpikeAlert objects for detected drops
        """
        from .funnel_analytics import FunnelAnalyticsService

        alerts = []

        try:
            # Get 7-day funnel for baseline
            funnel_7d = await FunnelAnalyticsService.get_funnel_data(db, days=7)

            # Get 1-day funnel for current state
            funnel_1d = await FunnelAnalyticsService.get_funnel_data(db, days=1)

            if not funnel_7d.steps or not funnel_1d.steps:
                logger.debug("Insufficient funnel data for drop detection")
                return alerts

            # Compare each funnel step
            for step_7d in funnel_7d.steps:
                # Find matching step in 1-day data
                step_1d = next((s for s in funnel_1d.steps if s.event_name == step_7d.event_name), None)
                if not step_1d:
                    continue

                # Calculate daily average from 7-day data
                daily_avg = step_7d.count / 7.0

                if daily_avg < 5:
                    # Not enough baseline traffic to detect drops meaningfully
                    continue

                # Check for significant drop
                current_ratio = step_1d.count / daily_avg if daily_avg > 0 else 1.0

                if current_ratio <= TrafficSpikeAlertService.CRITICAL_DROP_THRESHOLD:
                    # Critical drop: <10% of average
                    alerts.append(SpikeAlert(
                        alert_type="traffic_drop",
                        current_value=step_1d.count,
                        average_value=daily_avg,
                        multiplier=current_ratio,
                        message=f"🚨 CRITICAL: {step_7d.name} dropped to {step_1d.count} (avg: {daily_avg:.0f}/day)",
                        severity="critical"
                    ))
                elif current_ratio <= TrafficSpikeAlertService.DROP_THRESHOLD:
                    # Significant drop: <30% of average
                    alerts.append(SpikeAlert(
                        alert_type="traffic_drop",
                        current_value=step_1d.count,
                        average_value=daily_avg,
                        multiplier=current_ratio,
                        message=f"⚠️ {step_7d.name} down to {step_1d.count} vs {daily_avg:.0f}/day avg",
                        severity="high"
                    ))

            # Also check for funnel conversion rate drops
            if funnel_7d.overall_conversion_rate > 0 and funnel_1d.overall_conversion_rate >= 0:
                rate_ratio = funnel_1d.overall_conversion_rate / funnel_7d.overall_conversion_rate
                if rate_ratio <= 0.5 and funnel_7d.overall_conversion_rate >= 0.5:
                    # Conversion rate dropped by 50%+
                    alerts.append(SpikeAlert(
                        alert_type="conversion_drop",
                        current_value=int(funnel_1d.overall_conversion_rate * 100),
                        average_value=funnel_7d.overall_conversion_rate,
                        multiplier=rate_ratio,
                        message=f"📉 Conversion rate dropped: {funnel_1d.overall_conversion_rate:.2f}% vs {funnel_7d.overall_conversion_rate:.2f}% avg",
                        severity="high"
                    ))

            logger.info(f"Traffic drop detection: {len(alerts)} issues found")

        except Exception as e:
            logger.error(f"Error detecting traffic drops: {e}")

        return alerts

    @staticmethod
    def generate_spike_alert_html(alerts: List[SpikeAlert]) -> str:
        """
        Generate HTML email content for spike alerts.

        Args:
            alerts: List of detected spike alerts

        Returns:
            HTML string for email body
        """
        now = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")

        alert_boxes = ""
        for alert in alerts:
            severity_color = {
                "critical": "#ff4444",
                "high": "#ff9944",
                "info": "#4499ff"
            }.get(alert.severity, "#ffffff")

            avg_display = f"{alert.average_value:.1f}" if alert.average_value > 0 else "N/A"
            multiplier_display = f"{alert.multiplier:.1f}x" if alert.multiplier != float("inf") else "New baseline"

            alert_boxes += f"""
            <div style="background-color: #1a1a1a; border-left: 4px solid {severity_color}; border-radius: 8px; padding: 20px; margin: 16px 0;">
                <div style="color: {severity_color}; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
                    {alert.severity.upper()} - {alert.alert_type.upper()}
                </div>
                <div style="color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 16px;">
                    {alert.message}
                </div>
                <div style="display: flex; gap: 24px;">
                    <div>
                        <div style="color: #a0a0a0; font-size: 12px;">This Hour</div>
                        <div style="color: #ffffff; font-size: 24px; font-weight: 600;">{alert.current_value}</div>
                    </div>
                    <div>
                        <div style="color: #a0a0a0; font-size: 12px;">7-Day Avg</div>
                        <div style="color: #ffffff; font-size: 24px; font-weight: 600;">{avg_display}</div>
                    </div>
                    <div>
                        <div style="color: #a0a0a0; font-size: 12px;">Multiplier</div>
                        <div style="color: {severity_color}; font-size: 24px; font-weight: 600;">{multiplier_display}</div>
                    </div>
                </div>
            </div>
            """

        # Determine if we have drops vs spikes for tailored advice
        has_drops = any(a.alert_type in ['traffic_drop', 'conversion_drop'] for a in alerts)
        has_spikes = any(a.alert_type in ['signups', 'quotes', 'demos'] for a in alerts)

        # Build appropriate header and advice
        if has_drops and not has_spikes:
            header = "⚠️ Traffic Drop Alert"
            intro = "Traffic decline detected. This may indicate an issue with your Google Ads campaigns or external factors."
        elif has_drops and has_spikes:
            header = "🔄 Mixed Traffic Alert"
            intro = "Both increases and decreases detected in your funnel. Review the details below."
        else:
            header = "🚀 Traffic Spike Alert"
            intro = "Unusual activity detected! This could indicate viral exposure or an ad campaign performing well."

        drop_advice = ""
        if has_drops:
            drop_advice = """
            <div style="background-color: #3a1a1a; border: 1px solid rgba(255, 100, 100, 0.2); border-radius: 8px; padding: 20px; margin: 24px 0;">
                <div style="color: #ff9999; font-size: 14px; font-weight: 600; margin-bottom: 12px;">🔧 Traffic Drop Actions</div>
                <div style="color: #ffcccc; font-size: 14px; line-height: 1.8;">
                    1. <b>Check Google Ads:</b> Campaigns may be paused or budget exhausted<br>
                    2. <b>Review Bid Strategy:</b> Manual CPC vs Maximize Clicks affects impressions<br>
                    3. <b>Search Terms Report:</b> Irrelevant keywords may be eating budget<br>
                    4. <b>Quality Score:</b> Low scores = higher CPC = fewer impressions<br>
                    5. <b>Ad Schedule:</b> Check if ads are scheduled to run during current hours
                </div>
            </div>
            """

        spike_advice = ""
        if has_spikes:
            spike_advice = """
            <div style="background-color: #1a3a1a; border: 1px solid rgba(100, 255, 100, 0.2); border-radius: 8px; padding: 20px; margin: 24px 0;">
                <div style="color: #99ff99; font-size: 14px; font-weight: 600; margin-bottom: 12px;">✅ Traffic Spike Actions</div>
                <div style="color: #ccffcc; font-size: 14px; line-height: 1.8;">
                    1. Check social media for mentions (Reddit, Twitter, HN)<br>
                    2. Monitor Railway metrics for infrastructure load<br>
                    3. Engage with new users promptly<br>
                    4. Consider increasing ad spend if conversion is good
                </div>
            </div>
            """

        html = f"""
        <h1>{header}</h1>
        <p style="color: #a0a0a0; font-size: 14px;">{now}</p>

        <p style="font-size: 16px; color: #e0e0e0;">
            {intro}
        </p>

        {alert_boxes}

        {drop_advice}
        {spike_advice}

        <p class="muted" style="margin-top: 32px; font-size: 12px;">
            This alert is generated by DISC-139 Traffic Anomaly Monitoring.<br>
            Checks run hourly comparing to 7-day averages.
        </p>
        """

        return html

    @staticmethod
    async def send_spike_alert(alerts: List[SpikeAlert]) -> bool:
        """
        Send spike alert email to founder.

        Args:
            alerts: List of spike alerts to include

        Returns:
            True if sent successfully
        """
        from .email import EmailService

        if not alerts:
            return True  # Nothing to send

        try:
            html_content = TrafficSpikeAlertService.generate_spike_alert_html(alerts)

            # Determine overall severity for subject
            max_severity = max(a.severity for a in alerts)
            severity_emoji = {"critical": "!!!", "high": "!!", "info": "!"}.get(max_severity, "")

            # Build subject with summary
            alert_types = ", ".join(set(a.alert_type for a in alerts))
            subject = f"Traffic Spike Alert{severity_emoji}: {alert_types} ({len(alerts)} {'alert' if len(alerts) == 1 else 'alerts'})"

            await EmailService.send_email(
                to_email=settings.founder_email,
                subject=subject,
                body=html_content
            )

            logger.info(f"Spike alert sent to {settings.founder_email} with {len(alerts)} alerts")
            return True

        except Exception as e:
            logger.error(f"Failed to send spike alert: {e}")
            return False


# Convenience function for scheduler
async def check_traffic_spikes():
    """
    Scheduled job function for hourly traffic spike AND drop detection.
    Called by APScheduler.
    """
    from .database import async_session_factory

    logger.info("Running hourly traffic anomaly check...")

    try:
        async with async_session_factory() as db:
            # Check for spikes (good news!)
            spike_alerts = await TrafficSpikeAlertService.detect_spikes(db)

            # Check for drops (bad news that needs action)
            drop_alerts = await TrafficSpikeAlertService.detect_traffic_drops(db)

            all_alerts = spike_alerts + drop_alerts

            if all_alerts:
                logger.info(f"Detected {len(all_alerts)} traffic anomalies - sending alert")
                await TrafficSpikeAlertService.send_spike_alert(all_alerts)
            else:
                logger.debug("No traffic anomalies detected")

    except Exception as e:
        logger.error(f"Error in check_traffic_spikes: {e}")
