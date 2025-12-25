# Acceptance Learning - Quick Reference Card

## One-Sentence Summary

Learn from quotes sent/accepted WITHOUT edit by boosting confidence (no new rules).

---

## Key Principle

| Correction Learning | Acceptance Learning |
|---------------------|---------------------|
| AI was WRONG | AI was RIGHT |
| Create new statements | NO new statements |
| Confidence +0.02 | Confidence +0.05 |
| Requires Claude analysis | No AI call needed |

---

## Trigger Conditions

### Trigger 1: Quote Sent Without Edit
```
sent_at: None → datetime
was_edited: False
status: "draft" → "sent"
→ FIRE acceptance learning
```

### Trigger 2: Quote Accepted by Customer
```
accepted_at: None → datetime
was_edited: False
status: "sent" → "won"
→ FIRE acceptance learning
```

---

## What Gets Updated

```python
category_data = {
    # INCREMENTS
    "confidence": 0.50 → 0.55 (+0.05),
    "samples": 5 → 6 (+1),
    "acceptance_count": 2 → 3 (+1),

    # NEW DATA
    "accepted_totals": [
        {"total": 8500, "signal_type": "sent", ...},
        {"total": 9200, "signal_type": "accepted", ...}
    ],
    "last_accepted_at": "2025-12-24T10:30:00Z",

    # UNCHANGED (KEY!)
    "learned_adjustments": [],  # NO NEW RULES
    "tailored_prompt": None,    # NO CHANGES
}
```

---

## Code Integration Points

### File: `backend/api/share.py`

**Location 1**: After line 213 (email sent)
```python
# After: await db.update_quote(quote_id, **share_updates)

if was_just_sent and not quote.was_edited:
    await learning_service.process_acceptance_learning(
        contractor_id=contractor.id,
        quote=quote,
        signal_type="sent",
    )
```

**Location 2**: After line 511 (quote accepted)
```python
# After: quote = await db.update_quote(str(quote.id), **update_fields)

if not quote.was_edited:
    await learning_service.process_acceptance_learning(
        contractor_id=quote.contractor_id,
        quote=quote,
        signal_type="accepted",
    )
```

---

## Confidence Calibration

**Formula**: `confidence_ceiling = min(0.95, actual_accuracy + 0.15)`

**Example**:
- 3 acceptances, 7 corrections → 30% accuracy
- Confidence ceiling: 0.30 + 0.15 = 0.45
- If confidence = 0.75 → cap to 0.45

**Why**: Prevents "overconfident but inaccurate" models

---

## Testing Quick Check

```python
# Generate quote
quote = await generate_quote(...)

# Send without edit
await share_quote_via_email(quote_id, ...)

# Verify learning
cat_data = pricing_model.pricing_knowledge["categories"][quote.job_type]
assert cat_data["acceptance_count"] == 1  # ✅ Incremented
assert cat_data["confidence"] > old_confidence  # ✅ Boosted
assert len(cat_data["learned_adjustments"]) == old_count  # ✅ Unchanged
```

---

## Analytics Event

**Event**: `acceptance_signal_processed`

**Key Properties**:
- `signal_type`: "sent" or "accepted"
- `accuracy_ratio`: acceptance_count / (acceptance + correction)
- `confidence_boost`: 0.05
- `old_confidence` vs `new_confidence`

---

## Success Metrics

**Week 1**: 100+ signals processed without errors
**Week 4**: 30%+ of quotes sent without edit
**Week 12**: High-confidence categories (0.80+) correlate with high acceptance

---

## Deployment Checklist

- [ ] Add `process_acceptance_learning()` to `learning.py`
- [ ] Integrate into `share.py` (2 locations)
- [ ] Unit tests (7 scenarios)
- [ ] Deploy to staging
- [ ] Smoke test: send quote without edit
- [ ] Check PostHog: event `acceptance_signal_processed`
- [ ] Deploy to production
- [ ] Monitor logs (Week 1)

---

## Common Issues

**Issue**: "Confidence not increasing"
**Fix**: Check `was_edited` flag (must be False)

**Issue**: "New learned_adjustments appearing"
**Fix**: Acceptance learning should NOT create rules (bug)

**Issue**: "Confidence > 0.95"
**Fix**: Check calibration logic (should cap at 0.95)

**Issue**: "accuracy_ratio < 0 or > 1"
**Fix**: Bug in calculation (check division by zero)
