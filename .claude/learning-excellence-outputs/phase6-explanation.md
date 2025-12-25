# Phase 6: Interpretable AI Explanation System

*Agent: explanation-generator-designer | Completed: 2025-12-24*

---

## Executive Summary

**What**: An Interpretable AI Explanation System that shows contractors exactly WHY their quote was priced the way it was, building trust through transparency and enabling faster corrections.

**Why**: Currently, contractors see "$5,175 total" but don't understand the reasoning. This causes:
1. **Distrust**: "Where did this number come from?"
2. **Slow corrections**: Can't identify which component is wrong
3. **Lost learning opportunities**: Can't validate AI reasoning

**Impact**:
- **Trust through transparency**: Contractors see the AI's reasoning, not just conclusions
- **Faster corrections**: Pinpoint exactly what needs adjustment
- **Better learning**: Contractors can validate patterns ("Yes, I do charge 15% for second story")
- **Anthropic showcase**: Exemplifies "Interpretable AI" principle

**Key Principle**: Show the chain of reasoning from learned patterns → voice signals → final price. Make the AI's thought process auditable.

---

## 1. Explanation Schema

### 1.1 Core Data Structure

```python
# backend/services/pricing_explanation.py (NEW FILE)

from typing import TypedDict, List, Optional, Literal
from datetime import datetime

class PricingComponent(TypedDict):
    """A single component of the pricing explanation."""
    type: Literal["base_rate", "modifier", "adjustment", "voice_signal"]
    label: str  # Human-readable label
    amount: float  # Dollar amount
    source: Literal["learned", "default", "dna_transfer", "voice_detected"]
    confidence: float  # 0.0-1.0
    learning_ref: Optional[str]  # Reference to specific learning ID
    pattern_id: Optional[str]  # Reference to contractor DNA pattern
    validation_count: Optional[int]  # How many times this pattern was validated


class AppliedPattern(TypedDict):
    """A pricing pattern that was applied to this quote."""
    pattern: str  # The pattern statement
    source_category: str  # Where this pattern came from
    times_validated: int  # How many quotes validated this
    last_validated: str  # ISO timestamp
    confidence: float  # Pattern confidence


class UncertaintyNote(TypedDict):
    """An area of uncertainty in the pricing."""
    area: str  # What we're uncertain about
    reason: str  # Why we're uncertain
    suggestion: Optional[str]  # How contractor can resolve


class PricingExplanation(TypedDict):
    """Complete explanation of how a quote was priced."""

    # High-level summary
    summary: str
    # "Based on your deck pricing with 15% premium for second story access"

    # Overall confidence
    overall_confidence: float  # 0.0-1.0
    confidence_label: str  # "High", "Medium", "Low"

    # Breakdown by component
    components: List[PricingComponent]
    """
    [
        {
            "type": "base_rate",
            "label": "Composite deck (material + labor)",
            "amount": 4500.00,
            "source": "learned",
            "confidence": 0.85,
            "learning_ref": "abc123",
            "validation_count": 47
        },
        {
            "type": "modifier",
            "label": "Second story access (+15%)",
            "amount": 675.00,
            "source": "learned",
            "confidence": 0.90,
            "learning_ref": "def456",
            "validation_count": 12
        },
        {
            "type": "voice_signal",
            "label": "ASAP timeline detected (+10%)",
            "amount": 450.00,
            "source": "voice_detected",
            "confidence": 0.70
        }
    ]
    """

    # What we're uncertain about
    uncertainties: List[UncertaintyNote]
    """
    [
        {
            "area": "Deck size complexity",
            "reason": "Limited data for composite decks over 400 sqft",
            "suggestion": "Consider adding 5-10% complexity factor"
        }
    ]
    """

    # Patterns applied
    patterns_applied: List[AppliedPattern]
    """
    [
        {
            "pattern": "Add 15% for second story access",
            "source_category": "deck",
            "times_validated": 12,
            "last_validated": "2025-12-20T10:30:00Z",
            "confidence": 0.90
        }
    ]
    """

    # DNA transfer information (if applicable)
    dna_transfers: List[dict]
    """
    [
        {
            "pattern": "ASAP timeline +20%",
            "from_category": "roofing",
            "inherited_confidence": 0.60,
            "reason": "Universal timing pattern across 3 categories"
        }
    ]
    """

    # Learning history context
    learning_context: dict
    """
    {
        "category": "deck",
        "quote_count": 47,
        "correction_count": 23,
        "acceptance_rate": 0.68,
        "avg_adjustment": 0.04  # 4% average edit
    }
    """
```

### 1.2 Database Storage

**Add to `quotes` table** (`backend/models/database.py`):

```python
# Add pricing explanation column
pricing_explanation = Column(JSON)  # Stores PricingExplanation as JSON
```

**Migration SQL**:
```sql
ALTER TABLE quotes ADD COLUMN pricing_explanation JSONB;
CREATE INDEX idx_quotes_confidence ON quotes ((pricing_explanation->>'overall_confidence'));
```

---

## 2. Explanation Generation Algorithm

### 2.1 Core Generation Logic

