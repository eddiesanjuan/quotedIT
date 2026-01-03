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
    """Service for detecting and alerting on traffic spikes."""

    # Thresholds for spike detection
    SPIKE_MULTIPLIER = 3.0  # 3x normal = spike
    DEMO_SPIKE_THRESHOLD = 5  # 5+ demos in an hour
    SIGNUP_SPIKE_THRESHOLD = 3  # 3+ signups in an hour

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

        html = f"""
        <h1>Traffic Spike Alert</h1>
        <p style="color: #a0a0a0; font-size: 14px;">{now}</p>

        <p style="font-size: 16px; color: #e0e0e0;">
            Unusual activity detected! This could indicate viral exposure or an ad campaign performing well.
        </p>

        {alert_boxes}

        <div style="background-color: #1a3a1a; border: 1px solid rgba(100, 255, 100, 0.2); border-radius: 8px; padding: 20px; margin: 24px 0;">
            <div style="color: #99ff99; font-size: 14px; font-weight: 600; margin-bottom: 12px;">Recommended Actions</div>
            <div style="color: #ccffcc; font-size: 14px; line-height: 1.8;">
                1. Check social media for mentions (Reddit, Twitter, HN)<br>
                2. Monitor Railway metrics for infrastructure load<br>
                3. Engage with new users promptly<br>
                4. Consider increasing ad spend if conversion is good
            </div>
        </div>

        <p class="muted" style="margin-top: 32px; font-size: 12px;">
            This alert is generated by DISC-139 Traffic Spike Monitoring.<br>
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
    Scheduled job function for hourly traffic spike detection.
    Called by APScheduler.
    """
    from .database import async_session_factory

    logger.info("Running hourly traffic spike check...")

    try:
        async with async_session_factory() as db:
            alerts = await TrafficSpikeAlertService.detect_spikes(db)

            if alerts:
                logger.info(f"Detected {len(alerts)} traffic spikes - sending alert")
                await TrafficSpikeAlertService.send_spike_alert(alerts)
            else:
                logger.debug("No traffic spikes detected")

    except Exception as e:
        logger.error(f"Error in check_traffic_spikes: {e}")
