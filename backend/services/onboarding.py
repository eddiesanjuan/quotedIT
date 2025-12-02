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
        labor_rate: Optional[float] = None,
        helper_rate: Optional[float] = None,
        base_rate_per_lf: Optional[float] = None,
        base_rate_per_sqft: Optional[float] = None,
        base_rate_per_square: Optional[float] = None,
        base_rate_per_unit: Optional[float] = None,
        tear_off_per_square: Optional[float] = None,
        project_management_fee: Optional[float] = None,
        material_markup: float = 20.0,
        minimum_job: float = 500.0,
        pricing_notes: Optional[str] = None,
    ) -> dict:
        """
        Quick setup without the full interview - supports varied pricing approaches.
        For contractors who just want to get started fast.

        Args:
            contractor_name: Business name
            primary_trade: What they do
            labor_rate: Hourly labor rate (for hourly-based trades)
            helper_rate: Helper hourly rate (optional)
            base_rate_per_lf: Linear foot rate (cabinet_maker)
            base_rate_per_sqft: Square foot rate (painter, flooring, etc)
            base_rate_per_square: Per square rate (roofer - 100 sq ft)
            base_rate_per_unit: Per unit rate (window_door)
            tear_off_per_square: Tear-off rate per square (roofer)
            project_management_fee: Project mgmt fee % (general_contractor)
            material_markup: Material markup percentage
            minimum_job: Minimum job amount
            pricing_notes: Any additional notes

        Returns:
            Basic pricing model ready to save
        """
        trade_defaults = self._get_trade_defaults(primary_trade)

        # Normalize varied inputs to a standard labor_rate_hourly for storage
        # This allows the system to work with varied pricing approaches internally
        normalized_labor_rate = labor_rate

        # Map per-unit rates to approximate hourly equivalents for internal storage
        # These are rough conversions - the actual rates are stored in pricing_knowledge
        if not normalized_labor_rate:
            if base_rate_per_lf:
                # Cabinet maker: ~$500/LF, assume 2-3 LF per hour = ~$150/hr
                normalized_labor_rate = base_rate_per_lf * 0.3
            elif base_rate_per_sqft:
                # Painter/flooring: ~$3-10/sqft, assume 50-100 sqft/hr = ~$150-500/hr
                normalized_labor_rate = base_rate_per_sqft * 50
            elif base_rate_per_square:
                # Roofer: ~$450/square, assume 1 square per 4 hours = ~$112/hr
                normalized_labor_rate = base_rate_per_square * 0.25
            elif base_rate_per_unit:
                # Window/door: ~$450/unit, assume 1 unit per 3 hours = ~$150/hr
                normalized_labor_rate = base_rate_per_unit * 0.33
            elif project_management_fee:
                # General contractor: typically 15%, assume $100/hr base
                normalized_labor_rate = 100.0
            else:
                # Default fallback
                normalized_labor_rate = 85.0

        # Build pricing_knowledge with both trade defaults and categories for Pricing Brain
        # Store the original per-unit rates for the Pricing Brain to use
        pricing_knowledge = {
            "trade_defaults": trade_defaults,
            "categories": self._seed_categories_from_trade(primary_trade, trade_defaults),
            "global_rules": [],
            "per_unit_rates": {
                "base_rate_per_lf": base_rate_per_lf,
                "base_rate_per_sqft": base_rate_per_sqft,
                "base_rate_per_square": base_rate_per_square,
                "base_rate_per_unit": base_rate_per_unit,
                "tear_off_per_square": tear_off_per_square,
                "project_management_fee": project_management_fee,
            },
        }

        return {
            "labor_rate_hourly": normalized_labor_rate,
            "helper_rate_hourly": helper_rate or (normalized_labor_rate * 0.6),
            "material_markup_percent": material_markup,
            "minimum_job_amount": minimum_job,
            "pricing_knowledge": pricing_knowledge,
            "pricing_notes": pricing_notes or f"Quick setup for {primary_trade}. Will learn more from quote corrections.",
            "terms": {
                "deposit_percent": 50.0,
                "quote_valid_days": 30,
                "labor_warranty_years": 2,
            },
            "setup_type": "quick",
            "created_at": datetime.utcnow().isoformat(),
        }

    def _seed_categories_from_trade(self, primary_trade: str, trade_defaults: dict) -> dict:
        """
        Seed initial Pricing Brain categories from trade defaults.
        This populates the categories dict so Pricing Brain has something to show.
        """
        categories = {}

        for category_key, category_data in trade_defaults.items():
            # Create display name from key (e.g., "composite_deck" -> "Composite Deck")
            display_name = category_key.replace("_", " ").title()

            # Build initial learned adjustments from trade defaults
            learned_adjustments = []
            if isinstance(category_data, dict):
                if "base_per_sqft" in category_data:
                    learned_adjustments.append(f"Base rate: ${category_data['base_per_sqft']}/sqft")
                if "base_per_linear_ft" in category_data:
                    learned_adjustments.append(f"Base rate: ${category_data['base_per_linear_ft']}/linear ft")
                if "base_rate" in category_data:
                    unit = category_data.get("unit", "each")
                    learned_adjustments.append(f"Base rate: ${category_data['base_rate']} per {unit}")
                if "typical_range" in category_data:
                    low, high = category_data["typical_range"]
                    learned_adjustments.append(f"Typical range: ${low} - ${high}")
                if "notes" in category_data:
                    learned_adjustments.append(category_data["notes"])

            categories[category_key] = {
                "display_name": display_name,
                "learned_adjustments": learned_adjustments,
                "samples": 0,
                "confidence": 0.7,  # Higher initial confidence for trade defaults
            }

        return categories

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
            "electrician": {
                "service_call": {
                    "base_rate": 125.0,
                    "unit": "flat",
                    "notes": "Standard diagnostic fee, typically credited toward work"
                },
                "outlet_install": {
                    "base_rate": 175.0,
                    "typical_range": [150.0, 250.0],
                    "unit": "per_outlet",
                },
                "panel_upgrade": {
                    "base_rate": 2500.0,
                    "typical_range": [2000.0, 3500.0],
                    "unit": "flat",
                    "notes": "200A panel upgrade, varies by complexity"
                },
                "rewiring_per_sqft": {
                    "base_rate": 7.0,
                    "typical_range": [5.0, 10.0],
                    "unit": "sqft",
                },
                "fixture_install": {
                    "base_rate": 150.0,
                    "unit": "each",
                },
            },
            "plumber": {
                "service_call": {
                    "base_rate": 150.0,
                    "unit": "flat",
                },
                "fixture_install": {
                    "base_rate": 250.0,
                    "typical_range": [200.0, 400.0],
                    "unit": "each",
                    "notes": "Toilet, sink, or faucet installation"
                },
                "water_heater_install": {
                    "base_rate": 1200.0,
                    "typical_range": [900.0, 1800.0],
                    "unit": "flat",
                },
                "drain_cleaning": {
                    "base_rate": 200.0,
                    "typical_range": [150.0, 350.0],
                    "unit": "flat",
                },
                "pipe_repair_per_linear_ft": {
                    "base_rate": 75.0,
                    "unit": "linear_ft",
                },
            },
            "hvac": {
                "service_call": {
                    "base_rate": 125.0,
                    "unit": "flat",
                },
                "ac_install": {
                    "base_rate": 5500.0,
                    "typical_range": [4000.0, 8000.0],
                    "unit": "flat",
                    "notes": "Central AC system, varies by tonnage"
                },
                "furnace_install": {
                    "base_rate": 4500.0,
                    "typical_range": [3500.0, 6500.0],
                    "unit": "flat",
                },
                "duct_work_per_linear_ft": {
                    "base_rate": 45.0,
                    "unit": "linear_ft",
                },
                "maintenance_contract": {
                    "base_rate": 250.0,
                    "unit": "annual",
                },
            },
            "roofer": {
                "repair": {
                    "base_rate": 500.0,
                    "typical_range": [300.0, 1200.0],
                    "unit": "flat",
                },
                "replacement_per_square": {
                    "base_rate": 450.0,
                    "typical_range": [350.0, 650.0],
                    "unit": "per_square",
                    "notes": "100 sqft = 1 square, asphalt shingles baseline"
                },
                "tear_off_per_square": {
                    "base_rate": 150.0,
                    "unit": "per_square",
                },
                "inspection": {
                    "base_rate": 200.0,
                    "unit": "flat",
                },
            },
            "flooring": {
                "hardwood_install_per_sqft": {
                    "base_rate": 12.0,
                    "typical_range": [8.0, 18.0],
                    "unit": "sqft",
                },
                "vinyl_install_per_sqft": {
                    "base_rate": 6.0,
                    "typical_range": [4.0, 9.0],
                    "unit": "sqft",
                },
                "tile_install_per_sqft": {
                    "base_rate": 15.0,
                    "typical_range": [10.0, 25.0],
                    "unit": "sqft",
                },
                "removal_per_sqft": {
                    "base_rate": 3.0,
                    "unit": "sqft",
                },
            },
            "tile": {
                "backsplash_per_sqft": {
                    "base_rate": 18.0,
                    "typical_range": [12.0, 30.0],
                    "unit": "sqft",
                },
                "bathroom_floor_per_sqft": {
                    "base_rate": 15.0,
                    "unit": "sqft",
                },
                "shower_install": {
                    "base_rate": 2500.0,
                    "typical_range": [2000.0, 4000.0],
                    "unit": "flat",
                },
                "floor_tile_per_sqft": {
                    "base_rate": 12.0,
                    "unit": "sqft",
                },
            },
            "concrete": {
                "driveway_per_sqft": {
                    "base_rate": 8.0,
                    "typical_range": [6.0, 12.0],
                    "unit": "sqft",
                },
                "patio_per_sqft": {
                    "base_rate": 10.0,
                    "typical_range": [8.0, 15.0],
                    "unit": "sqft",
                },
                "foundation_per_linear_ft": {
                    "base_rate": 150.0,
                    "unit": "linear_ft",
                },
                "stamped_concrete_per_sqft": {
                    "base_rate": 18.0,
                    "typical_range": [15.0, 25.0],
                    "unit": "sqft",
                },
            },
            "framing": {
                "wall_framing_per_linear_ft": {
                    "base_rate": 35.0,
                    "unit": "linear_ft",
                },
                "addition_per_sqft": {
                    "base_rate": 125.0,
                    "typical_range": [100.0, 200.0],
                    "unit": "sqft",
                },
                "deck_framing_per_sqft": {
                    "base_rate": 20.0,
                    "unit": "sqft",
                },
                "roof_framing_per_sqft": {
                    "base_rate": 15.0,
                    "unit": "sqft",
                },
            },
            "drywall": {
                "hang_per_sqft": {
                    "base_rate": 1.50,
                    "unit": "sqft",
                },
                "tape_per_sqft": {
                    "base_rate": 0.75,
                    "unit": "sqft",
                },
                "texture_per_sqft": {
                    "base_rate": 0.50,
                    "unit": "sqft",
                },
                "complete_per_sqft": {
                    "base_rate": 3.50,
                    "typical_range": [2.50, 5.00],
                    "unit": "sqft",
                    "notes": "Hang, tape, texture complete"
                },
            },
            "window_door": {
                "window_install": {
                    "base_rate": 450.0,
                    "typical_range": [350.0, 700.0],
                    "unit": "each",
                },
                "door_install": {
                    "base_rate": 500.0,
                    "typical_range": [400.0, 800.0],
                    "unit": "each",
                },
                "storm_door_install": {
                    "base_rate": 250.0,
                    "unit": "each",
                },
                "sliding_door_install": {
                    "base_rate": 800.0,
                    "typical_range": [600.0, 1200.0],
                    "unit": "each",
                },
            },
            "siding": {
                "vinyl_per_sqft": {
                    "base_rate": 6.0,
                    "typical_range": [5.0, 8.0],
                    "unit": "sqft",
                },
                "fiber_cement_per_sqft": {
                    "base_rate": 9.0,
                    "typical_range": [7.0, 12.0],
                    "unit": "sqft",
                },
                "wood_per_sqft": {
                    "base_rate": 10.0,
                    "typical_range": [8.0, 15.0],
                    "unit": "sqft",
                },
                "removal_per_sqft": {
                    "base_rate": 2.0,
                    "unit": "sqft",
                },
            },
            "gutters": {
                "install_per_linear_ft": {
                    "base_rate": 12.0,
                    "typical_range": [8.0, 18.0],
                    "unit": "linear_ft",
                },
                "guards_per_linear_ft": {
                    "base_rate": 8.0,
                    "unit": "linear_ft",
                },
                "cleaning": {
                    "base_rate": 200.0,
                    "typical_range": [150.0, 300.0],
                    "unit": "flat",
                },
                "downspout_install": {
                    "base_rate": 75.0,
                    "unit": "each",
                },
            },
            "insulation": {
                "blown_per_sqft": {
                    "base_rate": 2.0,
                    "typical_range": [1.50, 3.00],
                    "unit": "sqft",
                },
                "batt_per_sqft": {
                    "base_rate": 1.50,
                    "unit": "sqft",
                },
                "spray_foam_per_sqft": {
                    "base_rate": 4.0,
                    "typical_range": [3.00, 6.00],
                    "unit": "sqft",
                },
            },
            "garage_door": {
                "door_install": {
                    "base_rate": 1200.0,
                    "typical_range": [800.0, 2000.0],
                    "unit": "each",
                },
                "opener_install": {
                    "base_rate": 350.0,
                    "typical_range": [250.0, 500.0],
                    "unit": "each",
                },
                "repair": {
                    "base_rate": 200.0,
                    "typical_range": [150.0, 400.0],
                    "unit": "flat",
                },
                "spring_replacement": {
                    "base_rate": 250.0,
                    "unit": "flat",
                },
            },
            "pool_spa": {
                "weekly_cleaning": {
                    "base_rate": 125.0,
                    "typical_range": [100.0, 150.0],
                    "unit": "monthly",
                },
                "repair": {
                    "base_rate": 300.0,
                    "typical_range": [200.0, 600.0],
                    "unit": "flat",
                },
                "opening": {
                    "base_rate": 250.0,
                    "unit": "flat",
                },
                "closing": {
                    "base_rate": 200.0,
                    "unit": "flat",
                },
            },
            "masonry": {
                "brick_per_sqft": {
                    "base_rate": 30.0,
                    "typical_range": [25.0, 40.0],
                    "unit": "sqft",
                },
                "block_per_sqft": {
                    "base_rate": 20.0,
                    "unit": "sqft",
                },
                "stone_per_sqft": {
                    "base_rate": 45.0,
                    "typical_range": [35.0, 60.0],
                    "unit": "sqft",
                },
                "repair": {
                    "base_rate": 400.0,
                    "typical_range": [300.0, 800.0],
                    "unit": "flat",
                },
            },
            "tree_service": {
                "removal": {
                    "base_rate": 1000.0,
                    "typical_range": [500.0, 3000.0],
                    "unit": "per_tree",
                    "notes": "Varies significantly by size and complexity"
                },
                "trimming": {
                    "base_rate": 400.0,
                    "typical_range": [200.0, 800.0],
                    "unit": "per_tree",
                },
                "stump_grinding": {
                    "base_rate": 200.0,
                    "typical_range": [100.0, 400.0],
                    "unit": "per_stump",
                },
                "emergency_service": {
                    "base_rate": 1500.0,
                    "unit": "flat",
                },
            },
            "pressure_washing": {
                "house_wash": {
                    "base_rate": 400.0,
                    "typical_range": [300.0, 600.0],
                    "unit": "flat",
                },
                "driveway_per_sqft": {
                    "base_rate": 0.30,
                    "unit": "sqft",
                },
                "deck_per_sqft": {
                    "base_rate": 0.50,
                    "unit": "sqft",
                },
                "roof_cleaning": {
                    "base_rate": 500.0,
                    "typical_range": [400.0, 800.0],
                    "unit": "flat",
                },
            },
            "closet_organizer": {
                "custom_system_per_linear_ft": {
                    "base_rate": 125.0,
                    "typical_range": [100.0, 200.0],
                    "unit": "linear_ft",
                },
                "reach_in_closet": {
                    "base_rate": 800.0,
                    "typical_range": [600.0, 1200.0],
                    "unit": "flat",
                },
                "walk_in_closet": {
                    "base_rate": 2500.0,
                    "typical_range": [2000.0, 4000.0],
                    "unit": "flat",
                },
                "pantry_system": {
                    "base_rate": 1500.0,
                    "unit": "flat",
                },
            },
            "cabinet_maker": {
                "custom_cabinets_per_linear_ft": {
                    "base_rate": 500.0,
                    "typical_range": [400.0, 800.0],
                    "unit": "linear_ft",
                    "notes": "Custom build, varies by materials and complexity"
                },
                "refacing_per_linear_ft": {
                    "base_rate": 150.0,
                    "typical_range": [100.0, 250.0],
                    "unit": "linear_ft",
                },
                "install_per_linear_ft": {
                    "base_rate": 100.0,
                    "unit": "linear_ft",
                },
                "countertop_per_sqft": {
                    "base_rate": 75.0,
                    "typical_range": [50.0, 150.0],
                    "unit": "sqft",
                },
            },
            "general_contractor": {
                "project_management": {
                    "base_rate": 15.0,
                    "typical_range": [10.0, 20.0],
                    "unit": "percent_of_project",
                    "notes": "Percentage of total project cost"
                },
                "remodel_per_sqft": {
                    "base_rate": 150.0,
                    "typical_range": [100.0, 250.0],
                    "unit": "sqft",
                    "notes": "Rough estimate for full renovation"
                },
                "addition_per_sqft": {
                    "base_rate": 200.0,
                    "typical_range": [150.0, 300.0],
                    "unit": "sqft",
                },
                "consultation": {
                    "base_rate": 200.0,
                    "unit": "flat",
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
