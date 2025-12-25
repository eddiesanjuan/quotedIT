# Phase 2: Enhanced Refinement Prompt

*Agent: prompt-engineer | Completed: 2025-12-24*

## Changes from Current

| Aspect | Current | Proposed | Impact |
|--------|---------|----------|--------|
| Quality criteria | Implicit | Explicit checklist | Prevents generic statements |
| Examples | None | 6 per layer (3 good, 3 bad) | Shows exactly what to generate |
| Self-critique | None | Required validation | Catches low-quality before return |
| Dollar requirement | Implied | Explicit + alternatives | Ensures actionability |

## Expected Improvements

| Metric | Current | After Enhancement |
|--------|---------|-------------------|
| Generic statement rate | ~30% | <10% |
| Statements with $ amounts | ~40% | >70% |
| Statements with action verbs | ~50% | >85% |
| Average quality score | ~50/100 | ~75/100 |

## Key Prompt Sections

### Good/Bad Examples

**GOOD Examples (generate these):**
- "Demo minimum is $1,500 for deck projects regardless of size"
- "Add 15% to labor for second-story access"
- "Composite decking materials are $85/sqft installed"

**BAD Examples (DO NOT generate):**
- "Review pricing carefully" (no number, no action)
- "Be aware of material costs" (too vague)
- "Adjust for difficulty" (what adjustment?)

### Self-Critique Protocol

Before finalizing, validate EACH statement:
1. Has specific number ($ or %)?
2. Has clear action verb?
3. Can be copy-pasted into future quotes?
4. Is about specific trigger/condition?

**If NO to any → Rewrite or EXCLUDE**

### Three-Layer Thresholds

| Layer | Update Frequency | Trigger |
|-------|------------------|---------|
| Injection Learnings | 100% of corrections | Always generate |
| Tailored Prompt | ~10% | Fundamental approach change |
| Philosophy | ~2% | Business model change |

## Integration

**File**: `backend/prompts/quote_generation.py`
**Replace**: Lines 231-388 (`get_quote_refinement_prompt` function)

## Full Prompt

[Complete prompt text available in agent output]

Key additions:
- Explicit quality checklist with checkboxes
- 6 example statements per quality tier
- Self-critique validation step
- "Quality over quantity" principle
- JSON output with required fields