```python
# backend/services/pricing_explanation.py

class PricingExplanationService:
    """Generates explanations for quote pricing decisions."""

    async def generate_explanation(
        self,
        quote: Quote,
        learned_adjustments: List[str],
        contractor_dna: ContractorDNA,
        voice_signals: Dict,
        confidence: PricingConfidence,
        pricing_model: dict,
        detected_category: str,
    ) -> PricingExplanation:
        """
        Build explanation by tracing each pricing decision.

        Algorithm:
        1. Identify base rate source (learned vs default vs DNA)
        2. Trace each modifier/adjustment to its origin
        3. Surface uncertainties from confidence system
        4. Generate human-readable summary

        Returns complete PricingExplanation.
        """

        components = []
        patterns_applied = []
        uncertainties = []
        dna_transfers = []

        # 1. BASE RATE IDENTIFICATION
        base_component = await self._identify_base_rate_source(
            quote=quote,
            pricing_model=pricing_model,
            detected_category=detected_category,
        )
        components.append(base_component)

        # 2. LEARNED MODIFIERS
        for adjustment in learned_adjustments:
            modifier = await self._trace_learned_modifier(
                adjustment=adjustment,
                quote=quote,
                pricing_model=pricing_model,
            )
            if modifier:
                components.append(modifier)

                # Add to patterns_applied if it's a validated pattern
                if modifier.get("validation_count", 0) > 5:
                    patterns_applied.append({
                        "pattern": modifier["label"],
                        "source_category": detected_category,
                        "times_validated": modifier["validation_count"],
                        "last_validated": modifier.get("last_validated", ""),
                        "confidence": modifier["confidence"],
                    })

        # 3. DNA TRANSFERS
        for pattern in contractor_dna.get("universal_patterns", []):
            if self._pattern_applies_to_quote(pattern, quote):
                transfer = await self._trace_dna_transfer(
                    pattern=pattern,
                    quote=quote,
                )
                if transfer:
                    components.append(transfer["component"])
                    dna_transfers.append(transfer["dna_info"])

        # 4. VOICE SIGNALS
        for signal_type, signal_data in voice_signals.items():
            if signal_data.get("detected"):
                voice_comp = self._create_voice_signal_component(
                    signal_type=signal_type,
                    signal_data=signal_data,
                    quote=quote,
                )
                components.append(voice_comp)

        # 5. SURFACE UNCERTAINTIES
        uncertainties = await self._identify_uncertainties(
            confidence=confidence,
            pricing_model=pricing_model,
            detected_category=detected_category,
            quote=quote,
        )

        # 6. GENERATE SUMMARY
        summary = self._generate_human_summary(
            components=components,
            patterns_applied=patterns_applied,
            confidence=confidence,
        )

        # 7. COMPILE LEARNING CONTEXT
        learning_context = await self._get_learning_context(
            pricing_model=pricing_model,
            detected_category=detected_category,
        )

        return PricingExplanation(
            summary=summary,
            overall_confidence=confidence.overall_confidence,
            confidence_label=confidence.confidence_label,
            components=components,
            uncertainties=uncertainties,
            patterns_applied=patterns_applied,
            dna_transfers=dna_transfers,
            learning_context=learning_context,
        )


    async def _identify_base_rate_source(
        self,
        quote: Quote,
        pricing_model: dict,
        detected_category: str,
    ) -> PricingComponent:
        """
        Identify where the base rate came from.

        Priority:
        1. Learned category pricing (best)
        2. DNA transfer from related category
        3. Default market rates (fallback)
        """
        pricing_knowledge = pricing_model.get("pricing_knowledge", {})
        categories = pricing_knowledge.get("categories", {})

        if detected_category in categories:
            cat_data = categories[detected_category]
            quote_count = cat_data.get("quote_count", 0)
            confidence = cat_data.get("confidence", 0.5)

            # Calculate base amount (quote total minus modifiers)
            # This is simplified - in reality we'd parse line items
            estimated_base = quote.subtotal * 0.80  # Assume modifiers are ~20%

            return PricingComponent(
                type="base_rate",
                label=f"{detected_category.replace('_', ' ').title()} base pricing",
                amount=estimated_base,
                source="learned",
                confidence=confidence,
                learning_ref=None,  # Could link to category data
                validation_count=quote_count,
            )

        else:
            # Check for DNA transfer
            contractor_dna = pricing_model.get("contractor_dna", {})
            related_category = self._find_related_category(
                target_category=detected_category,
                contractor_dna=contractor_dna,
            )

            if related_category:
                return PricingComponent(
                    type="base_rate",
                    label=f"Using {related_category} pricing patterns (first {detected_category} quote)",
                    amount=quote.subtotal * 0.70,
                    source="dna_transfer",
                    confidence=0.50,  # Lower confidence for transfers
                    learning_ref=None,
                    validation_count=0,
                )
            else:
                return PricingComponent(
                    type="base_rate",
                    label="Market average pricing (no prior data)",
                    amount=quote.subtotal * 0.70,
                    source="default",
                    confidence=0.30,
                    learning_ref=None,
                    validation_count=0,
                )


    async def _trace_learned_modifier(
        self,
        adjustment: str,
        quote: Quote,
        pricing_model: dict,
    ) -> Optional[PricingComponent]:
        """
        Trace a learned adjustment to create a component.

        Parse adjustment statements like:
        - "Add 15% for second story access"
        - "Repeat customer: reduce by 5%"
        - "ASAP timeline: increase by 20%"
        """
        # Extract numeric value
        numeric_value = self._extract_numeric_from_statement(adjustment)
        if not numeric_value:
            return None  # Can't create component without amount

        # Calculate dollar amount
        modifier_amount = quote.subtotal * (numeric_value / 100)

        # Get validation count from pricing model
        # This would require tracking which learning ID this came from
        # For now, estimate based on confidence
        validation_count = 5  # Placeholder

        return PricingComponent(
            type="modifier",
            label=self._humanize_adjustment_label(adjustment),
            amount=modifier_amount,
            source="learned",
            confidence=0.85,  # From pricing model
            learning_ref="abc123",  # Would be actual learning ID
            validation_count=validation_count,
        )


    async def _identify_uncertainties(
        self,
        confidence: PricingConfidence,
        pricing_model: dict,
        detected_category: str,
        quote: Quote,
    ) -> List[UncertaintyNote]:
        """
        Surface areas of uncertainty for contractor review.

        Common uncertainty sources:
        1. Low data confidence (< 0.60)
        2. First quote in category
        3. Unusual job characteristics (size, complexity)
        4. Conflicting patterns detected
        """
        uncertainties = []

        # 1. Low overall confidence
        if confidence.overall_confidence < 0.60:
            reason_parts = []

            if confidence.data_confidence < 0.50:
                reason_parts.append(f"limited prior data ({confidence.quote_count} quotes)")

            if confidence.accuracy_confidence < 0.70:
                reason_parts.append("past quotes in this category needed significant edits")

            if confidence.recency_confidence < 0.60:
                reason_parts.append("haven't quoted this type recently")

            uncertainties.append(UncertaintyNote(
                area="Overall pricing accuracy",
                reason=", ".join(reason_parts).capitalize(),
                suggestion="Review line items carefully, especially material costs",
            ))

        # 2. First quote in category
        categories = pricing_model.get("pricing_knowledge", {}).get("categories", {})
        if detected_category not in categories:
            uncertainties.append(UncertaintyNote(
                area=f"First {detected_category.replace('_', ' ')} quote",
                reason="No prior quotes in this category, using DNA patterns from other work",
                suggestion="This quote will establish baseline pricing for future similar jobs",
            ))

        # 3. Unusual size/complexity
        # This would analyze quote.line_items for outliers
        # Placeholder implementation
        if quote.subtotal > 10000:
            uncertainties.append(UncertaintyNote(
                area="Large project complexity",
                reason="Limited data for projects over $10,000",
                suggestion="Consider adding complexity factor for project management overhead",
            ))

        return uncertainties


    def _generate_human_summary(
        self,
        components: List[PricingComponent],
        patterns_applied: List[AppliedPattern],
        confidence: PricingConfidence,
    ) -> str:
        """
        Generate 1-2 sentence human-readable summary.

        Template:
        "Based on [SOURCE] with [KEY_MODIFIERS]"

        Examples:
        - "Based on 47 previous deck quotes, with 15% premium for second story access"
        - "Using roofing patterns (first fence quote) with repeat customer discount"
        - "Market average pricing (no prior data) with ASAP rush premium"
        """
        # Identify primary source
        base_component = next((c for c in components if c["type"] == "base_rate"), None)
        if not base_component:
            return "Pricing breakdown unavailable"

        source_map = {
            "learned": f"{base_component.get('validation_count', 0)} previous similar quotes",
            "dna_transfer": f"patterns from {base_component.get('label', 'related work')}",
            "default": "market averages (no prior data)",
        }

        source_phrase = source_map.get(base_component["source"], "available data")

        # Identify key modifiers (top 2 by amount)
        modifiers = [c for c in components if c["type"] in ["modifier", "voice_signal"]]
        modifiers.sort(key=lambda x: x["amount"], reverse=True)
        top_modifiers = modifiers[:2]

        if top_modifiers:
            modifier_phrases = [
                self._modifier_to_phrase(m) for m in top_modifiers
            ]
            modifier_str = ", ".join(modifier_phrases)
            return f"Based on {source_phrase} with {modifier_str}"
        else:
            return f"Based on {source_phrase}"


    def _modifier_to_phrase(self, component: PricingComponent) -> str:
        """Convert modifier component to natural language phrase."""
        label = component["label"].lower()

        # Strip common prefixes/suffixes
        label = label.replace("detected", "").replace("premium", "").strip()

        # Add validation context if high confidence
        if component.get("validation_count", 0) > 10:
            return f"{label} (validated {component['validation_count']}×)"
        else:
            return label


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def _extract_numeric_from_statement(statement: str) -> Optional[float]:
    """
    Extract percentage or dollar amount from learning statement.

    Examples:
    - "Add 15% for second story" → 15.0
    - "Reduce by 5%" → -5.0
    - "$500 demolition fee" → None (not a modifier)
    """
    import re

    # Match percentage patterns
    pct_match = re.search(r'(\+|-)?(\d+(?:\.\d+)?)\s*%', statement)
    if pct_match:
        sign = -1 if pct_match.group(1) == '-' else 1
        value = float(pct_match.group(2))

        # Check for decrease keywords
        if any(word in statement.lower() for word in ['reduce', 'discount', 'lower', 'decrease']):
            sign = -1

        return sign * value

    return None


def _humanize_adjustment_label(statement: str) -> str:
    """
    Convert learning statement to human-readable label.

    Examples:
    - "Add 15% for second story access" → "Second story access (+15%)"
    - "Repeat customer: reduce by 5%" → "Repeat customer discount (-5%)"
    """
    # Extract key phrase
    phrases = statement.split(':')
    if len(phrases) > 1:
        return phrases[0].strip()

    # Extract from "for X" pattern
    for_match = re.search(r'for (.+?)(?:\s|$)', statement, re.IGNORECASE)
    if for_match:
        return for_match.group(1).strip().title()

    # Fallback to full statement (cleaned)
    return statement.replace("Add", "").replace("Increase", "").strip()
```

