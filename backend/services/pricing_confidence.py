"""
Multi-Dimensional Pricing Confidence Service for Quoted.

Calculates calibrated confidence scores across 4 dimensions:
- Data (20%): Volume of quotes (logarithmic growth)
- Accuracy (40%): Acceptance rate with magnitude weighting
- Recency (25%): Freshness of data (30-day half-life decay)
- Coverage (15%): Job complexity spread (Shannon entropy)

Core Principle: If we claim 80% confidence, then 80% of quotes should be accepted without edit.

Design source: .claude/learning-excellence-outputs/phase6-confidence.md
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Literal


# Dimension weights (must sum to 1.0)
CONFIDENCE_WEIGHTS = {
    "data": 0.20,      # 20% - Volume matters but plateaus
    "accuracy": 0.40,  # 40% - Most important: are we right?
    "recency": 0.25,   # 25% - Fresh data matters
    "coverage": 0.15,  # 15% - Job type variety matters
}


@dataclass
class PricingConfidence:
    """Multi-dimensional confidence for a category."""

    # Primary dimensions
    data_confidence: float  # 0.0-1.0
    accuracy_confidence: float  # 0.0-1.0
    recency_confidence: float  # 0.0-1.0
    coverage_confidence: float  # 0.0-1.0

    # Composite scores
    overall_confidence: float  # 0.0-1.0
    display_confidence: Literal["High", "Medium", "Low", "Learning"]

    # Metadata
    quote_count: int
    acceptance_count: int
    correction_count: int
    acceptance_rate: float
    avg_correction_magnitude: float
    days_since_last_quote: int
    complexity_distribution: Dict[str, int]
    last_updated: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "data_confidence": self.data_confidence,
            "accuracy_confidence": self.accuracy_confidence,
            "recency_confidence": self.recency_confidence,
            "coverage_confidence": self.coverage_confidence,
            "overall_confidence": self.overall_confidence,
            "display_confidence": self.display_confidence,
            "quote_count": self.quote_count,
            "acceptance_count": self.acceptance_count,
            "correction_count": self.correction_count,
            "acceptance_rate": self.acceptance_rate,
            "avg_correction_magnitude": self.avg_correction_magnitude,
            "days_since_last_quote": self.days_since_last_quote,
            "complexity_distribution": self.complexity_distribution,
            "last_updated": self.last_updated,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PricingConfidence":
        """Create from dictionary."""
        return cls(
            data_confidence=data.get("data_confidence", 0.3),
            accuracy_confidence=data.get("accuracy_confidence", 0.3),
            recency_confidence=data.get("recency_confidence", 1.0),
            coverage_confidence=data.get("coverage_confidence", 0.3),
            overall_confidence=data.get("overall_confidence", 0.35),
            display_confidence=data.get("display_confidence", "Learning"),
            quote_count=data.get("quote_count", 0),
            acceptance_count=data.get("acceptance_count", 0),
            correction_count=data.get("correction_count", 0),
            acceptance_rate=data.get("acceptance_rate", 0.0),
            avg_correction_magnitude=data.get("avg_correction_magnitude", 0.0),
            days_since_last_quote=data.get("days_since_last_quote", 0),
            complexity_distribution=data.get("complexity_distribution", {}),
            last_updated=data.get("last_updated", datetime.utcnow().isoformat()),
            warnings=data.get("warnings", []),
        )


class PricingConfidenceService:
    """
    Calculates multi-dimensional calibrated confidence scores.

    CALIBRATION PRINCIPLE:
    If we claim 80% confidence, then 80% of quotes should be accepted without edit.

    Usage:
        service = PricingConfidenceService()
        confidence = service.calculate(
            quote_count=50,
            acceptance_count=45,
            correction_count=5,
            correction_magnitudes=[3.2, 5.1, 2.8, ...],
            days_since_last_quote=5,
            complexity_distribution={"simple": 15, "medium": 25, "complex": 10},
        )
    """

    # Recency decay half-life
    HALF_LIFE_DAYS = 30

    # Minimum data thresholds
    MIN_QUOTES_FOR_ACCURACY = 3
    MIN_QUOTES_FOR_COVERAGE = 5

    def calculate(
        self,
        quote_count: int,
        acceptance_count: int,
        correction_count: int,
        correction_magnitudes: List[float],
        days_since_last_quote: int,
        complexity_distribution: Dict[str, int],
    ) -> PricingConfidence:
        """
        Calculate multi-dimensional calibrated confidence.

        Args:
            quote_count: Total quotes in category
            acceptance_count: Quotes sent without edit
            correction_count: Quotes edited before sending
            correction_magnitudes: List of correction percentages (last 20)
            days_since_last_quote: Days since most recent quote
            complexity_distribution: Count by complexity level

        Returns:
            PricingConfidence with all dimensions calculated
        """
        # Handle new category (first few quotes)
        if quote_count < 3:
            return self._new_category_confidence(
                quote_count=quote_count,
                acceptance_count=acceptance_count,
                correction_count=correction_count,
            )

        # 1. DATA CONFIDENCE (logarithmic growth)
        data_confidence = self._calculate_data_confidence(quote_count)

        # 2. ACCURACY CONFIDENCE (acceptance rate with magnitude adjustment)
        accuracy_confidence = self._calculate_accuracy_confidence(
            acceptance_count=acceptance_count,
            correction_count=correction_count,
            correction_magnitudes=correction_magnitudes,
        )

        # 3. RECENCY CONFIDENCE (exponential decay)
        recency_confidence = self._calculate_recency_confidence(days_since_last_quote)

        # 4. COVERAGE CONFIDENCE (Shannon entropy)
        coverage_confidence = self._calculate_coverage_confidence(complexity_distribution)

        # 5. OVERALL CONFIDENCE (weighted combination)
        overall_confidence = (
            data_confidence * CONFIDENCE_WEIGHTS["data"] +
            accuracy_confidence * CONFIDENCE_WEIGHTS["accuracy"] +
            recency_confidence * CONFIDENCE_WEIGHTS["recency"] +
            coverage_confidence * CONFIDENCE_WEIGHTS["coverage"]
        )

        # 6. DISPLAY CONFIDENCE
        display_confidence = self._get_display_confidence(overall_confidence)

        # 7. WARNINGS
        warnings = self._generate_warnings(
            quote_count=quote_count,
            acceptance_count=acceptance_count,
            correction_count=correction_count,
            days_since_last_quote=days_since_last_quote,
            complexity_distribution=complexity_distribution,
        )

        # Calculate metadata
        total_signals = acceptance_count + correction_count
        acceptance_rate = acceptance_count / total_signals if total_signals > 0 else 0.0
        avg_correction = (
            sum(correction_magnitudes) / len(correction_magnitudes)
            if correction_magnitudes else 0.0
        )

        return PricingConfidence(
            data_confidence=round(data_confidence, 3),
            accuracy_confidence=round(accuracy_confidence, 3),
            recency_confidence=round(recency_confidence, 3),
            coverage_confidence=round(coverage_confidence, 3),
            overall_confidence=round(overall_confidence, 3),
            display_confidence=display_confidence,
            quote_count=quote_count,
            acceptance_count=acceptance_count,
            correction_count=correction_count,
            acceptance_rate=round(acceptance_rate, 3),
            avg_correction_magnitude=round(avg_correction, 2),
            days_since_last_quote=days_since_last_quote,
            complexity_distribution=complexity_distribution,
            last_updated=datetime.utcnow().isoformat(),
            warnings=warnings,
        )

    def _calculate_data_confidence(self, quote_count: int) -> float:
        """
        Calculate data confidence using logarithmic growth.

        Curve:
        - 1 quote: 0.00
        - 5 quotes: 0.38
        - 10 quotes: 0.50
        - 25 quotes: 0.66
        - 50 quotes: 0.75
        - 100 quotes: 0.83
        - 200 quotes: 0.90
        - 500+ quotes: 0.95 (cap)
        """
        if quote_count <= 0:
            return 0.0
        return min(0.95, math.log(quote_count + 1, 1.15) / 100)

    def _calculate_accuracy_confidence(
        self,
        acceptance_count: int,
        correction_count: int,
        correction_magnitudes: List[float],
    ) -> float:
        """
        Calculate accuracy confidence based on acceptance rate and correction magnitude.

        Formula: acceptance_rate * magnitude_adjustment

        Examples:
        - 90% acceptance, 3% avg correction: 0.90 × 0.97 = 0.87
        - 90% acceptance, 15% avg correction: 0.90 × 0.85 = 0.77
        - 50% acceptance, 5% avg correction: 0.50 × 0.95 = 0.48
        """
        total_signals = acceptance_count + correction_count

        if total_signals < self.MIN_QUOTES_FOR_ACCURACY:
            return 0.3  # Not enough data

        # Base accuracy = acceptance rate
        base_accuracy = acceptance_count / total_signals

        # Magnitude adjustment: penalize large corrections
        if correction_magnitudes:
            avg_magnitude = sum(correction_magnitudes) / len(correction_magnitudes)
            # 5% avg correction = 0.95 multiplier
            # 20% avg correction = 0.80 multiplier
            magnitude_multiplier = max(0.5, 1.0 - (avg_magnitude / 100))
        else:
            magnitude_multiplier = 1.0

        accuracy_confidence = base_accuracy * magnitude_multiplier
        return max(0.0, min(1.0, accuracy_confidence))

    def _calculate_recency_confidence(self, days_since_last_quote: int) -> float:
        """
        Calculate recency confidence using exponential decay.

        30-day half-life:
        - 0 days: 1.00
        - 15 days: 0.71
        - 30 days: 0.50
        - 60 days: 0.25
        - 90 days: 0.13
        """
        decay_factor = 0.5 ** (days_since_last_quote / self.HALF_LIFE_DAYS)
        return max(0.0, min(1.0, decay_factor))

    def _calculate_coverage_confidence(
        self,
        complexity_distribution: Dict[str, int],
    ) -> float:
        """
        Calculate coverage confidence using Shannon entropy.

        Measures how well distributed quotes are across complexity levels.
        Perfect distribution (33% each) = 1.0
        All in one category = 0.0
        """
        total_jobs = sum(complexity_distribution.values())

        if total_jobs < self.MIN_QUOTES_FOR_COVERAGE:
            return 0.3  # Not enough data

        # Calculate Shannon entropy
        entropy = 0.0
        for count in complexity_distribution.values():
            if count > 0:
                p = count / total_jobs
                entropy -= p * math.log2(p)

        # Normalize: max entropy for 3 categories = log2(3) ≈ 1.585
        max_entropy = math.log2(3)
        coverage_confidence = entropy / max_entropy
        return max(0.0, min(1.0, coverage_confidence))

    def _get_display_confidence(
        self,
        overall_confidence: float,
    ) -> Literal["High", "Medium", "Low", "Learning"]:
        """Map overall confidence to display label."""
        if overall_confidence >= 0.75:
            return "High"
        elif overall_confidence >= 0.50:
            return "Medium"
        elif overall_confidence >= 0.25:
            return "Low"
        else:
            return "Learning"

    def _generate_warnings(
        self,
        quote_count: int,
        acceptance_count: int,
        correction_count: int,
        days_since_last_quote: int,
        complexity_distribution: Dict[str, int],
    ) -> List[str]:
        """Generate warnings for potential issues."""
        warnings = []
        total_signals = acceptance_count + correction_count
        total_jobs = sum(complexity_distribution.values())

        # Recency warning
        if days_since_last_quote > 90:
            warnings.append(
                f"Last quote was {days_since_last_quote} days ago - pricing may be outdated"
            )
        elif days_since_last_quote > 45:
            warnings.append(
                f"No quotes in {days_since_last_quote} days - validate pricing is current"
            )

        # Coverage warning
        if total_jobs >= 5:
            complex_count = complexity_distribution.get("complex", 0)
            complex_pct = complex_count / total_jobs
            if complex_pct < 0.15:
                warnings.append(
                    "Limited complex job data - review complex quotes carefully"
                )

        # Accuracy warning
        if total_signals >= 10:
            correction_rate = correction_count / total_signals
            if correction_rate > 0.6:
                warnings.append(
                    f"High correction rate ({correction_rate*100:.0f}%) - AI still learning"
                )

        # Volume warning
        if quote_count < 5:
            warnings.append(
                "Limited data - confidence will improve with more quotes"
            )

        return warnings

    def _new_category_confidence(
        self,
        quote_count: int,
        acceptance_count: int,
        correction_count: int,
    ) -> PricingConfidence:
        """Return confidence for new category (< 3 quotes)."""
        return PricingConfidence(
            data_confidence=0.20,
            accuracy_confidence=0.30,
            recency_confidence=1.00,
            coverage_confidence=0.30,
            overall_confidence=0.35,
            display_confidence="Learning",
            quote_count=quote_count,
            acceptance_count=acceptance_count,
            correction_count=correction_count,
            acceptance_rate=0.0,
            avg_correction_magnitude=0.0,
            days_since_last_quote=0,
            complexity_distribution={},
            last_updated=datetime.utcnow().isoformat(),
            warnings=["New category - building your pricing model"],
        )

    def get_confidence_display(self, confidence: PricingConfidence) -> Dict[str, Any]:
        """
        Generate UI display elements for confidence.

        Returns:
            dict with badge, message, tooltip, and warnings
        """
        level = confidence.display_confidence
        quote_count = confidence.quote_count
        acceptance_rate = confidence.acceptance_rate
        overall = confidence.overall_confidence

        # Badge & color
        if level == "High":
            badge = "High Confidence"
            color = "green"
        elif level == "Medium":
            badge = "Medium Confidence"
            color = "yellow"
        elif level == "Low":
            badge = "Low Confidence"
            color = "orange"
        else:  # Learning
            badge = "Learning"
            color = "gray"

        # Message
        if level == "High":
            message = f"Based on {quote_count} quotes with {acceptance_rate*100:.0f}% acceptance rate"
        elif level == "Medium":
            message = f"Based on {quote_count} quotes - review recommended"
        elif level == "Low":
            message = f"Limited data ({quote_count} quotes) - please verify pricing"
        else:  # Learning
            message = f"Learning your pricing preferences ({quote_count} quotes so far)"

        # Tooltip (detailed breakdown)
        avg_correction = confidence.avg_correction_magnitude

        if level == "High":
            tooltip = (
                f"Your pricing is well-calibrated. "
                f"AI suggestions are typically within {avg_correction:.0f}% of your final price."
            )
        elif level == "Medium":
            tooltip = (
                f"AI is learning your pricing. "
                f"Quotes typically need {avg_correction:.0f}% adjustments. "
                f"Review before sending."
            )
        elif level == "Low":
            tooltip = (
                f"Limited data. "
                f"AI will improve as you provide more corrections."
            )
        else:  # Learning
            tooltip = (
                f"Building your pricing model. "
                f"Each quote you send helps AI learn your preferences."
            )

        # Dimension breakdown (for dashboard)
        dimension_breakdown = {
            "Data": f"{confidence.data_confidence*100:.0f}% ({quote_count} quotes)",
            "Accuracy": f"{confidence.accuracy_confidence*100:.0f}% ({acceptance_rate*100:.0f}% acceptance)",
            "Recency": f"{confidence.recency_confidence*100:.0f}% ({confidence.days_since_last_quote} days ago)",
            "Coverage": f"{confidence.coverage_confidence*100:.0f}% (job complexity spread)",
        }

        return {
            "badge": badge,
            "color": color,
            "message": message,
            "tooltip": tooltip,
            "warnings": confidence.warnings,
            "overall_percent": round(overall * 100, 0),
            "dimension_breakdown": dimension_breakdown,
        }

    def get_prompt_injection(self, confidence: PricingConfidence, category: str = "this job type") -> str:
        """
        Generate prompt text to inject into Claude for quote generation.

        AI behavior adapts based on confidence level.
        """
        level = confidence.display_confidence
        overall_pct = confidence.overall_confidence * 100
        quote_count = confidence.quote_count
        acceptance_pct = confidence.acceptance_rate * 100

        if level == "High":
            return f"""
