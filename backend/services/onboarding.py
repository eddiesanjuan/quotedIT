"""
Onboarding service for Quoted.
Handles the interactive setup interview to learn a contractor's pricing model.

Flow:
1. Create new contractor account
2. Start setup conversation
3. Conduct multi-turn interview to learn pricing
4. Extract and save pricing model
"""

import json
import re
from typing import Optional
from datetime import datetime

import anthropic

from ..config import settings
from ..prompts import (
    get_setup_system_prompt,
    get_setup_initial_message,
    get_pricing_extraction_prompt,
)


class OnboardingService:
    """
    Manages the onboarding interview process for new contractors.
    Uses Claude to conduct a natural conversation about pricing.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens

    async def start_setup(
        self,
        contractor_name: str,
        primary_trade: str,
    ) -> dict:
        """
        Start a new setup interview session.

        Args:
            contractor_name: Business name
            primary_trade: What they do (deck_builder, painter, etc.)

        Returns:
            dict with:
            - session_id: Unique identifier for this setup session
            - system_prompt: The system prompt being used
            - initial_message: The opening message to display
            - messages: The conversation so far
        """
        system_prompt = get_setup_system_prompt(contractor_name, primary_trade)
        initial_message = get_setup_initial_message(contractor_name, primary_trade)

        return {
            "session_id": f"setup_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "contractor_name": contractor_name,
            "primary_trade": primary_trade,
            "system_prompt": system_prompt,
            "initial_message": initial_message,
            "messages": [
                {"role": "assistant", "content": initial_message}
            ],
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
        }

    async def continue_setup(
        self,
        session: dict,
        user_message: str,
    ) -> dict:
        """
        Continue an ongoing setup conversation.

        Args:
            session: The current session state (from start_setup or previous continue_setup)
            user_message: What the contractor said

        Returns:
            Updated session dict with new messages
        """
        # Add user message to history
        session["messages"].append({
            "role": "user",
            "content": user_message,
        })

        # Generate AI response
        response = await self._generate_response(
            system_prompt=session["system_prompt"],
            messages=session["messages"],
        )

        # Add AI response to history
        session["messages"].append({
            "role": "assistant",
            "content": response,
        })

        # Check if we should end the conversation
        # (Look for signals that the AI thinks we have enough info)
        if self._should_end_conversation(response, session["messages"]):
            session["status"] = "ready_to_extract"

        return session

    async def extract_pricing_model(self, session: dict) -> dict:
        """
        Extract the pricing model from a completed setup conversation.

        Args:
            session: The completed session with all messages

        Returns:
            Structured pricing model ready to save
        """
        prompt = get_pricing_extraction_prompt(session["messages"])

        response = await self._generate_response(
            system_prompt="You are a data extraction assistant. Extract structured pricing data from conversations.",
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse the JSON response
        pricing_model = self._parse_extraction_response(response)

        # Add metadata
        pricing_model["extracted_at"] = datetime.utcnow().isoformat()
        pricing_model["session_id"] = session.get("session_id")
        pricing_model["message_count"] = len(session["messages"])

        return pricing_model

    async def _generate_response(
        self,
        system_prompt: str,
        messages: list,
    ) -> str:
        """Generate a response from Claude."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def _should_end_conversation(self, response: str, messages: list) -> bool:
        """
        Determine if the setup conversation should end.

        Signals:
        - AI summarizes and asks "anything else?"
        - Conversation has gone 20+ turns
        - AI says it has enough information
        """
        # Check for summary signals in the response
        end_signals = [
            "anything else",
            "is there anything else",
            "have enough information",
            "got everything i need",
            "we're all set",
            "that's everything",
            "we're good to go",
        ]

        response_lower = response.lower()
        for signal in end_signals:
            if signal in response_lower:
                return True

        # End if conversation is very long
        if len(messages) >= 20:
            return True

        return False

    def _parse_extraction_response(self, response: str) -> dict:
        """Parse the pricing model extraction response."""
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Return empty model if parsing fails
        return {
            "error": "Could not parse extraction response",
            "raw_response": response,
            "labor_rate_hourly": None,
            "pricing_knowledge": {},
            "pricing_notes": "Manual review required",
        }

    async def quick_setup(
        self,
        contractor_name: str,
        primary_trade: str,
        labor_rate: float,
        material_markup: float = 20.0,
        minimum_job: float = 500.0,
        pricing_notes: Optional[str] = None,
    ) -> dict:
        """
        Quick setup without the full interview.
        For contractors who just want to get started fast.

        Args:
            contractor_name: Business name
            primary_trade: What they do
            labor_rate: Hourly labor rate
            material_markup: Material markup percentage
            minimum_job: Minimum job amount
            pricing_notes: Any additional notes

        Returns:
            Basic pricing model ready to save
        """
        return {
            "labor_rate_hourly": labor_rate,
            "helper_rate_hourly": labor_rate * 0.6,  # Reasonable default
            "material_markup_percent": material_markup,
            "minimum_job_amount": minimum_job,
            "pricing_knowledge": self._get_trade_defaults(primary_trade),
            "pricing_notes": pricing_notes or f"Quick setup for {primary_trade}. Will learn more from quote corrections.",
            "terms": {
                "deposit_percent": 50.0,
                "quote_valid_days": 30,
                "labor_warranty_years": 2,
            },
            "setup_type": "quick",
            "created_at": datetime.utcnow().isoformat(),
        }

    def _get_trade_defaults(self, primary_trade: str) -> dict:
        """Get default pricing knowledge for a trade."""
        trade_defaults = {
            "deck_builder": {
                "composite_deck": {
                    "base_per_sqft": 55.0,
                    "typical_range": [45.0, 75.0],
                    "unit": "sqft",
                    "notes": "Trex/TimberTech baseline, adjust for premium lines"
                },
                "wood_deck": {
                    "base_per_sqft": 38.0,
                    "typical_range": [30.0, 50.0],
                    "unit": "sqft",
                },
                "railing": {
                    "base_per_linear_ft": 35.0,
                    "unit": "linear_ft",
                },
                "demolition": {
                    "base_rate": 800.0,
                    "per_sqft_adder": 2.0,
                },
            },
            "painter": {
                "interior_per_sqft": {
                    "base_rate": 3.50,
                    "unit": "sqft",
                },
                "exterior_per_sqft": {
                    "base_rate": 4.50,
                    "unit": "sqft",
                },
                "cabinet_per_linear_ft": {
                    "base_rate": 75.0,
                    "unit": "linear_ft",
                },
            },
            "fence_installer": {
                "wood_fence": {
                    "base_per_linear_ft": 35.0,
                    "typical_range": [25.0, 50.0],
                    "unit": "linear_ft",
                },
                "vinyl_fence": {
                    "base_per_linear_ft": 45.0,
                    "unit": "linear_ft",
                },
                "chain_link": {
                    "base_per_linear_ft": 20.0,
                    "unit": "linear_ft",
                },
                "gate": {
                    "base_rate": 350.0,
                    "unit": "each",
                },
            },
            "landscaper": {
                "design_fee": {
                    "base_rate": 500.0,
                    "unit": "flat",
                },
                "planting_per_sqft": {
                    "base_rate": 15.0,
                    "unit": "sqft",
                },
                "hardscape_per_sqft": {
                    "base_rate": 25.0,
                    "unit": "sqft",
                },
            },
        }

        return trade_defaults.get(primary_trade, {})


# Singleton pattern
_onboarding_service: Optional[OnboardingService] = None


def get_onboarding_service() -> OnboardingService:
    """Get the onboarding service singleton."""
    global _onboarding_service
    if _onboarding_service is None:
        _onboarding_service = OnboardingService()
    return _onboarding_service
