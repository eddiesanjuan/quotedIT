"""
Quote generation prompts for Quoted.
These prompts synthesize voice transcriptions into structured quotes
using the contractor's learned pricing model.
"""

from typing import Optional


def get_quote_generation_prompt(
    transcription: str,
    contractor_name: str,
    pricing_model: dict,
    pricing_notes: Optional[str] = None,
    job_types: Optional[list] = None,
    terms: Optional[dict] = None,
    correction_examples: Optional[list] = None,
    detected_category: Optional[str] = None,
) -> str:
    """
    Generate the main quote generation prompt.

    This prompt takes:
    - The transcribed voice note from the contractor
    - Their pricing model (learned rates, knowledge)
    - Their terms and conditions
    - The detected category for this quote

    And produces:
    - Structured quote with line items
    - Professional description
    - Timeline estimate
    """

    # Extract category-specific learnings (THE KEY LEARNING INJECTION)
    # DISC-052: Hybrid format + priority selection for token efficiency
    category_learnings_str = ""
    pricing_knowledge = pricing_model.get("pricing_knowledge", {})

    if detected_category and "categories" in pricing_knowledge:
        categories = pricing_knowledge.get("categories", {})
        if detected_category in categories:
            cat_data = categories[detected_category]
            learned_adjustments = cat_data.get("learned_adjustments", [])
            cat_confidence = cat_data.get("confidence", 0.5)
            cat_samples = cat_data.get("samples", 0)
            correction_count = cat_data.get("correction_count", 0)

            if learned_adjustments:
                # DISC-052: Priority selection - inject only top 7 most recent learnings
                # Most recent corrections are most relevant (recency bias)
                # Token budget: ~240 tokens for learnings (60% reduction from ~720)
                top_learnings = learned_adjustments[-7:]  # Last 7 are most recent

                # DISC-052: Hybrid format - structured data + natural language summary
                # Calculate learning pattern summary
                increase_pattern = sum(1 for adj in top_learnings if "increase" in adj.lower() or "higher" in adj.lower())
                decrease_pattern = sum(1 for adj in top_learnings if "reduce" in adj.lower() or "lower" in adj.lower())

                if increase_pattern > decrease_pattern:
                    tendency = "Conservative pricing - you typically price HIGHER than industry averages"
                elif decrease_pattern > increase_pattern:
                    tendency = "Aggressive pricing - you typically price LOWER to win jobs"
                else:
                    tendency = "Balanced pricing - mixed adjustments based on job specifics"

                # Format learnings in compact hybrid format
                adjustments_compact = "\n".join(f"- {adj}" for adj in top_learnings)

                category_learnings_str = f"""
## ⚠️ CRITICAL: Your Learned Pricing Pattern for "{cat_data.get('display_name', detected_category)}"

**Pattern Summary** ({correction_count} corrections, {cat_confidence:.0%} confidence):
{tendency}

**Top Adjustments to Apply**:
{adjustments_compact}

IMPORTANT: Apply these learned adjustments to match your actual pricing style.
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
{category_learnings_str}

## Contractor's Pricing Information

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
4. **Timeline**: Estimated days and crew size
5. **Total**: Sum of all line items

## Important Guidelines

1. Use the contractor's actual pricing when available
2. If pricing isn't clear, use reasonable industry estimates and set confidence to "low"
3. Round all amounts to whole dollars
4. Include demolition/removal only if mentioned
5. Include permit costs only if mentioned
6. Be conservative - it's better to estimate slightly high than low
7. Always include at least 2-3 questions if you had to make assumptions
8. Set confidence based on how much information you have:
   - "high": Clear scope, contractor has pricing for this type of work
   - "medium": Some assumptions needed, but reasonable estimates possible
   - "low": Many unknowns, significant assumptions made

Use the generate_quote tool now:"""


def get_quote_refinement_prompt(
    original_quote: dict,
    corrections: dict,
    contractor_notes: Optional[str] = None,
) -> str:
    """
    Generate a prompt to learn from quote corrections.

    When a contractor edits a generated quote, we use this to:
    1. Understand what was wrong
    2. Extract learning STATEMENTS that will be injected into future prompts

    CRITICAL: The learning_statements output will be directly injected into
    future quote generation prompts. Write them as instructions to yourself.
    """
    job_type = original_quote.get('job_type', 'unknown')

    return f"""A contractor has corrected a quote you generated. Your job is to extract LEARNING STATEMENTS that will help you generate more accurate quotes in the future.

## Original Quote Generated

Job Type: {job_type}
Job Description: {original_quote.get('job_description')}

Original Line Items:
{_format_line_items(original_quote.get('line_items', []))}

Original Total: ${original_quote.get('subtotal', 0):.2f}

## Contractor's Corrections

{_format_corrections(corrections)}

{f"Contractor's Notes: {contractor_notes}" if contractor_notes else ""}

## Your Task

Generate LEARNING STATEMENTS that will be injected into future quote prompts for "{job_type}" jobs. These statements should be:

1. **Self-contained**: Include all context needed to understand and apply the learning
2. **Specific**: Reference actual dollar amounts, percentages, or conditions when possible
3. **Actionable**: Written as instructions to yourself for future quotes
4. **Contextual**: Include the WHY when you can infer it (job conditions, customer type, etc.)

### Good Learning Statement Examples:
- "For demolition on deck projects, charge $1,200 minimum - the $1,000 estimate was consistently too low"
- "When the job involves difficult access (steep yard, narrow gates), add 15% to labor costs"
- "This contractor prices labor at $75/hour, not $65 - always use their rate, not industry average"
- "Composite decking materials should be estimated at $14/sqft, not $12 - they use premium Trex"

### Bad Learning Statement Examples:
- "Increase demolition" (too vague - by how much? under what conditions?)
- "Price higher" (not actionable - which items? by what percentage?)
- "Labor was wrong" (no guidance on what the correct approach is)

## Output Format

Respond with valid JSON:

{{
    "learning_statements": [
        "First learning statement - specific, actionable instruction for future quotes",
        "Second learning statement - include context and reasoning",
        "Third learning statement (if applicable)"
    ],
    "pricing_direction": "higher" | "lower" | "mixed",
    "confidence": "high" | "medium" | "low",
    "summary": "One sentence summary of the key insight from this correction"
}}

Generate 1-3 learning statements (more is not better - only include distinct, valuable learnings):"""


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
