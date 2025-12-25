"""
Learning Relevance Selection Service for Quoted.

Replaces the naive `learned_adjustments[-7:]` with intelligent selection
based on 4 dimensions:
- Keyword Match (40%): Does the learning mention terms from current job?
- Recency (30%): How recent is the learning? (30-day half-life decay)
- Specificity (20%): Higher quality learnings rank higher
- Foundational (10%): Universal rules ("always", "never") get bonus

Design source: .claude/learning-excellence-outputs/phase3-relevance.md
"""

import re
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from .learning_quality import LearningQualityScorer, QualityScore


@dataclass
class RelevanceScore:
    """Complete relevance assessment for a learning statement."""
    overall_score: float  # 0-100
    keyword_score: float
    recency_score: float
    specificity_score: float
    foundational_score: float

    # Metadata
    matched_keywords: List[str]
    is_foundational: bool
    days_old: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "overall_score": self.overall_score,
            "keyword_score": self.keyword_score,
            "recency_score": self.recency_score,
            "specificity_score": self.specificity_score,
            "foundational_score": self.foundational_score,
            "matched_keywords": self.matched_keywords,
            "is_foundational": self.is_foundational,
            "days_old": self.days_old,
        }


@dataclass
class LearningMetadata:
    """Metadata stored alongside each learning statement."""
    text: str
    quality_score: float
    created_at: datetime
    source: str  # "correction" | "acceptance" | "dna_transfer"
    outcome_boost: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningMetadata":
        """Create from dictionary (JSON storage format)."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        elif created_at is None:
            created_at = datetime.utcnow()

        return cls(
            text=data.get("text", ""),
            quality_score=data.get("quality_score", 50.0),
            created_at=created_at,
            source=data.get("source", "correction"),
            outcome_boost=data.get("outcome_boost", 0.0),
        )


class LearningRelevanceSelector:
    """
    Selects the most relevant learnings for a given job context.

    Replaces naive recency-based selection ([-7:]) with intelligent
    multi-factor ranking.

    Usage:
        selector = LearningRelevanceSelector()
        relevant = selector.select(
            learnings=all_category_learnings,
            transcription="20x20 composite deck with cable railings",
            category="composite_deck",
            max_learnings=7,
        )
    """

    # Dimension weights (must sum to 1.0)
    KEYWORD_WEIGHT = 0.40
    RECENCY_WEIGHT = 0.30
    SPECIFICITY_WEIGHT = 0.20
    FOUNDATIONAL_WEIGHT = 0.10

    # Recency decay parameters
    RECENCY_HALF_LIFE_DAYS = 30  # Score halves every 30 days

    # Foundational keywords (universal rules get bonus)
    FOUNDATIONAL_KEYWORDS = [
        "always", "never", "all", "every",
        "minimum", "maximum", "at least", "no more than",
        "must", "required", "standard",
    ]

    # Common contractor keywords to extract from transcription
    DOMAIN_KEYWORDS = [
        # Materials
        "composite", "trex", "azek", "timbertech", "wood", "cedar", "redwood",
        "pressure treated", "pt", "aluminum", "steel", "cable", "glass",
        # Job types
        "deck", "fence", "patio", "pergola", "stairs", "railing", "siding",
        "roof", "gutter", "window", "door", "paint", "concrete",
        # Conditions
        "demolition", "demo", "removal", "second story", "elevated", "ground level",
        "permit", "inspection", "slope", "drainage", "waterproofing",
        # Sizes
        "sqft", "sq ft", "linear ft", "feet", "foot", "yard",
    ]

    def __init__(self):
        """Initialize the selector with quality scorer."""
        self._quality_scorer = LearningQualityScorer()
        self._foundational_pattern = re.compile(
            r'\b(' + '|'.join(self.FOUNDATIONAL_KEYWORDS) + r')\b',
            re.IGNORECASE
        )
        self._domain_patterns = [
            re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
            for kw in self.DOMAIN_KEYWORDS
        ]

    def select(
        self,
        learnings: List[Union[str, Dict[str, Any]]],
        transcription: str,
        category: str,
        max_learnings: int = 7,
    ) -> List[str]:
        """
        Select the most relevant learnings for the current job.

        Args:
            learnings: List of learning texts or metadata dicts
            transcription: Current job transcription
            category: Job category for context
            max_learnings: Maximum learnings to return (default 7)

        Returns:
            List of most relevant learning texts, ordered by relevance
        """
        if not learnings:
            return []

        # Extract keywords from transcription
        job_keywords = self._extract_keywords(transcription)

        # Score each learning
        scored_learnings: List[Tuple[str, RelevanceScore]] = []

        for learning in learnings:
            # Handle both plain strings and metadata dicts
            if isinstance(learning, dict):
                metadata = LearningMetadata.from_dict(learning)
                text = metadata.text
                quality = metadata.quality_score
                created_at = metadata.created_at
            else:
                text = learning
                # For legacy plain strings, estimate quality and use default date
                quality = self._quality_scorer.score(text).overall_score
                created_at = datetime.utcnow() - timedelta(days=7)  # Assume 1 week old

            score = self._score_relevance(
                text=text,
                job_keywords=job_keywords,
                quality_score=quality,
                created_at=created_at,
            )
            scored_learnings.append((text, score))

        # Sort by overall score descending
        scored_learnings.sort(key=lambda x: x[1].overall_score, reverse=True)

        # Return top N texts
        return [text for text, _ in scored_learnings[:max_learnings]]

    def select_with_scores(
        self,
        learnings: List[Union[str, Dict[str, Any]]],
        transcription: str,
        category: str,
        max_learnings: int = 7,
    ) -> List[Tuple[str, RelevanceScore]]:
        """
        Select learnings and return with their relevance scores.

        Same as select() but includes scores for debugging/logging.
        """
        if not learnings:
            return []

        job_keywords = self._extract_keywords(transcription)
        scored_learnings: List[Tuple[str, RelevanceScore]] = []

        for learning in learnings:
            if isinstance(learning, dict):
                metadata = LearningMetadata.from_dict(learning)
                text = metadata.text
                quality = metadata.quality_score
                created_at = metadata.created_at
            else:
                text = learning
                quality = self._quality_scorer.score(text).overall_score
                created_at = datetime.utcnow() - timedelta(days=7)

            score = self._score_relevance(
                text=text,
                job_keywords=job_keywords,
                quality_score=quality,
                created_at=created_at,
            )
            scored_learnings.append((text, score))

        scored_learnings.sort(key=lambda x: x[1].overall_score, reverse=True)
        return scored_learnings[:max_learnings]

    def _extract_keywords(self, transcription: str) -> List[str]:
        """Extract domain-relevant keywords from transcription."""
        keywords = []
        text_lower = transcription.lower()

        for pattern in self._domain_patterns:
            if pattern.search(transcription):
                # Extract the actual keyword that matched
                match = pattern.search(transcription)
                if match:
                    keywords.append(match.group(0).lower())

        # Also extract numbers for specificity matching
        numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', transcription)
        keywords.extend(numbers[:5])  # Limit to 5 numbers

        return list(set(keywords))  # Deduplicate

    def _score_relevance(
        self,
        text: str,
        job_keywords: List[str],
        quality_score: float,
        created_at: datetime,
    ) -> RelevanceScore:
        """Score a single learning for relevance."""

        # 1. Keyword match score
        keyword_score, matched = self._score_keywords(text, job_keywords)

        # 2. Recency score (exponential decay)
        recency_score, days_old = self._score_recency(created_at)

        # 3. Specificity score (from quality)
        specificity_score = min(100, quality_score * 1.2)  # Boost slightly

        # 4. Foundational bonus
        foundational_score, is_foundational = self._score_foundational(text)

        # Calculate weighted overall
        overall = (
            keyword_score * self.KEYWORD_WEIGHT +
            recency_score * self.RECENCY_WEIGHT +
            specificity_score * self.SPECIFICITY_WEIGHT +
            foundational_score * self.FOUNDATIONAL_WEIGHT
        )

        return RelevanceScore(
            overall_score=round(overall, 1),
            keyword_score=round(keyword_score, 1),
            recency_score=round(recency_score, 1),
            specificity_score=round(specificity_score, 1),
            foundational_score=round(foundational_score, 1),
            matched_keywords=matched,
            is_foundational=is_foundational,
            days_old=days_old,
        )

    def _score_keywords(self, text: str, job_keywords: List[str]) -> Tuple[float, List[str]]:
        """Score based on keyword overlap with current job."""
        if not job_keywords:
            return 50.0, []  # Neutral if no keywords to match

        text_lower = text.lower()
        matched = [kw for kw in job_keywords if kw.lower() in text_lower]

        # Scale: 0 matches = 20, 1 = 50, 2 = 70, 3+ = 85
        match_count = len(matched)
        if match_count == 0:
            return 20.0, matched
        elif match_count == 1:
            return 50.0, matched
        elif match_count == 2:
            return 70.0, matched
        else:
            return min(90.0, 70.0 + (match_count - 2) * 10), matched

    def _score_recency(self, created_at: datetime) -> Tuple[float, int]:
        """Score based on age with exponential decay."""
        now = datetime.utcnow()
        if created_at.tzinfo:
            # Make naive for comparison
            created_at = created_at.replace(tzinfo=None)

        delta = now - created_at
        days_old = max(0, delta.days)

        # Exponential decay: score = 100 * (0.5 ^ (days / half_life))
        decay_factor = math.pow(0.5, days_old / self.RECENCY_HALF_LIFE_DAYS)
        score = 100 * decay_factor

        # Floor at 10 to prevent total irrelevance
        return max(10.0, score), days_old

    def _score_foundational(self, text: str) -> Tuple[float, bool]:
        """Score bonus for foundational/universal rules."""
        is_foundational = bool(self._foundational_pattern.search(text))
        # Foundational rules get 100, others get 50
        return (100.0 if is_foundational else 50.0), is_foundational


# Convenience function for direct use in quote_generation.py
def select_relevant_learnings(
    learned_adjustments: List[Union[str, Dict[str, Any]]],
    transcription: str,
    category: str,
    max_learnings: int = 7,
) -> List[str]:
    """
    Select relevant learnings for injection into quote generation.

    Drop-in replacement for `learned_adjustments[-7:]` in quote_generation.py
    """
    selector = LearningRelevanceSelector()
    return selector.select(
        learnings=learned_adjustments,
        transcription=transcription,
        category=category,
        max_learnings=max_learnings,
    )
