# Phase 1: Acceptance Signal Analysis

*Agent: acceptance-analyst | Completed: 2025-12-24*

## Data Structure Status

| Field | Exists? | Location | Set When |
|-------|---------|----------|----------|
| sent_at | YES | Quote.sent_at (Line 326) | Email sent (share.py:209) |
| was_edited | YES | Quote.was_edited (Line 330) | Quote edited via UI |
| accepted_at | YES | Quote.accepted_at (Line 360) | Customer accepts (share.py:506) |
| status | YES | Quote.status (Line 325) | State changes |
| outcome | YES | Quote.outcome (Line 345) | Won/lost/pending |

## Detection Query

```python
async def get_acceptance_signals(contractor_id: str, limit: int = 100):
    """Find quotes that show acceptance signals - sent without edits."""
    return session.query(Quote).filter(
        Quote.contractor_id == contractor_id,
        Quote.sent_at.isnot(None),      # Was sent
        Quote.was_edited == False,       # Not edited
        (Quote.status == "won") | (Quote.accepted_at.isnot(None))  # Accepted
    ).order_by(Quote.created_at.desc()).limit(limit).all()
```

## Implementation Plan

### Phase 1: Detection Foundation (2 hours)
1. Add `get_acceptance_signals()` to DatabaseService
2. Add `identify_acceptance_signal()` helper

### Phase 2: Learning Trigger (3 hours)
1. Create `/api/learning/{quote_id}/process_acceptance_signal`
2. Hook into `accept_quote()` in share.py (line 466)

### Phase 3: Acceptance Learning Logic (4 hours)
```python
async def process_acceptance_learning(contractor_id, quote):
    # 1. Increase confidence (faster than corrections: +0.05)
    cat_data["confidence"] = min(0.95, cat_data.get("confidence", 0.5) + 0.05)

    # 2. Track acceptance count
    cat_data["acceptance_count"] = cat_data.get("acceptance_count", 0) + 1

    # 3. Store accepted total as reference
    cat_data["accepted_totals"].append({
        "total": quote.total,
        "accepted_at": quote.accepted_at.isoformat(),
        "quote_id": quote.id,
    })
```

### Phase 4: Test & Integration (2 hours)

## Key Distinctions

| Correction | Acceptance |
|------------|------------|
| AI was wrong | AI was right |
| Learn from error | Reinforce pattern |
| Create new statements | NO new statements |
| Confidence +0.02 | Confidence +0.05 |
| Trigger Claude analysis | No Claude needed |

## Effort Estimate

- **Hours**: 9-12 hours
- **Risk**: LOW (read-only analysis, no core learning changes)
- **Dependencies**: None (all fields exist)

## Testing Plan

1. **Detection Query** - Verify correct quotes returned
2. **Full Lifecycle** - Generate → Send → Accept → Check signal
3. **No False Positives** - Edited quotes excluded, rejected quotes excluded