---

## 3. UI Display Specifications

### 3.1 Quote View - Explanation Section

**Location**: Below quote total, above line items

```
┌─────────────────────────────────────────────────────────┐
│  QUOTE TOTAL: $5,175.00                    [85% Conf ✓] │
├─────────────────────────────────────────────────────────┤
│  📊 How this was priced:                                │
│                                                         │
│  Based on 47 previous deck quotes with second story    │
│  access premium (validated 12×)                         │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Base: Composite deck 20×15 ft      $4,500.00    │   │
│  │   └ From 47 previous deck quotes                │   │
│  │                                                  │   │
│  │ + Second story access (+15%)          $675.00   │   │
│  │   └ Pattern validated 12 times                  │   │
│  │                                                  │   │
│  │ ⚠️ Note: This is your first composite over 400   │   │
│  │   sqft. Consider adding complexity factor.      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Looks Good ✓] [Edit Price ✏️] [See Details →]        │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Progressive Disclosure (3 Levels)

**Level 1: Summary (Always Visible)**
```
📊 How this was priced:
Based on 47 previous deck quotes with second story premium

[Show breakdown →]
```

**Level 2: Component Breakdown (First Expand)**
```
📊 How this was priced:

Summary: Based on 47 previous deck quotes with second story access premium

Components:
  Base: Composite deck 20×15 ft           $4,500.00
    └ From 47 previous deck quotes (85% confidence)

  + Second story access (+15%)               $675.00
    └ Pattern validated 12 times (90% confidence)

⚠️ Uncertainties:
  • First composite deck over 400 sqft
    → Consider adding complexity factor

[Hide] [Deep dive →]
```

**Level 3: Deep Dive (Second Expand)**
```
📊 How this was priced:

Summary: Based on 47 previous deck quotes with second story access premium

Components:
  Base: Composite deck 20×15 ft           $4,500.00
    └ Source: Learned from 47 quotes (category: deck)
    └ Confidence: 85% (data: 0.90, accuracy: 0.82, recency: 0.95)
    └ Learning ref: category_deck_base_pricing

  + Second story access (+15%)               $675.00
    └ Source: Learning #def456 from 2025-12-15
    └ Statement: "Add 15% for second story access"
    └ Validated: 12 quotes since creation
    └ Confidence: 90%

Patterns Applied:
  1. "Add 15% for second story access"
     - From: deck category
     - Validated: 12× (most recent: 2025-12-20)
     - Confidence: 90%

Learning Context:
  - Category: Deck
  - Total quotes: 47
  - Corrections: 23 (49% edit rate)
  - Acceptance rate: 68% (sent as-is)
  - Avg adjustment: 4%

