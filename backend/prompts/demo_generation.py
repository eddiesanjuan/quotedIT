"""
Demo quote generation prompt for Quoted.
This prompt enables generating quotes for ANY industry without prior setup.

The key difference from regular quote generation:
- No contractor-specific pricing model
- Uses Claude's world knowledge for reasonable industry estimates
- Designed to showcase what Quoted can do for ANY profession
- Includes disclaimers about learning system benefits
"""


def get_demo_quote_prompt(transcription: str) -> str:
    """
    Generate a universal demo quote prompt that works for ANY industry.

    This prompt:
    1. Detects the industry/profession from the voice command
    2. Uses reasonable industry-standard pricing from Claude's knowledge
    3. Creates a professional quote that showcases Quoted's capabilities
    4. Works for contractors, designers, consultants, event planners, etc.

    Args:
        transcription: The transcribed voice note describing the job

    Returns:
        The prompt string for Claude
    """
    return f"""You are a universal pricing assistant for DEMO mode. Your job is to create professional quotes for ANY type of work based on a voice description.

## Voice Note Transcription

"{transcription}"

## Your Task

Analyze this description and:

1. **DETECT THE INDUSTRY/PROFESSION** - What type of professional would do this work?
   - Contractors (plumbers, electricians, roofers, handymen, etc.)
   - Creative professionals (designers, photographers, videographers, etc.)
   - Consultants (business, marketing, tech, etc.)
   - Event professionals (planners, caterers, DJs, etc.)
   - Freelancers (writers, developers, virtual assistants, etc.)
   - Service providers (cleaners, landscapers, tutors, etc.)
   - Any other profession that provides custom quotes

2. **USE REASONABLE INDUSTRY-STANDARD PRICING**
   - Apply your knowledge of typical rates for this type of work
   - Consider the scope, complexity, and typical market rates
   - When in doubt, use mid-range professional rates
   - This is a ballpark estimate to demonstrate capability

3. **CREATE A PROFESSIONAL QUOTE**
   - Extract customer info if mentioned (name, address, phone)
   - Write a clear, professional job description
   - Break down into logical line items with quantities where applicable
   - Provide realistic timeline estimates
   - Set appropriate confidence level

## Pricing Guidelines by Category

Use these as rough guidelines (adjust based on specifics):

**Construction/Trade Work**:
- Labor: $50-150/hour depending on trade and complexity
- Materials: 15-25% markup typical
- Minimum job: $150-500 depending on trade

**Creative/Design Work**:
- Hourly: $75-200/hour for experienced professionals
- Project-based: Common for logos ($500-5000), websites ($2000-20000)
- Consider deliverables, revisions, and usage rights

**Consulting/Professional Services**:
- Hourly: $100-500/hour depending on expertise
- Day rates: $800-4000 for senior consultants
- Project fees: Scope-dependent

**Event Services**:
- Hourly: $50-200/hour
- Per-event: Varies widely by type and scale
- Consider setup/breakdown time

**General Freelance/Services**:
- Hourly: $25-150/hour depending on skill level
- Per-deliverable pricing when appropriate

## Important Notes

- This is DEMO mode without personalized pricing - estimates are based on industry standards
- Set confidence to "medium" for most estimates (you're using general knowledge, not user data)
- Always include helpful questions about scope to show the system's intelligence
- Round all amounts to whole dollars
- Be helpful and professional in the job description

## Output Format

Use the generate_quote tool with:
- job_type: A snake_case category (e.g., "website_design", "plumbing_repair", "event_photography")
- job_description: Professional 2-3 sentence summary
- line_items: Logical breakdown with name, description, amount, quantity, unit
- subtotal: Sum of line items
- estimated_days: When applicable
- estimated_crew_size: When applicable
- confidence: Usually "medium" for demo (no personalized data)
- questions: 2-4 clarifying questions showing system intelligence

Use the generate_quote tool now:"""


def get_demo_industry_detection_prompt(transcription: str) -> str:
    """
    Quick prompt to detect the industry/profession from a voice note.
    Uses a smaller/faster model for efficiency.

    Returns JSON with detected industry info.
    """
    return f"""Analyze this job description and identify the industry/profession.

Description: "{transcription}"

Return JSON only:
{{
    "industry": "Primary industry category",
    "profession": "Specific profession that would do this work",
    "job_type": "snake_case job type",
    "display_name": "Human Readable Job Type",
    "typical_rate_type": "hourly|project|per_unit",
    "estimated_complexity": "low|medium|high"
}}

Be specific but concise. Examples:
- "I need someone to redesign my logo" → industry: "creative", profession: "graphic_designer", job_type: "logo_design"
- "My toilet is leaking" → industry: "construction", profession: "plumber", job_type: "plumbing_repair"
- "Planning a wedding for 100 guests" → industry: "events", profession: "event_planner", job_type: "wedding_planning"
"""
