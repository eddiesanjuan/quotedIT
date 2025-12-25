# Phase 1: Database Audit

*Agent: db-auditor | Completed: 2025-12-24*

## Access Status

| Method | Result | Notes |
|--------|--------|-------|
| Railway CLI `railway run python` | FAILED | Container-based, no local execution |
| Railway shell | FAILED | Would need psycopg2 installed locally |
| Direct DATABASE_URL | BLOCKED | Internal hostname (postgres.railway.internal) |

**Blocker**: BLOCK-001 remains active - cannot directly query production database from local environment.

## Resolution: Admin Endpoint Approach

**Recommended**: Add temporary `/api/learning/audit` endpoint

### Audit Script Created

Created `scripts/audit_learning_data.py` with quality scoring heuristic:

```python
def score_statement(statement: str, category: str) -> dict:
    score = 0
    # +30 pts: Has dollar amounts ($X)
    # +25 pts: Has percentages (X%)
    # +30 pts: Has specific items (deck, tile, etc.)
    # +20 pts: Has action words (increase, add, charge)
    # +10 pts: Reasonable length (30-200 chars)
    # -15 pts: Vague phrases (sometimes, maybe)
    # -10 pts: Generic phrases (review, careful)

    # Quality tiers:
    # High: 70+
    # Medium: 40-69
    # Low: 20-39
    # Useless: <20
```

### Admin Endpoint Specification

```python
# Add to backend/api/learning.py

@router.get("/audit", response_model=LearningAuditResponse)
async def audit_learning_data(
    current_user: dict = Depends(get_admin_user)  # Admin only
):
    """
    Returns anonymized learning quality statistics for audit.
    """
    # Query all PricingModels
    # Score each learning statement
    # Return quality distribution + samples
```

**Response shape**:
```json
{
  "total_statements": 245,
  "categories_count": 18,
  "contractors_count": 5,
  "quality_distribution": {
    "high": 65,
    "medium": 98,
    "low": 52,
    "useless": 30
  },
  "samples": {
    "high": ["Add $85/sqft for composite decking", "..."],
    "medium": ["Consider adding markup for access", "..."],
    "low": ["Be careful with pricing", "..."],
    "useless": ["Review this", "..."]
  }
}
```

## Next Steps

1. Add `/api/learning/audit` endpoint (5 min)
2. Deploy to production
3. Call endpoint to get actual quality metrics
4. Remove endpoint after audit

## Estimated Quality Distribution (Based on Code Analysis)

Without production data, estimated based on prompt structure:

| Quality | Estimated % | Why |
|---------|-------------|-----|
| High (70+) | ~30% | Strong prompts ask for specifics |
| Medium (40-69) | ~40% | Some learnings naturally generic |
| Low (20-39) | ~20% | Edge cases and early learning |
| Useless (<20) | ~10% | System sometimes fails to extract |

**These are estimates. Actual data needed via admin endpoint.**
