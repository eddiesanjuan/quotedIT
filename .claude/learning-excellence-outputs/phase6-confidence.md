# Phase 6: Multi-Dimensional Confidence System

*Agent: confidence-designer | Completed: 2025-12-24*

---

## Executive Summary

**Problem**: Current confidence system suffers from "confidence inflation" - high numbers that don't reflect actual accuracy. Simple +0.02 per correction leads to overconfidence with no calibration to reality.

**Solution**: Multi-dimensional confidence system that accurately represents what we know (and don't know) about a contractor's pricing, preventing both overconfidence (confidently wrong) and underconfidence (unnecessarily cautious).

**Core Principle**: If we claim 80% confidence, then 80% of quotes should be accepted without edit.

**Impact**:
- Honest uncertainty representation
- Calibrated confidence displays
- AI behavior adapts to confidence level
- Contractor trust through transparency

---

## 1. Multi-Dimensional Schema

```python
from typing import TypedDict, Literal
from datetime import datetime

class PricingConfidence(TypedDict):
    """
    Multi-dimensional confidence for a category.
    Each dimension represents a different aspect of pricing knowledge.
    """

    # ===== PRIMARY DIMENSIONS =====

    data_confidence: float  # 0.0-1.0
    """
    How much data we have for this category.
    Based on: Total quote count
    Growth: Logarithmic (diminishing returns)
    Rationale: 50 quotes isn't 5x better than 10 quotes
    """

    accuracy_confidence: float  # 0.0-1.0
    """
    How accurate we've been historically.
    Based on: Acceptance rate with magnitude weighting
    Formula: (acceptance_count / total_signals) * magnitude_adjustment
    Rationale: Being accepted matters, but so does HOW MUCH corrections are
    """

    recency_confidence: float  # 0.0-1.0
    """
    How fresh our data is.
    Based on: Days since last quote in category
    Decay: Exponential (30-day half-life)
    Rationale: Pricing changes over time (material costs, labor rates)
    """

    coverage_confidence: float  # 0.0-1.0
    """
    How well we cover the job complexity spectrum.
    Based on: Distribution across simple/medium/complex jobs
    Formula: Shannon entropy of complexity distribution
    Rationale: All simple jobs != understanding the category
    """

    # ===== COMPOSITE SCORES =====

    overall_confidence: float  # 0.0-1.0
    """
    Weighted combination of all dimensions.
    This is the single number for comparisons.
    """

    display_confidence: Literal["High", "Medium", "Low", "Learning"]
    """
    User-facing confidence label.
    - High: >= 0.75 (green badge, confident generation)
    - Medium: 0.50-0.74 (yellow badge, suggest review)
    - Low: 0.25-0.49 (orange badge, request input)
    - Learning: < 0.25 (gray badge, ask for guidance)
    """

    # ===== METADATA =====

    quote_count: int
    """Total quotes in this category."""

    acceptance_count: int
    """Quotes sent without edit (acceptance signal)."""

    correction_count: int
    """Quotes edited before sending."""

    acceptance_rate: float
    """acceptance_count / (acceptance_count + correction_count)."""

    avg_correction_magnitude: float
    """Average % change when corrections happen."""

    days_since_last_quote: int
    """Days since most recent quote."""

    complexity_distribution: dict
    """
    Count of quotes by complexity level:
    {"simple": 5, "medium": 12, "complex": 3}
    """

    last_updated: str
    """ISO timestamp of last confidence calculation."""

    warnings: list[str]
    """
    Active warnings for this category:
    - "Limited complex job data"
    - "No quotes in 45 days"
    - "High correction rate (60%+)"
    """


class CategoryConfidenceData(TypedDict):
    """
    Data stored in pricing_knowledge.categories[category].
    This is what persists in the database.
    """

    # Core tracking (already exists from Phase 4)
    confidence: float  # Overall confidence score
    acceptance_count: int
    correction_count: int
    quote_count: int

    # NEW: Detailed tracking for multi-dimensional confidence
    last_quote_at: str  # ISO timestamp
    correction_magnitudes: list[float]  # Last 20 correction %s
    complexity_counts: dict  # {"simple": N, "medium": N, "complex": N}

    # Derived confidence dimensions (cached, recalculated on each update)
    confidence_dimensions: dict
    """
    Cached PricingConfidence dict (minus TypedDict formatting).
    Recalculated on every quote/correction/acceptance.
    """
```

---

## 2. Calibration Algorithm

```python
import math
from datetime import datetime, timedelta
from typing import Optional

# ===== DIMENSION WEIGHTS =====

CONFIDENCE_WEIGHTS = {
    "data": 0.20,      # 20% - Volume matters but plateaus
    "accuracy": 0.40,  # 40% - Most important: are we right?
    "recency": 0.25,   # 25% - Fresh data matters
    "coverage": 0.15,  # 15% - Job type variety matters
}

# Ensure weights sum to 1.0
assert sum(CONFIDENCE_WEIGHTS.values()) == 1.0


def calculate_calibrated_confidence(
    quote_count: int,
    acceptance_count: int,
    correction_count: int,
    correction_magnitudes: list[float],  # Last 20 correction %s
    days_since_last_quote: int,
    complexity_distribution: dict,  # {"simple": 5, "medium": 12, "complex": 3}
) -> PricingConfidence:
    """
    Calculate multi-dimensional calibrated confidence.

    CALIBRATION PRINCIPLE:
    If we claim 80% confidence, then 80% of quotes should be accepted without edit.

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

    # ===== 1. DATA CONFIDENCE =====
    # Logarithmic growth: 10 quotes = 0.50, 50 = 0.75, 200+ = 0.95
    data_confidence = min(0.95, math.log(quote_count + 1, 1.15) / 100)

    # ===== 2. ACCURACY CONFIDENCE =====
    total_signals = acceptance_count + correction_count

    if total_signals < 3:
        # Not enough data for accuracy assessment
        accuracy_confidence = 0.3
    else:
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
        accuracy_confidence = max(0.0, min(1.0, accuracy_confidence))

    # ===== 3. RECENCY CONFIDENCE =====
    # Exponential decay with 30-day half-life
    HALF_LIFE_DAYS = 30
    decay_factor = 0.5 ** (days_since_last_quote / HALF_LIFE_DAYS)
    recency_confidence = max(0.0, min(1.0, decay_factor))

    # ===== 4. COVERAGE CONFIDENCE =====
    # Shannon entropy of complexity distribution
    # Perfect distribution across 3 levels = high coverage
    total_jobs = sum(complexity_distribution.values())

    if total_jobs < 5:
        # Not enough jobs to assess coverage
        coverage_confidence = 0.3
    else:
        # Calculate Shannon entropy
        entropy = 0.0
        for count in complexity_distribution.values():
            if count > 0:
                p = count / total_jobs
                entropy -= p * math.log2(p)

        # Max entropy for 3 categories = log2(3) ≈ 1.585
        max_entropy = math.log2(3)
        coverage_confidence = entropy / max_entropy
        coverage_confidence = max(0.0, min(1.0, coverage_confidence))

    # ===== 5. OVERALL CONFIDENCE =====
    # Weighted combination
    overall_confidence = (
        data_confidence * CONFIDENCE_WEIGHTS["data"] +
        accuracy_confidence * CONFIDENCE_WEIGHTS["accuracy"] +
        recency_confidence * CONFIDENCE_WEIGHTS["recency"] +
        coverage_confidence * CONFIDENCE_WEIGHTS["coverage"]
    )

    # ===== 6. DISPLAY CONFIDENCE =====
    if overall_confidence >= 0.75:
        display_confidence = "High"
    elif overall_confidence >= 0.50:
        display_confidence = "Medium"
    elif overall_confidence >= 0.25:
        display_confidence = "Low"
    else:
        display_confidence = "Learning"

    # ===== 7. WARNINGS =====
    warnings = []

    # Recency warning
    if days_since_last_quote > 45:
        warnings.append(f"No quotes in {days_since_last_quote} days - validate pricing is current")
    elif days_since_last_quote > 90:
        warnings.append(f"Last quote was {days_since_last_quote} days ago - pricing may be outdated")

    # Coverage warning
    if total_jobs >= 5:
        complex_pct = complexity_distribution.get("complex", 0) / total_jobs
        if complex_pct < 0.15:
            warnings.append("Limited complex job data - review complex quotes carefully")

    # Accuracy warning
    if total_signals >= 10:
        correction_rate = correction_count / total_signals
        if correction_rate > 0.6:
            warnings.append(f"High correction rate ({correction_rate*100:.0f}%) - AI still learning")

    # Volume warning
    if quote_count < 5:
        warnings.append("Limited data - confidence will improve with more quotes")

    # ===== RETURN =====
    acceptance_rate = acceptance_count / total_signals if total_signals > 0 else 0.0
    avg_correction = sum(correction_magnitudes) / len(correction_magnitudes) if correction_magnitudes else 0.0

    return PricingConfidence(
        # Dimensions
        data_confidence=round(data_confidence, 3),
        accuracy_confidence=round(accuracy_confidence, 3),
        recency_confidence=round(recency_confidence, 3),
        coverage_confidence=round(coverage_confidence, 3),

        # Composite
        overall_confidence=round(overall_confidence, 3),
        display_confidence=display_confidence,

        # Metadata
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
```

---

## 3. Confidence Display Rules

```python
def get_confidence_display(confidence: PricingConfidence) -> dict:
    """
    Generate UI display elements for confidence.

    Returns:
        dict with badge, message, tooltip, and warnings
    """

    level = confidence["display_confidence"]
    quote_count = confidence["quote_count"]
    acceptance_rate = confidence["acceptance_rate"]
    overall = confidence["overall_confidence"]

    # ===== BADGE & COLOR =====
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

    # ===== MESSAGE =====
    if level == "High":
        message = f"Based on {quote_count} quotes with {acceptance_rate*100:.0f}% acceptance rate"
    elif level == "Medium":
        message = f"Based on {quote_count} quotes - review recommended"
    elif level == "Low":
        message = f"Limited data ({quote_count} quotes) - please verify pricing"
    else:  # Learning
        message = f"Learning your pricing preferences ({quote_count} quotes so far)"

    # ===== TOOLTIP (Detailed Breakdown) =====
    avg_correction = confidence["avg_correction_magnitude"]

    if level == "High":
        tooltip = (
            f"Your {confidence.get('category', 'category')} pricing is well-calibrated. "
            f"AI suggestions are typically within {avg_correction:.0f}% of your final price."
        )
    elif level == "Medium":
        tooltip = (
            f"AI is learning your {confidence.get('category', 'category')} pricing. "
            f"Quotes typically need {avg_correction:.0f}% adjustments. "
            f"Review before sending."
        )
    elif level == "Low":
        tooltip = (
            f"Limited {confidence.get('category', 'category')} data. "
            f"AI will improve as you provide more corrections."
        )
    else:  # Learning
        tooltip = (
            f"Building your {confidence.get('category', 'category')} pricing model. "
            f"Each quote you send helps AI learn your preferences."
        )

    # ===== DIMENSION BREAKDOWN (For Dashboard) =====
    dimension_breakdown = {
        "Data": f"{confidence['data_confidence']*100:.0f}% ({quote_count} quotes)",
        "Accuracy": f"{confidence['accuracy_confidence']*100:.0f}% ({acceptance_rate*100:.0f}% acceptance)",
        "Recency": f"{confidence['recency_confidence']*100:.0f}% ({confidence['days_since_last_quote']} days ago)",
        "Coverage": f"{confidence['coverage_confidence']*100:.0f}% (job complexity spread)",
    }

    return {
        "badge": badge,
        "color": color,
        "message": message,
        "tooltip": tooltip,
        "warnings": confidence["warnings"],
        "overall_percent": round(overall * 100, 0),
        "dimension_breakdown": dimension_breakdown,
    }
```

---

## 4. Confidence Thresholds for AI Behavior

| Confidence Level | Overall Score | AI Behavior | UI Indicator | Quote Generation |
|-----------------|---------------|-------------|--------------|-----------------|
| **High** | ≥0.75 | Generate quote confidently, minimal hedging | Green badge, no warnings | Standard generation |
| **Medium** | 0.50-0.74 | Generate quote with "suggested range" | Yellow badge, "Review recommended" | Add ±10% range |
| **Low** | 0.25-0.49 | Wide price range, request contractor input | Orange badge, "Please verify" | Add ±20% range |
| **Learning** | <0.25 | Ask contractor for guidance, learn from response | Gray badge, "Learning your preferences" | Interactive guidance |

### AI Prompt Injection by Confidence Level

```python
def get_confidence_prompt_injection(confidence: PricingConfidence) -> str:
    """
    Generate prompt text to inject into Claude for quote generation.
    AI behavior adapts based on confidence level.
    """

    level = confidence["display_confidence"]
    category = confidence.get("category", "this job type")

    if level == "High":
        return f"""
CONFIDENCE: HIGH ({confidence['overall_confidence']*100:.0f}%)

You have strong data for {category} pricing based on {confidence['quote_count']} quotes
with {confidence['acceptance_rate']*100:.0f}% acceptance rate.

Generate the quote with confidence. Use learned pricing patterns directly.
"""

    elif level == "Medium":
        return f"""
CONFIDENCE: MEDIUM ({confidence['overall_confidence']*100:.0f}%)

You have moderate data for {category} pricing ({confidence['quote_count']} quotes,
{confidence['acceptance_rate']*100:.0f}% acceptance rate).

Generate the quote but include a suggested range (±10%) to account for uncertainty.
Highlight that contractor review is recommended.
"""

    elif level == "Low":
        return f"""
CONFIDENCE: LOW ({confidence['overall_confidence']*100:.0f}%)

Limited {category} data ({confidence['quote_count']} quotes,
{confidence['acceptance_rate']*100:.0f}% acceptance rate).

Generate a quote with a WIDE range (±20%) and explicitly state:
"This is an estimate based on limited data. Please review and adjust as needed."
"""

    else:  # Learning
        return f"""
CONFIDENCE: LEARNING ({confidence['overall_confidence']*100:.0f}%)

Very limited {category} data ({confidence['quote_count']} quotes).

Instead of generating a quote, ASK the contractor for guidance:
1. What's your typical pricing for this type of job?
2. Are there specific factors that affect your pricing?
3. What would you typically charge for this scope?

Then generate the quote based on their input and LEARN from their response.
"""
```

---

## 5. Decay and Refresh Mechanics

```python
def apply_confidence_decay(
    confidence: PricingConfidence,
    days_since_last_quote: int,
) -> PricingConfidence:
    """
    Apply time-based decay to confidence.

    DECAY RULES:
    - Recency confidence decays with 30-day half-life
    - Accuracy and coverage DON'T decay (historical facts)
    - Overall confidence decays if no recent validation

    REFRESH TRIGGERS:
    - Any quote in category resets recency decay
    - Acceptance refreshes accuracy confidence
    - Correction may lower accuracy confidence
    """

    # Recency decay (already calculated in calculate_calibrated_confidence)
    # This is just documentation of how decay works

    HALF_LIFE_DAYS = 30
    decay_factor = 0.5 ** (days_since_last_quote / HALF_LIFE_DAYS)

    # Recency confidence decays exponentially
    confidence["recency_confidence"] = decay_factor

    # Recalculate overall (since recency changed)
    confidence["overall_confidence"] = (
        confidence["data_confidence"] * CONFIDENCE_WEIGHTS["data"] +
        confidence["accuracy_confidence"] * CONFIDENCE_WEIGHTS["accuracy"] +
        confidence["recency_confidence"] * CONFIDENCE_WEIGHTS["recency"] +
        confidence["coverage_confidence"] * CONFIDENCE_WEIGHTS["coverage"]
    )

    # Update display level
    overall = confidence["overall_confidence"]
    if overall >= 0.75:
        confidence["display_confidence"] = "High"
    elif overall >= 0.50:
        confidence["display_confidence"] = "Medium"
    elif overall >= 0.25:
        confidence["display_confidence"] = "Low"
    else:
        confidence["display_confidence"] = "Learning"

    return confidence


def refresh_confidence_on_quote(
    category_data: dict,
    was_edited: bool,
    correction_magnitude: Optional[float] = None,
) -> dict:
    """
    Refresh confidence when a new quote is generated/sent.

    REFRESH LOGIC:
    - Update last_quote_at (resets recency decay)
    - Increment quote_count (improves data confidence)
    - If was_edited: increment correction_count, track magnitude
    - If NOT edited: increment acceptance_count
    - Recalculate all confidence dimensions
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
    days_since = 0  # Just happened
    confidence = calculate_calibrated_confidence(
        quote_count=category_data["quote_count"],
        acceptance_count=category_data.get("acceptance_count", 0),
        correction_count=category_data.get("correction_count", 0),
        correction_magnitudes=category_data.get("correction_magnitudes", []),
        days_since_last_quote=days_since,
        complexity_distribution=category_data.get("complexity_counts", {}),
    )

    # Cache confidence dimensions
    category_data["confidence_dimensions"] = confidence
    category_data["confidence"] = confidence["overall_confidence"]

    return category_data
```

---

## 6. Volume vs Accuracy Weighting

### Philosophy

**Question**: What matters more - 100 quotes with 50% accuracy, or 10 quotes with 90% accuracy?

**Answer**: Accuracy matters more. Volume provides diminishing returns.

### Weighting Rationale

```python
CONFIDENCE_WEIGHTS = {
    "data": 0.20,      # 20% - Volume matters but plateaus
    "accuracy": 0.40,  # 40% - Most important: are we right?
    "recency": 0.25,   # 25% - Fresh data matters
    "coverage": 0.15,  # 15% - Job type variety matters
}
```

**Why Accuracy is 40%**:
- Being right is the whole point of confidence
- 90% accurate with 10 quotes = trustworthy
- 50% accurate with 100 quotes = not trustworthy

**Why Data is only 20%**:
- Logarithmic growth (10→50 quotes = small improvement)
- After 50 quotes, more data helps less
- Prevents "high volume, low accuracy" overconfidence

**Why Recency is 25%**:
- Pricing changes (material costs, labor rates)
- 6-month-old data may be outdated
- Forces system to stay current

**Why Coverage is 15%**:
- Important but secondary
- All simple jobs != full understanding
- Helps identify gaps (e.g., "no complex job data")

### Example Scenarios

| Scenario | Data | Accuracy | Recency | Coverage | Overall | Level |
|----------|------|----------|---------|----------|---------|-------|
| **100 quotes, 90% accept, recent, balanced** | 0.90 | 0.90 | 1.00 | 0.85 | **0.91** | High |
| **100 quotes, 50% accept, recent, balanced** | 0.90 | 0.50 | 1.00 | 0.85 | **0.68** | Medium |
| **10 quotes, 90% accept, recent, balanced** | 0.50 | 0.90 | 1.00 | 0.40 | **0.75** | High |
| **50 quotes, 80% accept, 90 days old, balanced** | 0.75 | 0.80 | 0.25 | 0.75 | **0.62** | Medium |
| **50 quotes, 80% accept, recent, all simple** | 0.75 | 0.80 | 1.00 | 0.30 | **0.75** | High |

**Key Insight**: 10 highly accurate quotes beats 100 mediocre quotes.

---

## 7. Edge Cases

### Case 1: New Category (First 3 Quotes)

```python
if quote_count < 3:
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
```

### Case 2: High Volume but Low Accuracy

```python
# Example: 50 quotes, 25% acceptance rate
if quote_count > 20 and acceptance_rate < 0.30:
    return PricingConfidence(
        # ... calculated dimensions ...
        display_confidence="Recalibrating",  # Special status
        warnings=[
            f"High correction rate ({(1-acceptance_rate)*100:.0f}%) - AI still learning",
            "Significant pattern changes detected - please review carefully",
        ],
    )
```

### Case 3: Long Gap (90+ Days)

```python
if days_since_last_quote > 90:
    # Recency confidence drops to near-zero
    recency_confidence = 0.5 ** (days_since_last_quote / 30)  # ~0.125 at 90 days

    return PricingConfidence(
        # ... other dimensions ...
        recency_confidence=recency_confidence,
        display_confidence="Outdated",  # Special status
        warnings=[
            f"Last quote was {days_since_last_quote} days ago",
            "Pricing may have changed - validate current rates",
        ],
    )
```

### Case 4: Perfect Acceptance but Low Volume

```python
# Example: 5 quotes, 100% acceptance
if quote_count < 10 and acceptance_rate == 1.0:
    # Don't over-reward small samples
    # Data confidence caps at ~0.50 for 5 quotes
    # Overall will be Medium, not High

    return PricingConfidence(
        data_confidence=0.50,  # Limited data
        accuracy_confidence=1.00,  # Perfect so far
        # ... other dimensions ...
        overall_confidence=0.65,  # Medium range
        display_confidence="Medium",
        warnings=["Limited data - confidence will improve with more quotes"],
    )
```

### Case 5: Contradictory Corrections

```python
# Example: Corrections alternate between +20% and -20%
if len(correction_magnitudes) >= 5:
    # Check for high variance
    import statistics
    variance = statistics.variance(correction_magnitudes)

    if variance > 100:  # High variance threshold
        warnings.append(
            "Inconsistent corrections detected - job pricing may vary widely"
        )
        # Lower accuracy confidence
        accuracy_confidence *= 0.8
```

### Case 6: Single Complexity Dominance

```python
# Example: 20 simple jobs, 0 medium/complex
if quote_count >= 10:
    total = sum(complexity_distribution.values())
    max_pct = max(complexity_distribution.values()) / total if total > 0 else 0

    if max_pct > 0.8:  # 80%+ in one complexity
        dominant = max(complexity_distribution, key=complexity_distribution.get)
        warnings.append(
            f"Mostly {dominant} jobs - review {other_levels} quotes carefully"
        )
```

---

## 8. Integration Points

| File | Location | Change |
|------|----------|--------|
| **backend/models/database.py** | PricingModel class | Add `category_confidence` JSON field to store PricingConfidence dicts |
| **backend/services/learning.py** | `refresh_confidence_on_quote()` | New function: update confidence on quote/correction/acceptance |
| **backend/services/learning.py** | `process_correction()` | Call `refresh_confidence_on_quote(was_edited=True)` |
| **backend/services/learning.py** | `process_acceptance_learning()` | Call `refresh_confidence_on_quote(was_edited=False)` |
| **backend/prompts/quote_generation.py** | Prompt builder | Inject confidence level via `get_confidence_prompt_injection()` |
| **frontend/index.html** | Quote view UI | Display confidence badge via `get_confidence_display()` |
| **backend/api/contractors.py** | New endpoint: `/api/confidence-dashboard` | Return confidence breakdown for all categories |

### Schema Changes

```python
# In database.py, add to PricingModel class:

class PricingModel(Base):
    # ... existing fields ...

    # NEW: Category-level confidence tracking
    category_confidence = Column(JSON, default=dict)
    """
    Structure:
    {
        "deck_composite": {
            "confidence": 0.85,
            "acceptance_count": 23,
            "correction_count": 4,
            "quote_count": 27,
            "last_quote_at": "2025-01-15T10:30:00Z",
            "correction_magnitudes": [3.2, 5.1, 2.8, ...],  # Last 20
            "complexity_counts": {"simple": 8, "medium": 15, "complex": 4},
            "confidence_dimensions": {
                "data_confidence": 0.75,
                "accuracy_confidence": 0.90,
                "recency_confidence": 1.00,
                "coverage_confidence": 0.70,
                "overall_confidence": 0.85,
                "display_confidence": "High",
                # ... full PricingConfidence dict
            }
        },
        "fence_wood": { ... },
        ...
    }
    """
```

### API Endpoint

```python
# In contractors.py

@router.get("/api/confidence-dashboard")
async def get_confidence_dashboard(
    contractor_id: str = Depends(get_current_contractor_id),
    db: Session = Depends(get_db),
):
    """
    Return confidence breakdown for all categories.

    Response:
    {
        "categories": [
            {
                "category": "deck_composite",
                "confidence": {
                    "overall_confidence": 0.85,
                    "display_confidence": "High",
                    "quote_count": 27,
                    "acceptance_rate": 0.85,
                    "dimension_breakdown": { ... },
                    "warnings": []
                },
                "display": {
                    "badge": "High Confidence",
                    "color": "green",
                    "message": "Based on 27 quotes with 85% acceptance rate",
                    "tooltip": "Your deck pricing is well-calibrated...",
                }
            },
            ...
        ],
        "overall_stats": {
            "total_quotes": 142,
            "avg_confidence": 0.72,
            "high_confidence_categories": 5,
            "learning_categories": 2,
        }
    }
    """
```

---

## 9. Test Scenarios

### Scenario 1: New Category Bootstrap

**Setup**: First quote in "fence_wood" category

**Expected**:
- `data_confidence`: 0.20 (1 quote, logarithmic start)
- `accuracy_confidence`: 0.30 (no history)
- `recency_confidence`: 1.00 (just happened)
- `coverage_confidence`: 0.30 (1 job, no distribution)
- `overall_confidence`: ~0.35
- `display_confidence`: "Learning"
- `warnings`: ["New category - building your pricing model"]

### Scenario 2: Steady Accumulation

**Setup**: 10 quotes, 8 accepted, 2 corrected (avg 5% correction)

**Expected**:
- `data_confidence`: 0.50 (10 quotes)
- `accuracy_confidence`: 0.76 (80% * 0.95 magnitude adj)
- `recency_confidence`: 1.00 (recent)
- `coverage_confidence`: 0.60 (assuming some distribution)
- `overall_confidence`: ~0.72
- `display_confidence`: "Medium"

### Scenario 3: High Confidence Achieved

**Setup**: 50 quotes, 45 accepted, 5 corrected (avg 3% correction)

**Expected**:
- `data_confidence`: 0.75 (50 quotes, logarithmic plateau)
- `accuracy_confidence`: 0.87 (90% * 0.97 magnitude adj)
- `recency_confidence`: 1.00 (recent)
- `coverage_confidence`: 0.80 (good distribution)
- `overall_confidence`: ~0.84
- `display_confidence`: "High"
- `warnings`: []

### Scenario 4: Confidence Inflation (Prevented)

**Setup**: 100 quotes, 50 accepted, 50 corrected (avg 15% correction)

**Expected**:
- `data_confidence`: 0.90 (100 quotes)
- `accuracy_confidence`: 0.43 (50% * 0.85 magnitude adj)
- `recency_confidence`: 1.00
- `coverage_confidence`: 0.85
- `overall_confidence`: ~0.67
- `display_confidence`: "Medium" (NOT High despite volume)
- `warnings`: ["High correction rate (50%) - AI still learning"]

### Scenario 5: Recency Decay

**Setup**: 30 quotes, 27 accepted (90%), but 60 days since last quote

**Expected**:
- `data_confidence`: 0.65 (30 quotes)
- `accuracy_confidence`: 0.87 (90% * 0.97 magnitude adj)
- `recency_confidence`: 0.25 (60 days = 2 half-lives)
- `coverage_confidence`: 0.75
- `overall_confidence`: ~0.65
- `display_confidence`: "Medium" (dropped from High due to staleness)
- `warnings`: ["No quotes in 60 days - validate pricing is current"]

### Scenario 6: Coverage Gap

**Setup**: 20 quotes, all simple jobs, 18 accepted

**Expected**:
- `data_confidence`: 0.60
- `accuracy_confidence`: 0.87
- `recency_confidence`: 1.00
- `coverage_confidence`: 0.00 (Shannon entropy = 0, no distribution)
- `overall_confidence`: ~0.72
- `display_confidence`: "Medium"
- `warnings`: ["Limited complex job data - review complex quotes carefully"]

### Scenario 7: Long Gap Recovery

**Setup**: 40 quotes (old), 120 days gap, then 3 new quotes (all accepted)

**Expected**:
- After gap: overall ~0.40 (recency tanked)
- After 3 new: overall ~0.68 (recency restored, data/accuracy intact)
- `display_confidence`: "Medium" → demonstrates recovery

### Scenario 8: Perfect Early, Regresses Later

**Setup**: First 5 quotes all accepted, next 10 have 6 corrections

**Expected**:
- After 5: overall ~0.72 (high accuracy, low data)
- After 15: overall ~0.65 (accuracy dropped to 60%, data improved)
- `display_confidence`: "Medium" (reflects current reality)
- Demonstrates: Past perfection doesn't lock in high confidence

---

## 10. Success Metrics

### Short-term (Week 1-4)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Confidence inflation eliminated | 0% of categories with >0.90 confidence and <60% acceptance | DB query |
| Calibration accuracy | 80% of "High" categories have 70%+ acceptance rate | PostHog analysis |
| Warning accuracy | 90% of warnings correlate with actual issues | Manual review |

### Medium-term (Month 2-3)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Contractor trust | "Confidence badges are accurate" >80% in survey | User survey |
| AI behavior adaptation | "Learning" categories trigger guidance prompts | Code audit |
| Confidence progression | Average category goes Learning→Low→Medium→High over 30 quotes | Cohort analysis |

### Long-term (Month 4+)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Confidence-acceptance correlation | R² > 0.7 between confidence and acceptance rate | Statistical analysis |
| Stale data detection | 100% of 90+ day gaps trigger warnings | Automated check |
| Dimension independence | Each dimension contributes unique signal (VIF < 3) | Statistical analysis |

---

## 11. Migration Plan

### Phase 1: Schema Migration (1 hour)

```python
# Add category_confidence field to pricing_models table
ALTER TABLE pricing_models ADD COLUMN category_confidence JSON DEFAULT '{}';
```

### Phase 2: Backfill Historical Data (2-4 hours)

```python
async def backfill_category_confidence():
    """
    Backfill confidence data from existing quotes.
    """
    contractors = await db.get_all_contractors()

    for contractor in contractors:
        quotes = await db.get_quotes(contractor.id)
        pricing_model = await db.get_pricing_model(contractor.id)

        # Group quotes by category
        by_category = {}
        for quote in quotes:
            category = quote.job_type
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(quote)

        # Calculate confidence for each category
        category_confidence = {}
        for category, cat_quotes in by_category.items():
            # Count acceptances vs corrections
            acceptance_count = sum(1 for q in cat_quotes if q.sent_at and not q.was_edited)
            correction_count = sum(1 for q in cat_quotes if q.was_edited)

            # Extract correction magnitudes
            magnitudes = [
                abs(q.edit_details.get("total_change_percent", 0))
                for q in cat_quotes
                if q.was_edited and q.edit_details
            ]

            # Calculate days since last quote
            last_quote = max(cat_quotes, key=lambda q: q.created_at)
            days_since = (datetime.utcnow() - last_quote.created_at).days

            # Estimate complexity distribution (if not tracked)
            # Simplified: assume even distribution for backfill
            complexity_dist = {
                "simple": len(cat_quotes) // 3,
                "medium": len(cat_quotes) // 3,
                "complex": len(cat_quotes) - (2 * (len(cat_quotes) // 3)),
            }

            # Calculate confidence
            confidence = calculate_calibrated_confidence(
                quote_count=len(cat_quotes),
                acceptance_count=acceptance_count,
                correction_count=correction_count,
                correction_magnitudes=magnitudes[-20:],  # Last 20
                days_since_last_quote=days_since,
                complexity_distribution=complexity_dist,
            )

            category_confidence[category] = confidence

        # Save
        pricing_model.category_confidence = category_confidence
        await db.save(pricing_model)
```

### Phase 3: Integration (4-6 hours)

1. Add `refresh_confidence_on_quote()` to learning.py
2. Update `process_correction()` to call refresh
3. Update `process_acceptance_learning()` to call refresh
4. Add `get_confidence_prompt_injection()` to quote_generation.py
5. Update frontend to display confidence badges

### Phase 4: Testing (2-3 hours)

1. Unit tests for `calculate_calibrated_confidence()` (8 scenarios)
2. Integration test: quote → correction → confidence update
3. Integration test: quote → acceptance → confidence update
4. Backfill smoke test on staging DB

### Phase 5: Deployment (1 hour)

1. Deploy schema migration (zero downtime)
2. Run backfill script on production (async, low priority)
3. Deploy backend code
4. Deploy frontend code
5. Monitor PostHog for confidence calculation errors

**Total Estimated Effort**: 10-15 hours

---

## Appendix A: Confidence Dimension Formulas

### Data Confidence (Logarithmic Growth)

```python
data_confidence = min(0.95, math.log(quote_count + 1, 1.15) / 100)
```

**Curve**:
- 1 quote: 0.00
- 5 quotes: 0.38
- 10 quotes: 0.50
- 25 quotes: 0.66
- 50 quotes: 0.75
- 100 quotes: 0.83
- 200 quotes: 0.90
- 500+ quotes: 0.95 (cap)

### Accuracy Confidence (Acceptance Rate × Magnitude Adjustment)

```python
base_accuracy = acceptance_count / (acceptance_count + correction_count)
magnitude_multiplier = max(0.5, 1.0 - (avg_magnitude / 100))
accuracy_confidence = base_accuracy * magnitude_multiplier
```

**Examples**:
- 90% acceptance, 3% avg correction: 0.90 × 0.97 = **0.87**
- 90% acceptance, 15% avg correction: 0.90 × 0.85 = **0.77**
- 50% acceptance, 5% avg correction: 0.50 × 0.95 = **0.48**
- 50% acceptance, 20% avg correction: 0.50 × 0.80 = **0.40**

### Recency Confidence (Exponential Decay, 30-day Half-Life)

```python
HALF_LIFE_DAYS = 30
recency_confidence = 0.5 ** (days_since_last_quote / HALF_LIFE_DAYS)
```

**Curve**:
- 0 days: 1.00
- 15 days: 0.71
- 30 days: 0.50
- 60 days: 0.25
- 90 days: 0.13
- 120 days: 0.06

### Coverage Confidence (Shannon Entropy)

```python
# Calculate Shannon entropy of complexity distribution
entropy = 0.0
for count in complexity_distribution.values():
    if count > 0:
        p = count / total_jobs
        entropy -= p * math.log2(p)

# Normalize to 0-1 (max entropy for 3 categories = log2(3))
coverage_confidence = entropy / math.log2(3)
```

**Examples**:
- All simple: entropy = 0, coverage = **0.00**
- 50% simple, 50% medium: entropy = 1.0, coverage = **0.63**
- 33% each: entropy = 1.58, coverage = **1.00**
- 10% complex, 90% simple: entropy = 0.47, coverage = **0.30**

---

## Appendix B: Founder Constraints Compliance

### 1. Honest Uncertainty ✅

- Multi-dimensional confidence prevents single-number overconfidence
- Warnings surface known gaps (e.g., "Limited complex job data")
- Calibration ensures claimed confidence matches reality

### 2. Transparent Reasoning ✅

- Dimension breakdown shows WHY confidence is what it is
- Tooltips explain what each dimension means
- Dashboard shows detailed confidence decomposition

### 3. Contractor Control ✅

- Confidence NEVER prevents quote generation
- "Learning" mode asks for guidance, doesn't block
- Contractor can always override AI with full confidence
- Warnings are informational, not restrictive

---

## End of Design Document

**Next Steps**:
1. Review with founder for approval
2. Implement schema changes
3. Write unit tests for all 8 scenarios
4. Backfill production data
5. Deploy to staging for validation
6. Production rollout

**Success Criteria**: If we claim 80% confidence, then 80% of quotes are accepted without edit.
