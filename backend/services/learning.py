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
from .analytics import analytics_service


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
        contractor_id: Optional[str] = None,
        category: Optional[str] = None,
        user_id: Optional[str] = None,
        existing_learnings: Optional[list] = None,
        existing_tailored_prompt: Optional[str] = None,
        existing_philosophy: Optional[str] = None,
    ) -> dict:
        """
        Process a quote correction and extract THREE-LAYER learnings.

        Args:
            original_quote: The AI-generated quote
            final_quote: The contractor-edited final quote
            contractor_notes: Any notes the contractor added about the correction
            contractor_id: Contractor ID for analytics tracking
            category: Job category for analytics tracking
            user_id: User ID for analytics tracking
            existing_learnings: Current injection learnings for this category
            existing_tailored_prompt: Current category-level tailored prompt
            existing_philosophy: Current global pricing philosophy

        Returns:
            dict with:
            - corrections: What changed
            - learnings: Dict containing learning_statements, tailored_prompt_update, philosophy_update
            - confidence: How confident we are in the learnings
        """
        # Calculate what changed
        corrections = self._calculate_corrections(original_quote, final_quote)

        if not corrections.get("has_changes"):
            return {
                "has_changes": False,
                "message": "No changes detected",
            }

        # Use Claude to analyze the corrections and return THREE-LAYER learnings
        # Claude sees existing context at all layers and can update any of them
        prompt = get_quote_refinement_prompt(
            original_quote=original_quote,
            corrections=corrections,
            contractor_notes=contractor_notes,
            existing_learnings=existing_learnings,
            existing_tailored_prompt=existing_tailored_prompt,
            existing_philosophy=existing_philosophy,
        )

        response = await self._call_claude(prompt)
        learnings = self._parse_learning_response(response)

        # Track learning correction event (DISC-012: Learning system metrics)
        if user_id and category:
            try:
                correction_magnitude = abs(corrections.get("total_change_percent", 0))

                analytics_service.track_event(
                    user_id=user_id,
                    event_name="learning_correction_recorded",
                    properties={
                        "contractor_id": contractor_id,
                        "category": category,
                        "correction_magnitude": round(correction_magnitude, 2),
                        "total_change_dollars": corrections.get("total_change", 0),
                        "has_line_item_changes": len(corrections.get("line_item_changes", [])) > 0,
                        "line_item_change_count": len(corrections.get("line_item_changes", [])),
                    }
                )
            except Exception as e:
                # Don't fail correction processing if analytics fails
                print(f"Warning: Failed to track learning correction: {e}")

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
        """
        Parse Claude's THREE-LAYER learning analysis response.

        Returns:
            dict with:
            - learning_statements: List of injection learnings (Level 1)
            - tailored_prompt_update: New category prompt or None (Level 2)
            - philosophy_update: New global philosophy or None (Level 3)
            - pricing_direction: higher/lower/mixed
            - confidence: high/medium/low
            - summary: Brief description
        """
        # Try to find JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                parsed = json.loads(json_match.group())

                # Ensure all three-layer fields exist
                result = {
                    "learning_statements": parsed.get("learning_statements", []),
                    "tailored_prompt_update": parsed.get("tailored_prompt_update"),
                    "tailored_prompt_reason": parsed.get("tailored_prompt_reason"),
                    "philosophy_update": parsed.get("philosophy_update"),
                    "philosophy_reason": parsed.get("philosophy_reason"),
                    "pricing_direction": parsed.get("pricing_direction", "mixed"),
                    "confidence": parsed.get("confidence", "medium"),
                    "summary": parsed.get("summary", ""),
                    "changes_made": parsed.get("changes_made", ""),
                }

                # Legacy format support - convert to new format
                if "pricing_adjustments" in parsed and not result["learning_statements"]:
                    statements = []

                    # Convert pricing adjustments to statements
                    for adj in parsed.get("pricing_adjustments", []):
                        learning = adj.get("learning", "")
                        if learning:
                            statements.append(learning)

                    # Convert rules to statements
                    for rule in parsed.get("new_pricing_rules", []):
                        rule_text = rule.get("rule", "")
                        if rule_text:
                            statements.append(rule_text)

                    # Add tendency as a statement if present
                    tendency = parsed.get("overall_tendency", "")
                    if tendency and len(tendency) > 10:
                        statements.append(tendency)

                    result["learning_statements"] = statements

                return result

            except json.JSONDecodeError:
                pass

        # Fallback - no learnings extracted
        return {
            "learning_statements": [],
            "tailored_prompt_update": None,
            "philosophy_update": None,
            "pricing_direction": "mixed",
            "confidence": "low",
            "summary": response[:500] if response else "Could not parse learning response",
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

    async def process_feedback(
        self,
        quote_id: str,
        feedback_data: dict,
        original_quote: dict,
    ) -> dict:
        """
        Process user feedback on a quote and extract learnings.

        Unlike corrections, feedback doesn't provide exact numbers,
        but gives signals about pricing direction and quality.

        Args:
            quote_id: ID of the quote being rated
            feedback_data: The feedback submitted by the user
            original_quote: The original quote data

        Returns:
            dict with extracted learnings
        """
        learnings = {
            "has_learnings": False,
            "adjustments": [],
            "signals": [],
        }

        job_type = original_quote.get("job_type", "general")
        original_total = original_quote.get("subtotal", 0)

        # Process pricing direction feedback
        pricing_direction = feedback_data.get("pricing_direction")
        if pricing_direction and original_total > 0:
            learnings["has_learnings"] = True

            # Estimate adjustment based on direction
            off_by_percent = feedback_data.get("pricing_off_by_percent", 10)

            if pricing_direction == "too_high":
                adjustment = -abs(off_by_percent) / 100
                learnings["signals"].append({
                    "type": "pricing_high",
                    "job_type": job_type,
                    "adjustment": adjustment,
                    "message": f"User indicated price was too high by ~{off_by_percent}%"
                })
            elif pricing_direction == "too_low":
                adjustment = abs(off_by_percent) / 100
                learnings["signals"].append({
                    "type": "pricing_low",
                    "job_type": job_type,
                    "adjustment": adjustment,
                    "message": f"User indicated price was too low by ~{off_by_percent}%"
                })
            else:  # about_right
                learnings["signals"].append({
                    "type": "pricing_accurate",
                    "job_type": job_type,
                    "message": "User confirmed pricing was about right"
                })

        # Process actual total if provided (more reliable signal)
        actual_total = feedback_data.get("actual_total")
        if actual_total and original_total > 0:
            learnings["has_learnings"] = True
            difference = actual_total - original_total
            percent_change = (difference / original_total) * 100

            learnings["adjustments"].append({
                "type": "total_correction",
                "job_type": job_type,
                "original": original_total,
                "actual": actual_total,
                "percent_change": percent_change,
            })

        # Process actual line items if provided
        actual_line_items = feedback_data.get("actual_line_items", [])
        if actual_line_items:
            learnings["has_learnings"] = True
            for item in actual_line_items:
                name = item.get("name")
                original_amount = item.get("original_amount", 0)
                actual_amount = item.get("actual_amount", 0)

                if original_amount > 0:
                    percent_change = ((actual_amount - original_amount) / original_amount) * 100
                    learnings["adjustments"].append({
                        "type": "line_item_correction",
                        "item_name": name,
                        "job_type": job_type,
                        "original": original_amount,
                        "actual": actual_amount,
                        "percent_change": percent_change,
                    })

        # Process issues (signals for learning)
        issues = feedback_data.get("issues", [])
        if issues:
            learnings["has_learnings"] = True
            for issue in issues:
                learnings["signals"].append({
                    "type": "issue",
                    "issue_code": issue,
                    "job_type": job_type,
                })

        return learnings


# Singleton pattern
_learning_service: Optional[LearningService] = None


def get_learning_service() -> LearningService:
    """Get the learning service singleton."""
    global _learning_service
    if _learning_service is None:
        _learning_service = LearningService()
    return _learning_service
