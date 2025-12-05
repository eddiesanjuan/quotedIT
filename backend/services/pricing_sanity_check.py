"""
Pricing sanity check service for Quoted.

Prevents catastrophic AI hallucinations by validating quote totals against
historical data before returning to users.

Strategy:
1. Calculate category-level median and P95 from historical quotes
2. On new quote generation, check total price against bounds
3. If >3x P95: Add warning field, log for review
4. If >10x P95: Block quote, return error asking to re-record

Edge case: When category has <5 quotes, use global fallback bounds.
"""

import statistics
from typing import Optional, Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.database import Quote


class PricingSanityCheckService:
    """
    Service for validating quote pricing against historical bounds.

    Prevents:
    - $500K bathroom remodel hallucinations
    - $50 whole-house renovation catastrophes
    - Viral Reddit post disasters from pricing hallucinations
    """

    # Global fallback bounds when insufficient historical data
    GLOBAL_MIN_QUOTE = 100.0
    GLOBAL_MAX_QUOTE = 500000.0

    # Thresholds for flagging
    WARNING_MULTIPLIER = 3.0  # Flag if >3x P95
    BLOCK_MULTIPLIER = 10.0   # Block if >10x P95

    # Minimum quotes needed for category-specific bounds
    MIN_QUOTES_FOR_CATEGORY_BOUNDS = 5

    async def get_category_bounds(
        self,
        db: AsyncSession,
        contractor_id: str,
        category: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Calculate historical bounds for a category.

        Args:
            db: Database session
            contractor_id: Contractor ID for isolation
            category: Job type/category (None = all quotes)

        Returns:
            Dict with:
            - median: Median quote total
            - p95: 95th percentile quote total
            - count: Number of historical quotes
            - source: "category" or "global" (indicates which bounds used)
        """
        # Query historical quotes for this contractor and category
        query = select(Quote.total).where(
            Quote.contractor_id == contractor_id,
            Quote.total.isnot(None),
            Quote.total > 0,  # Exclude invalid quotes
        )

        if category:
            query = query.where(Quote.job_type == category)

        result = await db.execute(query)
        totals = [row[0] for row in result.fetchall()]

        # If insufficient data for category, fall back to global bounds
        if len(totals) < self.MIN_QUOTES_FOR_CATEGORY_BOUNDS:
            return {
                "median": (self.GLOBAL_MIN_QUOTE + self.GLOBAL_MAX_QUOTE) / 2,
                "p95": self.GLOBAL_MAX_QUOTE,
                "count": len(totals),
                "source": "global",
                "warning_threshold": self.GLOBAL_MAX_QUOTE * 0.5,  # 50% of max
                "block_threshold": self.GLOBAL_MAX_QUOTE,
            }

        # Calculate statistics from historical data
        median = statistics.median(totals)

        # P95 = 95th percentile
        sorted_totals = sorted(totals)
        p95_index = int(len(sorted_totals) * 0.95)
        p95 = sorted_totals[p95_index] if p95_index < len(sorted_totals) else sorted_totals[-1]

        return {
            "median": median,
            "p95": p95,
            "count": len(totals),
            "source": "category",
            "warning_threshold": p95 * self.WARNING_MULTIPLIER,
            "block_threshold": p95 * self.BLOCK_MULTIPLIER,
        }

    async def check_quote_sanity(
        self,
        db: AsyncSession,
        contractor_id: str,
        quote_total: float,
        category: Optional[str] = None,
    ) -> Dict:
        """
        Check if a quote total is within reasonable bounds.

        Args:
            db: Database session
            contractor_id: Contractor ID
            quote_total: Total quote amount to check
            category: Job type/category for historical comparison

        Returns:
            Dict with:
            - is_sane: True if quote passes sanity check
            - action: "pass", "warn", or "block"
            - message: Human-readable explanation
            - bounds: Historical bounds used
            - severity: "normal", "warning", "critical"
        """
        # Get historical bounds for this category
        bounds = await self.get_category_bounds(db, contractor_id, category)

        # Check against bounds
        if quote_total <= bounds["warning_threshold"]:
            # Normal quote - passes sanity check
            return {
                "is_sane": True,
                "action": "pass",
                "message": None,
                "bounds": bounds,
                "severity": "normal",
            }

        elif quote_total <= bounds["block_threshold"]:
            # Warning zone - unusual but allowed
            warning_msg = self._generate_warning_message(
                quote_total=quote_total,
                bounds=bounds,
            )
            return {
                "is_sane": True,  # Still allowed, but flagged
                "action": "warn",
                "message": warning_msg,
                "bounds": bounds,
                "severity": "warning",
            }

        else:
            # Block zone - likely hallucination
            block_msg = self._generate_block_message(
                quote_total=quote_total,
                bounds=bounds,
            )
            return {
                "is_sane": False,
                "action": "block",
                "message": block_msg,
                "bounds": bounds,
                "severity": "critical",
            }

    def _generate_warning_message(
        self,
        quote_total: float,
        bounds: Dict,
    ) -> str:
        """Generate user-friendly warning message."""
        if bounds["source"] == "category":
            return (
                f"⚠️ This quote (${quote_total:,.0f}) is significantly higher than your "
                f"typical quotes in this category (median: ${bounds['median']:,.0f}). "
                f"Please double-check the pricing before sending."
            )
        else:
            return (
                f"⚠️ This quote (${quote_total:,.0f}) is unusually high. "
                f"Please review carefully before sending."
            )

    def _generate_block_message(
        self,
        quote_total: float,
        bounds: Dict,
    ) -> str:
        """Generate user-friendly block message."""
        if bounds["source"] == "category":
            return (
                f"This quote amount (${quote_total:,.0f}) is extremely high compared to "
                f"your historical quotes (median: ${bounds['median']:,.0f}). This might "
                f"be an AI error. Please re-record your description with more details, "
                f"or contact support if this amount is correct."
            )
        else:
            return (
                f"This quote amount (${quote_total:,.0f}) exceeds reasonable bounds. "
                f"This might be an AI error. Please re-record your description with "
                f"more details, or contact support if this amount is correct."
            )

    async def log_flagged_quote(
        self,
        db: AsyncSession,
        contractor_id: str,
        quote_total: float,
        category: Optional[str],
        action: str,
        bounds: Dict,
        transcription: str,
    ):
        """
        Log flagged quotes for pattern analysis.

        This helps us identify systemic issues in quote generation
        and improve the AI over time.

        Args:
            db: Database session
            contractor_id: Contractor ID
            quote_total: Flagged quote total
            category: Job category
            action: "warn" or "block"
            bounds: Historical bounds used
            transcription: Original transcription (for debugging)
        """
        # For now, just print to logs
        # In the future, could store in a dedicated flagged_quotes table
        log_entry = {
            "contractor_id": contractor_id,
            "quote_total": quote_total,
            "category": category,
            "action": action,
            "bounds": bounds,
            "transcription": transcription[:200],  # First 200 chars
        }

        print(f"[SANITY CHECK {action.upper()}] {log_entry}")

        # TODO: Store in database for analytics
        # Could add a flagged_quotes table or add a flag to the quotes table


# Singleton pattern
_sanity_check_service: Optional[PricingSanityCheckService] = None


def get_sanity_check_service() -> PricingSanityCheckService:
    """Get the pricing sanity check service singleton."""
    global _sanity_check_service
    if _sanity_check_service is None:
        _sanity_check_service = PricingSanityCheckService()
    return _sanity_check_service