Confidence Breakdown:
  - Data confidence: 90% (47 quotes)
  - Accuracy confidence: 82% (past edits averaged 4%)
  - Recency confidence: 95% (last quote 3 days ago)
  - Overall: 85%

[Hide deep dive]
```

### 3.3 Mobile Layout (375px width)

```
┌─────────────────────────────┐
│ QUOTE TOTAL: $5,175.00      │
│ [85% Confidence ✓]          │
├─────────────────────────────┤
│ 📊 How this was priced:     │
│                             │
│ Based on 47 deck quotes     │
│ + second story premium      │
│                             │
│ [Show breakdown ↓]          │
└─────────────────────────────┘
```

---

## 4. Correction Flow Integration

### 4.1 Explanation-Aware Correction UI

**When contractor edits price:**

```
┌─────────────────────────────────────────────────────────┐
│  You changed: $5,175 → $5,500 (+$325, +6.3%)           │
├─────────────────────────────────────────────────────────┤
│  Help me learn - what should I adjust?                  │
│                                                          │
│  Based on my pricing breakdown:                          │
│    ✓ Base deck pricing: $4,500 (from 47 quotes)         │
│    ✓ Second story premium: $675 (+15%)                  │
│                                                          │
│  What needs to change?                                   │
│  ○ Base rate too low for composite                      │
│  ○ Second story premium should be higher                │
│  ● Add complexity modifier for 400+ sqft                │
│  ○ Other (explain)                                       │
│                                                          │
│  [Continue] [Skip learning]                             │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Component-Level Corrections

**Allow contractors to correct specific components:**

```javascript
// frontend/index.html - correction flow

async function handleExplanationCorrection(quoteId, correctionData) {
    // correctionData = {
    //   corrected_component: "base_rate" | "modifier_xyz",
    //   correction_type: "too_low" | "too_high" | "missing" | "wrong",
    //   suggested_value: 5000.00,
    //   reason: "Composite decks over 400 sqft need complexity factor"
    // }

    const response = await fetch(`/api/quotes/${quoteId}/correct`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            ...correctionData,
            explanation_aware: true  // Flag for new correction type
        })
    });

    if (response.ok) {
        showToast("Learning recorded! Future large deck quotes will include complexity factor.");
    }
}
```

### 4.3 Learning Extraction from Explanation Corrections

```python
# backend/services/learning.py - enhancement

async def process_explanation_correction(
    quote_id: str,
    corrected_component: str,
    correction_type: str,
    suggested_value: float,
    reason: str,
) -> dict:
    """
    Process a correction made via explanation UI.

    This is MORE PRECISE than traditional corrections because
    we know EXACTLY which component was wrong.

    Traditional: "Quote was $500 too low" (which part?)
    Explanation: "Base rate should be $5,000 not $4,500" (precise!)
    """

    # Generate targeted learning statement
    if corrected_component == "base_rate":
        learning_statement = f"Base pricing for {reason}"
    elif corrected_component.startswith("modifier_"):
        modifier_name = corrected_component.replace("modifier_", "")
        if correction_type == "too_low":
            learning_statement = f"Increase {modifier_name} premium (was too conservative)"
        elif correction_type == "too_high":
            learning_statement = f"Reduce {modifier_name} premium (was too aggressive)"
        elif correction_type == "missing":
            learning_statement = f"Add {reason}"

    return {
        "learning_statement": learning_statement,
        "confidence": "high",  # More confident because it's targeted
        "source": "explanation_correction",
    }
```

---

## 5. Explanation Templates

### 5.1 Common Scenarios

```python
# backend/services/explanation_templates.py

EXPLANATION_TEMPLATES = {
    "learned_pricing": {
        "summary": "Based on {quote_count} previous {category} quotes, with {acceptance_rate}% sent as-is",
        "component_label": "{category_display} base pricing",
        "uncertainty_note": None,  # High confidence, no note needed
    },

    "dna_transfer": {
        "summary": "Using {source_category} pricing patterns (first {target_category} quote)",
        "component_label": "Transferred from {source_category}",
        "uncertainty_note": "This is your first {target_category} quote. Pricing will improve as you create more.",
    },

    "voice_signal_rush": {
        "summary": "Based on {source} with ASAP rush premium",
        "component_label": "ASAP timeline detected (+{pct}%)",
        "uncertainty_note": None,
    },

    "voice_signal_relationship": {
        "summary": "Based on {source} with repeat customer discount",
        "component_label": "Repeat customer (-{pct}%)",
        "uncertainty_note": None,
    },

    "high_confidence": {
        "summary": "Based on {quote_count} {category} quotes (AI matches your pricing {accuracy}% of the time)",
        "component_label": "{category_display} pricing (well-calibrated)",
        "uncertainty_note": None,
    },

    "low_confidence": {
        "summary": "Limited data for {category}. Review carefully.",
        "component_label": "Estimated {category} pricing",
        "uncertainty_note": "Limited prior data. This quote will help calibrate future {category} pricing.",
    },

    "first_quote_ever": {
        "summary": "Market average pricing (this is your first quote!)",
        "component_label": "Industry standard rates",
        "uncertainty_note": "This quote establishes your baseline pricing. Edit to match your actual rates.",
    },

    "conflicting_patterns": {
        "summary": "Based on {source}, but detected conflicting patterns",
        "component_label": "Mixed signals detected",
        "uncertainty_note": "Past quotes show both increases and decreases for similar work. Review carefully.",
    },
}


def apply_template(
    template_name: str,
    **kwargs
) -> dict:
    """Apply template with variable substitution."""
    template = EXPLANATION_TEMPLATES.get(template_name)
    if not template:
        return EXPLANATION_TEMPLATES["learned_pricing"]  # Default

    return {
        "summary": template["summary"].format(**kwargs),
        "component_label": template["component_label"].format(**kwargs) if template["component_label"] else "",
        "uncertainty_note": template["uncertainty_note"].format(**kwargs) if template["uncertainty_note"] else None,
    }
```

---

## 6. API Response Enhancement

### 6.1 Quote Generation Response

