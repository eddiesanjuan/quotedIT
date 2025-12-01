"""
Learning service for Quoted.
Processes quote corrections and updates the contractor's pricing model.

This is the feedback loop that makes Quoted smarter over time:
1. Contractor edits a generated quote
2. We analyze what changed
3. We update the pricing model with learned adjustments
4. Future quotes are more accurate

The moat: After 50+ quotes, the system knows YOUR pricing deeply.
"""

import json
import re
from typing import Optional
from datetime import datetime

import anthropic

from ..config import settings
from ..prompts import get_quote_refinement_prompt


class LearningService:
    """
    Processes quote corrections to improve the pricing model.
    The core of Quoted's learning and personalization.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model

    async def process_correction(
        self,
        original_quote: dict,
        final_quote: dict,
        contractor_notes: Optional[str] = None,
    ) -> dict:
        """
        Process a quote correction and extract learnings.

        Args:
            original_quote: The AI-generated quote
            final_quote: The contractor-edited final quote
            contractor_notes: Any notes the contractor added about the correction

        Returns:
            dict with:
            - corrections: What changed
            - learnings: What to update in the pricing model
            - confidence: How confident we are in the learnings
        """
        # Calculate what changed
        corrections = self._calculate_corrections(original_quote, final_quote)

        if not corrections.get("has_changes"):
            return {
                "has_changes": False,
                "message": "No changes detected",
            }

        # Use Claude to analyze the corrections and extract learnings
        prompt = get_quote_refinement_prompt(
            original_quote=original_quote,
            corrections=corrections,
            contractor_notes=contractor_notes,
        )

        response = await self._call_claude(prompt)
        learnings = self._parse_learning_response(response)

        return {
            "has_changes": True,
            "corrections": corrections,
            "learnings": learnings,
            "processed_at": datetime.utcnow().isoformat(),
        }

    def _calculate_corrections(
        self,
        original: dict,
        final: dict,
    ) -> dict:
        """
        Calculate the detailed differences between original and final quote.
        """
        corrections = {
            "has_changes": False,
            "total_change": 0,
            "total_change_percent": 0,
            "line_item_changes": [],
        }

        # Calculate total change
        original_total = original.get("subtotal", 0)
        final_total = final.get("subtotal", 0)

        if original_total != final_total:
            corrections["has_changes"] = True
            corrections["total_change"] = final_total - original_total
            if original_total > 0:
                corrections["total_change_percent"] = (
                    (final_total - original_total) / original_total * 100
                )

        # Compare line items
        original_items = {
            item.get("name"): item for item in original.get("line_items", [])
        }
        final_items = {
            item.get("name"): item for item in final.get("line_items", [])
        }

        # Check for changes in existing items
        for name, orig_item in original_items.items():
            if name in final_items:
                final_item = final_items[name]
                orig_amount = orig_item.get("amount", 0)
                final_amount = final_item.get("amount", 0)

                if orig_amount != final_amount:
                    corrections["has_changes"] = True
                    corrections["line_item_changes"].append({
                        "item": name,
                        "original": orig_amount,
                        "final": final_amount,
                        "change": final_amount - orig_amount,
                        "change_type": "modified",
                    })
            else:
                # Item was removed
                corrections["has_changes"] = True
                corrections["line_item_changes"].append({
                    "item": name,
                    "original": orig_item.get("amount", 0),
                    "final": 0,
                    "change": -orig_item.get("amount", 0),
                    "change_type": "removed",
                })

        # Check for new items
        for name, final_item in final_items.items():
            if name not in original_items:
                corrections["has_changes"] = True
                corrections["line_item_changes"].append({
                    "item": name,
                    "original": 0,
                    "final": final_item.get("amount", 0),
                    "change": final_item.get("amount", 0),
                    "change_type": "added",
                })

        # Check for description changes
        if original.get("job_description") != final.get("job_description"):
            corrections["description_changed"] = True

        # Check for timeline changes
        if original.get("estimated_days") != final.get("estimated_days"):
            corrections["timeline_changed"] = {
                "original_days": original.get("estimated_days"),
                "final_days": final.get("estimated_days"),
            }

        return corrections

    async def update_pricing_model(
        self,
        pricing_model: dict,
        learnings: dict,
    ) -> dict:
        """
        Update a pricing model with new learnings.

        Args:
            pricing_model: Current pricing model
            learnings: Learnings from process_correction

        Returns:
            Updated pricing model
        """
        updated = pricing_model.copy()
        pricing_knowledge = updated.get("pricing_knowledge", {})

        # Apply pricing adjustments
        for adjustment in learnings.get("pricing_adjustments", []):
            item_type = adjustment.get("item_type")
            if item_type and item_type in pricing_knowledge:
                # Update existing knowledge
                existing = pricing_knowledge[item_type]
                if isinstance(existing, dict):
                    # Weighted average toward the correction
                    # Weight new learning at 30%, existing at 70%
                    if "base_rate" in existing:
                        old_rate = existing.get("base_rate", 0)
                        new_rate = adjustment.get("corrected_value", old_rate)
                        # Simple weighted update
                        existing["base_rate"] = old_rate * 0.7 + new_rate * 0.3

                    # Increment sample count
                    existing["samples"] = existing.get("samples", 1) + 1

                    # Update confidence
                    existing["confidence"] = min(
                        0.95,
                        existing.get("confidence", 0.5) + 0.02
                    )

                pricing_knowledge[item_type] = existing

        # Add new pricing rules
        for rule in learnings.get("new_pricing_rules", []):
            rule_key = rule.get("applies_to", "general")
            if rule_key not in pricing_knowledge:
                pricing_knowledge[rule_key] = {}

            if isinstance(pricing_knowledge[rule_key], dict):
                # Add the rule as a note
                existing_notes = pricing_knowledge[rule_key].get("notes", "")
                new_note = rule.get("rule", "")
                if new_note and new_note not in existing_notes:
                    pricing_knowledge[rule_key]["notes"] = (
                        f"{existing_notes}\n{new_note}".strip()
                    )

        updated["pricing_knowledge"] = pricing_knowledge

        # Update pricing notes with overall tendency
        tendency = learnings.get("overall_tendency", "")
        if tendency:
            current_notes = updated.get("pricing_notes", "")
            # Don't duplicate notes
            if tendency not in current_notes:
                updated["pricing_notes"] = f"{current_notes}\n\nLearned: {tendency}".strip()

        # Update metadata
        updated["last_learning_at"] = datetime.utcnow().isoformat()
        updated["correction_count"] = updated.get("correction_count", 0) + 1

        return updated

    async def get_pricing_confidence(
        self,
        pricing_model: dict,
        job_type: str,
    ) -> dict:
        """
        Get confidence level for a specific job type.

        Returns:
            dict with confidence info
        """
        pricing_knowledge = pricing_model.get("pricing_knowledge", {})

        if job_type in pricing_knowledge:
            knowledge = pricing_knowledge[job_type]
            if isinstance(knowledge, dict):
                samples = knowledge.get("samples", 0)
                confidence = knowledge.get("confidence", 0.5)

                return {
                    "job_type": job_type,
                    "known": True,
                    "samples": samples,
                    "confidence": confidence,
                    "confidence_label": self._confidence_label(confidence, samples),
                }

        return {
            "job_type": job_type,
            "known": False,
            "samples": 0,
            "confidence": 0.3,  # Low confidence for unknown job types
            "confidence_label": "Low - new job type, will learn from corrections",
        }

    def _confidence_label(self, confidence: float, samples: int) -> str:
        """Generate a human-readable confidence label."""
        if samples >= 20 and confidence >= 0.85:
            return "High - well-calibrated from many quotes"
        elif samples >= 10 and confidence >= 0.7:
            return "Good - learning from your patterns"
        elif samples >= 5:
            return "Medium - still learning"
        else:
            return "Low - limited data, review carefully"

    async def _call_claude(self, prompt: str) -> str:
        """Make a call to Claude API."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def _parse_learning_response(self, response: str) -> dict:
        """Parse Claude's learning analysis response."""
        # Try to find JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback
        return {
            "pricing_adjustments": [],
            "new_pricing_rules": [],
            "overall_tendency": "Could not parse learning response",
            "summary": response[:500],
        }

    def calculate_accuracy_stats(
        self,
        quote_history: list,
    ) -> dict:
        """
        Calculate accuracy statistics from quote history.

        Args:
            quote_history: List of quotes with was_edited and edit_details

        Returns:
            Accuracy statistics
        """
        total = len(quote_history)
        if total == 0:
            return {
                "total_quotes": 0,
                "accuracy_rate": 0,
                "average_adjustment": 0,
            }

        edited = sum(1 for q in quote_history if q.get("was_edited"))
        unedited = total - edited

        # Calculate average adjustment percentage
        adjustments = []
        for quote in quote_history:
            if quote.get("was_edited") and quote.get("edit_details"):
                pct = quote["edit_details"].get("total_change_percent", 0)
                adjustments.append(abs(pct))

        avg_adjustment = sum(adjustments) / len(adjustments) if adjustments else 0

        return {
            "total_quotes": total,
            "edited_count": edited,
            "unedited_count": unedited,
            "accuracy_rate": (unedited / total * 100) if total > 0 else 0,
            "average_adjustment_percent": avg_adjustment,
            "within_5_percent": sum(1 for a in adjustments if a <= 5),
            "within_10_percent": sum(1 for a in adjustments if a <= 10),
        }


# Singleton pattern
_learning_service: Optional[LearningService] = None


def get_learning_service() -> LearningService:
    """Get the learning service singleton."""
    global _learning_service
    if _learning_service is None:
        _learning_service = LearningService()
    return _learning_service
