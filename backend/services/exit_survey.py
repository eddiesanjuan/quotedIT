"""
Exit Survey Service (DISC-137).

Handles exit intent survey data:
- Storing survey responses
- Instant alerts for concerning keywords
- Daily digest generation and sending

Concerning keywords trigger immediate founder alerts:
- "bug", "broken", "doesn't work", "not working", "error"
- These indicate potential product issues that need immediate attention
"""

import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from collections import Counter

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import ExitSurvey
from ..config import settings
from .logging import get_logger

logger = get_logger("quoted.exit_survey")

# Keywords that trigger instant alerts (lowercase for matching)
CONCERNING_KEYWORDS = [
    "bug", "broken", "doesn't work", "doesn't work", "not working",
    "error", "crash", "crashed", "failing", "failed", "issue",
    "problem", "glitch", "down", "unavailable"
]

# Map of reason codes to human-readable labels
REASON_LABELS = {
    "not_my_trade": "Not sure it works for my trade",
    "pricing_high": "Pricing seems high",
    "no_time": "Don't have time right now",
    "need_examples": "Need to see real examples first",
    "other": "Other"
}


class ExitSurveyService:
    """Service for managing exit intent survey data."""

    @staticmethod
    async def create_survey(
        db: AsyncSession,
        reasons: List[str],
        other_text: Optional[str] = None,
        page_url: Optional[str] = None,
        referrer: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_hash: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ExitSurvey:
        """
        Create a new exit survey record.

        Args:
            db: Database session
            reasons: List of reason codes
            other_text: Verbatim "Other" reason
            page_url: URL where survey was shown
            referrer: HTTP referrer
            user_agent: Browser user agent
            ip_hash: Hashed IP for deduplication
            session_id: Browser session ID

        Returns:
            Created ExitSurvey record
        """
        survey = ExitSurvey(
            reasons=reasons,
            other_text=other_text,
            page_url=page_url,
            referrer=referrer,
            user_agent=user_agent,
            ip_hash=ip_hash,
            session_id=session_id
        )
        db.add(survey)
        await db.flush()

        logger.info(f"Created exit survey {survey.id}: reasons={reasons}")
        return survey

    @staticmethod
    def contains_concerning_keyword(text: str) -> bool:
        """
        Check if text contains any concerning keywords.

        Args:
            text: Text to check

        Returns:
            True if concerning keywords found
        """
        if not text:
            return False

        text_lower = text.lower()
        for keyword in CONCERNING_KEYWORDS:
            if keyword in text_lower:
                return True
        return False

    @staticmethod
    async def check_and_send_alert(
        db: AsyncSession,
        survey: ExitSurvey
    ) -> bool:
        """
        Check survey for concerning keywords and send instant alert if found.

        Args:
            db: Database session
            survey: ExitSurvey record to check

        Returns:
            True if alert was sent
        """
        if not survey.other_text:
            return False

        if not ExitSurveyService.contains_concerning_keyword(survey.other_text):
            return False

        # Send instant alert
        try:
            from .email import EmailService

            # Extract the triggering keywords for context
            text_lower = survey.other_text.lower()
            found_keywords = [k for k in CONCERNING_KEYWORDS if k in text_lower]

            content = f"""
            <h1>Exit Survey Alert</h1>

            <div style="background-color: #2a1a1a; border: 1px solid rgba(255, 100, 100, 0.3); border-radius: 8px; padding: 20px; margin: 24px 0;">
                <div style="color: #ff9999; font-size: 14px; font-weight: 600; margin-bottom: 12px;">
                    Concerning Keywords Detected
                </div>
                <div style="color: #ffcccc; font-size: 13px; margin-bottom: 12px;">
                    Keywords: {", ".join(found_keywords)}
                </div>
            </div>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #a0a0a0; font-size: 13px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Verbatim Feedback
                </div>
                <div style="color: #ffffff; font-size: 16px; line-height: 1.6; font-style: italic;">
                    "{survey.other_text}"
                </div>
            </div>

            <div style="background-color: #1a1a1a; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 20px; margin: 24px 0;">
                <div style="color: #ffffff; font-size: 14px; font-weight: 600; margin-bottom: 12px;">Survey Details</div>
                <div style="color: #e0e0e0; font-size: 14px; line-height: 1.8;">
                    <strong>Reasons Selected:</strong> {", ".join([REASON_LABELS.get(r, r) for r in survey.reasons])}<br>
                    <strong>Time:</strong> {survey.created_at.strftime("%Y-%m-%d %H:%M UTC") if survey.created_at else "N/A"}<br>
                    <strong>Page:</strong> {survey.page_url or "N/A"}
                </div>
            </div>

            <p class="muted" style="margin-top: 32px; font-size: 12px;">
                This alert is triggered by DISC-137 Exit Survey Reporting.<br>
                Concerning keywords: {", ".join(CONCERNING_KEYWORDS[:5])}...
            </p>
            """

            await EmailService.send_email(
                to_email=settings.founder_email,
                subject=f"Exit Survey Alert: \"{survey.other_text[:50]}...\"" if len(survey.other_text) > 50 else f"Exit Survey Alert: \"{survey.other_text}\"",
                body=content
            )

            # Mark alert as sent
            survey.alert_sent = True
            survey.alert_sent_at = datetime.utcnow()

            logger.info(f"Sent exit survey alert for survey {survey.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send exit survey alert: {e}")
            return False

    @staticmethod
    async def get_surveys_for_digest(
        db: AsyncSession,
        since: Optional[datetime] = None
    ) -> List[ExitSurvey]:
        """
        Get surveys that haven't been included in a digest yet.

        Args:
            db: Database session
            since: Only include surveys after this datetime

        Returns:
            List of ExitSurvey records
        """
        query = select(ExitSurvey).where(
            ExitSurvey.included_in_digest == False
        )

        if since:
            query = query.where(ExitSurvey.created_at >= since)

        query = query.order_by(ExitSurvey.created_at.desc())

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_daily_stats(
        db: AsyncSession,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated stats for a specific date.

        Args:
            db: Database session
            date: Date to query (defaults to yesterday)

        Returns:
            Dict with aggregated stats
        """
        if date is None:
            date = datetime.utcnow() - timedelta(days=1)

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Get surveys for the day
        result = await db.execute(
            select(ExitSurvey).where(
                and_(
                    ExitSurvey.created_at >= start_of_day,
                    ExitSurvey.created_at < end_of_day
                )
            )
        )
        surveys = result.scalars().all()

        # Aggregate reasons
        reason_counts = Counter()
        other_texts = []

        for survey in surveys:
            for reason in survey.reasons:
                reason_counts[reason] += 1
            if survey.other_text:
                other_texts.append(survey.other_text)

        return {
            "date": start_of_day,
            "total_count": len(surveys),
            "reason_counts": dict(reason_counts),
            "other_texts": other_texts
        }

    @staticmethod
    def generate_digest_html(
        stats: Dict[str, Any],
        prev_day_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate HTML content for daily digest email.

        Args:
            stats: Today's aggregated stats
            prev_day_stats: Previous day's stats for comparison

        Returns:
            HTML string for email body
        """
        date_str = stats["date"].strftime("%B %d, %Y")
        total = stats["total_count"]

        # Trend indicator
        trend = ""
        if prev_day_stats:
            prev_total = prev_day_stats["total_count"]
            if prev_total > 0:
                diff = total - prev_total
                if diff > 0:
                    trend = f"(+{diff} from previous day)"
                elif diff < 0:
                    trend = f"({diff} from previous day)"
                else:
                    trend = "(same as previous day)"

        # Build reason breakdown
        reason_html = ""
        if stats["reason_counts"]:
            reason_items = []
            for reason_code, count in sorted(stats["reason_counts"].items(), key=lambda x: -x[1]):
                label = REASON_LABELS.get(reason_code, reason_code)
                reason_items.append(f"<li><strong>{count}</strong> - {label}</li>")
            reason_html = f"""
            <div style="background-color: #1a1a1a; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 20px; margin: 24px 0;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 16px;">Reasons Breakdown</div>
                <ul style="color: #e0e0e0; font-size: 15px; line-height: 1.8; padding-left: 24px;">
                    {"".join(reason_items)}
                </ul>
            </div>
            """

        # Build other texts section (most valuable)
        other_html = ""
        if stats["other_texts"]:
            other_items = []
            for text in stats["other_texts"]:
                # Escape HTML in user input
                safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                other_items.append(f"""
                <div style="background-color: #1a1a1a; border-left: 3px solid #666; padding: 12px 16px; margin-bottom: 12px; color: #e0e0e0; font-style: italic;">
                    "{safe_text}"
                </div>
                """)
            other_html = f"""
            <div style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 600; margin-bottom: 16px;">Verbatim "Other" Responses (Most Valuable)</div>
                {"".join(other_items)}
            </div>
            """

        html = f"""
        <h1>Exit Survey Digest</h1>
        <p style="color: #a0a0a0; font-size: 14px;">{date_str}</p>

        <div class="stats-grid" style="margin: 24px 0;">
            <div class="stat-box">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Exit Surveys</div>
                <div style="color: #a0a0a0; font-size: 12px; margin-top: 8px;">{trend}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(stats["other_texts"])}</div>
                <div class="stat-label">With Comments</div>
            </div>
        </div>

        {reason_html}
        {other_html}

        <p class="muted" style="margin-top: 32px; font-size: 12px;">
            This digest is generated by DISC-137 Exit Survey Reporting.<br>
            Instant alerts are sent for concerning keywords (bug, broken, etc.).
        </p>
        """

        return html

    @staticmethod
    async def send_daily_digest(db: AsyncSession) -> bool:
        """
        Generate and send the daily exit survey digest.

        Args:
            db: Database session

        Returns:
            True if sent successfully
        """
        from .email import EmailService

        logger.info("Generating exit survey digest...")

        try:
            # Get yesterday's stats
            yesterday = datetime.utcnow() - timedelta(days=1)
            stats = await ExitSurveyService.get_daily_stats(db, yesterday)

            # Skip if no surveys
            if stats["total_count"] == 0:
                logger.info("No exit surveys yesterday, skipping digest")
                return True

            # Get day before for comparison
            day_before = yesterday - timedelta(days=1)
            prev_stats = await ExitSurveyService.get_daily_stats(db, day_before)

            # Generate HTML
            html_content = ExitSurveyService.generate_digest_html(stats, prev_stats)

            # Send email
            date_str = yesterday.strftime("%b %d")
            subject = f"Exit Surveys: {stats['total_count']} responses ({date_str})"

            await EmailService.send_email(
                to_email=settings.founder_email,
                subject=subject,
                body=html_content
            )

            # Mark surveys as included in digest
            start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_yesterday = start_of_yesterday + timedelta(days=1)

            result = await db.execute(
                select(ExitSurvey).where(
                    and_(
                        ExitSurvey.created_at >= start_of_yesterday,
                        ExitSurvey.created_at < end_of_yesterday,
                        ExitSurvey.included_in_digest == False
                    )
                )
            )
            surveys = result.scalars().all()
            for survey in surveys:
                survey.included_in_digest = True
                survey.digest_date = datetime.utcnow()

            await db.commit()

            logger.info(f"Exit survey digest sent to {settings.founder_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send exit survey digest: {e}")
            return False


# Convenience function for scheduler
async def run_exit_survey_digest():
    """
    Scheduled job function for daily exit survey digest.
    Called by APScheduler.
    """
    from .database import async_session_factory

    try:
        async with async_session_factory() as db:
            await ExitSurveyService.send_daily_digest(db)
    except Exception as e:
        logger.error(f"Error in run_exit_survey_digest: {e}")