```python
# backend/api/quotes.py - enhancement

@router.post("/generate")
async def generate_quote(request: QuoteRequest):
    """Generate quote with explanation."""

    # ... existing quote generation logic ...

    # Generate explanation
    from backend.services.pricing_explanation import PricingExplanationService

    explanation_service = PricingExplanationService()
    explanation = await explanation_service.generate_explanation(
        quote=generated_quote,
        learned_adjustments=learned_adjustments_used,
        contractor_dna=contractor.pricing_model.contractor_dna,
        voice_signals=detected_voice_signals,
        confidence=confidence_metrics,
        pricing_model=contractor.pricing_model,
        detected_category=detected_category,
    )

    # Save explanation with quote
    generated_quote.pricing_explanation = explanation
    await db.commit()

    return {
        "quote_id": generated_quote.id,
        "total": generated_quote.total,
        "line_items": generated_quote.line_items,
        "explanation": explanation,  # NEW: Full explanation
        "confidence": confidence_metrics,
    }
```

### 6.2 API Response Schema

```json
{
  "quote_id": "abc123",
  "total": 5175.00,
  "line_items": [...],

  "explanation": {
    "summary": "Based on 47 previous deck quotes with second story access premium",
    "overall_confidence": 0.85,
    "confidence_label": "High",

    "components": [
      {
        "type": "base_rate",
        "label": "Composite deck base pricing",
        "amount": 4500.00,
        "source": "learned",
        "confidence": 0.85,
        "validation_count": 47
      },
      {
        "type": "modifier",
        "label": "Second story access (+15%)",
        "amount": 675.00,
        "source": "learned",
        "confidence": 0.90,
        "learning_ref": "def456",
        "validation_count": 12
      }
    ],

    "uncertainties": [
      {
        "area": "Deck size complexity",
        "reason": "Limited data for composite decks over 400 sqft",
        "suggestion": "Consider adding 5-10% complexity factor"
      }
    ],

    "patterns_applied": [
      {
        "pattern": "Add 15% for second story access",
        "source_category": "deck",
        "times_validated": 12,
        "last_validated": "2025-12-20T10:30:00Z",
        "confidence": 0.90
      }
    ],

    "learning_context": {
      "category": "deck",
      "quote_count": 47,
      "correction_count": 23,
      "acceptance_rate": 0.68,
      "avg_adjustment": 0.04
    }
  }
}
```

---

## 7. Frontend Implementation (SECURE)

### 7.1 Explanation Component - Safe DOM Creation

