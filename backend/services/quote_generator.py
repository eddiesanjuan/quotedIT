"""
Quote generation service for Quoted.
This is the core service that synthesizes voice transcriptions into structured quotes.

Pipeline:
1. Receive transcribed text (or audio → transcribe first)
2. Load contractor's pricing model
3. Call Claude with the quote generation prompt
4. Parse response into structured Quote
5. Save and return
"""

import json
import re
from typing import Optional
from datetime import datetime

import anthropic

from ..config import settings
from ..prompts import get_quote_generation_prompt


class QuoteGenerationService:
    """
    Generates structured quotes from voice transcriptions.
    Uses the contractor's learned pricing model to produce accurate estimates.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens

    async def generate_quote(
        self,
        transcription: str,
        contractor: dict,
        pricing_model: dict,
        job_types: Optional[list] = None,
        terms: Optional[dict] = None,
        correction_examples: Optional[list] = None,
    ) -> dict:
        """
        Generate a quote from a voice transcription.

        Args:
            transcription: The transcribed voice note
            contractor: Contractor data (business_name, primary_trade, etc.)
            pricing_model: The contractor's pricing model
            job_types: List of job types the contractor has done
            terms: Standard terms and conditions
            correction_examples: Past quote corrections for few-shot learning

        Returns:
            dict with the generated quote structure:
            - customer_name, customer_address, customer_phone
            - job_type, job_description
            - line_items (list)
            - subtotal, total
            - estimated_days, estimated_crew_size
            - confidence, questions
        """
        # Build the prompt with correction examples for learning
        prompt = get_quote_generation_prompt(
            transcription=transcription,
            contractor_name=contractor.get("business_name", "Contractor"),
            pricing_model=pricing_model,
            pricing_notes=pricing_model.get("pricing_notes"),
            job_types=job_types,
            terms=terms,
            correction_examples=correction_examples,
        )

        # Call Claude
        response = await self._call_claude(prompt)

        # Parse the response
        quote_data = self._parse_quote_response(response)

        # Add metadata
        quote_data["generated_at"] = datetime.utcnow().isoformat()
        quote_data["transcription"] = transcription
        quote_data["ai_generated_total"] = quote_data.get("subtotal", 0)

        return quote_data

    async def generate_quote_from_audio(
        self,
        audio_file_path: str,
        contractor: dict,
        pricing_model: dict,
        job_types: Optional[list] = None,
        terms: Optional[dict] = None,
        correction_examples: Optional[list] = None,
        transcription_service=None,
    ) -> dict:
        """
        Full pipeline: Audio → Transcription → Quote.

        Args:
            audio_file_path: Path to the audio file
            contractor: Contractor data
            pricing_model: Pricing model
            job_types: Job types
            terms: Terms and conditions
            correction_examples: Past quote corrections for few-shot learning
            transcription_service: TranscriptionService instance

        Returns:
            dict with quote data plus transcription info
        """
        # Import here to avoid circular imports
        if transcription_service is None:
            from .transcription import get_transcription_service
            transcription_service = get_transcription_service()

        # Transcribe the audio
        transcription_result = await transcription_service.transcribe(audio_file_path)
        transcription_text = transcription_result.get("text", "")

        if not transcription_text.strip():
            return {
                "error": "No speech detected in audio",
                "transcription": "",
                "audio_duration": transcription_result.get("duration", 0),
            }

        # Generate the quote with learning from past corrections
        quote_data = await self.generate_quote(
            transcription=transcription_text,
            contractor=contractor,
            pricing_model=pricing_model,
            job_types=job_types,
            terms=terms,
            correction_examples=correction_examples,
        )

        # Add transcription metadata
        quote_data["audio_duration"] = transcription_result.get("duration", 0)
        quote_data["transcription_confidence"] = transcription_result.get("confidence")

        return quote_data

    async def detect_job_type(self, transcription: str) -> str:
        """
        Quick first-pass to detect job type from transcription.
        Uses a fast, cheap model call to categorize before full quote generation.

        Returns a standardized job_type string like:
        - deck_composite, deck_wood, deck_repair
        - fence_wood, fence_vinyl, fence_chain_link
        - paint_exterior, paint_interior
        - roofing, siding, concrete, electrical, plumbing
        - general (fallback)
        """
        detection_prompt = """Analyze this contractor voice note and identify the PRIMARY job type.

