"""
Data package for Quoted backend.

Contains static data like pricing templates for different industries.
"""

from .pricing_templates import PRICING_TEMPLATES, get_template, list_all_templates

__all__ = ['PRICING_TEMPLATES', 'get_template', 'list_all_templates']
