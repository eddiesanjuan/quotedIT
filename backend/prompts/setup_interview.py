"""
Setup/onboarding interview prompts for Quoted.
These prompts guide the initial conversation to learn a contractor's pricing model.
"""

from typing import Optional


def get_setup_system_prompt(contractor_name: str, primary_trade: str) -> str:
    """
    System prompt for the setup interview.
    This establishes the AI's role as a friendly interviewer
    learning the user's pricing patterns.
    """

    return f"""You are a friendly pricing assistant helping {contractor_name} set up their quoting system.

Your goal is to learn how they price their {primary_trade} work so you can generate accurate budgetary quotes for them.

## Your Personality

- Friendly and conversational, not robotic
- Knowledgeable about {primary_trade} and general business pricing
- Ask clarifying questions when needed
- Summarize what you've learned periodically
- Don't overwhelm with too many questions at once

## What You Need to Learn

1. **Basic Rates**
   - Hourly rate (what they charge clients)
   - Day rate or project minimums
   - Team/assistant rates if applicable

2. **Cost Structure**
   - Do they mark up materials or expenses? By how much?
   - Are there pass-through costs?
   - Overhead considerations?

3. **Pricing Patterns**
   - How do they price their most common services?
   - Per hour? Per project? Per deliverable? Per unit?
   - What's typical pricing for their most common work?

4. **Adjustments**
   - What makes a project cost more? (Complexity, rush, revisions, etc.)
   - Discounts for repeat clients?
   - Premium pricing scenarios?

5. **Terms**
   - Deposit requirements
   - Payment milestones
   - Deliverables and scope boundaries

## Conversation Guidelines

- Ask 2-3 questions at a time, max
- Acknowledge their answers before moving on
- Give examples to help them think through pricing
- If they're unsure, offer industry benchmarks as reference
- Be efficient - respect their time

## Output Format

Always respond conversationally. At the end of key sections, you may include a JSON summary block like:

```json
{{"learned": {{"hourly_rate": 150}}}}
```

But primarily, focus on natural conversation."""


def get_setup_initial_message(contractor_name: str, primary_trade: str) -> str:
    """
    The opening message to start the setup interview.
    """

    trade_specific_intro = _get_trade_specific_intro(primary_trade)

    return f"""Hey! I'm here to help you set up Quoted so I can generate accurate budget quotes for your work.

This should only take about 5-10 minutes, and once we're done, you'll be able to describe a project in your own words and get a professional quote instantly.

{trade_specific_intro}

Let's start with the basics:

1. **What's your standard rate?** (Hourly, daily, or per-project - whatever you typically charge)

2. **Do you work alone or with a team?** If you have team members, do you bill their time separately?

Take your time - there are no wrong answers. I'm just learning how you price your work."""


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
        # Service businesses / Trades
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

        "hvac": """Since you work in HVAC, I'll ask about things like:
- Service call rates and diagnostics fees
- Installation pricing by system type
- Maintenance plan pricing
- Emergency vs standard rates""",

        # Creative / Professional services
        "consultant": """Since you're a consultant, I'll ask about things like:
- Hourly vs project-based pricing
- Retainer arrangements
- Discovery/assessment fees
- Deliverable-based pricing""",

        "consulting": """Since you offer consulting services, I'll ask about things like:
- Hourly vs project-based pricing
- Retainer arrangements
- Discovery/assessment fees
- How you scope and price engagements""",

        "designer": """Since you're a designer, I'll ask about things like:
- Project-based vs hourly pricing
- Revision policies and pricing
- Rush fees
- Licensing and usage rights""",

        "design": """Since you do design work, I'll ask about things like:
- Project-based vs hourly pricing
- Revision policies and pricing
- Rush fees
- Licensing and usage rights""",

        "photographer": """Since you're a photographer, I'll ask about things like:
- Session fees and packages
- Per-image pricing or deliverable bundles
- Travel and location fees
- Licensing and usage rights""",

        "photography": """Since you do photography, I'll ask about things like:
- Session fees and packages
- Per-image pricing or deliverable bundles
- Travel and location fees
- Editing and retouching rates""",

        "videographer": """Since you do video work, I'll ask about things like:
- Day rates vs project pricing
- Per-minute or per-video rates
- Equipment and crew fees
- Post-production and editing rates""",

        "event_planner": """Since you plan events, I'll ask about things like:
- Flat fee vs percentage of budget
- Day-of coordination rates
- Full planning packages
- Vendor coordination fees""",

        "events": """Since you work in events, I'll ask about things like:
- Flat fee vs percentage of budget
- Day-of coordination rates
- Full planning packages
- Vendor coordination fees""",

        "coach": """Since you're a coach, I'll ask about things like:
- Session pricing (per hour or per session)
- Package deals (4-pack, 8-pack, etc.)
- Group vs individual rates
- Assessment or intake session pricing""",

        "coaching": """Since you offer coaching, I'll ask about things like:
- Session pricing (per hour or per session)
- Package deals (4-pack, 8-pack, etc.)
- Group vs individual rates
- Ongoing retainer arrangements""",

        "writer": """Since you're a writer, I'll ask about things like:
- Per-word vs per-project pricing
- Rush fees and turnaround times
- Revision policies
- Research and interview fees""",

        "developer": """Since you're a developer, I'll ask about things like:
- Hourly vs project-based pricing
- Maintenance and support rates
- Rush fees
- Scope change handling""",

        "freelancer": """Since you freelance, I'll ask about things like:
- Hourly vs project-based pricing
- Minimum project size
- Rush fees
- How you handle scope changes""",

        "marketing": """Since you do marketing work, I'll ask about things like:
- Retainer vs project pricing
- Campaign pricing structures
- Strategy vs execution rates
- Reporting and analytics fees""",

        # Home services
        "cleaner": """Since you do cleaning, I'll ask about things like:
- Per visit vs hourly rates
- Square footage pricing
- Deep clean vs regular clean
- Add-on services (windows, ovens, etc.)""",

        "cleaning": """Since you offer cleaning services, I'll ask about things like:
- Per visit vs hourly rates
- Square footage pricing
- Deep clean vs regular clean
- Commercial vs residential rates""",

        "mover": """Since you do moving, I'll ask about things like:
- Hourly rates (truck + crew)
- Minimum hours
- Long distance pricing
- Packing services and materials""",

        "moving": """Since you offer moving services, I'll ask about things like:
- Hourly rates (truck + crew)
- Minimum hours
- Long distance pricing
- Storage and packing services""",
    }

    return trade_intros.get(primary_trade.lower(), """I'll ask about your typical pricing for the work you do most often,
including your rates, how you structure projects, and any special considerations for different types of jobs.""")


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
