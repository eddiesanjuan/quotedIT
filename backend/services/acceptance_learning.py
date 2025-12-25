"""
Acceptance Learning Service for Quoted.

Learns from SENT quotes (without edits) to reinforce correct AI pricing.
This is the OPPOSITE of correction learning:
- Corrections = AI was WRONG -> Create new statements
- Acceptance = AI was RIGHT -> Boost confidence, NO new statements

Design source: .claude/learning-excellence-outputs/phase4-acceptance.md
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List


@dataclass
class AcceptanceResult:
    """Result of processing an acceptance signal."""
    processed: bool
    reason: Optional[str]
    old_confidence: float
    new_confidence: float
    signal_type: str  # "sent" or "accepted"
    category: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "processed": self.processed,
            "reason": self.reason,
            "old_confidence": self.old_confidence,
            "new_confidence": self.new_confidence,
            "signal_type": self.signal_type,
            "category": self.category,
        }


class AcceptanceLearningService:
    """
    Processes acceptance signals when quotes are sent/accepted WITHOUT edits.

    Key difference from correction learning:
    - Corrections create NEW learning statements
    - Acceptances boost confidence WITHOUT new statements

    Confidence boost: +0.05 for acceptance (vs +0.02 for corrections)

    Usage:
        service = AcceptanceLearningService()
        result = await service.process_acceptance(
            contractor_id="abc123",
            quote=quote,
            signal_type="sent",  # or "accepted"
        )
    """

    # Confidence boost per acceptance signal
    ACCEPTANCE_CONFIDENCE_BOOST = 0.05

    # Maximum confidence ceiling
    MAX_CONFIDENCE = 0.95

    # Minimum signals before calibration kicks in
    MIN_SIGNALS_FOR_CALIBRATION = 5

    # Maximum accepted_totals entries to keep (for performance)
    MAX_ACCEPTED_TOTALS = 10

    async def process_acceptance(
        self,
        contractor_id: str,
        quote: Any,  # Quote model
        signal_type: str = "sent",  # "sent" or "accepted"
        pricing_model: Optional[Dict[str, Any]] = None,
    ) -> AcceptanceResult:
        """
        Process acceptance signal - when quote sent/accepted WITHOUT edit.

        Args:
            contractor_id: The contractor's ID
            quote: The quote that was sent/accepted
            signal_type: "sent" (quote sent without edit) or "accepted" (customer accepted)
            pricing_model: Pre-loaded pricing model (optional, will fetch if not provided)

        Returns:
            AcceptanceResult with processing details
        """
        # Validation: Don't process edited quotes
        if hasattr(quote, 'was_edited') and quote.was_edited:
            return AcceptanceResult(
                processed=False,
                reason="Quote was edited - not an acceptance signal",
                old_confidence=0.0,
                new_confidence=0.0,
                signal_type=signal_type,
                category="",
            )

        # Get category from quote
        category = getattr(quote, 'job_type', None)
        if not category:
            return AcceptanceResult(
                processed=False,
                reason="No job_type on quote",
                old_confidence=0.0,
                new_confidence=0.0,
                signal_type=signal_type,
                category="",
            )

        # Load pricing model if not provided
        if pricing_model is None:
            # In production, this would fetch from database
            # For now, return a placeholder result
            return AcceptanceResult(
                processed=False,
                reason="Pricing model not provided",
                old_confidence=0.0,
                new_confidence=0.0,
                signal_type=signal_type,
                category=category,
            )

        # Get category data from pricing_knowledge
        pricing_knowledge = pricing_model.get("pricing_knowledge", {})
        categories = pricing_knowledge.get("categories", {})

        if category not in categories:
            # Initialize new category
            categories[category] = self._init_category_data()

        cat_data = categories[category]

        # Store old confidence
        old_confidence = cat_data.get("confidence", 0.5)

        # Apply confidence boost
        new_confidence = min(self.MAX_CONFIDENCE, old_confidence + self.ACCEPTANCE_CONFIDENCE_BOOST)

        # Apply calibration if enough signals
        acceptance_count = cat_data.get("acceptance_count", 0) + 1
        correction_count = cat_data.get("correction_count", 0)

        new_confidence = self._apply_calibration(
            acceptance_count=acceptance_count,
            correction_count=correction_count,
            current_confidence=new_confidence,
        )

        # Update category data
        cat_data["confidence"] = new_confidence
        cat_data["acceptance_count"] = acceptance_count
        cat_data["last_acceptance_at"] = datetime.utcnow().isoformat()

        # Track accepted totals (capped for performance)
        accepted_totals = cat_data.get("accepted_totals", [])
        quote_total = getattr(quote, 'total', 0) or getattr(quote, 'subtotal', 0) or 0
        accepted_totals.append({
            "total": float(quote_total),
            "signal_type": signal_type,
            "timestamp": datetime.utcnow().isoformat(),
        })
        cat_data["accepted_totals"] = accepted_totals[-self.MAX_ACCEPTED_TOTALS:]

        # NO NEW LEARNED_ADJUSTMENTS (key difference from corrections)
        # Acceptance reinforces existing patterns, doesn't create new ones

        return AcceptanceResult(
            processed=True,
            reason=None,
            old_confidence=old_confidence,
            new_confidence=new_confidence,
            signal_type=signal_type,
            category=category,
        )

    def _apply_calibration(
        self,
        acceptance_count: int,
        correction_count: int,
        current_confidence: float,
    ) -> float:
        """
        Apply confidence calibration based on actual accuracy.

        Confidence ceiling = actual_accuracy + 0.15
        Prevents "overconfident but inaccurate" scenarios.
        """
        total_signals = acceptance_count + correction_count

        if total_signals < self.MIN_SIGNALS_FOR_CALIBRATION:
            return current_confidence  # Not enough data for calibration

        actual_accuracy = acceptance_count / total_signals
        confidence_ceiling = min(self.MAX_CONFIDENCE, actual_accuracy + 0.15)

        return min(current_confidence, confidence_ceiling)

    def _init_category_data(self) -> Dict[str, Any]:
        """Initialize data structure for a new category."""
        return {
            "confidence": 0.5,
            "acceptance_count": 0,
            "correction_count": 0,
            "learned_adjustments": [],
            "accepted_totals": [],
            "last_acceptance_at": None,
            "last_correction_at": None,
        }

    def should_process_acceptance(
        self,
        quote: Any,
        was_just_sent: bool = False,
        was_just_accepted: bool = False,
    ) -> tuple[bool, str]:
        """
        Determine if a quote should trigger acceptance learning.

        Args:
            quote: The quote to check
            was_just_sent: Whether quote was just sent
            was_just_accepted: Whether quote was just accepted by customer

        Returns:
            Tuple of (should_process, signal_type)
        """
        # Must have a signal
        if not was_just_sent and not was_just_accepted:
            return False, ""

        # Must not be edited
        if hasattr(quote, 'was_edited') and quote.was_edited:
            return False, ""

        # Determine signal type
        if was_just_accepted:
            return True, "accepted"
        elif was_just_sent:
            return True, "sent"

        return False, ""


# Convenience function for direct use
async def process_acceptance_learning(
    contractor_id: str,
    quote: Any,
    signal_type: str = "sent",
    pricing_model: Optional[Dict[str, Any]] = None,
) -> AcceptanceResult:
    """Process acceptance signal for a quote."""
    service = AcceptanceLearningService()
    return await service.process_acceptance(
        contractor_id=contractor_id,
        quote=quote,
        signal_type=signal_type,
        pricing_model=pricing_model,
    )
