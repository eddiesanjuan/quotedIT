# Pricing Brain Management - Feature Design

**Date**: 2025-12-02
**Status**: Approved for Implementation
**Author**: CEO + Founder (Brainstorm Session)

---

## Overview

A new "Pricing Brain" tab in the Account section where users can see what Quoted has learned about their pricing and make corrections with AI assistance.

### Core Value Proposition

- **Transparency**: Users see exactly what the system learned from their corrections
- **Control**: Users can fix mistakes, add rules, and tune their pricing model
- **Trust**: Demystifies the "magic" - users understand why quotes are generated the way they are

### What's NOT in v1

- Bulk adjustments ("raise all prices 10%")
- Confidence overrides
- Import/export pricing models
- Comparison with industry benchmarks

---

## User Flow

1. User navigates to Account → Pricing Brain
2. Sees category cards showing all learned pricing knowledge
3. Clicks "Edit" on any category
4. Sees guided form with pattern-based insights pre-populated
5. Can modify values, accept/reject AI suggestions, add/remove rules
6. Optionally clicks "Get AI Analysis" for deeper Haiku-powered suggestions
7. Saves changes → pricing model updates → future quotes reflect changes

---

## UI Design

### Pricing Brain Dashboard

Main view shows all learned categories as cards in a responsive grid:

