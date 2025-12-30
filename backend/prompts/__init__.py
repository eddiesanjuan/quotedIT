"""
Prompt templates for Quoted.
These are the core prompts that power quote generation and learning.
"""

from .quote_generation import (
    get_quote_generation_prompt,
    get_quote_refinement_prompt,
)
from .setup_interview import (
    get_setup_system_prompt,
    get_setup_initial_message,
    get_pricing_extraction_prompt,
)
from .demo_generation import (
    get_demo_quote_prompt,
    get_demo_industry_detection_prompt,
    get_demo_regenerate_prompt,
)

__all__ = [
    "get_quote_generation_prompt",
    "get_quote_refinement_prompt",
    "get_setup_system_prompt",
    "get_setup_initial_message",
    "get_pricing_extraction_prompt",
    "get_demo_quote_prompt",
    "get_demo_industry_detection_prompt",
    "get_demo_regenerate_prompt",
]
