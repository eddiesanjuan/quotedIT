# Phase 0: Architecture Analysis

*Agent: arch-analyst | Completed: 2025-12-24*

## Data Flow

```
VOICE INPUT
    ↓
QUOTE GENERATION (claude_service.py)
    ├─ Input: transcription
    ├─ Input: pricing_model (contractor's learned brain)
    └─ Output: Quote with line_items + subtotal
    ↓
CONTRACTOR VIEWS QUOTE
    ├─ Status: "draft"
    └─ Displays ai_generated_total
    ↓
CONTRACTOR CORRECTS (PUT /quotes/{quote_id})
    ├─ Updates: line_items, subtotal, job_description
    ├─ Sets: was_edited = TRUE
    ├─ Stores: original_quote state
    └─ Generates: corrections dict (line item changes)
    ↓
LEARNING TRIGGER (quotes.py:1407-1426)
    ├─ Step 1: Fetch existing_learnings from pricing_model.categories[job_type]
    ├─ Step 2: Fetch existing_tailored_prompt (category-level)
    ├─ Step 3: Fetch existing_philosophy (global)
    ├─ Step 4: Call Claude with THREE-LAYER context
    └─ Step 5: Apply learnings to pricing_model
    ↓
LEARNING INJECTION (quote_generation.py:82)
    └─ BUG LOCATION: Takes learned_adjustments[-7:]
       (MOST RECENT, not MOST RELEVANT)
    ↓
NEXT QUOTE GENERATION
    └─ Uses injected learnings in prompt
       (but 7 most recent might not be best)
```

## Learning Layers

| Layer | File Location | Update Frequency | Purpose | Storage |
|-------|---------------|------------------|---------|---------|
| **Layer 1: Injection Learnings** | pricing_model.pricing_knowledge["categories"][job_type]["learned_adjustments"] | EVERY correction | Specific rules like "Demo minimum $1,500" | JSON array (max 20) |
| **Layer 2: Tailored Prompt** | pricing_model.pricing_knowledge["categories"][job_type]["tailored_prompt"] | ~10% of corrections | Category-level understanding | Text field |
| **Layer 3: Pricing Philosophy** | pricing_model.pricing_philosophy | ~2% of corrections | Global pricing DNA | Text field |

## Critical Decision Points

| Decision | What Happens | Risk | Severity | File:Line |
|----------|--------------|------|----------|-----------|
| **Learning Statement Selection** | Takes `learned_adjustments[-7:]` (most recent 7) | Injects irrelevant old learnings; ignores important ones | CRITICAL | quote_generation.py:82 |
| **Max Learnings Limit** | Keeps only last 20 per category via `[-20:]` | Oldest important rules get purged | CRITICAL | database.py:381-383 |
| **Correction Detection** | Checks `was_edited = TRUE` | Could miss subtle changes | MEDIUM | quotes.py:1363 |
| **Confidence Increment** | Dynamic rate: +0.04/+0.02/+0.01 → cap at 0.95 | Low confidence in early learning | LOW | database.py:352-359 |

## THE BUG - Line 82

**Location**: `backend/prompts/quote_generation.py:82`

```python
if learned_adjustments:
    # Priority selection - inject only top 7 most recent learnings
    top_learnings = learned_adjustments[-7:]  # <-- TAKES LAST 7 (most RECENT)
```

**Problem**: Recent ≠ Relevant. A seasonal rule ("storm surcharge") could be injected while foundational rules ("minimum $2,500") are ignored.

**Example Failure**:
```
Contractor's learning_adjustments for "deck_building" = [
  "Composite deck baseline $58/sqft",      ← CRITICAL - not injected!
  "Add 15% for difficult access",
  ...
  "Never quote below $2,500 minimum",      ← 7 most recent starts here
  "Trex boards $8/sq ft",
  "Add 10% for customer indecision"        ← Top 7 ends here
]
→ Missing foundational rules, quotes below minimum
```

## Quality Degradation Pathways

### Pathway 1: Recency Bias Spiral
```
1. Learn "Add 20% for storm season" (off-season)
2. Injected as one of top 7 (high recency)
3. Summer quotes corrected to remove surcharge
4. Summer "corrections" are now most recent
5. Winter quote gets "no storm surcharge" (WRONG)
→ OSCILLATION: Learns and unlearns same rule
```

### Pathway 2: Dilution with Max 20 Limit
```
1. Contractor learns 30+ rules over 50+ corrections
2. System keeps only most recent 20
3. Critical "Never quote below $2,500" gets purged
4. Quotes suddenly violate minimum
→ REGRESSION: Loss of foundational rules
```

## Acceptance Signal Status

| Signal | Exists? | Location | Detection |
|--------|---------|----------|-----------|
| **sent_at** | YES | Quote.sent_at | Set when quote emailed |
| **was_edited** | YES | Quote.was_edited | Set on contractor edit |
| **accepted_at** | YES | Quote.accepted_at | Set on customer accept |
| **status** | YES | Quote.status | "draft" → "sent" → "won"/"lost" |

**Best Query**: `status = 'won' AND accepted_at IS NOT NULL`

## Recommended Fixes (Priority Order)

1. **CRITICAL**: Replace recency selection with relevance scoring
2. **CRITICAL**: Implement quality-aware pruning at 20-item limit
3. **HIGH**: Add per-rule confidence scores from Claude
4. **HIGH**: Weight won vs lost quotes differently
5. **MEDIUM**: Implement A/B testing for rule effectiveness
6. **MEDIUM**: Add semantic deduplication

## Files to Modify

| File | Lines | Change |
|------|-------|--------|
| backend/prompts/quote_generation.py | 82, 336-389 | Replace recency selection |
| backend/services/database.py | 380-383, 347-358 | Quality-aware pruning |
| backend/services/learning.py | 339-417 | Per-rule confidence |
| backend/api/quotes.py | 1383-1426 | Win/loss weighting |