```javascript
// frontend/index.html - add explanation component (XSS-SAFE)

class QuoteExplanation {
    constructor(explanation, quoteTotal) {
        this.explanation = explanation;
        this.quoteTotal = quoteTotal;
        this.expandLevel = 1;  // 1 = summary, 2 = breakdown, 3 = deep
    }

    render() {
        const container = document.createElement('div');
        container.className = 'explanation-container';

        // Header
        const header = this._createHeader();
        container.appendChild(header);

        // Summary
        const summary = this._createSummary();
        container.appendChild(summary);

        // Breakdown (if expanded)
        if (this.expandLevel >= 2) {
            const breakdown = this._createBreakdown();
            container.appendChild(breakdown);
        }

        // Deep dive (if expanded)
        if (this.expandLevel >= 3) {
            const deepDive = this._createDeepDive();
            container.appendChild(deepDive);
        }

        // Expand button
        const expandBtn = this._createExpandButton();
        container.appendChild(expandBtn);

        return container;
    }

    _createHeader() {
        const header = document.createElement('div');
        header.className = 'explanation-header';

        const title = document.createElement('h3');
        title.textContent = '📊 How this was priced:';

        const badge = document.createElement('span');
        badge.className = `confidence-badge ${this.getConfidenceBadgeClass()}`;
        badge.textContent = `${Math.round(this.explanation.overall_confidence * 100)}% Confidence`;

        header.appendChild(title);
        header.appendChild(badge);

        return header;
    }

    _createSummary() {
        const summary = document.createElement('div');
        summary.className = 'explanation-summary';
        summary.textContent = this.explanation.summary;
        return summary;
    }

    _createBreakdown() {
        const breakdown = document.createElement('div');
        breakdown.className = 'explanation-breakdown';

        // Render components
        this.explanation.components.forEach(comp => {
            const compEl = this._createComponentElement(comp);
            breakdown.appendChild(compEl);
        });

        // Render uncertainties
        if (this.explanation.uncertainties.length > 0) {
            const uncertainties = this._createUncertaintiesSection();
            breakdown.appendChild(uncertainties);
        }

        return breakdown;
    }

    _createComponentElement(comp) {
        const compDiv = document.createElement('div');
        compDiv.className = `explanation-component ${comp.type}`;

        // Main row
        const mainRow = document.createElement('div');
        mainRow.className = 'comp-main';

        const icon = document.createElement('span');
        icon.className = 'comp-icon';
        icon.textContent = this.getComponentIcon(comp.type);

        const label = document.createElement('span');
        label.className = 'comp-label';
        label.textContent = comp.label;

        const amount = document.createElement('span');
        amount.className = 'comp-amount';
        amount.textContent = `$${comp.amount.toLocaleString()}`;

        mainRow.appendChild(icon);
        mainRow.appendChild(label);
        mainRow.appendChild(amount);

        // Meta row
        const metaRow = document.createElement('div');
        metaRow.className = 'comp-meta';
        metaRow.textContent = `└ ${this.getComponentMeta(comp)} `;

        const confBadge = this._createConfidenceBadge(comp.confidence);
        metaRow.appendChild(confBadge);

        compDiv.appendChild(mainRow);
        compDiv.appendChild(metaRow);

        return compDiv;
    }

    _createUncertaintiesSection() {
        const section = document.createElement('div');
        section.className = 'uncertainties';

        const title = document.createElement('h4');
        title.textContent = '⚠️ Things to review:';
        section.appendChild(title);

        this.explanation.uncertainties.forEach(u => {
            const note = document.createElement('div');
            note.className = 'uncertainty-note';

            const strong = document.createElement('strong');
            strong.textContent = u.area;
            note.appendChild(strong);

            const text = document.createTextNode(`: ${u.reason}`);
            note.appendChild(text);

            if (u.suggestion) {
                const br = document.createElement('br');
                note.appendChild(br);

                const suggestion = document.createElement('em');
                suggestion.textContent = `→ ${u.suggestion}`;
                note.appendChild(suggestion);
            }

            section.appendChild(note);
        });

        return section;
    }

    _createDeepDive() {
        const deep = document.createElement('div');
        deep.className = 'explanation-deep';

        // Patterns section
        if (this.explanation.patterns_applied.length > 0) {
            const patternsTitle = document.createElement('h4');
            patternsTitle.textContent = 'Patterns Applied:';
            deep.appendChild(patternsTitle);

            this.explanation.patterns_applied.forEach(p => {
                const patternDiv = this._createPatternDetail(p);
                deep.appendChild(patternDiv);
            });
        }

        // Learning context
        const contextTitle = document.createElement('h4');
        contextTitle.textContent = 'Learning Context:';
        deep.appendChild(contextTitle);

        const stats = this._createLearningStats();
        deep.appendChild(stats);

        return deep;
    }

    _createPatternDetail(pattern) {
        const div = document.createElement('div');
        div.className = 'pattern-detail';

        const strong = document.createElement('strong');
        strong.textContent = `"${pattern.pattern}"`;
        div.appendChild(strong);

        const br = document.createElement('br');
        div.appendChild(br);

        const text = document.createTextNode(
            `Validated ${pattern.times_validated}× ` +
            `(most recent: ${this.formatDate(pattern.last_validated)}) - ` +
            `${Math.round(pattern.confidence * 100)}% confidence`
        );
        div.appendChild(text);

        return div;
    }

    _createLearningStats() {
        const stats = document.createElement('div');
        stats.className = 'learning-stats';

        const ctx = this.explanation.learning_context;

        const stat1 = this._createStat(ctx.quote_count, 'Total quotes');
        const stat2 = this._createStat(
            `${Math.round(ctx.acceptance_rate * 100)}%`,
            'Sent as-is'
        );
        const stat3 = this._createStat(
            `${Math.round(ctx.avg_adjustment * 100)}%`,
            'Avg adjustment'
        );

        stats.appendChild(stat1);
        stats.appendChild(stat2);
        stats.appendChild(stat3);

        return stats;
    }

    _createStat(value, label) {
        const stat = document.createElement('div');
        stat.className = 'stat';

        const valueSpan = document.createElement('span');
        valueSpan.className = 'stat-value';
        valueSpan.textContent = value;

        const labelSpan = document.createElement('span');
        labelSpan.className = 'stat-label';
        labelSpan.textContent = label;

        stat.appendChild(valueSpan);
        stat.appendChild(labelSpan);

        return stat;
    }

    _createConfidenceBadge(confidence) {
        const badge = document.createElement('span');
        const pct = Math.round(confidence * 100);
        const className = confidence >= 0.80 ? 'high' : confidence >= 0.60 ? 'med' : 'low';
        badge.className = `conf-badge ${className}`;
        badge.textContent = `${pct}%`;
        return badge;
    }

    _createExpandButton() {
        const btn = document.createElement('button');
        btn.className = 'expand-btn';
        btn.textContent = this.getExpandButtonText();
        btn.onclick = () => this.toggleExpand();
        return btn;
    }

    toggleExpand() {
        this.expandLevel = (this.expandLevel % 3) + 1;
        this.rerenderInPlace();
    }

    rerenderInPlace() {
        const parent = this.containerElement.parentNode;
        const newElement = this.render();
        parent.replaceChild(newElement, this.containerElement);
        this.containerElement = newElement;
    }

    getExpandButtonText() {
        if (this.expandLevel === 1) return 'Show breakdown →';
        if (this.expandLevel === 2) return 'Deep dive →';
        return '← Hide details';
    }

    getConfidenceBadgeClass() {
        const conf = this.explanation.overall_confidence;
        if (conf >= 0.80) return 'confidence-high';
        if (conf >= 0.60) return 'confidence-medium';
        return 'confidence-low';
    }

    getComponentIcon(type) {
        const icons = {
            'base_rate': '💰',
            'modifier': '📊',
            'adjustment': '⚙️',
            'voice_signal': '🎤'
        };
        return icons[type] || '•';
    }

    getComponentMeta(comp) {
        if (comp.source === 'learned' && comp.validation_count) {
            return `From ${comp.validation_count} previous quotes`;
        } else if (comp.source === 'dna_transfer') {
            return `Transferred from related work`;
        } else if (comp.source === 'voice_detected') {
            return `Detected in your voice note`;
        } else {
            return `Market average (no prior data)`;
        }
    }

    formatDate(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'today';
        if (diffDays === 1) return 'yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    }
}

// Usage
let explanationComponent;

function displayQuoteWithExplanation(quoteData) {
    // ... existing quote display logic ...

    // Add explanation (SAFE - uses DOM creation, not innerHTML)
    explanationComponent = new QuoteExplanation(
        quoteData.explanation,
        quoteData.total
    );

    const explanationContainer = document.getElementById('explanation-container');
    explanationContainer.textContent = '';  // Clear safely
    const renderedExplanation = explanationComponent.render();
    explanationComponent.containerElement = renderedExplanation;  // Store reference
    explanationContainer.appendChild(renderedExplanation);
}
```

### 7.2 CSS Styling

```css
/* frontend/index.html - add to <style> section */

.explanation-container {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}

.explanation-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.confidence-badge {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.85em;
    font-weight: 600;
}

.confidence-badge.confidence-high {
    background: #d4edda;
    color: #155724;
}

.confidence-badge.confidence-medium {
    background: #fff3cd;
    color: #856404;
}

.confidence-badge.confidence-low {
    background: #f8d7da;
    color: #721c24;
}

.explanation-summary {
    font-size: 1.05em;
    color: #495057;
    margin-bottom: 16px;
    line-height: 1.5;
}

.explanation-breakdown {
    margin: 16px 0;
}

.explanation-component {
    background: white;
    border-left: 3px solid #007bff;
    padding: 12px;
    margin: 8px 0;
    border-radius: 4px;
}

.explanation-component.base_rate {
    border-left-color: #28a745;
}

.explanation-component.modifier {
    border-left-color: #007bff;
}

.explanation-component.voice_signal {
    border-left-color: #ffc107;
}

.comp-main {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
}

.comp-icon {
    font-size: 1.2em;
}

.comp-label {
    flex: 1;
}

.comp-amount {
    font-weight: 600;
    color: #28a745;
}

.comp-meta {
    font-size: 0.9em;
    color: #6c757d;
    margin-top: 4px;
    padding-left: 32px;
}

.conf-badge {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.85em;
    font-weight: 600;
    margin-left: 8px;
}

.conf-badge.high {
    background: #d4edda;
    color: #155724;
}

.conf-badge.med {
    background: #fff3cd;
    color: #856404;
}

.conf-badge.low {
    background: #f8d7da;
    color: #721c24;
}

.uncertainties {
    background: #fff3cd;
    border-left: 3px solid #ffc107;
    padding: 12px;
    margin-top: 16px;
    border-radius: 4px;
}

.uncertainties h4 {
    margin: 0 0 8px 0;
    font-size: 1em;
    color: #856404;
}

.uncertainty-note {
    margin: 8px 0;
    font-size: 0.95em;
    color: #856404;
}

.expand-btn {
    background: transparent;
    border: 1px solid #007bff;
    color: #007bff;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
    margin-top: 12px;
    transition: all 0.2s;
}

.expand-btn:hover {
    background: #007bff;
    color: white;
}

.explanation-deep {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #dee2e6;
}

.pattern-detail {
    background: #e9ecef;
    padding: 8px;
    margin: 8px 0;
    border-radius: 4px;
    font-size: 0.9em;
}

.learning-stats {
    display: flex;
    gap: 16px;
    margin-top: 12px;
}

.stat {
    flex: 1;
    text-align: center;
    padding: 12px;
    background: white;
    border-radius: 4px;
}

.stat-value {
    display: block;
    font-size: 1.5em;
    font-weight: 700;
    color: #007bff;
}

.stat-label {
    display: block;
    font-size: 0.85em;
    color: #6c757d;
    margin-top: 4px;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .explanation-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }

    .learning-stats {
        flex-direction: column;
        gap: 8px;
    }

    .comp-main {
        flex-wrap: wrap;
    }
}
```

