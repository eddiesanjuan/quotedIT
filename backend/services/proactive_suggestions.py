"""
INNOV-9: Proactive Suggestions Service for Quoted.

Analyzes contractor data and surfaces timely, actionable suggestions:
- Re-engagement opportunities (dormant customers)
- Pricing optimization hints (win rate analysis)
- Follow-up reminders (stale quotes)
- Business health alerts (revenue trends)
- Quote optimization tips (based on patterns)

Core Principle: Surface the RIGHT insight at the RIGHT time.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from .logging import get_logger

logger = get_logger("quoted.proactive_suggestions")


@dataclass
class Suggestion:
    """A proactive suggestion for the contractor."""
    id: str  # Unique ID for tracking dismissal
    type: Literal[
        "re_engagement",      # Customer hasn't been quoted in a while
        "pricing_hint",       # Win rate suggests price adjustment
        "follow_up",          # Stale quotes need attention
        "revenue_alert",      # Revenue trend warning
        "quote_optimization", # Tips for better quotes
        "learning_milestone", # Learning system milestone reached
        "efficiency_tip",     # Time/effort optimization
    ]
    priority: Literal["high", "medium", "low"]
    title: str
    message: str
    action_label: Optional[str] = None  # CTA button text
    action_url: Optional[str] = None  # Where to go
    data: Dict[str, Any] = field(default_factory=dict)
    dismissible: bool = True
    expires_at: Optional[str] = None  # When this becomes stale

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "priority": self.priority,
            "title": self.title,
            "message": self.message,
            "action_label": self.action_label,
            "action_url": self.action_url,
            "data": self.data,
            "dismissible": self.dismissible,
            "expires_at": self.expires_at,
        }


class ProactiveSuggestionsService:
    """
    Generates proactive suggestions based on contractor data analysis.

    Usage:
        service = ProactiveSuggestionsService()
        suggestions = await service.get_suggestions(db, contractor_id)
    """

    # Thresholds for triggering suggestions
    DORMANT_CUSTOMER_DAYS = 90  # Days since last quote
    STALE_QUOTE_DAYS = 7  # Days a sent quote hasn't been viewed/acted on
    LOW_WIN_RATE_THRESHOLD = 0.3  # Below this suggests pricing too high
    HIGH_WIN_RATE_THRESHOLD = 0.8  # Above this suggests pricing too low
    REVENUE_DROP_THRESHOLD = 0.2  # 20% drop triggers alert
    MIN_QUOTES_FOR_PRICING_HINT = 10  # Need enough data

    async def get_suggestions(
        self,
        db: AsyncSession,
        contractor_id: str,
        max_suggestions: int = 5,
    ) -> List[Suggestion]:
        """
        Get all proactive suggestions for a contractor.

        Runs multiple analyzers and returns prioritized suggestions.

        Args:
            db: Database session
            contractor_id: Contractor to analyze
            max_suggestions: Maximum suggestions to return

        Returns:
            List of Suggestion objects, sorted by priority
        """
        suggestions = []

        # Run all analyzers in parallel (async)
        try:
            # Each analyzer adds suggestions to the list
            suggestions.extend(await self._analyze_dormant_customers(db, contractor_id))
            suggestions.extend(await self._analyze_stale_quotes(db, contractor_id))
            suggestions.extend(await self._analyze_pricing(db, contractor_id))
            suggestions.extend(await self._analyze_revenue(db, contractor_id))
            suggestions.extend(await self._analyze_learning_milestones(db, contractor_id))
            suggestions.extend(await self._analyze_efficiency(db, contractor_id))

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")

        # Sort by priority and limit
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 99))

        return suggestions[:max_suggestions]

    async def _analyze_dormant_customers(
        self,
        db: AsyncSession,
        contractor_id: str,
    ) -> List[Suggestion]:
        """Find customers who haven't been quoted recently."""
        from ..models.database import Customer

        suggestions = []
        cutoff = datetime.utcnow() - timedelta(days=self.DORMANT_CUSTOMER_DAYS)

        result = await db.execute(
            select(Customer)
            .where(
                and_(
                    Customer.contractor_id == contractor_id,
                    Customer.status == "active",
                    Customer.last_quote_at < cutoff,
                    Customer.total_won > 0,  # Only customers who've bought before
                )
            )
            .order_by(Customer.total_won.desc())
            .limit(3)
        )
        dormant_customers = result.scalars().all()

        for customer in dormant_customers:
            days_since = (datetime.utcnow() - customer.last_quote_at).days if customer.last_quote_at else 0
            suggestions.append(Suggestion(
                id=f"dormant_{customer.id}",
                type="re_engagement",
                priority="medium",
                title=f"Reconnect with {customer.name}",
                message=f"It's been {days_since} days since you last quoted {customer.name}. "
                        f"They've spent ${customer.total_won:,.0f} with you previously.",
                action_label="Create Quote",
                action_url=f"/quotes/new?customer_id={customer.id}",
                data={
                    "customer_id": str(customer.id),
                    "customer_name": customer.name,
                    "days_since_quote": days_since,
                    "total_spent": customer.total_won,
                },
            ))

        return suggestions

    async def _analyze_stale_quotes(
        self,
        db: AsyncSession,
        contractor_id: str,
    ) -> List[Suggestion]:
        """Find quotes that need follow-up attention."""
        from ..models.database import Quote

        suggestions = []
        cutoff = datetime.utcnow() - timedelta(days=self.STALE_QUOTE_DAYS)

        # Sent quotes not viewed
        result = await db.execute(
            select(Quote)
            .where(
                and_(
                    Quote.contractor_id == contractor_id,
                    Quote.status == "sent",
                    Quote.sent_at < cutoff,
                    Quote.view_count == 0,
                )
            )
            .limit(5)
        )
        unviewed_quotes = result.scalars().all()

        if len(unviewed_quotes) >= 2:
            total_value = sum(q.total or 0 for q in unviewed_quotes)
            suggestions.append(Suggestion(
                id=f"stale_unviewed_{datetime.utcnow().date().isoformat()}",
                type="follow_up",
                priority="high",
                title=f"{len(unviewed_quotes)} quotes haven't been opened",
                message=f"${total_value:,.0f} in quotes sent over {self.STALE_QUOTE_DAYS} days ago "
                        f"haven't been viewed yet. Consider resending or calling.",
                action_label="View Quotes",
                action_url="/quotes?status=sent",
                data={
                    "count": len(unviewed_quotes),
                    "total_value": total_value,
                    "quote_ids": [str(q.id) for q in unviewed_quotes],
                },
            ))

        # Viewed but no action
        result = await db.execute(
            select(Quote)
            .where(
                and_(
                    Quote.contractor_id == contractor_id,
                    Quote.status == "viewed",
                    Quote.first_viewed_at < cutoff,
                )
            )
            .limit(5)
        )
        pending_quotes = result.scalars().all()

        if len(pending_quotes) >= 2:
            total_value = sum(q.total or 0 for q in pending_quotes)
            suggestions.append(Suggestion(
                id=f"stale_pending_{datetime.utcnow().date().isoformat()}",
                type="follow_up",
                priority="high",
                title=f"{len(pending_quotes)} quotes awaiting decision",
                message=f"${total_value:,.0f} in quotes have been viewed but not accepted/rejected. "
                        f"A quick follow-up call could close these.",
                action_label="View Pending",
                action_url="/quotes?status=viewed",
                data={
                    "count": len(pending_quotes),
                    "total_value": total_value,
                    "quote_ids": [str(q.id) for q in pending_quotes],
                },
            ))

        return suggestions

    async def _analyze_pricing(
        self,
        db: AsyncSession,
        contractor_id: str,
    ) -> List[Suggestion]:
        """Analyze win rates to suggest pricing adjustments."""
        from ..models.database import Quote

        suggestions = []

        # Get quotes from last 90 days with outcomes
        cutoff = datetime.utcnow() - timedelta(days=90)

        result = await db.execute(
            select(Quote)
            .where(
                and_(
                    Quote.contractor_id == contractor_id,
                    Quote.created_at >= cutoff,
                    or_(
                        Quote.status == "won",
                        Quote.status == "lost",
                        Quote.outcome == "won",
                        Quote.outcome == "lost",
                    )
                )
            )
        )
        quotes = result.scalars().all()

        if len(quotes) < self.MIN_QUOTES_FOR_PRICING_HINT:
            return suggestions

        # Calculate overall win rate
        won = sum(1 for q in quotes if q.status == "won" or q.outcome == "won")
        total = len(quotes)
        win_rate = won / total if total > 0 else 0

        if win_rate < self.LOW_WIN_RATE_THRESHOLD:
            suggestions.append(Suggestion(
                id=f"pricing_high_{datetime.utcnow().date().isoformat()}",
                type="pricing_hint",
                priority="medium",
                title="Your win rate is low",
                message=f"You're winning only {win_rate*100:.0f}% of quotes. "
                        f"Consider adjusting prices or improving quote presentation.",
                action_label="View Analytics",
                action_url="/analytics",
                data={
                    "win_rate": win_rate,
                    "won_count": won,
                    "total_count": total,
                    "suggestion": "price_too_high",
                },
            ))
        elif win_rate > self.HIGH_WIN_RATE_THRESHOLD:
            avg_quote = sum(q.total or 0 for q in quotes) / len(quotes) if quotes else 0
            potential_increase = avg_quote * 0.1  # 10% increase
            suggestions.append(Suggestion(
                id=f"pricing_low_{datetime.utcnow().date().isoformat()}",
                type="pricing_hint",
                priority="low",
                title="Consider raising your prices",
                message=f"You're winning {win_rate*100:.0f}% of quotes! "
                        f"A 10% price increase could add ~${potential_increase:,.0f} per job.",
                action_label="View Pricing",
                action_url="/pricing-brain",
                data={
                    "win_rate": win_rate,
                    "won_count": won,
                    "total_count": total,
                    "suggestion": "price_too_low",
                    "potential_increase": potential_increase,
                },
            ))

        # Analyze by job type
        job_type_stats = {}
        for q in quotes:
            if q.job_type:
                if q.job_type not in job_type_stats:
                    job_type_stats[q.job_type] = {"won": 0, "total": 0}
                job_type_stats[q.job_type]["total"] += 1
                if q.status == "won" or q.outcome == "won":
                    job_type_stats[q.job_type]["won"] += 1

        for job_type, stats in job_type_stats.items():
            if stats["total"] >= 5:  # Enough data for this type
                jt_win_rate = stats["won"] / stats["total"]
                if jt_win_rate < 0.25:  # Very low for this type
                    suggestions.append(Suggestion(
                        id=f"pricing_type_{job_type}_{datetime.utcnow().date().isoformat()}",
                        type="pricing_hint",
                        priority="medium",
                        title=f"Low win rate for {job_type} jobs",
                        message=f"Only {jt_win_rate*100:.0f}% of {job_type} quotes are winning. "
                                f"Review your pricing for this category.",
                        action_label="Review Category",
                        action_url=f"/pricing-brain/{job_type}",
                        data={
                            "job_type": job_type,
                            "win_rate": jt_win_rate,
                            "won_count": stats["won"],
                            "total_count": stats["total"],
                        },
                    ))

        return suggestions

    async def _analyze_revenue(
        self,
        db: AsyncSession,
        contractor_id: str,
    ) -> List[Suggestion]:
        """Analyze revenue trends and alert on drops."""
        from ..models.database import Quote

        suggestions = []

        # Compare this week to last week
        now = datetime.utcnow()
        this_week_start = now - timedelta(days=7)
        last_week_start = now - timedelta(days=14)

        # This week's won quotes
        result = await db.execute(
            select(func.sum(Quote.total))
            .where(
                and_(
                    Quote.contractor_id == contractor_id,
                    Quote.created_at >= this_week_start,
                    or_(Quote.status == "won", Quote.outcome == "won"),
                )
            )
        )
        this_week_revenue = result.scalar() or 0

        # Last week's won quotes
        result = await db.execute(
            select(func.sum(Quote.total))
            .where(
                and_(
                    Quote.contractor_id == contractor_id,
                    Quote.created_at >= last_week_start,
                    Quote.created_at < this_week_start,
                    or_(Quote.status == "won", Quote.outcome == "won"),
                )
            )
        )
        last_week_revenue = result.scalar() or 0

        if last_week_revenue > 0:
            change = (this_week_revenue - last_week_revenue) / last_week_revenue
            if change < -self.REVENUE_DROP_THRESHOLD:
                suggestions.append(Suggestion(
                    id=f"revenue_drop_{datetime.utcnow().date().isoformat()}",
                    type="revenue_alert",
                    priority="high",
                    title="Revenue is down this week",
                    message=f"Won revenue is down {abs(change)*100:.0f}% from last week "
                            f"(${this_week_revenue:,.0f} vs ${last_week_revenue:,.0f}). "
                            f"Consider following up on pending quotes.",
                    action_label="View Dashboard",
                    action_url="/dashboard",
                    data={
                        "this_week": this_week_revenue,
                        "last_week": last_week_revenue,
                        "change_percent": change * 100,
                    },
                ))

        # Check quote volume
        result = await db.execute(
            select(func.count(Quote.id))
            .where(
                and_(
                    Quote.contractor_id == contractor_id,
                    Quote.created_at >= this_week_start,
                )
            )
        )
        this_week_count = result.scalar() or 0

        result = await db.execute(
            select(func.count(Quote.id))
            .where(
                and_(
                    Quote.contractor_id == contractor_id,
                    Quote.created_at >= last_week_start,
                    Quote.created_at < this_week_start,
                )
            )
        )
        last_week_count = result.scalar() or 0

        if last_week_count > 3 and this_week_count < last_week_count * 0.5:
            suggestions.append(Suggestion(
                id=f"quote_volume_{datetime.utcnow().date().isoformat()}",
                type="revenue_alert",
                priority="medium",
                title="Quote volume is down",
                message=f"Only {this_week_count} quotes this week vs {last_week_count} last week. "
                        f"Slow period or time for more marketing?",
                action_label="Create Quote",
                action_url="/quotes/new",
                data={
                    "this_week_count": this_week_count,
                    "last_week_count": last_week_count,
                },
            ))

        return suggestions

    async def _analyze_learning_milestones(
        self,
        db: AsyncSession,
        contractor_id: str,
    ) -> List[Suggestion]:
        """Check for learning system milestones."""
        from ..models.database import Quote

        suggestions = []

        # Count total quotes
        result = await db.execute(
            select(func.count(Quote.id))
            .where(Quote.contractor_id == contractor_id)
        )
        total_quotes = result.scalar() or 0

        # Milestone messages
        milestones = {
            10: ("10 quotes!", "Your pricing brain is starting to learn your patterns."),
            25: ("25 quotes!", "Your pricing accuracy should be noticeably improving."),
            50: ("50 quotes milestone!", "The AI has learned significant pricing patterns from your work."),
            100: ("100 quotes!", "You've built a robust pricing model. The AI knows your business well."),
            250: ("250 quotes - Expert level!", "Your pricing brain is now highly accurate for most jobs."),
        }

        for milestone, (title, message) in milestones.items():
            # Check if just passed milestone (within last 5 quotes)
            if milestone <= total_quotes < milestone + 5:
                suggestions.append(Suggestion(
                    id=f"milestone_{milestone}",
                    type="learning_milestone",
                    priority="low",
                    title=title,
                    message=message,
                    action_label="View Pricing Brain",
                    action_url="/pricing-brain",
                    data={
                        "milestone": milestone,
                        "total_quotes": total_quotes,
                    },
                    dismissible=True,
                ))
                break  # Only show one milestone

        return suggestions

    async def _analyze_efficiency(
        self,
        db: AsyncSession,
        contractor_id: str,
    ) -> List[Suggestion]:
        """Suggest efficiency improvements."""
        from ..models.database import Quote, Contractor

        suggestions = []

        # Check if contractor has logo
        result = await db.execute(
            select(Contractor).where(Contractor.id == contractor_id)
        )
        contractor = result.scalar_one_or_none()

        if contractor and not contractor.logo_url:
            # Count quotes to see if they're active
            result = await db.execute(
                select(func.count(Quote.id))
                .where(Quote.contractor_id == contractor_id)
            )
            quote_count = result.scalar() or 0

            if quote_count >= 5:  # Active user without logo
                suggestions.append(Suggestion(
                    id="add_logo",
                    type="efficiency_tip",
                    priority="low",
                    title="Add your logo for professional quotes",
                    message="Quotes with a company logo appear more professional "
                            "and can improve your win rate.",
                    action_label="Add Logo",
                    action_url="/settings/branding",
                    data={},
                ))

        return suggestions


# Singleton instance
proactive_suggestions = ProactiveSuggestionsService()
