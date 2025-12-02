# Pricing Model Schema Documentation

## Overview

The `pricing_model` is the core data structure that stores how a contractor prices their work. It is used by the quote generation system to create accurate estimates.

**CRITICAL**: Both onboarding paths (Quick Setup and Interview) MUST produce the exact same schema structure. The only difference is completeness/richness of data.

## Standard Schema

```python
{
    # Core pricing parameters
    "labor_rate_hourly": float,        # $/hour for owner (ESSENTIAL)
    "helper_rate_hourly": float,       # $/hour for helpers (ESSENTIAL)
    "material_markup_percent": float,  # % markup on materials (ESSENTIAL, default: 20.0)
    "minimum_job_amount": float,       # Minimum job threshold (ESSENTIAL, default: 500.0)

    # Flexible learned pricing knowledge (JSON blob)
    "pricing_knowledge": {
        # Trade defaults - baseline rates for this trade
        "trade_defaults": {
            "category_name": {
                "base_per_sqft": float,
                "typical_range": [low, high],
                "unit": "sqft|linear_ft|each|...",
                "notes": "Additional context"
            }
        },

        # Categories - learned pricing patterns by job type
        "categories": {
            "category_key": {
                "display_name": "Human Readable Name",
                "learned_adjustments": [
                    "Adjustment 1",
                    "Adjustment 2"
                ],
                "samples": int,          # Number of quotes in this category
                "confidence": float,     # 0.0-1.0 confidence score
                "typical_price_range": [low, high],
                "pricing_unit": "sqft|hour|project",
                "base_rate": float,
                "notes": "Category-specific notes"
            }
        },

        # Global rules - apply to ALL quotes
        "global_rules": [
            "Rule 1",
            "Rule 2"
        ],

        # Per-unit rates (for non-hourly trades)
        "per_unit_rates": {
            "base_rate_per_lf": float,           # Linear foot rate
            "base_rate_per_sqft": float,         # Square foot rate
            "base_rate_per_square": float,       # Per square (100 sqft)
            "base_rate_per_unit": float,         # Per unit (windows, doors)
            "tear_off_per_square": float,        # Roofer-specific
            "project_management_fee": float      # GC-specific
        }
    },

    # Natural language pricing notes (used in prompts)
    "pricing_notes": str,

    # Standard terms and conditions
    "terms": {
        "deposit_percent": float,       # Default: 50.0
        "quote_valid_days": int,        # Default: 30
        "labor_warranty_years": int     # Default: 2
    },

    # Metadata
    "setup_type": "quick" | "interview",  # Which onboarding path was used
    "created_at": str,                    # ISO timestamp
    "extracted_at": str,                  # ISO timestamp (interview only)
    "session_id": str,                    # Session ID (interview only)
    "message_count": int                  # Message count (interview only)
}
```

## Field Categories

### Essential Fields (MUST have for basic quoting)

These fields are required for the system to generate any quotes:

- `labor_rate_hourly` - Used for hourly estimates
- `helper_rate_hourly` - Used for crew calculations
- `material_markup_percent` - Applied to all material costs
- `minimum_job_amount` - Prevents quoting below threshold
- `pricing_knowledge.trade_defaults` - Baseline rates for the trade
- `pricing_knowledge.categories` - At least basic categories seeded from trade
- `terms` - Standard quote terms

**Quick Setup**: Provides ALL essential fields immediately using trade defaults and user input.

**Interview**: Extracts from conversation, then backfills with trade defaults to ensure completeness.

### Learned-Over-Time Fields (Refined through quote corrections)

These fields start sparse and get richer as the contractor corrects quotes:

- `pricing_knowledge.categories[].learned_adjustments` - Grows with each correction
- `pricing_knowledge.categories[].samples` - Increments with each quote
- `pricing_knowledge.categories[].confidence` - Increases as samples grow
- `pricing_knowledge.global_rules` - Added when patterns emerge across categories
- `pricing_notes` - Appended with learnings from corrections

