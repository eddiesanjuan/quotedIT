"""
Quote generation prompts for Quoted.
These prompts synthesize voice transcriptions into structured quotes
using the contractor's learned pricing model.
"""

from typing import Optional, Dict, Any

from ..services.learning_relevance import select_relevant_learnings


def get_quote_generation_prompt(
    transcription: str,
    contractor_name: str,
    pricing_model: dict,
    pricing_notes: Optional[str] = None,
    job_types: Optional[list] = None,
    terms: Optional[dict] = None,
    correction_examples: Optional[list] = None,
    detected_category: Optional[str] = None,
    voice_signals: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate the main quote generation prompt.

    This prompt uses a THREE-LAYER ARCHITECTURE for pricing context:

    1. GLOBAL PRICING PHILOSOPHY (pricing_philosophy)
       The contractor's overall "pricing DNA" - their approach, rates, philosophy.
       Applied to ALL quotes regardless of category.

    2. CATEGORY-SPECIFIC TAILORED PROMPT (tailored_prompt)
       Deep understanding of how they price THIS specific type of work.
       Built from initial setup and refined through corrections.

    3. CATEGORY-SPECIFIC INJECTIONS (learned_adjustments)
       Specific learned corrections and rules for this category.
       The most granular layer - individual lessons from corrections.

    This layered approach allows the model to learn at multiple levels of abstraction.
    """

    pricing_knowledge = pricing_model.get("pricing_knowledge", {})

    # ============================================================
    # LAYER 1: GLOBAL PRICING PHILOSOPHY
    # ============================================================
    pricing_philosophy = pricing_model.get("pricing_philosophy", "")
    philosophy_str = ""
    if pricing_philosophy:
        philosophy_str = f"""
## 🧠 Your Pricing Philosophy (Apply to ALL quotes)

{pricing_philosophy}
"""

    # ============================================================
    # LAYER 2 & 3: CATEGORY-SPECIFIC CONTEXT
    # ============================================================
    category_context_str = ""

    if detected_category and "categories" in pricing_knowledge:
        categories = pricing_knowledge.get("categories", {})
        if detected_category in categories:
            cat_data = categories[detected_category]
            display_name = cat_data.get("display_name", detected_category.replace("_", " ").title())
            tailored_prompt = cat_data.get("tailored_prompt")
            learned_adjustments = cat_data.get("learned_adjustments", [])
            cat_confidence = cat_data.get("confidence", 0.5)
            correction_count = cat_data.get("correction_count", 0)

            # Layer 2: Category tailored prompt (deep understanding)
            tailored_str = ""
            if tailored_prompt:
                tailored_str = f"""
### Your Pricing Approach for {display_name}

{tailored_prompt}
"""

            # Layer 3: Specific learned adjustments (injections)
            adjustments_str = ""
            if learned_adjustments:
                # Intelligent relevance-based selection (Learning Excellence)
                # Replaces naive [-7:] with multi-dimensional scoring:
                # - Keyword Match (40%): Terms from current job
                # - Recency (30%): 30-day half-life decay
                # - Specificity (20%): Quality score from learning
                # - Foundational (10%): Universal rules bonus
                top_learnings = select_relevant_learnings(
                    learned_adjustments=learned_adjustments,
                    transcription=transcription,
                    category=detected_category,
                    max_learnings=7,
                )

                # Calculate learning pattern summary
                increase_pattern = sum(1 for adj in top_learnings if "increase" in adj.lower() or "higher" in adj.lower())
                decrease_pattern = sum(1 for adj in top_learnings if "reduce" in adj.lower() or "lower" in adj.lower())

                if increase_pattern > decrease_pattern:
                    tendency = "Conservative - you typically price HIGHER"
                elif decrease_pattern > increase_pattern:
                    tendency = "Aggressive - you typically price LOWER"
                else:
                    tendency = "Balanced - mixed adjustments"

                adjustments_compact = "\n".join(f"- {adj}" for adj in top_learnings)

                adjustments_str = f"""
### ⚠️ Learned Adjustments ({correction_count} corrections, {cat_confidence:.0%} confidence)

**Pattern**: {tendency}

**Apply These Rules**:
{adjustments_compact}
"""

            # Combine category layers if we have any content
            if tailored_str or adjustments_str:
                category_context_str = f"""
## 🎯 Category-Specific Context: "{display_name}"
{tailored_str}{adjustments_str}
IMPORTANT: Apply these category-specific learnings to match your actual pricing.
"""

    # ============================================================
    # LAYER 4: VOICE SIGNALS (Learning Excellence)
    # ============================================================
    # Extract pricing signals from the way the contractor spoke
    voice_signals_str = ""
    if voice_signals:
        signal_hints = []

        # Difficulty signal
        difficulty = voice_signals.get("difficulty_signal", {})
        if difficulty.get("detected") and difficulty.get("adjustment_hint"):
            signal_hints.append(f"- **Difficulty**: {difficulty.get('adjustment_hint')}")

        # Relationship signal
        relationship = voice_signals.get("relationship_signal", {})
        if relationship.get("detected") and relationship.get("adjustment_hint"):
            signal_hints.append(f"- **Relationship**: {relationship.get('adjustment_hint')}")

        # Timeline signal
        timeline = voice_signals.get("timeline_signal", {})
        if timeline.get("detected") and timeline.get("adjustment_hint"):
            signal_hints.append(f"- **Timeline**: {timeline.get('adjustment_hint')}")

        # Quality signal
        quality = voice_signals.get("quality_signal", {})
        if quality.get("detected") and quality.get("adjustment_hint"):
            signal_hints.append(f"- **Quality**: {quality.get('adjustment_hint')}")

        # Correction signal (most important - explicit pricing direction)
        correction = voice_signals.get("correction_signal", {})
        if correction.get("detected") and correction.get("adjustment_hint"):
            signal_hints.append(f"- **⚠️ Explicit Direction**: {correction.get('adjustment_hint')}")

        if signal_hints:
            voice_signals_str = f"""
## 🎤 Voice Signal Analysis (Learning Excellence)

The contractor's tone and word choice suggest these pricing adjustments:

{chr(10).join(signal_hints)}

Consider these signals when setting line item prices.
"""

    # Format pricing knowledge for the prompt
    pricing_knowledge_str = ""
    if pricing_knowledge:
        pricing_knowledge_str = f"""
## Your Learned Pricing Knowledge

{_format_pricing_knowledge(pricing_knowledge)}
"""

    # Add global rules if they exist
    global_rules = pricing_knowledge.get("global_rules", [])
    if global_rules:
        rules_list = "\n".join(f"- {rule}" for rule in global_rules)
        pricing_knowledge_str += f"""
## Global Pricing Rules (Apply to ALL quotes)

{rules_list}
"""

    # Format job types if available
    job_types_str = ""
    if job_types:
        job_types_str = f"""
## Job Types You've Quoted Before

{_format_job_types(job_types)}
"""

    # Format terms
    terms_str = ""
    if terms:
        terms_str = f"""
## Your Standard Terms

- Deposit: {terms.get('deposit_percent', 50)}% to schedule
- Quote valid for: {terms.get('quote_valid_days', 30)} days
- Labor warranty: {terms.get('labor_warranty_years', 2)} years
"""

    # Format correction examples (the learning context)
    corrections_str = ""
    if correction_examples:
        corrections_str = f"""
## IMPORTANT: Learned From Past Corrections

The contractor has corrected previous quotes. Learn from these examples:

{_format_correction_examples(correction_examples)}

Use these corrections to inform your pricing. If you see a pattern (e.g., contractor always increases demolition costs), apply that learning to this quote.
"""

    # Handle None values with 'or' to ensure defaults even when key exists but is None
    labor_rate = pricing_model.get('labor_rate_hourly') or 65
    helper_rate = pricing_model.get('helper_rate_hourly') or 35
    material_markup = pricing_model.get('material_markup_percent') or 20
    minimum_job = pricing_model.get('minimum_job_amount') or 500

    return f"""You are a quoting assistant for {contractor_name}, a professional contractor.

Your job is to take the contractor's voice notes about a job and produce a professional budgetary quote.

IMPORTANT: This is a BUDGETARY quote - a ballpark estimate to help the customer understand general pricing. It is NOT a detailed takeoff or binding contract. Make this clear in the quote.

## Voice Note Transcription

"{transcription}"
{philosophy_str}
{category_context_str}
{voice_signals_str}
## Contractor's Base Pricing Information

Labor Rate: ${labor_rate}/hour
Helper Rate: ${helper_rate}/hour
Material Markup: {material_markup}%
Minimum Job: ${minimum_job}

{pricing_knowledge_str}

{pricing_notes or ""}

{job_types_str}

{terms_str}

{corrections_str}

## Your Task

Based on the voice note, use the generate_quote tool to create a structured budgetary quote. Extract:

1. **Customer Info** (if mentioned): name, address, contact
2. **Job Description**: Clear, professional summary of the work
3. **Line Items**: Break down the quote into logical components
   - When quantities are mentioned (e.g., "two paintings", "three rooms"), extract them separately
   - Set quantity and unit price, not just total (e.g., Qty: 2 × $500 = $1,000)
4. **Timeline**: Estimated days and crew size
5. **Total**: Sum of all line items

## Important Guidelines

1. **Apply the layered pricing context above** - philosophy first, then category-specific rules
2. Use the contractor's actual pricing when available
3. If pricing isn't clear, use reasonable industry estimates and set confidence to "low"
4. Round all amounts to whole dollars
5. Include demolition/removal only if mentioned
6. Include permit costs only if mentioned
7. Be conservative - it's better to estimate slightly high than low
8. Always include at least 2-3 questions if you had to make assumptions
9. Set confidence based on how much information you have:
   - "high": Clear scope, contractor has pricing for this type of work
   - "medium": Some assumptions needed, but reasonable estimates possible
   - "low": Many unknowns, significant assumptions made

Use the generate_quote tool now:"""


def get_quote_refinement_prompt(
    original_quote: dict,
    corrections: dict,
    contractor_notes: Optional[str] = None,
    existing_learnings: Optional[list] = None,
    existing_tailored_prompt: Optional[str] = None,
    existing_philosophy: Optional[str] = None,
) -> str:
    """
    Generate a prompt to learn from quote corrections.

    This implements THREE-LAYER LEARNING:

    1. INJECTION LEARNINGS (learning_statements)
       Specific rules like "Demo minimum $1,500" or "Add 15% for difficult access"
       Updated on EVERY correction.

    2. TAILORED PROMPT UPDATE (tailored_prompt_update)
       Category-level understanding. Only update when correction reveals a
       fundamental misunderstanding of HOW they price this category.
       Updated RARELY - maybe 1 in 10 corrections.

    3. PHILOSOPHY UPDATE (philosophy_update)
       Global pricing DNA. Only update when correction reveals a fundamental
       change to their overall approach (e.g., "I'm now pricing premium").
       Updated VERY RARELY - maybe 1 in 50 corrections.

    Args:
        original_quote: The AI-generated quote
        corrections: What the contractor changed
        contractor_notes: Optional notes from the contractor
        existing_learnings: Current learning statements for this category
        existing_tailored_prompt: Current category-level tailored prompt
        existing_philosophy: Current global pricing philosophy
    """
    job_type = original_quote.get('job_type', 'unknown')

    # Format existing learnings for the prompt
    if existing_learnings and len(existing_learnings) > 0:
        existing_str = "\n".join(f"  {i+1}. \"{stmt}\"" for i, stmt in enumerate(existing_learnings))
        existing_section = f"""## Current Injection Learnings for "{job_type}"

You have {len(existing_learnings)} existing learning statement(s):

{existing_str}
"""
    else:
        existing_section = f"""## Current Injection Learnings for "{job_type}"

No existing learning statements yet - this is the first correction for this category.
"""

    # Format existing tailored prompt
    tailored_section = ""
    if existing_tailored_prompt:
        tailored_section = f"""## Current Category Tailored Prompt for "{job_type}"

"{existing_tailored_prompt}"

This describes the overall pricing approach for this category. Only suggest an update if this correction reveals a FUNDAMENTAL misunderstanding (not just a specific rule).
"""
    else:
        tailored_section = f"""## Current Category Tailored Prompt for "{job_type}"

None yet. If this correction reveals enough about how they price {job_type} jobs generally, you can suggest one.
"""

    # Format existing philosophy
    philosophy_section = ""
    if existing_philosophy:
        philosophy_section = f"""## Current Global Pricing Philosophy

"{existing_philosophy}"

This is their overall pricing DNA. Only suggest an update if this correction reveals a FUNDAMENTAL change to their business approach (very rare).
"""

    return f"""A contractor has corrected a quote you generated. Analyze this correction and determine what should be learned at each level.

## Original Quote Generated

Job Type: {job_type}
Job Description: {original_quote.get('job_description')}

Original Line Items:
{_format_line_items(original_quote.get('line_items', []))}

Original Total: ${original_quote.get('subtotal', 0):.2f}

## Contractor's Corrections

{_format_corrections(corrections)}

{f"Contractor's Notes: {contractor_notes}" if contractor_notes else ""}

{existing_section}

{tailored_section}

{philosophy_section}

## THREE-LAYER LEARNING SYSTEM

Determine what should be learned at each level:

### Level 1: Injection Learnings (ALWAYS update)
Specific rules to inject into future quotes. Examples:
- "Demo minimum $1,500 for deck projects"
- "Add 15% for difficult access"
- "Railing is $40/LF, not $35"

### Level 2: Tailored Prompt Update (SOMETIMES - ~10% of corrections)
Only update if this correction reveals a fundamental misunderstanding of HOW they price this category. NOT for specific numbers.

Signs you should update tailored_prompt:
- Multiple line items were wrong in the same direction
- The correction suggests a completely different pricing APPROACH
- Contractor notes indicate "I always price [category] this way..."

Signs you should NOT update:
- Just one line item was off
- The correction is about a specific number, not an approach
- This is an edge case, not the norm

### Level 3: Philosophy Update (RARELY - ~2% of corrections)
Only suggest if correction reveals a fundamental change to their BUSINESS:
- They've repositioned as premium/budget
- They've changed their overall markup strategy
- They explicitly say their general approach has changed

Almost all corrections should be Level 1 only.

## Output Format

Respond with valid JSON:

{{
    "learning_statements": [
        "Updated list of specific injection learnings for this category",
        "Keep existing ones that are still valid",
        "Update/add based on this correction"
    ],
    "changes_made": "Brief description of what changed in learning_statements",

    "tailored_prompt_update": null | "New tailored prompt text if Level 2 update needed",
    "tailored_prompt_reason": null | "Why you're suggesting this update (only if tailored_prompt_update is not null)",

    "philosophy_update": null | "New philosophy text if Level 3 update needed",
    "philosophy_reason": null | "Why you're suggesting this update (only if philosophy_update is not null)",

    "pricing_direction": "higher" | "lower" | "mixed",
    "confidence": "high" | "medium" | "low",
    "summary": "One sentence summary of the key insight from this correction"
}}

IMPORTANT: Most corrections should have tailored_prompt_update: null and philosophy_update: null. Only suggest updates when truly warranted.

Keep learning_statements concise (5-10 max). Quality over quantity:"""


def _format_pricing_knowledge(pricing_knowledge: dict) -> str:
    """Format pricing knowledge dict into readable string."""
    lines = []

    # Handle new categories structure
    if "categories" in pricing_knowledge:
        categories = pricing_knowledge.get("categories", {})
        if categories:
            lines.append("**Your Pricing Categories:**\n")
            for cat_name, cat_data in categories.items():
                if isinstance(cat_data, dict):
                    display_name = cat_data.get("display_name") or cat_name.replace("_", " ").title()
                    price_range = cat_data.get("typical_price_range") or []
                    pricing_unit = cat_data.get("pricing_unit") or ""
                    base_rate = cat_data.get("base_rate") or 0
                    notes = cat_data.get("notes") or ""
                    confidence = cat_data.get("confidence") or 0.5
                    samples = cat_data.get("samples") or 0

                    line = f"  **{display_name}**"
                    # Ensure price_range values are numeric before formatting
                    if price_range and len(price_range) == 2 and price_range[0] is not None and price_range[1] is not None:
                        try:
                            line += f" - Range: ${float(price_range[0]):,.0f}-${float(price_range[1]):,.0f}"
                        except (ValueError, TypeError):
                            pass
                    if base_rate:
                        try:
                            line += f" (Base: ${float(base_rate):,.0f})"
                        except (ValueError, TypeError):
                            pass
                    if pricing_unit:
                        line += f" [{pricing_unit}]"
                    lines.append(line)

                    if notes:
                        lines.append(f"    Notes: {notes}")
                    if samples and samples > 0:
                        try:
                            lines.append(f"    (Confidence: {float(confidence):.0%} from {samples} quotes)")
                        except (ValueError, TypeError):
                            lines.append(f"    ({samples} quotes)")
                    lines.append("")

    # Handle legacy flat structure for backward compatibility
    for key, data in pricing_knowledge.items():
        if key in ["categories", "global_rules"]:
            continue  # Already handled or handled separately

        if isinstance(data, dict):
            lines.append(f"**{key}**:")
            for k, v in data.items():
                if k not in ["learned_adjustments"]:  # Don't duplicate adjustments
                    lines.append(f"  - {k}: {v}")
        else:
            lines.append(f"- {key}: {data}")

    return "\n".join(lines) if lines else "No learned pricing knowledge yet."


def _format_job_types(job_types: list) -> str:
    """Format job types into readable string."""
    lines = []
    for jt in job_types:
        name = jt.get("display_name") or jt.get("name") or "Unknown"
        count = jt.get("quote_count") or 0
        avg = jt.get("average_quote_amount") or 0
        try:
            lines.append(f"- {name}: {count} quotes, avg ${float(avg):.0f}")
        except (ValueError, TypeError):
            lines.append(f"- {name}: {count} quotes")
    return "\n".join(lines) if lines else "No previous job types."


def _format_line_items(line_items: list) -> str:
    """Format line items for display."""
    lines = []
    for item in line_items:
        name = item.get("name", "Item")
        amount = item.get("amount", 0)
        lines.append(f"- {name}: ${amount:.2f}")
    return "\n".join(lines) if lines else "No line items."


def _format_corrections(corrections: dict) -> str:
    """Format corrections for the prompt."""
    lines = []

    if "total_change" in corrections:
        lines.append(f"Total changed by: ${corrections['total_change']:.2f} ({corrections.get('total_change_percent', 0):.1f}%)")

    if "line_item_changes" in corrections:
        lines.append("\nLine Item Changes:")
        for change in corrections["line_item_changes"]:
            item = change.get("item", "Unknown")
            orig = change.get("original", 0)
            final = change.get("final", 0)
            reason = change.get("reason", "")
            lines.append(f"- {item}: ${orig:.2f} → ${final:.2f} ({reason})")

    if "learning_note" in corrections:
        lines.append(f"\nContractor Note: {corrections['learning_note']}")

    return "\n".join(lines) if lines else "No specific corrections noted."


def _format_correction_examples(examples: list) -> str:
    """
    Format correction examples for injection into the prompt.

    This is the core of the learning system - showing Claude real examples
    of what the contractor changed so it can learn patterns.
    """
    if not examples:
        return "No corrections yet - this is a new contractor."

    formatted = []
    for i, ex in enumerate(examples[:5], 1):  # Max 5 examples
        job_type = ex.get("job_type", "Unknown job")

        # Format line item changes
        changes = []
        original_items = ex.get("original_line_items", [])
        final_items = ex.get("final_line_items", [])

        # Build a map of items for comparison
        orig_map = {item.get("name", ""): item.get("amount", 0) for item in original_items}
        final_map = {item.get("name", ""): item.get("amount", 0) for item in final_items}

        # Find changes
        all_items = set(orig_map.keys()) | set(final_map.keys())
        for item_name in all_items:
            orig_amt = orig_map.get(item_name, 0)
            final_amt = final_map.get(item_name, 0)
            if orig_amt != final_amt:
                if orig_amt == 0:
                    changes.append(f"  + Added '{item_name}': ${final_amt:.0f}")
                elif final_amt == 0:
                    changes.append(f"  - Removed '{item_name}' (was ${orig_amt:.0f})")
                else:
                    diff = final_amt - orig_amt
                    pct = (diff / orig_amt * 100) if orig_amt else 0
                    direction = "↑" if diff > 0 else "↓"
                    changes.append(f"  {direction} '{item_name}': ${orig_amt:.0f} → ${final_amt:.0f} ({pct:+.0f}%)")

        # Total change
        orig_total = ex.get("original_total", 0)
        final_total = ex.get("final_total", 0)
        total_diff = final_total - orig_total
        total_pct = (total_diff / orig_total * 100) if orig_total else 0

        # Contractor notes
        notes = ex.get("correction_notes", "")

        example_str = f"""**Example {i}: {job_type}**
- AI quoted: ${orig_total:.0f} → Contractor set: ${final_total:.0f} ({total_pct:+.0f}%)
{chr(10).join(changes) if changes else "- Minor adjustments only"}
{f'- Contractor note: "{notes}"' if notes else ""}"""

        formatted.append(example_str)

    return "\n\n".join(formatted)
