"""
Voice Signal Extraction Service for Quoted.

Extracts pricing-relevant signals from voice transcriptions:
- Difficulty signals: "tricky access", "tight space", "complicated"
- Relationship signals: "repeat customer", "referred by", "new client"
- Timeline signals: "rush job", "flexible", "needs it by"
- Quality signals: "premium", "budget", "basic", "high-end"
- Correction signals: "actually", "change that", "make it"

These signals inform learning without explicit user feedback.

Design source: .claude/learning-excellence-outputs/phase3-voice.md
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class SignalCategory(Enum):
    """Categories of voice signals."""
    DIFFICULTY = "difficulty"
    RELATIONSHIP = "relationship"
    TIMELINE = "timeline"
    QUALITY = "quality"
    CORRECTION = "correction"


class SignalPolarity(Enum):
    """Whether signal indicates higher or lower pricing."""
    INCREASE = "increase"  # Higher price expected
    DECREASE = "decrease"  # Lower price expected
    NEUTRAL = "neutral"    # Informational only


@dataclass
class VoiceSignal:
    """A detected pricing signal from voice input."""
    category: SignalCategory
    polarity: SignalPolarity
    text: str  # The matched phrase
    confidence: float  # 0-1 confidence in detection
    impact_estimate: float  # Estimated % impact on price (-1 to 1)
    context: str  # Surrounding text for debugging

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "category": self.category.value,
            "polarity": self.polarity.value,
            "text": self.text,
            "confidence": self.confidence,
            "impact_estimate": self.impact_estimate,
            "context": self.context,
        }


@dataclass
class SignalExtractionResult:
    """Complete signal extraction from a transcription."""
    signals: List[VoiceSignal]
    overall_price_adjustment: float  # Suggested % adjustment
    dominant_category: Optional[SignalCategory]
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "signals": [s.to_dict() for s in self.signals],
            "overall_price_adjustment": self.overall_price_adjustment,
            "dominant_category": self.dominant_category.value if self.dominant_category else None,
            "summary": self.summary,
        }


class VoiceSignalExtractor:
    """
    Extracts pricing signals from voice transcriptions.

    Signals are soft inputs that inform the learning system without
    requiring explicit user feedback.

    Usage:
        extractor = VoiceSignalExtractor()
        result = extractor.extract("Rush job for a repeat customer, needs it done by Friday")
        # result.signals contains detected signals
        # result.overall_price_adjustment suggests total impact
    """

    # Signal patterns: (category, polarity, pattern, confidence, impact)
    SIGNAL_PATTERNS = [
        # Difficulty signals - increase price
        (SignalCategory.DIFFICULTY, SignalPolarity.INCREASE,
         r'(?:tricky|difficult|complicated|complex)\s+(?:access|job|work|project)',
         0.8, 0.10),
        (SignalCategory.DIFFICULTY, SignalPolarity.INCREASE,
         r'(?:tight|narrow|limited)\s+(?:space|area|access)',
         0.7, 0.08),
        (SignalCategory.DIFFICULTY, SignalPolarity.INCREASE,
         r'second\s+(?:story|floor|level)',
         0.9, 0.15),
        (SignalCategory.DIFFICULTY, SignalPolarity.INCREASE,
         r'(?:steep|sloped|sloping)\s+(?:yard|lot|grade|hill)',
         0.8, 0.12),
        (SignalCategory.DIFFICULTY, SignalPolarity.INCREASE,
         r'(?:hard\s+to|difficult\s+to)\s+(?:get\s+to|access|reach)',
         0.7, 0.10),
        (SignalCategory.DIFFICULTY, SignalPolarity.DECREASE,
         r'(?:easy|simple|straightforward|basic)\s+(?:job|project|work)',
         0.7, -0.05),

        # Relationship signals
        (SignalCategory.RELATIONSHIP, SignalPolarity.DECREASE,
         r'repeat\s+customer',
         0.9, -0.05),
        (SignalCategory.RELATIONSHIP, SignalPolarity.DECREASE,
         r'(?:referred\s+by|referral\s+from|friend\s+of)',
         0.8, -0.05),
        (SignalCategory.RELATIONSHIP, SignalPolarity.NEUTRAL,
         r'(?:new\s+client|first\s+time|new\s+customer)',
         0.8, 0.0),
        (SignalCategory.RELATIONSHIP, SignalPolarity.DECREASE,
         r'(?:neighbor|next\s+door)',
         0.6, -0.03),

        # Timeline signals
        (SignalCategory.TIMELINE, SignalPolarity.INCREASE,
         r'(?:rush|urgent|asap|emergency)',
         0.9, 0.20),
        (SignalCategory.TIMELINE, SignalPolarity.INCREASE,
         r'needs?\s+(?:it|this)\s+(?:by|done\s+by)\s+(?:tomorrow|next\s+week|friday)',
         0.8, 0.15),
        (SignalCategory.TIMELINE, SignalPolarity.DECREASE,
         r'(?:flexible|no\s+rush|whenever|take\s+your\s+time)',
         0.7, -0.05),
        (SignalCategory.TIMELINE, SignalPolarity.NEUTRAL,
         r'(?:spring|summer|fall|winter)\s+(?:project|job)',
         0.6, 0.0),

        # Quality signals
        (SignalCategory.QUALITY, SignalPolarity.INCREASE,
         r'(?:premium|high[\s-]?end|top[\s-]?of[\s-]?the[\s-]?line|best)',
         0.8, 0.15),
        (SignalCategory.QUALITY, SignalPolarity.INCREASE,
         r'(?:trex\s+transcend|azek|timbertech\s+pro)',
         0.9, 0.12),
        (SignalCategory.QUALITY, SignalPolarity.DECREASE,
         r'(?:budget|basic|economy|cheap|affordable)',
         0.8, -0.10),
        (SignalCategory.QUALITY, SignalPolarity.DECREASE,
         r'(?:pressure\s+treated|pt|pine)',
         0.7, -0.08),
        (SignalCategory.QUALITY, SignalPolarity.NEUTRAL,
         r'(?:standard|regular|normal)',
         0.6, 0.0),

        # Correction signals (user changing their mind mid-speech)
        (SignalCategory.CORRECTION, SignalPolarity.NEUTRAL,
         r'(?:actually|wait|no|scratch\s+that|change\s+that)',
         0.6, 0.0),
        (SignalCategory.CORRECTION, SignalPolarity.INCREASE,
         r'(?:actually|wait).*(?:bigger|more|larger|extra)',
         0.7, 0.05),
        (SignalCategory.CORRECTION, SignalPolarity.DECREASE,
         r'(?:actually|wait).*(?:smaller|less|simpler)',
         0.7, -0.05),
    ]

    def __init__(self):
        """Initialize the extractor with compiled patterns."""
        self._patterns = [
            (cat, pol, re.compile(pattern, re.IGNORECASE), conf, impact)
            for cat, pol, pattern, conf, impact in self.SIGNAL_PATTERNS
        ]

    def extract(self, transcription: str) -> SignalExtractionResult:
        """
        Extract all pricing signals from a transcription.

        Args:
            transcription: Voice transcription text

        Returns:
            SignalExtractionResult with all detected signals
        """
        if not transcription or not transcription.strip():
            return SignalExtractionResult(
                signals=[],
                overall_price_adjustment=0.0,
                dominant_category=None,
                summary="No transcription provided",
            )

        signals = []
        text = transcription.strip()

        for category, polarity, pattern, confidence, impact in self._patterns:
            match = pattern.search(text)
            if match:
                # Extract context (30 chars before and after)
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]
                if start > 0:
                    context = "..." + context
                if end < len(text):
                    context = context + "..."

                signals.append(VoiceSignal(
                    category=category,
                    polarity=polarity,
                    text=match.group(0),
                    confidence=confidence,
                    impact_estimate=impact,
                    context=context,
                ))

        # Calculate overall adjustment (sum of impacts, weighted by confidence)
        total_adjustment = sum(
            s.impact_estimate * s.confidence
            for s in signals
        )
        # Cap at +/- 30%
        overall_adjustment = max(-0.30, min(0.30, total_adjustment))

        # Find dominant category
        dominant = self._find_dominant_category(signals)

        # Generate summary
        summary = self._generate_summary(signals, overall_adjustment)

        return SignalExtractionResult(
            signals=signals,
            overall_price_adjustment=round(overall_adjustment, 3),
            dominant_category=dominant,
            summary=summary,
        )

    def _find_dominant_category(
        self, signals: List[VoiceSignal]
    ) -> Optional[SignalCategory]:
        """Find the category with most/strongest signals."""
        if not signals:
            return None

        category_scores: Dict[SignalCategory, float] = {}
        for signal in signals:
            if signal.category not in category_scores:
                category_scores[signal.category] = 0
            category_scores[signal.category] += abs(signal.impact_estimate) * signal.confidence

        if not category_scores:
            return None

        return max(category_scores.keys(), key=lambda c: category_scores[c])

    def _generate_summary(
        self,
        signals: List[VoiceSignal],
        overall_adjustment: float,
    ) -> str:
        """Generate human-readable summary of signals."""
        if not signals:
            return "No pricing signals detected"

        parts = []

        # Group by polarity
        increases = [s for s in signals if s.polarity == SignalPolarity.INCREASE]
        decreases = [s for s in signals if s.polarity == SignalPolarity.DECREASE]

        if increases:
            reasons = [s.text for s in increases[:3]]
            parts.append(f"Price increase signals: {', '.join(reasons)}")

        if decreases:
            reasons = [s.text for s in decreases[:3]]
            parts.append(f"Price decrease signals: {', '.join(reasons)}")

        if overall_adjustment > 0:
            parts.append(f"Suggested adjustment: +{overall_adjustment:.0%}")
        elif overall_adjustment < 0:
            parts.append(f"Suggested adjustment: {overall_adjustment:.0%}")
        else:
            parts.append("Net adjustment: neutral")

        return "; ".join(parts)

    def extract_for_category(
        self,
        transcription: str,
        category: SignalCategory,
    ) -> List[VoiceSignal]:
        """Extract signals for a specific category only."""
        result = self.extract(transcription)
        return [s for s in result.signals if s.category == category]


# Convenience function for quick extraction
def extract_voice_signals(transcription: str) -> SignalExtractionResult:
    """Quick extract signals from transcription."""
    return VoiceSignalExtractor().extract(transcription)
