# Phase 2: Quality Scoring Framework

*Agent: quality-designer | Completed: 2025-12-24*

## Scoring Dimensions

| Dimension | Max Points | Criteria |
|-----------|------------|----------|
| **Specificity** | 35 | Dollar amounts (+15), Percentages (+10), Specific items (+10) |
| **Actionability** | 25 | Action verb (+15), Quantity/unit (+10) |
| **Clarity** | 20 | Single rule (+10), Length 30-200 chars (+10) |
| **Anti-patterns** | -25 max | Vague language (-15), Generic advice (-10) |

## Thresholds

| Score | Tier | Recommendation |
|-------|------|----------------|
| 70-100 | High | Accept immediately |
| 60-69 | High | Accept (borderline) |
| 40-59 | Medium | Accept with logging |
| 20-39 | Low | Reject → retry |
| 0-19 | Reject | Reject → retry |

**Retry limit**: 2 attempts, then accept best available

## Core Algorithm

```python
def score_learning_statement(statement: str, category: str) -> dict:
    score = 0
    issues = []

    # Specificity (0-35)
    if re.search(r'\$\d+', statement): score += 15
    else: issues.append("no_dollar_amounts")
    if re.search(r'\d+%', statement): score += 10
    if any(term in statement.lower() for term in SPECIFIC_TERMS): score += 10

    # Actionability (0-25)
    if any(verb in statement.lower() for verb in ACTION_VERBS): score += 15
    if any(unit in statement.lower() for unit in UNITS): score += 10

    # Clarity (0-20)
    if 30 <= len(statement) <= 200: score += 10
    if single_sentence(statement): score += 10

    # Anti-patterns (negative)
    if any(word in statement.lower() for word in VAGUE_WORDS): score -= 15
    if any(phrase in statement.lower() for phrase in GENERIC_PHRASES): score -= 10

    return {"score": max(0, min(100, score)), "issues": issues, ...}
```

## Rejection Feedback Templates

| Issue | Feedback to Claude |
|-------|-------------------|
| no_dollar_amounts | "Include specific dollar amounts (e.g., '$85/sqft')" |
| vague_language | "Remove vague words like 'sometimes', 'maybe'" |
| generic_advice | "Be specific about what to add/change" |
| too_generic | "Mention specific items/materials" |
| too_short | "Provide more context (30-200 chars)" |
| too_long | "Simplify to one clear rule" |

## Integration

**File**: `backend/services/learning.py`
**Location**: After `_parse_learning_response()` returns

```python
# Score and filter statements before storage
scored = filter_learning_statements(
    statements=result["learning_statements"],
    category=category
)
result["learning_statements"] = [s["statement"] for s in scored["accepted"]]

if scored["needs_retry"] and retry_count < 2:
    # Re-extract with feedback
    return await process_correction(..., retry_count=retry_count+1)
```

## Test Cases

| Statement | Expected Score | Tier |
|-----------|---------------|------|
| "Add $85/sqft for composite decking" | 85+ | High |
| "Increase demo by 20% for elevated decks" | 80+ | High |
| "Be careful with pricing" | <25 | Reject |
| "Maybe increase sometimes" | <15 | Reject |