---

## 8. Integration Points

### 8.1 Quote Generation Flow

```python
# backend/services/quote_generator.py - enhancement

class QuoteGenerationService:

    async def generate_quote(self, request: QuoteRequest) -> Quote:
        # ... existing quote generation ...

        # NEW: Generate explanation
        explanation_service = PricingExplanationService()
        explanation = await explanation_service.generate_explanation(
            quote=generated_quote,
            learned_adjustments=learned_adjustments_injected,
            contractor_dna=contractor.pricing_model.contractor_dna,
            voice_signals=voice_signals_detected,
            confidence=confidence_calculated,
            pricing_model=contractor.pricing_model,
            detected_category=detected_category,
        )

        # Store with quote
        generated_quote.pricing_explanation = explanation

        return generated_quote
```

### 8.2 Correction Processing

```python
# backend/services/learning.py - enhancement

async def process_correction(
    self,
    original_quote: dict,
    final_quote: dict,
    contractor_notes: Optional[str] = None,
    # NEW: Explanation-aware correction
    corrected_component: Optional[str] = None,
    correction_type: Optional[str] = None,
    **kwargs
) -> dict:
    """Process correction with optional explanation context."""

    # ... existing correction logic ...

    # NEW: If explanation-aware correction
    if corrected_component:
        targeted_learning = await self._extract_targeted_learning(
            component=corrected_component,
            correction_type=correction_type,
            original=original_quote,
            final=final_quote,
            notes=contractor_notes,
        )

        # Append to learnings with higher confidence
        learnings["learning_statements"].append(targeted_learning)
        learnings["confidence"] = "high"  # More confident

    return learnings
```

### 8.3 File Changes Summary

| File | Change Type | Description |
|------|-------------|-------------|
| `backend/services/pricing_explanation.py` | **NEW FILE** | Core explanation generation service |
| `backend/models/database.py` | **SCHEMA** | Add `pricing_explanation` column to quotes |
| `backend/services/quote_generator.py` | **ENHANCE** | Call explanation service during generation |
| `backend/api/quotes.py` | **ENHANCE** | Include explanation in API response |
| `backend/services/learning.py` | **ENHANCE** | Support explanation-aware corrections |
| `frontend/index.html` | **ENHANCE** | Add QuoteExplanation component + CSS (XSS-safe) |

---

## 9. Test Scenarios

### 9.1 High Confidence Scenario

**Setup**: 50 deck quotes, 70% acceptance rate, recent activity

**Expected Explanation**:
```
Summary: "Based on 50 previous deck quotes (AI matches your pricing 92% of the time)"

Components:
- Base: Composite deck 20×15 ft - $4,500 (learned, 90% conf, 50 quotes)
- + Second story (+15%) - $675 (learned, 90% conf, 18 validations)

Uncertainties: None

Patterns: "Add 15% for second story" (18× validated, 90% conf)
```

### 9.2 DNA Transfer Scenario

**Setup**: First fence quote, has 30 deck quotes

**Expected Explanation**:
```
Summary: "Using deck pricing patterns (first fence quote) with ASAP rush premium"

Components:
- Base: Transferred from deck category - $3,200 (dna_transfer, 50% conf)
- + ASAP timeline (+20%) - $640 (dna_transfer, 60% conf, universal pattern)

Uncertainties:
- "First fence quote" - Using DNA patterns from deck work
  → This quote establishes baseline pricing for future fence quotes

DNA Transfers:
- "ASAP timeline +20%" from deck (universal pattern, 3 categories)
```

### 9.3 Low Confidence Scenario

**Setup**: Third quote ever, different category each time

**Expected Explanation**:
```
Summary: "Limited data for painting (no prior quotes). Review carefully."

Components:
- Base: Market average painting rates - $2,800 (default, 30% conf)

Uncertainties:
- "Overall pricing accuracy" - No prior painting quotes, using industry averages
  → This quote establishes baseline pricing for future painting quotes
- "Limited data" - Only 2 total quotes in system
  → System will improve with more quotes

Patterns: None
```

### 9.4 Voice Signal Scenario

**Setup**: Voice note says "ASAP, repeat customer John Smith"

**Expected Explanation**:
```
Summary: "Based on 20 deck quotes with ASAP rush premium and repeat customer discount"

Components:
- Base: Deck base pricing - $4,000 (learned, 80% conf, 20 quotes)
- + ASAP timeline (+20%) - $800 (voice_detected, 70% conf)
- - Repeat customer (-5%) - $200 (voice_detected, 65% conf)

Voice Signals Detected:
- "ASAP" → Rush premium applied
- "repeat customer" → Loyalty discount applied

Patterns:
- "ASAP +20%" (validated 8×)
- "Repeat customer -5%" (validated 5×)
```

### 9.5 Conflicting Patterns Scenario

**Setup**: Past quotes show both +10% and -5% for same trigger

