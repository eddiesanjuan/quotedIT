"""
Win/Loss Analytics Service for Quoted (INNOV-5).

Provides comprehensive analytics for quote outcomes:
- Win rate tracking over time periods
- Loss reason analysis and patterns
- Revenue insights from won quotes
- Trend comparisons (week over week, month over month)
- Performance by job type
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, asdict

from sqlalchemy import select, func, and_, case, or_
from sqlalchemy.ext.asyncio import AsyncSession

from .logging import get_logger

logger = get_logger("quoted.win_loss_analytics")


class TimePeriod(str, Enum):
    """Standard time periods for analytics."""
    TODAY = "today"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_QUARTER = "this_quarter"
    LAST_QUARTER = "last_quarter"
    THIS_YEAR = "this_year"
    LAST_YEAR = "last_year"
    ALL_TIME = "all_time"


@dataclass
class WinLossStats:
    """Win/loss statistics for a time period."""
    period: str
    start_date: str
    end_date: str
    total_quotes: int
    quotes_with_outcome: int
    won: int
    lost: int
    pending: int
    win_rate: float
    total_value_quoted: float
    total_value_won: float
    total_value_lost: float
    average_quote_value: float
    average_won_value: float
    average_days_to_win: Optional[float]
    average_days_to_loss: Optional[float]


@dataclass
class LossReasonAnalysis:
    """Analysis of loss reasons."""
    reason: str
    count: int
    total_value_lost: float
    percentage_of_losses: float
    average_value: float
    common_job_types: List[str]


@dataclass
class TrendComparison:
    """Comparison between two time periods."""
    current_period: str
    previous_period: str
    current_win_rate: float
    previous_win_rate: float
    win_rate_change: float
    current_quotes: int
    previous_quotes: int
    quotes_change_percent: float
    current_revenue: float
    previous_revenue: float
    revenue_change_percent: float


class WinLossAnalyticsService:
    """
    Analytics service for win/loss tracking and insights.
    """

    @staticmethod
    def get_date_range(period: TimePeriod) -> tuple:
        """Get start and end dates for a time period."""
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if period == TimePeriod.TODAY:
            start = today
            end = today + timedelta(days=1)
        elif period == TimePeriod.THIS_WEEK:
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=7)
        elif period == TimePeriod.LAST_WEEK:
            this_week_start = today - timedelta(days=today.weekday())
            start = this_week_start - timedelta(days=7)
            end = this_week_start
        elif period == TimePeriod.THIS_MONTH:
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1)
            else:
                end = today.replace(month=today.month + 1, day=1)
        elif period == TimePeriod.LAST_MONTH:
            this_month_start = today.replace(day=1)
            if today.month == 1:
                start = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start = today.replace(month=today.month - 1, day=1)
            end = this_month_start
        elif period == TimePeriod.THIS_QUARTER:
            quarter = (today.month - 1) // 3
            start = today.replace(month=quarter * 3 + 1, day=1)
            if quarter == 3:
                end = today.replace(year=today.year + 1, month=1, day=1)
            else:
                end = today.replace(month=(quarter + 1) * 3 + 1, day=1)
        elif period == TimePeriod.LAST_QUARTER:
            quarter = (today.month - 1) // 3
            if quarter == 0:
                start = today.replace(year=today.year - 1, month=10, day=1)
                end = today.replace(month=1, day=1)
            else:
                start = today.replace(month=(quarter - 1) * 3 + 1, day=1)
                end = today.replace(month=quarter * 3 + 1, day=1)
        elif period == TimePeriod.THIS_YEAR:
            start = today.replace(month=1, day=1)
            end = today.replace(year=today.year + 1, month=1, day=1)
        elif period == TimePeriod.LAST_YEAR:
            start = today.replace(year=today.year - 1, month=1, day=1)
            end = today.replace(month=1, day=1)
        else:  # ALL_TIME
            start = datetime(2020, 1, 1)
            end = today + timedelta(days=1)

        return start, end

    @staticmethod
    async def get_win_loss_stats(
        db: AsyncSession,
        contractor_id: str,
        period: TimePeriod = TimePeriod.THIS_MONTH
    ) -> WinLossStats:
        """Get comprehensive win/loss statistics for a period."""
        from ..models.database import Quote

        start_date, end_date = WinLossAnalyticsService.get_date_range(period)

        # Main stats query
        result = await db.execute(
            select(
                func.count(Quote.id).label("total"),
                func.sum(case((Quote.outcome.isnot(None), 1), else_=0)).label("with_outcome"),
                func.sum(case((Quote.outcome == "won", 1), else_=0)).label("won"),
                func.sum(case((Quote.outcome == "lost", 1), else_=0)).label("lost"),
                func.sum(case((Quote.outcome.is_(None), 1), else_=0)).label("pending"),
                func.coalesce(func.sum(Quote.total), 0).label("total_value"),
                func.coalesce(func.sum(case((Quote.outcome == "won", Quote.total), else_=0)), 0).label("won_value"),
                func.coalesce(func.sum(case((Quote.outcome == "lost", Quote.total), else_=0)), 0).label("lost_value"),
            )
            .where(
                Quote.contractor_id == contractor_id,
                Quote.created_at >= start_date,
                Quote.created_at < end_date
            )
        )
        row = result.first()

        total = row.total or 0
        with_outcome = row.with_outcome or 0
        won = row.won or 0
        lost = row.lost or 0
        pending = row.pending or 0
        total_value = float(row.total_value or 0)
        won_value = float(row.won_value or 0)
        lost_value = float(row.lost_value or 0)

        win_rate = (won / with_outcome * 100) if with_outcome > 0 else 0
        avg_value = (total_value / total) if total > 0 else 0
        avg_won_value = (won_value / won) if won > 0 else 0

        # Calculate average days to win (SQLite compatible)
        days_to_win_result = await db.execute(
            select(Quote.accepted_at, Quote.sent_at)
            .where(
                Quote.contractor_id == contractor_id,
                Quote.outcome == "won",
                Quote.accepted_at.isnot(None),
                Quote.sent_at.isnot(None),
                Quote.created_at >= start_date,
                Quote.created_at < end_date
            )
        )
        win_rows = days_to_win_result.fetchall()
        if win_rows:
            days_list = [(r.accepted_at - r.sent_at).days for r in win_rows if r.accepted_at and r.sent_at]
            avg_days_to_win = sum(days_list) / len(days_list) if days_list else None
        else:
            avg_days_to_win = None

        # Calculate average days to loss
        days_to_loss_result = await db.execute(
            select(Quote.outcome_recorded_at, Quote.sent_at)
            .where(
                Quote.contractor_id == contractor_id,
                Quote.outcome == "lost",
                Quote.outcome_recorded_at.isnot(None),
                Quote.sent_at.isnot(None),
                Quote.created_at >= start_date,
                Quote.created_at < end_date
            )
        )
        loss_rows = days_to_loss_result.fetchall()
        if loss_rows:
            days_list = [(r.outcome_recorded_at - r.sent_at).days for r in loss_rows if r.outcome_recorded_at and r.sent_at]
            avg_days_to_loss = sum(days_list) / len(days_list) if days_list else None
        else:
            avg_days_to_loss = None

        return WinLossStats(
            period=period.value,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            total_quotes=total,
            quotes_with_outcome=with_outcome,
            won=won,
            lost=lost,
            pending=pending,
            win_rate=round(win_rate, 1),
            total_value_quoted=total_value,
            total_value_won=won_value,
            total_value_lost=lost_value,
            average_quote_value=round(avg_value, 2),
            average_won_value=round(avg_won_value, 2),
            average_days_to_win=round(avg_days_to_win, 1) if avg_days_to_win else None,
            average_days_to_loss=round(avg_days_to_loss, 1) if avg_days_to_loss else None,
        )

    @staticmethod
    async def get_loss_reason_analysis(
        db: AsyncSession,
        contractor_id: str,
        period: TimePeriod = TimePeriod.THIS_YEAR
    ) -> List[LossReasonAnalysis]:
        """Analyze loss reasons to identify patterns."""
        from ..models.database import Quote

        start_date, end_date = WinLossAnalyticsService.get_date_range(period)

        # Get loss count by reason
        result = await db.execute(
            select(
                func.coalesce(Quote.outcome_notes, "No reason provided").label("reason"),
                func.count(Quote.id).label("count"),
                func.coalesce(func.sum(Quote.total), 0).label("total_value"),
            )
            .where(
                Quote.contractor_id == contractor_id,
                Quote.outcome == "lost",
                Quote.created_at >= start_date,
                Quote.created_at < end_date
            )
            .group_by(Quote.outcome_notes)
            .order_by(func.count(Quote.id).desc())
        )
        rows = result.fetchall()

        total_losses = sum(r.count for r in rows) if rows else 0
        analyses = []

        for row in rows:
            # Get common job types for this loss reason
            job_types_result = await db.execute(
                select(Quote.job_type, func.count(Quote.id).label("count"))
                .where(
                    Quote.contractor_id == contractor_id,
                    Quote.outcome == "lost",
                    or_(
                        Quote.outcome_notes == row.reason,
                        and_(Quote.outcome_notes.is_(None), row.reason == "No reason provided")
                    ),
                    Quote.created_at >= start_date,
                    Quote.created_at < end_date
                )
                .group_by(Quote.job_type)
                .order_by(func.count(Quote.id).desc())
                .limit(3)
            )
            common_jobs = [r.job_type for r in job_types_result.fetchall() if r.job_type]

            analyses.append(LossReasonAnalysis(
                reason=row.reason or "No reason provided",
                count=row.count,
                total_value_lost=float(row.total_value or 0),
                percentage_of_losses=round((row.count / total_losses * 100) if total_losses > 0 else 0, 1),
                average_value=round(float(row.total_value or 0) / row.count if row.count > 0 else 0, 2),
                common_job_types=common_jobs,
            ))

        return analyses

    @staticmethod
    async def get_trend_comparison(
        db: AsyncSession,
        contractor_id: str,
        current_period: TimePeriod = TimePeriod.THIS_MONTH,
        previous_period: TimePeriod = TimePeriod.LAST_MONTH
    ) -> TrendComparison:
        """Compare performance between two periods."""
        current_stats = await WinLossAnalyticsService.get_win_loss_stats(db, contractor_id, current_period)
        previous_stats = await WinLossAnalyticsService.get_win_loss_stats(db, contractor_id, previous_period)

        win_rate_change = current_stats.win_rate - previous_stats.win_rate

        quotes_change = 0
        if previous_stats.total_quotes > 0:
            quotes_change = ((current_stats.total_quotes - previous_stats.total_quotes) /
                            previous_stats.total_quotes * 100)

        revenue_change = 0
        if previous_stats.total_value_won > 0:
            revenue_change = ((current_stats.total_value_won - previous_stats.total_value_won) /
                             previous_stats.total_value_won * 100)

        return TrendComparison(
            current_period=current_period.value,
            previous_period=previous_period.value,
            current_win_rate=current_stats.win_rate,
            previous_win_rate=previous_stats.win_rate,
            win_rate_change=round(win_rate_change, 1),
            current_quotes=current_stats.total_quotes,
            previous_quotes=previous_stats.total_quotes,
            quotes_change_percent=round(quotes_change, 1),
            current_revenue=current_stats.total_value_won,
            previous_revenue=previous_stats.total_value_won,
            revenue_change_percent=round(revenue_change, 1),
        )

    @staticmethod
    async def get_performance_by_job_type(
        db: AsyncSession,
        contractor_id: str,
        period: TimePeriod = TimePeriod.THIS_YEAR
    ) -> List[Dict[str, Any]]:
        """Get win/loss breakdown by job type."""
        from ..models.database import Quote

        start_date, end_date = WinLossAnalyticsService.get_date_range(period)

        result = await db.execute(
            select(
                Quote.job_type,
                func.count(Quote.id).label("total"),
                func.sum(case((Quote.outcome == "won", 1), else_=0)).label("won"),
                func.sum(case((Quote.outcome == "lost", 1), else_=0)).label("lost"),
                func.coalesce(func.sum(Quote.total), 0).label("total_value"),
                func.coalesce(func.sum(case((Quote.outcome == "won", Quote.total), else_=0)), 0).label("won_value"),
            )
            .where(
                Quote.contractor_id == contractor_id,
                Quote.created_at >= start_date,
                Quote.created_at < end_date
            )
            .group_by(Quote.job_type)
            .order_by(func.count(Quote.id).desc())
            .limit(10)
        )
        rows = result.fetchall()

        return [
            {
                "job_type": row.job_type or "Other",
                "total_quotes": row.total,
                "won": row.won or 0,
                "lost": row.lost or 0,
                "win_rate": round((row.won / (row.won + row.lost) * 100) if (row.won + row.lost) > 0 else 0, 1),
                "total_value": float(row.total_value or 0),
                "won_value": float(row.won_value or 0),
            }
            for row in rows
        ]

    @staticmethod
    async def get_monthly_trend(
        db: AsyncSession,
        contractor_id: str,
        months: int = 6
    ) -> List[Dict[str, Any]]:
        """Get monthly win/loss trend for charting."""
        from ..models.database import Quote

        now = datetime.utcnow()
        trends = []

        for i in range(months - 1, -1, -1):
            # Calculate month boundaries
            if now.month - i <= 0:
                year = now.year - 1
                month = 12 + (now.month - i)
            else:
                year = now.year
                month = now.month - i

            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)

            result = await db.execute(
                select(
                    func.count(Quote.id).label("total"),
                    func.sum(case((Quote.outcome == "won", 1), else_=0)).label("won"),
                    func.sum(case((Quote.outcome == "lost", 1), else_=0)).label("lost"),
                    func.coalesce(func.sum(case((Quote.outcome == "won", Quote.total), else_=0)), 0).label("won_value"),
                )
                .where(
                    Quote.contractor_id == contractor_id,
                    Quote.created_at >= start_date,
                    Quote.created_at < end_date
                )
            )
            row = result.first()

            total = row.total or 0
            won = row.won or 0
            lost = row.lost or 0
            with_outcome = won + lost

            trends.append({
                "month": start_date.strftime("%b %Y"),
                "total_quotes": total,
                "won": won,
                "lost": lost,
                "win_rate": round((won / with_outcome * 100) if with_outcome > 0 else 0, 1),
                "won_value": float(row.won_value or 0),
            })

        return trends

    @staticmethod
    async def get_recent_outcomes(
        db: AsyncSession,
        contractor_id: str,
        outcome: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent won or lost quotes."""
        from ..models.database import Quote

        result = await db.execute(
            select(Quote)
            .where(
                Quote.contractor_id == contractor_id,
                Quote.outcome == outcome
            )
            .order_by(Quote.outcome_recorded_at.desc().nullslast())
            .limit(limit)
        )
        quotes = result.scalars().all()

        return [
            {
                "id": q.id,
                "customer_name": q.customer_name,
                "job_type": q.job_type,
                "total": q.total,
                "outcome_date": q.outcome_recorded_at.isoformat() if q.outcome_recorded_at else None,
                "outcome_notes": q.outcome_notes,
                "days_to_outcome": (
                    (q.outcome_recorded_at - q.sent_at).days
                    if q.outcome_recorded_at and q.sent_at else None
                ),
            }
            for q in quotes
        ]

    @staticmethod
    async def get_full_dashboard(
        db: AsyncSession,
        contractor_id: str,
        period: TimePeriod = TimePeriod.THIS_MONTH
    ) -> Dict[str, Any]:
        """Get complete win/loss dashboard data."""
        # Determine comparison period
        period_comparison = {
            TimePeriod.THIS_WEEK: TimePeriod.LAST_WEEK,
            TimePeriod.THIS_MONTH: TimePeriod.LAST_MONTH,
            TimePeriod.THIS_QUARTER: TimePeriod.LAST_QUARTER,
            TimePeriod.THIS_YEAR: TimePeriod.LAST_YEAR,
        }
        comparison_period = period_comparison.get(period, TimePeriod.LAST_MONTH)

        # Gather all dashboard components
        overview = await WinLossAnalyticsService.get_win_loss_stats(db, contractor_id, period)
        trend = await WinLossAnalyticsService.get_trend_comparison(db, contractor_id, period, comparison_period)
        loss_reasons = await WinLossAnalyticsService.get_loss_reason_analysis(db, contractor_id, period)
        by_job_type = await WinLossAnalyticsService.get_performance_by_job_type(db, contractor_id, period)
        recent_wins = await WinLossAnalyticsService.get_recent_outcomes(db, contractor_id, "won", 5)
        recent_losses = await WinLossAnalyticsService.get_recent_outcomes(db, contractor_id, "lost", 5)
        monthly_trend = await WinLossAnalyticsService.get_monthly_trend(db, contractor_id, 6)

        return {
            "overview": asdict(overview),
            "trend": asdict(trend),
            "loss_reasons": [asdict(lr) for lr in loss_reasons],
            "by_job_type": by_job_type,
            "recent_wins": recent_wins,
            "recent_losses": recent_losses,
            "monthly_trend": monthly_trend,
            "generated_at": datetime.utcnow().isoformat(),
        }


# Singleton instance
win_loss_analytics = WinLossAnalyticsService()
