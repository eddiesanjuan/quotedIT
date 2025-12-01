"""
Setup/onboarding interview prompts for Quoted.
These prompts guide the initial conversation to learn a contractor's pricing model.
"""

from typing import Optional


def get_setup_system_prompt(contractor_name: str, primary_trade: str) -> str:
    """
    System prompt for the setup interview.
    This establishes the AI's role as a friendly interviewer
    learning the contractor's pricing patterns.
    """

    return f"""You are a friendly pricing assistant helping {contractor_name} set up their quoting system.

Your goal is to learn how they price their {primary_trade} jobs so you can generate accurate budgetary quotes for them.

## Your Personality

- Friendly and conversational, not robotic
- Knowledgeable about the {primary_trade} trade
- Ask clarifying questions when needed
- Summarize what you've learned periodically
- Don't overwhelm with too many questions at once

## What You Need to Learn

1. **Basic Rates**
   - Hourly labor rate (what they charge, not what they pay)
   - Helper/crew rates
   - Daily rates if they use them
   - Minimum job size

2. **Material Handling**
   - Do they mark up materials? By how much?
   - Do they include materials in labor rates?
   - Preferred suppliers/brands?

3. **Job Pricing Patterns**
   - How do they price common job types?
   - Per square foot? Per linear foot? Flat rates?
   - What's typical pricing for their most common jobs?

4. **Adjustments**
   - What makes a job cost more? (Difficulty, access, height, etc.)
   - Discounts for repeat customers?
   - Seasonal adjustments?

5. **Terms**
   - Deposit requirements
   - Payment methods accepted
   - Warranty offered

## Conversation Guidelines

- Ask 2-3 questions at a time, max
- Acknowledge their answers before moving on
- Give examples to help them think through pricing
- If they're unsure, offer industry benchmarks as reference
- Be efficient - respect their time

## Output Format

Always respond conversationally. At the end of key sections, you may include a JSON summary block like:

```json
{{"learned": {{"labor_rate_hourly": 75}}}}
```

But primarily, focus on natural conversation."""


def get_setup_initial_message(contractor_name: str, primary_trade: str) -> str:
    """
    The opening message to start the setup interview.
    """

    trade_specific_intro = _get_trade_specific_intro(primary_trade)

    return f"""Hey! I'm here to help you set up Quoted so I can generate accurate budgetary quotes for your jobs.

This should only take about 5-10 minutes, and once we're done, you'll be able to describe a job in your own words and get a professional quote instantly.

{trade_specific_intro}

Let's start with the basics:

1. **What's your standard hourly labor rate?** (What you charge customers, not what you pay yourself)

2. **Do you typically work alone, or do you have helpers/crew?** If you have help, what do you charge for their time?

Take your time - there are no wrong answers. I'm just learning how you run your business."""


def get_pricing_extraction_prompt(conversation_messages: list) -> str:
    """
    Prompt to extract structured pricing data from the setup conversation.
    Called after the conversation is complete to build the pricing model.
    """

    # Format the conversation
    conversation_text = "\n".join([
        f"{'Assistant' if msg.get('role') == 'assistant' else 'Contractor'}: {msg.get('content', '')}"
        for msg in conversation_messages
    ])

    return f"""You just completed a setup interview with a contractor to learn their pricing.
Extract all the pricing information into a structured format.

## The Conversation

{conversation_text}

## Your Task

Extract everything you learned into a structured pricing model. Be thorough - capture every pricing detail mentioned.

## Output Format

Respond with valid JSON:

{{
    "labor_rate_hourly": null,
    "helper_rate_hourly": null,
    "labor_rate_daily": null,
    "material_markup_percent": null,
    "minimum_job_amount": null,

    "pricing_knowledge": {{
        "example_category": {{
            "base_rate": 0,
            "unit": "sqft or linear_ft or each or flat",
            "notes": "Any specifics mentioned"
        }}
    }},

    "pricing_notes": "Free-form notes about their pricing style, preferences, special cases",

    "terms": {{
        "deposit_percent": null,
        "deposit_description": null,
        "final_payment_terms": null,
        "accepted_payment_methods": [],
        "credit_card_fee_percent": null,
        "quote_valid_days": null,
        "labor_warranty_years": null,
        "custom_terms": null
    }},

    "job_types": [
        {{
            "name": "internal_name",
            "display_name": "Display Name",
            "pricing_pattern": {{
                "unit": "sqft",
                "base_rate": 0,
                "typical_range": [0, 0],
                "notes": ""
            }}
        }}
    ],

    "confidence_summary": "How confident are you in this extracted pricing model? What's missing?",

    "follow_up_questions": ["Questions to ask later to improve accuracy"]
}}

Extract the pricing model:"""


