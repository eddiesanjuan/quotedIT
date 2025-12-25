# Phase 4: Acceptance Learning - Complete Implementation

*Agent: acceptance-impl | Completed: 2025-12-24*

## Executive Summary

**What**: Learning from SENT quotes (without edits) to reinforce correct AI pricing.
**Why**: Current system only learns from WRONG prices (corrections). Need to learn from RIGHT prices too.
**How**: Confidence boost + reference storage + category performance tracking.

**Key Principle**: Acceptance learning is the OPPOSITE of correction learning:
- Corrections = AI was WRONG -> Create new statements
- Acceptance = AI was RIGHT -> Boost confidence, NO new statements

## Architecture

```
TRIGGER POINT 1: Quote Sent Without Edit
backend/api/share.py:share_quote_via_email() Line 213
Conditions: sent_at just set, was_edited == False

TRIGGER POINT 2: Quote Accepted by Customer
backend/api/share.py:accept_quote() Line 511
Conditions: accepted_at just set, was_edited == False
```

## Core Implementation

```python
async def process_acceptance_learning(
    self,
    contractor_id: str,
    quote: Quote,
    signal_type: str = "sent",  # "sent" or "accepted"
) -> dict:
    """
    Process acceptance signal - when quote sent/accepted WITHOUT edit.
    """
    # Validation
    if quote.was_edited:
        return {"processed": False, "reason": "Quote was edited"}

    category = quote.job_type
    if not category:
        return {"processed": False, "reason": "No job_type"}

    # Get pricing model
    pricing_model = await db.get_pricing_model(contractor_id)
    cat_data = pricing_model.pricing_knowledge["categories"][category]

    # CONFIDENCE BOOST: +0.05 (vs +0.02 for corrections)
    old_confidence = cat_data.get("confidence", 0.5)
    cat_data["confidence"] = min(0.95, old_confidence + 0.05)

    # Apply calibration
    cat_data["confidence"] = calculate_calibrated_confidence(
        acceptance_count=cat_data["acceptance_count"],
        correction_count=cat_data.get("correction_count", 0),
        current_confidence=cat_data["confidence"],
    )

    # Track acceptance
    cat_data["acceptance_count"] += 1
    cat_data["accepted_totals"].append({
        "total": quote.total,
        "signal_type": signal_type,
        "timestamp": datetime.utcnow().isoformat(),
    })

    # NO NEW LEARNED_ADJUSTMENTS (key difference from corrections)

    # Save
    await db.update_pricing_model(contractor_id, pricing_knowledge)

    return {"processed": True, "new_confidence": cat_data["confidence"]}
```

## Confidence Calibration

```python
def calculate_calibrated_confidence(
    acceptance_count: int,
    correction_count: int,
    current_confidence: float,
) -> float:
    """
    Confidence ceiling = actual_accuracy + 0.15
    Prevents "overconfident but inaccurate" scenarios.
    """
    total_signals = acceptance_count + correction_count

    if total_signals < 5:
        return current_confidence  # Not enough data

    actual_accuracy = acceptance_count / total_signals
    confidence_ceiling = min(0.95, actual_accuracy + 0.15)

    return min(current_confidence, confidence_ceiling)
```

## Integration Points

| Location | Trigger |
|----------|---------|
| share.py:213 | After quote sent (was_just_sent and not was_edited) |
| share.py:511 | After customer accepts (not was_edited) |

## Key Differences from Correction Learning

| Aspect | Correction | Acceptance |
|--------|------------|------------|
| Signal | AI was WRONG | AI was RIGHT |
| Statements | Create new rules | NO new rules |
| Confidence | +0.02 | +0.05 |
| AI Call | Required (Claude) | Not needed |

## Test Scenarios

1. **Basic Acceptance**: Quote sent without edit -> confidence +0.05
2. **Accumulation**: Multiple acceptances -> confidence accumulates
3. **Mixed Signals**: Acceptance + correction -> accuracy ratio tracked
4. **Calibration**: High confidence + low accuracy -> capped
5. **Customer Accept**: Signal type = "accepted" stored
6. **Edited Quote**: was_edited=True -> NO acceptance learning
7. **High Volume**: accepted_totals capped at 10 entries

## Success Metrics

- Week 1: 100+ signals processed without errors
- Week 4: 30%+ of quotes sent without edit
- Week 12: High-confidence categories correlate with high acceptance

## Deployment Checklist

- [ ] Add process_acceptance_learning() to learning.py
- [ ] Integrate into share.py (2 locations)
- [ ] Unit tests (7 scenarios)
- [ ] Deploy to staging
- [ ] Smoke test: send quote without edit
- [ ] Check PostHog: acceptance_signal_processed events
- [ ] Deploy to production