```
┌─────────────────────────────────────────────────────────────┐
│  Pricing Brain                                              │
│  Your AI has learned from 47 quotes across 6 categories     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │ Bathroom Remodel    │  │ Interior Paint      │          │
│  │ ──────────────────  │  │ ──────────────────  │          │
│  │ 12 quotes learned   │  │ 23 quotes learned   │          │
│  │ Confidence: Good    │  │ Confidence: High    │          │
│  │ 2 pricing rules     │  │ 4 pricing rules     │          │
│  │          [Edit]     │  │          [Edit]     │          │
│  └─────────────────────┘  └─────────────────────┘          │
│                                                             │
│  ┌─────────────────────────────────────────────┐           │
│  │ Global Settings                             │           │
│  │ Base rates and rules that apply everywhere  │           │
│  │ Labor: $75/hr | Materials: +20% | Min: $500 │           │
│  │                                    [Edit]   │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Card States

- **Empty state**: "No pricing data yet - complete your first quote to start learning"
- **Low confidence**: Subtle warning styling, "Still learning..."
- **High confidence**: Green accent, "Well-calibrated"

---

### Edit Modal

When user clicks "Edit" on a category card:

```
┌─────────────────────────────────────────────────────────────┐
│  Edit: Bathroom Remodel                              [X]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Category Name                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Bathroom Remodel                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│  RATE ADJUSTMENTS                                           │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Labor Rate Modifier        Pattern detected                │
│  ┌──────────────┐          "You've adjusted up 12% on      │
│  │ +12%     [▼] │           your last 6 bathroom quotes"   │
│  └──────────────┘          [Apply +12%]                    │
│                                                             │
│  Material Markup                                            │
│  ┌──────────────┐          Consistent with your quotes     │
│  │ +0%      [▼] │                                          │
│  └──────────────┘                                          │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│  LEARNED RULES                                              │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  - "Add 15% for tile work"              [Edit] [Remove]    │
│  - "Rush jobs (< 1 week) add 20%"       [Edit] [Remove]    │
│                                                             │
│  [+ Add New Rule]                                          │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  [Get AI Analysis]        [Delete Category]                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                        [Cancel]    [Save Changes]           │
└─────────────────────────────────────────────────────────────┘
```

### Editable Fields

| Field | Included | Notes |
|-------|----------|-------|
| Base rate adjustments | Yes | "+10% for this category vs default" |
| Learned rules | Yes | Text rules like "Rush jobs +20%" |
| Category name | Yes | Rename for personalization |
| Delete category | Yes | Safety valve if AI learned garbage |
| Confidence override | No | Risky, excluded from v1 |

### Interaction Details

| Element | Behavior |
|---------|----------|
| Rate modifier dropdown | -50% to +100% in 5% increments, or type custom |
| Pattern hints | Appear instantly from local calculation (no API) |
| [Apply +X%] button | One-click to accept the suggestion |
| Learned rules | Inline edit, confirm on blur |
| [+ Add New Rule] | Opens text input, AI can suggest phrasing |
| [Get AI Analysis] | Calls Haiku, returns deeper insights in ~2 sec |
| [Delete Category] | Confirmation modal, warns about data loss |

---

### AI Analysis Panel (On-Demand)

When user clicks "Get AI Analysis":

```
┌─────────────────────────────────────────────────────────────┐
│  AI Analysis: Bathroom Remodel                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Based on your 12 bathroom quotes:                         │
│                                                             │
│  PRICING PATTERN                                           │
│  You consistently adjust labor up by 10-15% for bathrooms. │
│  This suggests your base rate is too low for this work.    │
│                                                             │
│  -> Suggested: Set labor modifier to +12%                  │
│                                    [Apply This]            │
│                                                             │
│  RULE SUGGESTION                                           │
│  I noticed you add ~$200-400 when "tile" is mentioned.     │
│  Consider adding a rule to capture this automatically.     │
│                                                             │
│  -> Suggested rule: "Tile work: add $300 base"             │
│                                    [Add This Rule]         │
│                                                             │
│  OBSERVATION                                               │
│  Your last 2 bathroom quotes were accepted without edits.  │
│  The model may already be well-calibrated for this type.   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                          [Close Analysis]   │
└─────────────────────────────────────────────────────────────┘
```

### AI Intelligence Levels

| Level | When Used | Cost |
|-------|-----------|------|
| Pattern-based | Instant on modal open | Zero (local calc) |
| Haiku analysis | On-demand via button | ~$0.001/analysis |

**Cost Control**: Limited to 1 AI analysis per category per day.

---

## API Design

### New Endpoints

```
GET  /api/pricing-brain              → Returns all categories + stats
GET  /api/pricing-brain/{category}   → Single category detail
PUT  /api/pricing-brain/{category}   → Update category (rate, rules, name)
DELETE /api/pricing-brain/{category} → Delete category
POST /api/pricing-brain/{category}/analyze → Trigger AI analysis (Haiku)
```

### Response: GET /api/pricing-brain

```json
{
  "global_settings": {
    "labor_rate_hourly": 75,
    "helper_rate_hourly": 35,
    "material_markup_percent": 20,
    "minimum_job_amount": 500
  },
  "categories": [
    {
      "id": "bathroom_remodel",
      "display_name": "Bathroom Remodel",
      "quotes_count": 12,
      "confidence": "good",
      "confidence_score": 0.78,
      "labor_modifier_percent": 12,
      "material_modifier_percent": 0,
      "learned_rules": [
        {"id": "rule_1", "text": "Add 15% for tile work"},
        {"id": "rule_2", "text": "Rush jobs add 20%"}
      ],
      "last_quote_at": "2025-12-01T...",
      "pattern_hint": "You've adjusted up 12% on last 6 quotes"
    }
  ],
  "total_quotes": 47,
  "total_categories": 6
}
```

### Request: PUT /api/pricing-brain/{category}

```json
{
  "display_name": "Full Bath Renovation",
  "labor_modifier_percent": 15,
  "material_modifier_percent": 5,
  "learned_rules": [
    {"id": "rule_1", "text": "Add 15% for tile work"},
    {"id": "rule_3", "text": "Custom showers add $500"}
  ]
}
```

### Response: POST /api/pricing-brain/{category}/analyze

```json
{
  "analysis": {
    "pricing_pattern": {
      "description": "You consistently adjust labor up by 10-15%",
      "suggestion": "Set labor modifier to +12%",
      "suggested_value": 12
    },
    "rule_suggestion": {
      "description": "You add $200-400 when tile is mentioned",
      "suggested_rule": "Tile work: add $300 base"
    },
    "observation": "Last 2 quotes accepted without edits"
  },
  "analyzed_at": "2025-12-02T..."
}
```

---

## Implementation Plan

### Files to Create

| File | Description |
|------|-------------|
| `backend/api/pricing_brain.py` | New API routes |
| `backend/services/pricing_brain.py` | Business logic + AI analysis |

### Files to Modify

| File | Changes |
|------|---------|
| `backend/main.py` | Register pricing_brain router |
| `frontend/index.html` | Add Pricing Brain tab to Account section |

### Implementation Order

1. **Backend API** - GET, PUT, DELETE endpoints
2. **Frontend Dashboard** - Category cards display
3. **Edit Modal** - Form with pattern-based hints
4. **AI Analysis** - Haiku integration + panel
5. **Polish** - Empty states, confirmations, error handling

### Estimated Scope

- Backend: ~300-400 lines
- Frontend: ~500-600 lines
- Complexity: Medium (1 autonomous session)

---

## Dependencies

- Existing `pricing_knowledge` JSON structure (compatible, no migration needed)
- Existing Haiku integration (reuse from category detection)
- Account section UI (already exists from PAY-003)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Users who view Pricing Brain | >50% of active users |
| Users who make edits | >20% of viewers |
| AI suggestions accepted | >40% of suggestions shown |
| Support tickets about "wrong pricing" | Decrease by 50% |

---

## Approved By

- Founder: Eddie San Juan (2025-12-02)
- Design: Brainstorm session with CEO agent
