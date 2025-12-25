"""
Smart Follow-Up Engine for Quoted (INNOV-3).

AI-optimized follow-up timing based on:
- Quote view patterns (count, timing, frequency)
- Customer behavior signals
- Optimal engagement windows

Key insight: 80% of sales require 5+ follow-ups, but contractors
feel awkward following up. This automates the uncomfortable.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import Quote, Contractor, FollowUpSequence, FollowUpEvent
from .logging import get_logger
from .email import EmailService
from .analytics import analytics_service

logger = get_logger("quoted.follow_up")


class FollowUpSignal(Enum):
    """Signals that indicate customer engagement level."""
    NEVER_VIEWED = "never_viewed"              # Quote not opened
    SINGLE_VIEW = "single_view"                # Viewed once
    MULTIPLE_VIEWS = "multiple_views"          # 3+ views - high interest
    LATE_NIGHT_VIEWS = "late_night_views"      # Viewing at unusual hours - urgent need
    REPEAT_VIEWS = "repeat_views"              # Coming back multiple times - comparing options
    LONG_SESSION = "long_session"              # Spending time on quote - serious consideration
    PDF_DOWNLOADED = "pdf_downloaded"          # Downloaded PDF - ready to decide


@dataclass
class FollowUpRecommendation:
    """Recommendation for when and how to follow up."""
    should_follow_up: bool
    recommended_delay_hours: int
    signal: FollowUpSignal
    urgency: str  # low, medium, high, critical
    message_template: str
    reasoning: str


class SmartFollowUpEngine:
    """
    AI-powered follow-up timing and messaging engine.

    The engine analyzes quote viewing patterns to determine:
    1. WHEN to follow up (optimal timing)
    2. HOW urgent the follow-up is
    3. WHAT to say (contextual messaging)
    """

    # Default follow-up sequence timing (hours after quote sent)
    DEFAULT_SEQUENCE = [
        72,    # 3 days - first gentle touch
        168,   # 7 days - check-in
        336,   # 14 days - final outreach
    ]

    # Smart timing adjustments based on signals
    SIGNAL_TIMING = {
        FollowUpSignal.NEVER_VIEWED: {
            "delay": 72,
            "urgency": "medium",
            "template": "not_viewed",
            "reasoning": "Quote hasn't been opened - may have missed the email"
        },
        FollowUpSignal.SINGLE_VIEW: {
            "delay": 48,
            "urgency": "low",
            "template": "single_view",
            "reasoning": "Viewed once - give them time to think"
        },
        FollowUpSignal.MULTIPLE_VIEWS: {
            "delay": 6,
            "urgency": "high",
            "template": "high_interest",
            "reasoning": "Multiple views indicate active consideration - strike while hot"
        },
        FollowUpSignal.LATE_NIGHT_VIEWS: {
            "delay": 4,
            "urgency": "critical",
            "template": "urgent_need",
            "reasoning": "Late night research suggests urgent need or deadline"
        },
        FollowUpSignal.REPEAT_VIEWS: {
            "delay": 12,
            "urgency": "high",
            "template": "comparing_options",
            "reasoning": "Coming back multiple times - likely comparing to competitors"
        },
        FollowUpSignal.LONG_SESSION: {
            "delay": 8,
            "urgency": "high",
            "template": "serious_buyer",
            "reasoning": "Spending significant time on quote - serious consideration"
        },
        FollowUpSignal.PDF_DOWNLOADED: {
            "delay": 4,
            "urgency": "critical",
            "template": "ready_to_decide",
            "reasoning": "Downloaded PDF - actively sharing or comparing"
        },
    }

    # Email templates for different scenarios
    EMAIL_TEMPLATES = {
        "not_viewed": {
            "subject": "Did you receive my quote?",
            "body": """Hi {customer_name},

I wanted to make sure my quote reached you. I sent it over on {sent_date} for the {job_type} project.

If you have any questions or need anything adjusted, just let me know!

{contractor_name}
{contractor_phone}"""
        },
        "single_view": {
            "subject": "Any questions on the quote?",
            "body": """Hi {customer_name},

I saw you had a chance to look at the quote I sent for {job_type}.

If anything doesn't look right or you'd like to discuss the scope, I'm happy to chat.

{contractor_name}
{contractor_phone}"""
        },
        "high_interest": {
            "subject": "Ready when you are",
            "body": """Hi {customer_name},

I noticed you've been reviewing the quote for {job_type} - great!

