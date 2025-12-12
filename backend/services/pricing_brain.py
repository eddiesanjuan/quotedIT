"""
Pricing Brain service for Quoted.

Provides access to learned pricing knowledge per category,
including on-demand AI analysis using Claude Haiku for cost efficiency.

This is the "show your work" for the learning system - contractors can see
what the AI has learned and edit it directly.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

import anthropic

from ..config import settings


class PricingBrainService:
    """
    Service for managing and analyzing learned pricing knowledge.

    Uses Claude Haiku for on-demand analysis (~$0.001/analysis) to provide
    insights without breaking the bank.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        # Use Haiku for cost-efficient analysis
        self.haiku_model = "claude-3-haiku-20240307"

    def get_all_categories(
        self,
        pricing_knowledge: Dict[str, Any],
        quotes: List[Any],
    ) -> List[Dict[str, Any]]:
        """
        Get all categories with statistics.

        Args:
            pricing_knowledge: The pricing_knowledge dict from PricingModel
            quotes: List of Quote objects for this contractor

        Returns:
            List of category dicts with stats
        """
        categories = pricing_knowledge.get("categories", {})

        # Calculate stats from quotes for backward compatibility / fallback
        quote_counts_from_db = {}
        for quote in quotes:
            job_type = quote.job_type
            if job_type:
                quote_counts_from_db[job_type] = quote_counts_from_db.get(job_type, 0) + 1

        result = []
        for category_key, category_data in categories.items():
            # Use stored quote_count if available, otherwise fall back to dynamic count
            stored_count = category_data.get("quote_count", 0)
            db_count = quote_counts_from_db.get(category_key, 0)
            # Use max of stored and calculated to handle migration
            quotes_count = max(stored_count, db_count)

            learned_adjustments = category_data.get("learned_adjustments", [])
            result.append({
                "category": category_key,
                "display_name": category_data.get("display_name", category_key.replace("_", " ").title()),
                "quotes_count": quotes_count,
                "confidence": category_data.get("confidence", 0.5),
                "samples": category_data.get("samples", 0),
                "learned_adjustments_count": len(learned_adjustments),
                "learned_adjustments": learned_adjustments,  # Include for card preview
            })

        # Sort by quotes_count descending
        result.sort(key=lambda x: x["quotes_count"], reverse=True)

        return result

    def get_category_detail(
        self,
        pricing_knowledge: Dict[str, Any],
        category: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific category.

        Args:
            pricing_knowledge: The pricing_knowledge dict from PricingModel
            category: Category key (snake_case)

        Returns:
            Category detail dict or None if not found
        """
        categories = pricing_knowledge.get("categories", {})

        if category not in categories:
            return None

        category_data = categories[category]

        return {
            "category": category,
            "display_name": category_data.get("display_name", category.replace("_", " ").title()),
            "learned_adjustments": category_data.get("learned_adjustments", []),
            "samples": category_data.get("samples", 0),
            "confidence": category_data.get("confidence", 0.5),
            "correction_count": category_data.get("correction_count", 0),  # DISC-035
        }

    def get_confidence_label(
        self,
        correction_count: int,
        samples: int = 0,
    ) -> Dict[str, Any]:
        """
        Get confidence label and level for a category based on correction count.

        DISC-035: Learning System Trust Indicators
        With <10 corrections per user in beta, need to set realistic expectations.

        Args:
            correction_count: Number of corrections for this category
            samples: Total quotes generated (optional, for additional context)

        Returns:
            Dict with confidence_level and confidence_label
        """
        if correction_count >= 10:
            return {
                "confidence_level": "high",
                "confidence_label": f"High Confidence ({correction_count} corrections)",
                "description": "Well-calibrated from many corrections",
            }
        elif correction_count >= 5:
            return {
                "confidence_level": "good",
                "confidence_label": f"Good ({correction_count} corrections)",
                "description": "Learning from your patterns",
            }
        elif correction_count >= 2:
            return {
                "confidence_level": "medium",
                "confidence_label": f"Learning ({correction_count} corrections)",
                "description": "Still learning, review carefully",
            }
        else:
            return {
                "confidence_level": "low",
                "confidence_label": f"Limited Data ({correction_count} corrections)",
                "description": "Few corrections, AI is still learning",
            }

    async def analyze_category(
        self,
        category: str,
        category_data: Dict[str, Any],
        recent_quotes: List[Dict[str, Any]],
        contractor_name: str,
    ) -> Dict[str, Any]:
        """
        Use Claude Haiku to analyze a category and provide insights.

        This is an on-demand operation (~$0.001/call) that provides
        intelligent analysis of learned pricing patterns.

        Args:
            category: Category key
            category_data: The category data from pricing_knowledge
            recent_quotes: Recent quotes for this category (for context)
            contractor_name: Contractor's business name

        Returns:
            Analysis dict with insights
        """
        learned_adjustments = category_data.get("learned_adjustments", [])
        samples = category_data.get("samples", 0)
        confidence = category_data.get("confidence", 0.5)

        # Build context from recent quotes
        quote_context = ""
        if recent_quotes:
            quote_context = "\n\nRecent quotes in this category:\n"
            for i, quote in enumerate(recent_quotes[:5], 1):
                quote_context += f"{i}. ${quote.get('subtotal', 0):,.0f} - {quote.get('job_description', 'N/A')[:100]}\n"

        # Build prompt for Haiku
        prompt = f"""You are a pricing analyst for {contractor_name}, a contractor.

Analyze this category's learned pricing patterns and provide actionable insights.

## Category: {category_data.get('display_name', category)}

**Stats:**
- Quotes generated: {samples}
- Confidence level: {confidence:.1%}

**Learned Adjustments:**
{chr(10).join(f"- {adj}" for adj in learned_adjustments) if learned_adjustments else "- None yet"}

{quote_context}

## Your Task:

Provide a brief analysis (3-4 sentences) covering:
1. **Pattern summary**: What pricing patterns have emerged?
2. **Confidence assessment**: Is the data sufficient for reliable estimates?
3. **Actionable insight**: What should the contractor know or do?

Keep it practical and specific to THIS category. No generic advice.

Format as plain text, no JSON."""

        try:
            message = self.client.messages.create(
                model=self.haiku_model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )

            analysis_text = message.content[0].text.strip()

            return {
                "category": category,
                "analysis": analysis_text,
                "analyzed_at": datetime.utcnow().isoformat(),
                "model": self.haiku_model,
            }

        except Exception as e:
            return {
                "category": category,
                "analysis": f"Analysis failed: {str(e)}",
                "analyzed_at": datetime.utcnow().isoformat(),
                "error": True,
            }

    def update_category(
        self,
        pricing_knowledge: Dict[str, Any],
        category: str,
        display_name: Optional[str] = None,
        learned_adjustments: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Update a category's data.

        Args:
            pricing_knowledge: The pricing_knowledge dict from PricingModel
            category: Category key
            display_name: New display name (optional)
            learned_adjustments: New learned adjustments list (optional)

        Returns:
            Updated pricing_knowledge dict
        """
        categories = pricing_knowledge.get("categories", {})

        if category not in categories:
            raise ValueError(f"Category '{category}' not found")

        category_data = categories[category]

        # Update fields
        if display_name is not None:
            category_data["display_name"] = display_name

        if learned_adjustments is not None:
            category_data["learned_adjustments"] = learned_adjustments

        categories[category] = category_data
        pricing_knowledge["categories"] = categories

        return pricing_knowledge

    def delete_category(
        self,
        pricing_knowledge: Dict[str, Any],
        category: str,
    ) -> Dict[str, Any]:
        """
        Delete a category from pricing_knowledge.

        Args:
            pricing_knowledge: The pricing_knowledge dict from PricingModel
            category: Category key to delete

        Returns:
            Updated pricing_knowledge dict
        """
        categories = pricing_knowledge.get("categories", {})

        if category not in categories:
            raise ValueError(f"Category '{category}' not found")

        del categories[category]
        pricing_knowledge["categories"] = categories

        return pricing_knowledge

    def get_global_settings(
        self,
        pricing_model: Any,
    ) -> Dict[str, Any]:
        """
        Get global pricing settings (base rates, markup, minimum).

        Args:
            pricing_model: PricingModel instance

        Returns:
            Global settings dict
        """
        return {
            "labor_rate_hourly": pricing_model.labor_rate_hourly,
            "helper_rate_hourly": pricing_model.helper_rate_hourly,
            "material_markup_percent": pricing_model.material_markup_percent,
            "minimum_job_amount": pricing_model.minimum_job_amount,
            "pricing_notes": pricing_model.pricing_notes,
        }


# Singleton pattern
_pricing_brain_service: Optional[PricingBrainService] = None


def get_pricing_brain_service() -> PricingBrainService:
    """Get the pricing brain service singleton."""
    global _pricing_brain_service
    if _pricing_brain_service is None:
        _pricing_brain_service = PricingBrainService()
    return _pricing_brain_service