Voice note: "{transcription}"

Return ONLY a single job_type code from this list (pick the closest match):
- deck_composite (Trex, TimberTech, composite decking)
- deck_wood (pressure treated, cedar, redwood decking)
- deck_repair (deck repairs, board replacement, railing fixes)
- fence_wood (wood privacy fence, picket fence, cedar fence)
- fence_vinyl (vinyl/PVC fence)
- fence_chain_link (chain link, metal fence)
- paint_exterior (exterior house painting, siding paint)
- paint_interior (interior room painting, walls, ceilings)
- roofing (roof replacement, shingles, roof repair)
- siding (siding installation, vinyl siding, hardie board)
- concrete (driveway, patio, sidewalk, foundation)
- electrical (wiring, panel, outlets, lighting)
- plumbing (pipes, fixtures, water heater)
- remodel_kitchen (kitchen renovation, cabinets, counters)
- remodel_bathroom (bathroom renovation, tile, shower)
- remodel_basement (basement finishing, egress)
- landscaping (grading, retaining walls, drainage)
- general (if none of the above fit)

Respond with ONLY the job_type code, nothing else.""".format(transcription=transcription)

        try:
            # Use haiku for speed and cost - this is just classification
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[{"role": "user", "content": detection_prompt}],
            )
            job_type = message.content[0].text.strip().lower()

            # Validate it's a known type, fallback to general
            valid_types = [
                "deck_composite", "deck_wood", "deck_repair",
                "fence_wood", "fence_vinyl", "fence_chain_link",
                "paint_exterior", "paint_interior",
                "roofing", "siding", "concrete", "electrical", "plumbing",
                "remodel_kitchen", "remodel_bathroom", "remodel_basement",
                "landscaping", "general"
            ]

            if job_type not in valid_types:
                # Try to match partial
                for vt in valid_types:
                    if vt in job_type or job_type in vt:
                        return vt
                return "general"

            return job_type

        except Exception as e:
            # On error, return general - don't block quote generation
            return "general"

    async def _call_claude(self, prompt: str) -> str:
        """Make a call to Claude API."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def _parse_quote_response(self, response: str) -> dict:
        """
        Parse Claude's response into structured quote data.
        Claude should return JSON, but we handle edge cases.
        """
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # If JSON parsing fails, try to extract key information
        # This is a fallback - ideally Claude returns clean JSON
        return self._extract_quote_from_text(response)

    def _extract_quote_from_text(self, text: str) -> dict:
        """
        Fallback extraction when JSON parsing fails.
        Try to extract quote components from natural language.
        """
        # This is a safety net - in practice, Claude usually returns valid JSON
        return {
            "error": "Could not parse quote response",
            "raw_response": text,
            "job_description": "Please review and edit manually",
            "line_items": [],
            "subtotal": 0,
            "confidence": "low",
            "questions": ["The AI response could not be parsed - please review manually"],
        }

    async def refine_quote(
        self,
        original_quote: dict,
        user_edits: dict,
        additional_context: Optional[str] = None,
    ) -> dict:
        """
        Refine a quote based on user feedback.
        Not a full regeneration - just adjustments based on input.
        """
        # For now, just apply the edits directly
        # In the future, this could use Claude to intelligently merge edits
        refined = original_quote.copy()

        # Apply line item edits
        if "line_items" in user_edits:
            refined["line_items"] = user_edits["line_items"]

        # Recalculate subtotal
        if refined.get("line_items"):
            refined["subtotal"] = sum(
                item.get("amount", 0) for item in refined["line_items"]
            )

        # Apply other direct edits
        for key in ["job_description", "customer_name", "customer_address",
                    "customer_phone", "estimated_days", "estimated_crew_size", "notes"]:
            if key in user_edits:
                refined[key] = user_edits[key]

        refined["was_edited"] = True
        refined["edited_at"] = datetime.utcnow().isoformat()

        return refined


# Singleton pattern
_quote_service: Optional[QuoteGenerationService] = None


def get_quote_service() -> QuoteGenerationService:
    """Get the quote generation service singleton."""
    global _quote_service
    if _quote_service is None:
        _quote_service = QuoteGenerationService()
    return _quote_service
