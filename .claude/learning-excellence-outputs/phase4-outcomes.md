# Phase 4: Outcome Tracking & Feedback Loop

*Agent: outcome-designer | Completed: 2025-12-24*

## Executive Summary

Creates a **frictionless, high-signal outcome tracking system** that:
- Collects win/loss data through natural workflow integration
- Correlates outcomes with learning effectiveness
- Auto-calibrates confidence based on actual win rates
- Feeds outcomes back into learning (amplify winners, decay losers)
- Shows contractors transparent "AI pricing scorecards"

## Outcome Collection Flow

### Core Principle: Zero Extra Work

Contractors won't manually log outcomes. Capture through **existing workflow signals**.

### Collection Mechanisms (Priority Order)

1. **PRIMARY**: Customer clicks "Accept Quote" link -> outcome = WON
2. **SECONDARY**: Follow-up prompts 7 days after sent
3. **TERTIARY**: CRM integration (future)

### Database Schema

```sql
ALTER TABLE quotes ADD COLUMN outcome_source VARCHAR(50);
-- Values: 'customer_acceptance', 'contractor_manual', 'auto_timeout'

ALTER TABLE quotes ADD COLUMN outcome_date TIMESTAMP;
ALTER TABLE quotes ADD COLUMN accept_quote_token VARCHAR(255) UNIQUE;
```

## Key Correlation Queries

### Query 1: Win Rate by Edit Status

```sql
SELECT
    CASE WHEN pricing_modified THEN 'edited' ELSE 'unedited' END AS quote_type,
    COUNT(*) AS total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE outcome = 'won') / COUNT(*), 1) AS win_rate
FROM quotes
WHERE status = 'sent' AND outcome IN ('won', 'lost')
GROUP BY quote_type;
```

**Insights**:
- unedited_win_rate > edited_win_rate -> AI pricing is effective
- edited_win_rate > unedited_win_rate -> Contractor corrections valuable

### Query 2: Win Rate by Category

```sql
SELECT
    category,
    COUNT(*) FILTER (WHERE outcome = 'won') AS won,
    ROUND(100.0 * COUNT(*) FILTER (WHERE outcome = 'won') / COUNT(*), 1) AS win_rate
FROM quotes
WHERE outcome IN ('won', 'lost')
GROUP BY category
HAVING COUNT(*) >= 3;
```

## Confidence Calibration Algorithm

```python
async def calculate_category_confidence(contractor_id: str, category: str) -> dict:
    """
    Confidence based on:
    1. Quote volume (40 pts max)
    2. Win rate (40 pts max)
    3. AI effectiveness (20 pts max)
    4. Recency bonus (10 pts)
    """
    stats = await get_category_stats(contractor_id, category)

    volume_score = min(40, stats.total_quotes * 4)
    win_rate_score = stats.win_rate * 40 if stats.decided >= 3 else 0
    ai_score = (1 - stats.edit_rate) * 20
    recency_bonus = min(10, stats.recent_decided * 2)

    total_score = volume_score + win_rate_score + ai_score + recency_bonus

    if total_score >= 70: level = "high"
    elif total_score >= 40: level = "medium"
    else: level = "low"

    return {"confidence_level": level, "confidence_score": total_score}
```

## Learning Feedback Integration

### Outcome-Weighted Learning Injection

```python
async def get_relevant_learnings_outcome_aware(contractor_id, category, limit=7):
    """
    Select learnings weighted by outcomes:
    - Won quotes: 2x weight
    - Lost unedited: -1x weight (AI was wrong)
    - Lost edited: 0x weight (contractor was wrong)
    - Recency decay: Exponential
    """
```

## Decay of Bad Learnings

```python
async def deprecate_losing_learnings(contractor_id: str):
    """
    Nightly job: Flag learnings that consistently appear in lost quotes.

    Criteria:
    - Appears in 3+ quotes
    - >70% of those were LOST
    - Active in last 30 days
    """
```

## Dashboard: AI Pricing Scorecard

```
Overall Win Rate: 68% (25 won / 37 decided)

AI Pricing: 72% win rate (18 won / 25 unedited)
Edited Quotes: 58% win rate (7 won / 12 edited)

Insight: Your unedited quotes win MORE often.
Consider trusting AI pricing more frequently.

Top Categories:
- Deck Composite: 85% win rate (High Trust)
- Painting Interior: 70% win rate (Medium)
- Roofing Repair: 40% win rate (Learning)
```

## API Endpoints

```python
# Customer accepts quote
POST /api/quotes/accept/{accept_token}

# Contractor manual update
PATCH /api/quotes/{quote_id}/outcome

# Batch update
POST /api/quotes/outcomes/batch

# Dashboard metrics
GET /api/contractors/pricing-performance
```

## Migration Plan

| Week | Focus |
|------|-------|
| 1 | Schema + customer acceptance + manual UI |
| 2 | Analysis queries + dashboard scorecard |
| 3 | Auto-deprecation + follow-up prompts |
| 4 | A/B testing + optimization |

## Success Metrics

- **Target**: 60%+ of quotes have outcome data within 30 days
- **Target**: High-confidence categories have >70% win rate
- **Target**: Deprecated learnings have <40% win rate

## Founder Decisions Needed

1. **Collection priority**: Customer acceptance vs manual input?
2. **Follow-up timing**: 7 days or longer?
3. **Deprecation threshold**: 70% loss rate too strict?
4. **Dashboard placement**: Main dashboard or analytics page?
