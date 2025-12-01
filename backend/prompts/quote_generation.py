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
) -> str:
    """
    Generate the main quote generation prompt.

    This prompt takes:
    - The transcribed voice note from the contractor
    - Their pricing model (learned rates, knowledge)
    - Their terms and conditions

    And produces:
    - Structured quote with line items
    - Professional description
    - Timeline estimate
    """

    # Format pricing knowledge for the prompt
    pricing_knowledge_str = ""
    if pricing_model.get("pricing_knowledge"):
        pricing_knowledge_str = f"""
## Your Learned Pricing Knowledge

{_format_pricing_knowledge(pricing_model["pricing_knowledge"])}
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

    return f"""You are a quoting assistant for {contractor_name}, a professional contractor.

Your job is to take the contractor's voice notes about a job and produce a professional budgetary quote.

IMPORTANT: This is a BUDGETARY quote - a ballpark estimate to help the customer understand general pricing. It is NOT a detailed takeoff or binding contract. Make this clear in the quote.

## Voice Note Transcription

"{transcription}"

## Contractor's Pricing Information

Labor Rate: ${pricing_model.get('labor_rate_hourly', 65)}/hour
Helper Rate: ${pricing_model.get('helper_rate_hourly', 35)}/hour
Material Markup: {pricing_model.get('material_markup_percent', 20)}%
Minimum Job: ${pricing_model.get('minimum_job_amount', 500)}

{pricing_knowledge_str}

{pricing_notes or ""}

{job_types_str}

{terms_str}

## Your Task

Based on the voice note, generate a structured quote. Extract:

1. **Customer Info** (if mentioned): name, address, contact
2. **Job Description**: Clear, professional summary of the work
3. **Line Items**: Break down the quote into logical components
4. **Timeline**: Estimated days and crew size
5. **Total**: Sum of all line items

## Output Format

Respond with valid JSON in exactly this structure:

{{
    "customer_name": "string or null",
    "customer_address": "string or null",
    "customer_phone": "string or null",
    "job_type": "detected job type (e.g., composite_deck, fence_wood, paint_exterior)",
    "job_description": "Professional 2-3 sentence description of the work",
    "line_items": [
        {{
            "name": "Item name (e.g., Demolition, Framing, Decking)",
            "description": "Brief description of this line item",
            "amount": 0.00
        }}
    ],
    "subtotal": 0.00,
    "notes": "Any notes about assumptions or what's NOT included",
    "estimated_days": 0,
    "estimated_crew_size": 0,
    "confidence": "high/medium/low - how confident you are in this estimate",
    "questions": ["Any clarifying questions you'd ask the contractor"]
}}

## Important Guidelines

1. Use the contractor's actual pricing when available
2. If pricing isn't clear, use reasonable industry estimates and note low confidence
3. Round to whole dollars
4. Include demolition/removal only if mentioned
5. Include permit costs only if mentioned
6. Be conservative - it's better to estimate slightly high than low
7. Always include at least 2-3 questions if you had to make assumptions

Generate the quote now:"""


def get_quote_refinement_prompt(
    original_quote: dict,
    corrections: dict,
    contractor_notes: Optional[str] = None,
) -> str:
    """
    Generate a prompt to learn from quote corrections.

    When a contractor edits a generated quote, we use this to:
    1. Understand what was wrong
    2. Extract learnings for future quotes
    """

    return f"""A contractor has corrected a quote you generated. Learn from this correction.

## Original Quote Generated

Job Type: {original_quote.get('job_type')}
Job Description: {original_quote.get('job_description')}

Original Line Items:
{_format_line_items(original_quote.get('line_items', []))}

Original Total: ${original_quote.get('subtotal', 0):.2f}

## Contractor's Corrections

{_format_corrections(corrections)}

{f"Contractor's Notes: {contractor_notes}" if contractor_notes else ""}

## Your Task

Analyze this correction and extract learnings. Consider:

1. Was the pricing too high or too low overall?
2. Which specific line items were adjusted and by how much?
3. What does this tell us about the contractor's pricing patterns?
4. Are there any new pricing rules we should remember?

## Output Format

Respond with valid JSON:

{{
    "pricing_adjustments": [
        {{
            "item_type": "e.g., decking, labor, demolition",
            "original_value": 0.00,
            "corrected_value": 0.00,
            "percent_change": 0.0,
            "learning": "What we learned from this correction"
        }}
    ],
    "new_pricing_rules": [
        {{
            "rule": "Natural language rule to remember",
            "applies_to": "job_type or item_type this applies to",
            "confidence": "high/medium/low"
        }}
    ],
    "overall_tendency": "Does this contractor typically price higher or lower than our estimates?",
    "summary": "One paragraph summary of what we learned"
}}

Analyze the correction:"""


def _format_pricing_knowledge(pricing_knowledge: dict) -> str:
    """Format pricing knowledge dict into readable string."""
    lines = []
    for category, data in pricing_knowledge.items():
        if isinstance(data, dict):
            lines.append(f"**{category}**:")
            for key, value in data.items():
                lines.append(f"  - {key}: {value}")
        else:
            lines.append(f"- {category}: {data}")
    return "\n".join(lines) if lines else "No learned pricing knowledge yet."


def _format_job_types(job_types: list) -> str:
    """Format job types into readable string."""
    lines = []
    for jt in job_types:
        name = jt.get("display_name", jt.get("name", "Unknown"))
        count = jt.get("quote_count", 0)
        avg = jt.get("average_quote_amount", 0)
        lines.append(f"- {name}: {count} quotes, avg ${avg:.0f}")
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