I have some availability opening up soon and wanted to see if you're ready to move forward. I can answer any questions you have.

{contractor_name}
{contractor_phone}"""
        },
        "urgent_need": {
            "subject": "Can I help move this forward?",
            "body": """Hi {customer_name},

I can tell the {job_type} project is on your mind. If you need this done quickly, I can prioritize getting it scheduled.

Let me know if you'd like to discuss timing or have any questions.

{contractor_name}
{contractor_phone}"""
        },
        "comparing_options": {
            "subject": "A few things that set me apart",
            "body": """Hi {customer_name},

When you're comparing quotes for {job_type}, here's what I offer:

- {differentiator_1}
- {differentiator_2}
- {differentiator_3}

Happy to answer any questions that help you decide.

{contractor_name}
{contractor_phone}"""
        },
        "serious_buyer": {
            "subject": "Let's make this happen",
            "body": """Hi {customer_name},

I see you're seriously considering the {job_type} project. That's great!

I'd love to get this on the schedule. What questions can I answer to help you decide?

{contractor_name}
{contractor_phone}"""
        },
        "ready_to_decide": {
            "subject": "Ready to get started?",
            "body": """Hi {customer_name},

It looks like you're ready to move forward with {job_type}.

If you'd like to proceed, just click the accept button in the quote, or give me a call and we can get you scheduled.