**Expected Explanation**:
```
Summary: "Based on 15 roofing quotes, but detected conflicting patterns for pitch"

Components:
- Base: Roofing base - $6,000 (learned, 75% conf, 15 quotes)
- + Steep pitch modifier - $600 (learned, 50% conf, CONFLICTING)

Uncertainties:
- "Conflicting patterns" - Past quotes show both increases (+10%) and decreases (-5%) for steep pitch
  → Review this modifier carefully

Patterns:
- "Steep pitch +10%" (5× validated, 60% conf)
- "Steep pitch -5%" (3× validated, 40% conf) ⚠️ CONFLICT
```

### 9.6 Large Project Complexity

**Setup**: $18,000 quote, contractor's largest deck ever

**Expected Explanation**:
```
Summary: "Based on 30 deck quotes, but this is 2.5× larger than typical"

Components:
- Base: Deck base pricing (scaled) - $16,000 (learned, 70% conf)
- + Second story (+15%) - $2,400 (learned, 90% conf)

Uncertainties:
- "Large project complexity" - This is 2.5× larger than your typical deck quote ($7,000 avg)
  → Consider adding project management overhead (5-10%)
- "Material pricing" - Bulk material pricing may differ at this scale
  → Verify supplier quotes for accuracy
```

---

## 10. Success Metrics

### 10.1 Measurement Plan

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| **Trust** | ? | 80%+ | Post-quote survey: "I understand how this price was calculated" |
| **Correction speed** | ? | -30% | Time from quote view → correction submit |
| **Learning quality** | ? | +25% | % of corrections that reference explanation components |
| **Contractor satisfaction** | ? | 4.5/5 | "Explanation helps me validate AI pricing" (1-5 scale) |
| **Feature adoption** | 0% | 60%+ | % of users who expand explanation at least once |

### 10.2 A/B Test Plan

**Control Group**: No explanation (current state)
**Treatment Group**: Full explanation system

**Measured outcomes**:
1. Quote edit rate (expect lower with explanation)
2. Time to first correction (expect faster)
3. Contractor confidence scores (expect higher)
4. Quote acceptance without edit (expect higher)

**Success criteria**: Treatment group shows ≥15% improvement in at least 3 of 4 metrics

---

## 11. Implementation Phases

### Phase 1: Core Explanation (Week 1)
- [ ] Create `pricing_explanation.py` service
- [ ] Add database column + migration
- [ ] Implement basic explanation generation
- [ ] Test with 10 real quotes

### Phase 2: UI Integration (Week 2)
- [ ] Build QuoteExplanation component (XSS-safe)
- [ ] Add CSS styling
- [ ] Implement 3-level progressive disclosure
- [ ] Mobile responsive design

### Phase 3: Correction Flow (Week 3)
- [ ] Explanation-aware correction UI
- [ ] Component-level correction tracking
- [ ] Enhanced learning extraction
- [ ] Test correction accuracy improvement

### Phase 4: Polish & Optimization (Week 4)
- [ ] Template library
- [ ] Edge case handling
- [ ] Performance optimization
- [ ] User testing + iteration

---

## 12. Anthropic Showcase Alignment

### How This Exemplifies "Interpretable AI"

**1. Transparent Reasoning**
- Shows the chain of logic from patterns → price
- Exposes confidence levels at each step
- Surfaces uncertainties proactively

**2. Human-AI Collaboration**
- AI explains, human validates
- Contractor can correct specific components
- System learns from corrections

**3. Honest Uncertainty**
- "I don't have enough data for this" → explicit
- Confidence scores shown, not hidden
- Suggests what would improve accuracy

**4. Aligned Incentives**
- AI optimizes for contractor success (accurate pricing)
- Explanation helps contractor win more bids
- Learning loop creates mutual benefit

**5. Educational Value**
- Contractors learn their own patterns
- "You typically charge 15% for X" → self-awareness
- Builds pricing expertise over time

---

## 13. Future Enhancements

### Post-V1 Ideas

**1. Visual Confidence Heat Map**
```
Quote Total: $5,175
┌────────────────────────────┐
│ Base     ████████░░  85%   │
│ Modifier ████████░░  90%   │
│ Signal   ██████░░░░  70%   │
└────────────────────────────┘
Overall: 85%
```

**2. Explanation Comparison**
"Your last 3 similar quotes averaged $4,800. This one is 8% higher because..."

**3. Win Rate Correlation**
"Quotes with 85%+ confidence have 92% acceptance rate (vs 68% overall)"

**4. Natural Language Questions**
Contractor: "Why is this higher than my last deck?"
AI: "Second story access adds $675 (+15%). Your last deck was ground-level."

**5. PDF Explanation Section**
Include summary explanation in generated PDF quote for customer transparency

---

## Appendix: Example Explanation JSON

```json
{
  "summary": "Based on 47 previous deck quotes with second story access premium (validated 12×)",
  "overall_confidence": 0.85,
  "confidence_label": "High",

  "components": [
    {
      "type": "base_rate",
      "label": "Composite deck 20×15 ft",
      "amount": 4500.00,
      "source": "learned",
      "confidence": 0.85,
      "learning_ref": "category_deck_base",
      "validation_count": 47
    },
    {
      "type": "modifier",
      "label": "Second story access (+15%)",
      "amount": 675.00,
      "source": "learned",
      "confidence": 0.90,
      "learning_ref": "learning_def456",
      "pattern_id": "pattern_second_story",
      "validation_count": 12
    }
  ],

  "uncertainties": [
    {
      "area": "Deck size complexity",
      "reason": "Limited data for composite decks over 400 sqft (only 2 prior quotes)",
      "suggestion": "Consider adding 5-10% complexity factor for large projects"
    }
  ],

  "patterns_applied": [
    {
      "pattern": "Add 15% for second story access",
      "source_category": "deck",
      "times_validated": 12,
      "last_validated": "2025-12-20T10:30:00Z",
      "confidence": 0.90
    }
  ],

  "dna_transfers": [],

  "learning_context": {
    "category": "deck",
    "quote_count": 47,
    "correction_count": 23,
    "acceptance_rate": 0.68,
    "avg_adjustment": 0.04
  }
}
```

---

**END OF DESIGN**

*Ready for implementation. Estimated: 3-4 weeks for full system.*

**Security Note**: All DOM manipulation uses safe methods (`createElement`, `textContent`, `appendChild`) to prevent XSS attacks. No `innerHTML` used with user data.