**Quick Setup**: Starts with minimal learned data, relies on trade defaults.

**Interview**: May have richer initial data extracted from conversation, but still learns over time.

## Onboarding Path Differences

### Quick Setup Path

**Produces**: Complete but MINIMAL pricing_model
- Uses trade defaults extensively
- Seeded categories from trade defaults (higher initial confidence 0.7)
- Standard terms with defaults
- Marked with `setup_type: "quick"`
- User gets started FAST, learns through corrections

**Use Case**: "I know my rates, just want to start quoting"

### Interview Path

**Produces**: Complete and potentially RICHER pricing_model
- Extracts detailed pricing from conversation
- Seeded categories from trade defaults (merged with extracted data)
- May have custom terms extracted from conversation
- Marked with `setup_type: "interview"`
- User has MORE context upfront, still learns through corrections

**Use Case**: "Walk me through understanding my pricing"

### The Guarantee

**BOTH paths produce the EXACT SAME schema structure.**

The only differences are:
1. **Metadata fields** - Interview has `extracted_at`, `session_id`, `message_count`
2. **Data richness** - Interview MAY have more detailed initial data
3. **Marker** - `setup_type` indicates which path was used

Quote generation works IDENTICALLY regardless of onboarding path.

## "Complete Your Profile" Logic

Quick Setup users should be prompted to "complete their profile" after demonstrating system competency:

### Trigger Conditions

- User has `setup_type: "quick"` in their pricing_model
- User has generated 5+ quotes
- User has made 2+ corrections (showing engagement)

### Prompt Message

"You're getting the hang of Quoted! Want to unlock more accurate pricing? Complete your profile with a 5-minute interview to teach the system your unique pricing patterns."

### Benefits of Completing

- More nuanced initial quotes (fewer corrections needed)
- Better category detection
- Custom terms and pricing rules
- Upgrade `setup_type` from "quick" to "interview"

## Migration Strategy

If a Quick Setup user completes the interview later:

1. Run interview extraction
2. MERGE interview data with existing pricing_model (don't overwrite learned corrections)
3. Update `setup_type` to "interview"
4. Preserve all `learned_adjustments` from quote corrections
5. Keep higher of (interview confidence, correction confidence) for each category

## Validation

Before saving any pricing_model to the database, validate:

```python
required_fields = [
    "labor_rate_hourly",
    "helper_rate_hourly",
    "material_markup_percent",
    "minimum_job_amount",
    "pricing_knowledge",
    "terms",
    "setup_type"
]

required_pricing_knowledge_fields = [
    "trade_defaults",
    "categories",
    "global_rules"
]

required_terms_fields = [
    "deposit_percent",
    "quote_valid_days",
    "labor_warranty_years"
]
```

If any required field is missing, backfill with trade defaults before saving.

## Quote Generation Usage

The quote generator uses the pricing_model as follows:

1. **Detect category** from transcription → matches against `pricing_knowledge.categories`
2. **Load learned adjustments** for that category → injects into prompt
3. **Use trade defaults** as fallback → from `pricing_knowledge.trade_defaults`
4. **Apply global rules** → from `pricing_knowledge.global_rules`
5. **Calculate with labor rates** → `labor_rate_hourly`, `helper_rate_hourly`
6. **Add material markup** → `material_markup_percent`
7. **Enforce minimum** → `minimum_job_amount`
8. **Include terms** → from `terms` object

**This flow is IDENTICAL for both Quick Setup and Interview users.**

## Future Enhancements

Potential additions to the schema (backward compatible):

- `pricing_knowledge.seasonal_adjustments` - Winter premium, summer discount
- `pricing_knowledge.client_tiers` - Repeat vs new customer pricing
- `pricing_knowledge.geographic_zones` - Location-based pricing
- `pricing_knowledge.crew_efficiency` - Actual vs estimated hours tracking
- `pricing_confidence_score` - Overall system confidence 0-1

All enhancements must maintain backward compatibility with existing pricing_models.