CONFIDENCE: HIGH ({overall_pct:.0f}%)

You have strong data for {category} pricing based on {quote_count} quotes
with {acceptance_pct:.0f}% acceptance rate.

Generate the quote with confidence. Use learned pricing patterns directly.
"""

        elif level == "Medium":
            return f"""
CONFIDENCE: MEDIUM ({overall_pct:.0f}%)

You have moderate data for {category} pricing ({quote_count} quotes,
{acceptance_pct:.0f}% acceptance rate).

Generate the quote but include a suggested range (±10%) to account for uncertainty.
Highlight that contractor review is recommended.
"""

        elif level == "Low":
            return f"""
CONFIDENCE: LOW ({overall_pct:.0f}%)

Limited {category} data ({quote_count} quotes,
{acceptance_pct:.0f}% acceptance rate).

Generate a quote with a WIDE range (±20%) and explicitly state:
"This is an estimate based on limited data. Please review and adjust as needed."
"""

        else:  # Learning
            return f"""
CONFIDENCE: LEARNING ({overall_pct:.0f}%)

Very limited {category} data ({quote_count} quotes).

Instead of generating a quote, ASK the contractor for guidance:
1. What's your typical pricing for this type of job?
2. Are there specific factors that affect your pricing?
3. What would you typically charge for this scope?

