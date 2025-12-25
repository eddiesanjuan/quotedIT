# Phase 3: Voice Content Extraction System

*Agent: voice-extractor | Completed: 2025-12-24*

## Overview

Extracts pricing signals from voice transcription **WORDS ONLY** (per founder constraint: no tone/hesitation analysis).

## Signal Categories

| Category | Levels | Adjustment Range | Example Keywords |
|----------|--------|------------------|------------------|
| **Difficulty** | high, medium, easy | -0% to +15% labor | "second story", "hard to access" |
| **Relationship** | repeat, referral, new | -5% to 0% | "repeat customer", "referral from" |
| **Timeline** | rush, flexible | 0% to +20% | "ASAP", "rush job", "this week" |
| **Quality** | premium, standard, budget | -10% to +15% | "high-end", "Trex", "budget" |
| **Corrections** | self_correction | N/A (context flag) | "actually", "no wait", "scratch that" |

## Pattern Database

```python
PRICING_SIGNALS = {
    "difficulty": {
        "high": {
            "patterns": [
                r"\b(second|2nd)\s+story\b",
                r"\bhard\s+to\s+access\b",
                r"\bsteep\s+(hill|slope|grade)\b",
                r"\bnarrow\s+(driveway|path)\b",
            ],
            "adjustment": 0.15,  # +15% labor
            "confidence": "HIGH"
        },
        # ...
    },
    "timeline": {
        "rush": {
            "patterns": [
                r"\brush\s+job\b",
                r"\bASAP\b",
                r"\bemergency\b",
                r"\bthis\s+week\b",
            ],
            "adjustment": 0.20,  # +20% rush premium
            "confidence": "HIGH"
        },
        # ...
    }
}
```

## Voice Signal Extractor Class

```python
class VoiceSignalExtractor:
    """Extract pricing signals from transcription words (not tone)."""

    def extract_signals(self, transcription: str) -> Dict:
        """
        Returns:
        {
            "difficulty": ExtractedSignal or None,
            "relationship": ExtractedSignal or None,
            "timeline": ExtractedSignal or None,
            "quality": ExtractedSignal or None,
            "corrections": List[Dict],
            "raw_signals": List[str],
            "summary": str
        }
        """
        # Pattern matching against PRICING_SIGNALS database
        # Takes highest-confidence match per category

    def calculate_suggested_adjustment(self, signals: Dict) -> float:
        """Calculate total multiplier (1.45 = 45% premium)."""
        multiplier = 1.0
        for category in ['difficulty', 'timeline', 'quality', 'relationship']:
            if signals.get(category):
                multiplier += signals[category].adjustment
        return multiplier
```

## Prompt Injection Enhancement

```python
## 🎙️ Voice Content Analysis (Extracted Pricing Signals)

**Access/Difficulty**: Difficult access requiring extra labor
  Keywords detected: "second story"
  Suggested adjustment: +15% to labor

**Timeline**: Rush job - premium pricing justified
  Keywords detected: "rush job, this week"
  Suggested adjustment: +20% rush premium

**IMPORTANT**: These are SUGGESTIONS based on detected keywords.
Apply them if they make sense, but trust learned pricing if conflict.
```

## Example End-to-End Flow

**Input Transcription:**
> "This is a second story deck repair for a repeat customer. They want premium composite. It's a rush job - need it done this week."

**Extracted Signals:**
- Difficulty: HIGH (second story) → +15% labor
- Relationship: REPEAT → -5% discount
- Timeline: RUSH → +20% premium
- Quality: PREMIUM → +15% materials

**Total Multiplier:** 1.45x (45% premium)

## Integration Points

| File | Change |
|------|--------|
| `backend/services/voice_signal_extractor.py` | NEW - Signal extraction engine |
| `backend/services/quote_generator.py` | MODIFY - Call extractor |
| `backend/prompts/quote_generation.py` | MODIFY - Inject signals to prompt |
| `backend/models/database.py` | MODIFY - Add `voice_signals` JSON column |

## Minimum Occurrence Thresholds

| Confidence | Min Occurrences | Rationale |
|------------|-----------------|-----------|
| HIGH | 2 | Clear signal, quick validation |
| MEDIUM | 3 | Need more samples |
| LOW | 5 | Conservative validation |

## Learning Integration (Future)

```python
async def correlate_signals_with_corrections(
    quote_id: str,
    original_signals: dict,
    final_quote: dict,
) -> dict:
    """
    Track if detected signals matched contractor's actual pricing.

    Example:
    - "second story" suggested +15% → contractor added +18%
    - Learn to suggest +18% for future "second story" jobs
    """
```

## Two-Layer Learning

1. **Category-level** (existing): "I price decks at $X/sqft"
2. **Signal-level** (NEW): "When I say 'second story', I add 18%"

Both layers compound for increasingly accurate quotes.