def _get_trade_specific_intro(primary_trade: str) -> str:
    """Get trade-specific introduction and example questions."""

    trade_intros = {
        "deck_builder": """Since you build decks, I'll ask about things like:
- Per square foot pricing for different materials (composite, wood, etc.)
- Railing pricing (per linear foot?)
- Demolition/removal rates
- Stairs and special features""",

        "fence_installer": """Since you install fences, I'll ask about things like:
- Per linear foot pricing for different fence types
- Post and gate pricing
- Removal/demolition rates
- Grade adjustments for slopes""",

        "painter": """Since you're a painter, I'll ask about things like:
- Per square foot rates for different surfaces
- Interior vs exterior pricing
- Prep work rates
- Cabinet and trim pricing""",

        "landscaper": """Since you do landscaping, I'll ask about things like:
- Design vs installation rates
- Plant and material markup
- Hardscape pricing
- Maintenance vs one-time project pricing""",

        "general_contractor": """Since you're a general contractor, I'll ask about things like:
- How you price different types of jobs
- Subcontractor markup
- Project management fees
- Your most common project types""",

        "handyman": """Since you're a handyman, I'll ask about things like:
- Hourly vs flat rate preferences
- Minimum service call
- How you price different types of repairs
- Material handling""",

        "roofer": """Since you do roofing, I'll ask about things like:
- Per square pricing for different materials
- Tear-off and disposal rates
- Flashing and detail pricing
- Emergency/repair rates vs full replacement""",

        "electrician": """Since you're an electrician, I'll ask about things like:
- Service call minimums
- Hourly rates for different work types
- Panel upgrade flat rates
- Rough-in vs finish pricing""",

        "plumber": """Since you're a plumber, I'll ask about things like:
- Service call rates
- Common repair flat rates
- Rough-in vs finish pricing
- Emergency rates""",
    }

    return trade_intros.get(primary_trade, """I'll ask about your typical pricing for the jobs you do most often,
including labor rates, material handling, and any special considerations.""")


def get_setup_continue_prompt(
    conversation_so_far: list,
    extracted_so_far: dict,
    areas_to_cover: list,
) -> str:
    """
    Prompt to continue the setup conversation, focusing on uncovered areas.
    Used when the conversation needs to continue to get more information.
    """

    covered = [k for k, v in extracted_so_far.items() if v is not None]
    uncovered = [area for area in areas_to_cover if area not in covered]

    return f"""You're continuing a setup interview with a contractor.

## What We've Learned So Far

{_format_extracted(extracted_so_far)}

## Areas Still to Cover

{', '.join(uncovered) if uncovered else 'All major areas covered!'}

## Recent Conversation

{_format_recent_messages(conversation_so_far[-4:])}

## Your Task

Continue the conversation naturally. If all major areas are covered, summarize what you've learned and ask if there's anything else they want you to know about their pricing.

If areas are still uncovered, ask about 1-2 of them in a natural way.

Remember: Be conversational, not robotic. Acknowledge what they've told you."""


def _format_extracted(extracted: dict) -> str:
    """Format extracted pricing for display."""
    lines = []
    for key, value in extracted.items():
        if value is not None:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines) if lines else "Nothing extracted yet."


def _format_recent_messages(messages: list) -> str:
    """Format recent messages for display."""
    lines = []
    for msg in messages:
        role = "You" if msg.get("role") == "assistant" else "Contractor"
        content = msg.get("content", "")[:200]
        lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "No messages yet."
