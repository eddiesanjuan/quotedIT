"""
Learning Quality Scoring Service for Quoted.

Scores learning statements on 4 dimensions:
- Specificity (25%): Does it mention specific numbers, materials, contexts?
- Actionability (35%): Can Claude apply this directly to future quotes?
- Clarity (25%): Is it unambiguous and well-formed?
- Anti-patterns (-15%): Penalty for vague or contradictory statements

Quality thresholds:
- REJECT: < 40 (logged but discarded)
- REVIEW: 40-60 (stored with flag for manual review)
- REFINE: 60-70 (stored, may be improved)
- ACCEPT: > 70 (high confidence, apply immediately)

Design source: .claude/learning-excellence-outputs/phase2-quality-scoring.md
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import re


class QualityTier(Enum):
    """Quality classification tiers for learning statements."""
    REJECT = "reject"      # < 40: Discard
    REVIEW = "review"      # 40-60: Store with flag
    REFINE = "refine"      # 60-70: Good but improvable
    ACCEPT = "accept"      # > 70: High quality


@dataclass
class QualityScore:
    """Complete quality assessment for a learning statement."""
    overall_score: float  # 0-100
    tier: QualityTier

    # Dimension scores (0-100 each)
    specificity_score: float
    actionability_score: float
    clarity_score: float
    anti_pattern_penalty: float

    # Metadata
    detected_anti_patterns: List[str]
    improvement_suggestions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "overall_score": self.overall_score,
            "tier": self.tier.value,
            "specificity": self.specificity_score,
            "actionability": self.actionability_score,
            "clarity": self.clarity_score,
            "anti_pattern_penalty": self.anti_pattern_penalty,
            "detected_anti_patterns": self.detected_anti_patterns,
            "improvement_suggestions": self.improvement_suggestions,
        }


class LearningQualityScorer:
    """
    Scores learning statements for quality before storage.

    Uses rule-based heuristics for speed and consistency.
    Claude-based scoring available for edge cases.

    Usage:
        scorer = LearningQualityScorer()
        score = scorer.score("Always add 15% for second story work")
        if score.tier != QualityTier.REJECT:
            # Store the learning with its quality metadata
            store_learning(text, score.to_dict())
    """

    # Dimension weights (must sum to 1.0 when anti-pattern applied)
    SPECIFICITY_WEIGHT = 0.25
    ACTIONABILITY_WEIGHT = 0.35
    CLARITY_WEIGHT = 0.25
    ANTI_PATTERN_WEIGHT = 0.15  # Subtracted, not added

    # Threshold boundaries
    REJECT_THRESHOLD = 40
    REVIEW_THRESHOLD = 60
    REFINE_THRESHOLD = 70

    # Specificity indicators (presence increases score)
    SPECIFICITY_PATTERNS = [
        r'\$?\d+(?:,\d{3})*(?:\.\d{2})?',  # Dollar amounts
        r'\d+%',  # Percentages
        r'\d+\s*(?:sqft|sq\s*ft|square\s*feet)',  # Square footage
        r'\d+\s*(?:linear\s*)?(?:ft|feet|foot)',  # Linear feet
        r'\d+\s*(?:hours?|days?|weeks?)',  # Time estimates
        r'(?:trex|azek|timbertech|certainteed)',  # Brand names (case insensitive)
        r'(?:composite|pressure[\s-]?treated|cedar|redwood)',  # Material types
        r'(?:second\s*story|ground\s*level|elevated)',  # Context
    ]

    # Actionability indicators
    ACTIONABILITY_PATTERNS = [
        r'(?:always|never|typically|usually)',  # Frequency indicators
        r'(?:add|increase|decrease|reduce|multiply)',  # Action verbs
        r'(?:when|if|for)\s+(?:\w+\s+){1,5}(?:,|$)',  # Conditional clauses
        r'(?:minimum|maximum|at\s*least|no\s*more\s*than)',  # Bounds
    ]

    # Clarity indicators (absence decreases score)
    CLARITY_NEGATIVE_PATTERNS = [
        r'(?:maybe|perhaps|might|could\s*be)',  # Uncertainty
        r'(?:etc\.?|and\s*so\s*on|\.\.\.)',  # Incomplete
        r'(?:it\s*depends|varies)',  # Too vague
    ]

    # Anti-patterns (each triggers penalty)
    ANTI_PATTERNS = {
        r'^(?:good|bad|nice|okay|fine)\s+': "Vague quality descriptor",
        r'(?:i\s*think|i\s*feel|i\s*believe)': "Subjective opinion marker",
        r'(?:sometimes|occasionally|once\s*in\s*a\s*while)': "Inconsistent applicability",
        r'^.{0,20}$': "Too short to be actionable",
        r'^.{500,}$': "Too long and unfocused",
        r'(?:don\'?t|do\s*not)\s+(?:know|remember)': "Knowledge gap",
    }

    def __init__(self):
        """Initialize the scorer with compiled regex patterns."""
        self._specificity_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.SPECIFICITY_PATTERNS
        ]
        self._actionability_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.ACTIONABILITY_PATTERNS
        ]
        self._clarity_negative_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.CLARITY_NEGATIVE_PATTERNS
        ]
        self._anti_patterns = {
            re.compile(k, re.IGNORECASE): v
            for k, v in self.ANTI_PATTERNS.items()
        }

    def score(self, learning_text: str) -> QualityScore:
        """
        Score a learning statement for quality.

        Args:
            learning_text: The learning statement to score

        Returns:
            QualityScore with dimension breakdown and tier classification
        """
        if not learning_text or not learning_text.strip():
            return QualityScore(
                overall_score=0,
                tier=QualityTier.REJECT,
                specificity_score=0,
                actionability_score=0,
                clarity_score=0,
                anti_pattern_penalty=100,
                detected_anti_patterns=["Empty or whitespace-only input"],
                improvement_suggestions=["Provide a non-empty learning statement"],
            )

        text = learning_text.strip()

        # Score each dimension
        specificity = self._score_specificity(text)
        actionability = self._score_actionability(text)
        clarity = self._score_clarity(text)
        anti_patterns, penalty = self._detect_anti_patterns(text)

        # Calculate weighted score
        raw_score = (
            specificity * self.SPECIFICITY_WEIGHT +
            actionability * self.ACTIONABILITY_WEIGHT +
            clarity * self.CLARITY_WEIGHT
        )

        # Apply anti-pattern penalty
        overall = max(0, raw_score - (penalty * self.ANTI_PATTERN_WEIGHT))

        # Determine tier
        tier = self._classify_tier(overall)

        # Generate improvement suggestions
        suggestions = self._generate_suggestions(
            text, specificity, actionability, clarity, anti_patterns
        )

        return QualityScore(
            overall_score=round(overall, 1),
            tier=tier,
            specificity_score=round(specificity, 1),
            actionability_score=round(actionability, 1),
            clarity_score=round(clarity, 1),
            anti_pattern_penalty=round(penalty, 1),
            detected_anti_patterns=anti_patterns,
            improvement_suggestions=suggestions,
        )

    def _score_specificity(self, text: str) -> float:
        """Score based on presence of specific details."""
        matches = sum(
            1 for pattern in self._specificity_patterns
            if pattern.search(text)
        )
        # Scale: 0 matches = 30, 1 = 50, 2 = 70, 3+ = 90
        if matches == 0:
            return 30.0
        elif matches == 1:
            return 50.0
        elif matches == 2:
            return 70.0
        else:
            return min(90.0, 70.0 + (matches - 2) * 10)

    def _score_actionability(self, text: str) -> float:
        """Score based on actionable language."""
        matches = sum(
            1 for pattern in self._actionability_patterns
            if pattern.search(text)
        )
        # Scale: 0 matches = 40, 1 = 60, 2+ = 80
        if matches == 0:
            return 40.0
        elif matches == 1:
            return 60.0
        else:
            return min(85.0, 60.0 + (matches - 1) * 12.5)

    def _score_clarity(self, text: str) -> float:
        """Score based on clarity (penalize uncertainty markers)."""
        negative_matches = sum(
            1 for pattern in self._clarity_negative_patterns
            if pattern.search(text)
        )
        # Start at 80, subtract 20 per negative marker
        base_score = 80.0
        return max(20.0, base_score - (negative_matches * 20))

    def _detect_anti_patterns(self, text: str) -> tuple[List[str], float]:
        """Detect anti-patterns and calculate penalty."""
        detected = []
        for pattern, description in self._anti_patterns.items():
            if pattern.search(text):
                detected.append(description)

        # Each anti-pattern is worth 25 penalty points
        penalty = min(100, len(detected) * 25)
        return detected, penalty

    def _classify_tier(self, score: float) -> QualityTier:
        """Classify score into quality tier."""
        if score < self.REJECT_THRESHOLD:
            return QualityTier.REJECT
        elif score < self.REVIEW_THRESHOLD:
            return QualityTier.REVIEW
        elif score < self.REFINE_THRESHOLD:
            return QualityTier.REFINE
        else:
            return QualityTier.ACCEPT

    def _generate_suggestions(
        self,
        text: str,
        specificity: float,
        actionability: float,
        clarity: float,
        anti_patterns: List[str],
    ) -> List[str]:
        """Generate improvement suggestions based on scores."""
        suggestions = []

        if specificity < 50:
            suggestions.append(
                "Add specific numbers (prices, percentages, measurements)"
            )

        if actionability < 60:
            suggestions.append(
                "Use action words (add, increase, reduce) and conditions (when, if, for)"
            )

        if clarity < 60:
            suggestions.append(
                "Remove uncertainty words (maybe, perhaps, it depends)"
            )

        if anti_patterns:
            suggestions.append(
                f"Remove anti-patterns: {', '.join(anti_patterns[:2])}"
            )

        if len(text) < 30:
            suggestions.append(
                "Expand with more context about when this applies"
            )

        return suggestions[:3]  # Return top 3 most important

    def batch_score(self, learnings: List[str]) -> List[QualityScore]:
        """Score multiple learning statements."""
        return [self.score(text) for text in learnings]

    def filter_by_tier(
        self,
        learnings: List[str],
        minimum_tier: QualityTier = QualityTier.REVIEW,
    ) -> List[tuple[str, QualityScore]]:
        """
        Filter learnings by minimum quality tier.

        Args:
            learnings: List of learning statements
            minimum_tier: Minimum tier to include (default: REVIEW)

        Returns:
            List of (text, score) tuples that meet minimum tier
        """
        tier_order = [QualityTier.REJECT, QualityTier.REVIEW, QualityTier.REFINE, QualityTier.ACCEPT]
        min_index = tier_order.index(minimum_tier)

        results = []
        for text in learnings:
            score = self.score(text)
            if tier_order.index(score.tier) >= min_index:
                results.append((text, score))

        return results


# Convenience function for quick scoring
def score_learning(text: str) -> QualityScore:
    """Quick score a single learning statement."""
    return LearningQualityScorer().score(text)


# Convenience function for filtering
def filter_quality_learnings(
    learnings: List[str],
    minimum_tier: QualityTier = QualityTier.REVIEW,
) -> List[str]:
    """Filter learnings to only include those meeting minimum quality."""
    scorer = LearningQualityScorer()
    return [
        text for text, score in scorer.filter_by_tier(learnings, minimum_tier)
    ]