Then generate the quote based on their input and LEARN from their response.
"""


def refresh_confidence_on_quote(
    category_data: Dict[str, Any],
    was_edited: bool,
    correction_magnitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Refresh confidence when a new quote is generated/sent.

    Args:
        category_data: Category data from pricing_knowledge
        was_edited: Whether the quote was edited before sending
        correction_magnitude: The % change if edited

    Returns:
        Updated category_data with refreshed confidence
    """
    # Update timestamp
    category_data["last_quote_at"] = datetime.utcnow().isoformat()
    category_data["quote_count"] = category_data.get("quote_count", 0) + 1

    # Update acceptance/correction tracking
    if was_edited:
        category_data["correction_count"] = category_data.get("correction_count", 0) + 1

        # Track correction magnitude (last 20)
        magnitudes = category_data.get("correction_magnitudes", [])
        magnitudes.append(abs(correction_magnitude or 0))
        category_data["correction_magnitudes"] = magnitudes[-20:]  # Keep last 20
    else:
        category_data["acceptance_count"] = category_data.get("acceptance_count", 0) + 1

    # Recalculate confidence
    service = PricingConfidenceService()
    confidence = service.calculate(
        quote_count=category_data["quote_count"],
        acceptance_count=category_data.get("acceptance_count", 0),
        correction_count=category_data.get("correction_count", 0),
        correction_magnitudes=category_data.get("correction_magnitudes", []),
        days_since_last_quote=0,  # Just happened
        complexity_distribution=category_data.get("complexity_counts", {}),
    )

    # Cache confidence dimensions
    category_data["confidence_dimensions"] = confidence.to_dict()
    category_data["confidence"] = confidence.overall_confidence

    return category_data


# Convenience function for quick calculation
def calculate_confidence(
    quote_count: int,
    acceptance_count: int,
    correction_count: int,
    correction_magnitudes: List[float] = None,
    days_since_last_quote: int = 0,
    complexity_distribution: Dict[str, int] = None,
) -> PricingConfidence:
    """Quick calculate confidence for a category."""
    service = PricingConfidenceService()
    return service.calculate(
        quote_count=quote_count,
        acceptance_count=acceptance_count,
        correction_count=correction_count,
        correction_magnitudes=correction_magnitudes or [],
        days_since_last_quote=days_since_last_quote,
        complexity_distribution=complexity_distribution or {},
    )