{contractor_name}
{contractor_phone}"""
        },
    }

    @classmethod
    def analyze_viewing_pattern(
        cls,
        quote: Quote,
    ) -> FollowUpSignal:
        """
        Analyze quote viewing pattern to determine customer signal.

        Returns the strongest signal based on viewing behavior.
        """
        view_count = quote.view_count or 0
        first_viewed = quote.first_viewed_at
        last_viewed = quote.last_viewed_at
        pdf_downloaded = getattr(quote, 'pdf_downloaded', False)

        # Check for PDF download first (strongest buying signal)
        if pdf_downloaded:
            return FollowUpSignal.PDF_DOWNLOADED

        # Never viewed
        if view_count == 0:
            return FollowUpSignal.NEVER_VIEWED

        # Check for late night viewing (10pm - 6am local time)
        if last_viewed:
            view_hour = last_viewed.hour
            if view_hour >= 22 or view_hour < 6:
                return FollowUpSignal.LATE_NIGHT_VIEWS

        # Multiple views indicates high interest
        if view_count >= 3:
            return FollowUpSignal.MULTIPLE_VIEWS

        # Check for repeat views (same quote, different sessions)
        if view_count >= 2 and first_viewed and last_viewed:
            time_between = last_viewed - first_viewed
            if time_between.total_seconds() > 3600:  # > 1 hour between views
                return FollowUpSignal.REPEAT_VIEWS

        # Default to single view
        return FollowUpSignal.SINGLE_VIEW

    @classmethod
    def get_recommendation(
        cls,
        quote: Quote,
        current_sequence_step: int = 0,
    ) -> FollowUpRecommendation:
        """
        Get follow-up recommendation for a quote.

        Returns recommendation on whether/when/how to follow up.
        """
        signal = cls.analyze_viewing_pattern(quote)
        timing = cls.SIGNAL_TIMING[signal]

        # Don't follow up on accepted/rejected quotes
        if quote.status in ['won', 'lost', 'accepted', 'rejected']:
            return FollowUpRecommendation(
                should_follow_up=False,
                recommended_delay_hours=0,
                signal=signal,
                urgency="none",
                message_template="",
                reasoning="Quote already has a final status"
            )

        return FollowUpRecommendation(
            should_follow_up=True,
            recommended_delay_hours=timing["delay"],
            signal=signal,
            urgency=timing["urgency"],
            message_template=timing["template"],
            reasoning=timing["reasoning"]
        )

    @classmethod
    def generate_follow_up_email(
        cls,
        quote: Quote,
        contractor: Contractor,
        template_key: str,
    ) -> Dict[str, str]:
        """
        Generate personalized follow-up email content.

        Returns dict with 'subject' and 'body'.
        """
        template = cls.EMAIL_TEMPLATES.get(template_key, cls.EMAIL_TEMPLATES["single_view"])

        # Build differentiators for comparing_options template
        differentiators = [
            "Licensed and insured",
            "Free detailed estimates",
            "Guaranteed start dates",
        ]

        subject = template["subject"]
        body = template["body"].format(
            customer_name=quote.customer_name or "there",
            job_type=quote.job_type or "your project",
            sent_date=quote.sent_at.strftime("%B %d") if quote.sent_at else "recently",
            contractor_name=contractor.owner_name or contractor.business_name,
            contractor_phone=contractor.phone or "",
            differentiator_1=differentiators[0],
            differentiator_2=differentiators[1],
            differentiator_3=differentiators[2],
        )

        return {"subject": subject, "body": body}


class FollowUpService:
    """
    Service for managing follow-up sequences and sending follow-ups.
    """

    @staticmethod
    async def create_sequence(
        db: AsyncSession,
        quote_id: str,
        contractor_id: str,
    ) -> Optional[str]:
        """
        Create a follow-up sequence for a quote.

        Returns sequence ID or None if already exists.
        """
        # Check if sequence already exists
        existing = await db.execute(
            select(FollowUpSequence).where(
                FollowUpSequence.quote_id == quote_id
            )
        )
        if existing.scalar_one_or_none():
            return None

        # Get quote for initial analysis
        quote_result = await db.execute(
            select(Quote).where(Quote.id == quote_id)
        )
        quote = quote_result.scalar_one_or_none()
        if not quote:
            return None

        # Calculate initial follow-up timing
        recommendation = SmartFollowUpEngine.get_recommendation(quote)

        sequence = FollowUpSequence(
            quote_id=quote_id,
            contractor_id=contractor_id,
            status="active",
            current_step=0,
            next_follow_up_at=datetime.utcnow() + timedelta(hours=recommendation.recommended_delay_hours),
            detected_signal=recommendation.signal.value,
        )

        db.add(sequence)
        await db.commit()
        await db.refresh(sequence)

        return str(sequence.id)

    # Maximum follow-up steps before stopping
    MAX_STEPS = 3

    @staticmethod
    async def process_due_followups(db: AsyncSession) -> int:
        """
        Process all follow-ups that are due.

        Returns count of follow-ups sent.
        """
        now = datetime.utcnow()

        # Get sequences due for follow-up
        result = await db.execute(
            select(FollowUpSequence).where(
                and_(
                    FollowUpSequence.status == "active",
                    FollowUpSequence.next_follow_up_at <= now,
                    FollowUpSequence.current_step < FollowUpService.MAX_STEPS
                )
            )
        )
        due_sequences = result.scalars().all()

        if not due_sequences:
            return 0

        sent_count = 0
        email_service = EmailService()

        for sequence in due_sequences:
            try:
                # Get quote and contractor
                quote_result = await db.execute(
                    select(Quote).where(Quote.id == sequence.quote_id)
                )
                quote = quote_result.scalar_one_or_none()

                contractor_result = await db.execute(
                    select(Contractor).where(Contractor.id == sequence.contractor_id)
                )
                contractor = contractor_result.scalar_one_or_none()

                if not quote or not contractor:
                    sequence.status = "cancelled"
                    continue

                # Skip if quote is resolved
                if quote.status in ['won', 'lost', 'accepted', 'rejected']:
                    sequence.status = "completed"
                    continue

                # Get smart recommendation
                recommendation = SmartFollowUpEngine.get_recommendation(
                    quote,
                    current_sequence_step=sequence.current_step
                )

                if not recommendation.should_follow_up:
                    sequence.status = "completed"
                    continue

                # Generate and send email
                email_content = SmartFollowUpEngine.generate_follow_up_email(
                    quote=quote,
                    contractor=contractor,
                    template_key=recommendation.message_template,
                )

                # Get customer email
                customer_email = quote.customer_email
                if not customer_email:
                    logger.warning(f"No customer email for quote {quote.id}")
                    continue

                # Send the follow-up email
                await email_service.send_email(
                    to_email=customer_email,
                    subject=email_content["subject"],
                    body=email_content["body"],
                    reply_to=contractor.email,
                )

                # Record the event
                event = FollowUpEvent(
                    sequence_id=sequence.id,
                    event_type="email_sent",
                    step_number=sequence.current_step,
                    event_data={
                        "template": recommendation.message_template,
                        "subject": email_content["subject"],
                        "to_email": customer_email,
                        "signal": recommendation.signal.value,
                        "urgency": recommendation.urgency,
                        "reasoning": recommendation.reasoning,
                    }
                )
                db.add(event)

                # Update sequence
                sequence.current_step += 1
                sequence.emails_sent = (sequence.emails_sent or 0) + 1
                sequence.detected_signal = recommendation.signal.value

                # Calculate next follow-up
                if sequence.current_step < FollowUpService.MAX_STEPS:
                    next_rec = SmartFollowUpEngine.get_recommendation(
                        quote,
                        current_sequence_step=sequence.current_step
                    )
                    sequence.next_follow_up_at = now + timedelta(hours=next_rec.recommended_delay_hours)
                else:
                    sequence.status = "completed"
                    sequence.completed_at = now
                    sequence.completion_reason = "max_attempts"

                sent_count += 1

                # Track analytics
                try:
                    analytics_service.track_event(
                        user_id=str(contractor.user_id),
                        event_name="follow_up_sent",
                        properties={
                            "quote_id": str(quote.id),
                            "step": sequence.current_step,
                            "signal": recommendation.signal.value,
                            "urgency": recommendation.urgency,
                            "template": recommendation.message_template,
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to track follow_up_sent: {e}")

            except Exception as e:
                logger.error(f"Error processing follow-up {sequence.id}: {e}")

        await db.commit()
        return sent_count

    @staticmethod
    async def pause_sequence(db: AsyncSession, quote_id: str) -> bool:
        """Pause follow-up sequence for a quote."""
        result = await db.execute(
            select(FollowUpSequence).where(FollowUpSequence.quote_id == quote_id)
        )
        sequence = result.scalar_one_or_none()

        if not sequence or sequence.status != "active":
            return False

        sequence.status = "paused"

        # Record pause event
        event = FollowUpEvent(
            sequence_id=sequence.id,
            event_type="sequence_paused",
            step_number=sequence.current_step,
            event_data={"paused_at": datetime.utcnow().isoformat()}
        )
        db.add(event)

        await db.commit()
        return True

    @staticmethod
    async def resume_sequence(db: AsyncSession, quote_id: str) -> bool:
        """Resume a paused follow-up sequence."""
        result = await db.execute(
            select(FollowUpSequence).where(FollowUpSequence.quote_id == quote_id)
        )
        sequence = result.scalar_one_or_none()

        if not sequence or sequence.status != "paused":
            return False

        sequence.status = "active"
        # Recalculate next follow-up time
        quote_result = await db.execute(
            select(Quote).where(Quote.id == quote_id)
        )
        quote = quote_result.scalar_one_or_none()

        if quote:
            recommendation = SmartFollowUpEngine.get_recommendation(
                quote,
                current_sequence_step=sequence.current_step
            )
            sequence.next_follow_up_at = datetime.utcnow() + timedelta(
                hours=recommendation.recommended_delay_hours
            )

            # Record resume event
            event = FollowUpEvent(
                sequence_id=sequence.id,
                event_type="sequence_resumed",
                step_number=sequence.current_step,
                event_data={"resumed_at": datetime.utcnow().isoformat()}
            )
            db.add(event)

        await db.commit()
        return True

    @staticmethod
    async def get_sequence_status(
        db: AsyncSession,
        quote_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get follow-up sequence status for a quote."""
        result = await db.execute(
            select(FollowUpSequence).where(FollowUpSequence.quote_id == quote_id)
        )
        sequence = result.scalar_one_or_none()

        if not sequence:
            return None

        # Get events
        events_result = await db.execute(
            select(FollowUpEvent)
            .where(FollowUpEvent.sequence_id == sequence.id)
            .order_by(FollowUpEvent.created_at.desc())
        )
        events = events_result.scalars().all()

        return {
            "id": str(sequence.id),
            "status": sequence.status,
            "current_step": sequence.current_step,
            "max_steps": FollowUpService.MAX_STEPS,
            "next_follow_up_at": sequence.next_follow_up_at.isoformat() if sequence.next_follow_up_at else None,
            "detected_signal": sequence.detected_signal,
            "emails_sent": sequence.emails_sent or 0,
            "events": [
                {
                    "type": e.event_type,
                    "step": e.step_number,
                    "data": e.event_data,
                    "created_at": e.created_at.isoformat(),
                }
                for e in events
            ]
        }


# Convenience function for scheduler integration
async def run_smart_followups():
    """Run smart follow-up processing. Called by scheduler."""
    from .database import async_session_factory

    logger.info("Running smart follow-up engine")

    try:
        async with async_session_factory() as db:
            sent = await FollowUpService.process_due_followups(db)
            if sent > 0:
                logger.info(f"Sent {sent} smart follow-up emails")
            else:
                logger.debug("No follow-ups due")
    except Exception as e:
        logger.error(f"Error in run_smart_followups: {e}")
