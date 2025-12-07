"""
Quote generation service for Quoted.
This is the core service that synthesizes voice transcriptions into structured quotes.

Pipeline:
1. Receive transcribed text (or audio → transcribe first)
2. Load contractor's pricing model
3. Call Claude with tool calling for structured output
4. Validate response with Pydantic
5. Save and return

Enhancement 1: Uses Claude's native structured outputs via tool calling
instead of brittle regex JSON extraction.
"""

import json
import asyncio
import re
import statistics
from typing import Optional, List, Tuple
from datetime import datetime
from enum import Enum

import anthropic
from pydantic import BaseModel, Field, validator

from ..config import settings
from ..prompts import get_quote_generation_prompt


# ============================================================================
# Pydantic Schemas for Structured Output
# ============================================================================

class ConfidenceLevel(str, Enum):
    """Confidence levels for quote estimates."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LineItem(BaseModel):
    """A single line item in a quote."""
    name: str = Field(..., description="Item name (e.g., Demolition, Framing, Decking)")
    description: Optional[str] = Field(None, description="Brief description of this line item")
    amount: float = Field(..., ge=0, description="Dollar amount for this line item")
    quantity: Optional[float] = Field(1.0, ge=0, description="Quantity if applicable")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., sqft, hours)")

    @validator('amount', pre=True)
    def round_amount(cls, v):
        """Round amounts to whole dollars."""
        if v is not None:
            return round(float(v))
        return v


class QuoteOutput(BaseModel):
    """Structured output for a generated quote."""
    customer_name: Optional[str] = Field(None, description="Customer name if mentioned")
    customer_address: Optional[str] = Field(None, description="Customer address if mentioned")
    customer_phone: Optional[str] = Field(None, description="Customer phone if mentioned")
    job_type: str = Field(..., description="Detected job type (e.g., composite_deck, fence_wood)")
    job_description: str = Field(..., description="Professional 2-3 sentence description of the work")
    line_items: List[LineItem] = Field(..., min_items=1, description="Breakdown of quote into components")
    subtotal: float = Field(..., ge=0, description="Sum of all line items")
    notes: Optional[str] = Field(None, description="Notes about assumptions or what's NOT included")
    estimated_days: Optional[int] = Field(None, ge=0, description="Estimated days to complete")
    estimated_crew_size: Optional[int] = Field(None, ge=0, description="Estimated crew size needed")
    confidence: ConfidenceLevel = Field(ConfidenceLevel.MEDIUM, description="Confidence in this estimate")
    questions: List[str] = Field(default_factory=list, description="Clarifying questions for the contractor")

    @validator('subtotal', pre=True)
    def round_subtotal(cls, v):
        """Round subtotal to whole dollars."""
        if v is not None:
            return round(float(v))
        return v

    @validator('line_items')
    def validate_subtotal_matches(cls, v, values):
        """Recalculate subtotal from line items to ensure consistency."""
        # This runs after line_items is set but before subtotal validation
        return v


class VarianceConfidence(BaseModel):
    """
    Variance-based confidence metrics from multi-sample generation.
    Enhancement 3: Confidence Sampling.
    """
    num_samples: int = Field(..., description="Number of samples generated")
    total_variance: float = Field(..., description="Variance in total quote amount")
    total_std_dev: float = Field(..., description="Standard deviation in total")
    coefficient_of_variation: float = Field(..., description="CV = std_dev / mean (0-1 scale)")
    confidence_score: float = Field(..., ge=0, le=1, description="Derived confidence 0-1")
    confidence_level: ConfidenceLevel = Field(..., description="Derived confidence category")
    line_item_variances: dict = Field(default_factory=dict, description="Per-item variance")
    sample_totals: List[float] = Field(default_factory=list, description="All sample totals")
    notes: str = Field("", description="Human-readable confidence explanation")


# Tool definition for Claude's tool calling
QUOTE_GENERATION_TOOL = {
    "name": "generate_quote",
    "description": "Generate a structured quote from the contractor's voice note. Always use this tool to output the quote.",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_name": {
                "type": ["string", "null"],
                "description": "Customer name if mentioned in the voice note"
            },
            "customer_address": {
                "type": ["string", "null"],
                "description": "Customer address if mentioned"
            },
            "customer_phone": {
                "type": ["string", "null"],
                "description": "Customer phone if mentioned"
            },
            "job_type": {
                "type": "string",
                "description": "Detected job type (e.g., composite_deck, fence_wood, paint_exterior)"
            },
            "job_description": {
                "type": "string",
                "description": "Professional 2-3 sentence description of the work"
            },
            "line_items": {
                "type": "array",
                "description": "Breakdown of the quote into logical components",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Item name (e.g., Demolition, Framing, Decking)"
                        },
                        "description": {
                            "type": ["string", "null"],
                            "description": "Brief description of this line item"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Dollar amount for this line item"
                        },
                        "quantity": {
                            "type": ["number", "null"],
                            "description": "Quantity if applicable"
                        },
                        "unit": {
                            "type": ["string", "null"],
                            "description": "Unit of measurement (e.g., sqft, hours)"
                        }
                    },
                    "required": ["name", "amount"]
                },
                "minItems": 1
            },
            "subtotal": {
                "type": "number",
                "description": "Sum of all line items (should match)"
            },
            "notes": {
                "type": ["string", "null"],
                "description": "Notes about assumptions or what's NOT included"
            },
            "estimated_days": {
                "type": ["integer", "null"],
                "description": "Estimated days to complete the job"
            },
            "estimated_crew_size": {
                "type": ["integer", "null"],
                "description": "Estimated crew size needed"
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "Confidence level in this estimate"
            },
            "questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Clarifying questions for the contractor"
            }
        },
        "required": ["job_type", "job_description", "line_items", "subtotal", "confidence"]
    }
}


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
        detected_category: Optional[str] = None,
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
            detected_category: The detected category for this quote (for learned adjustments injection)

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
        # AND category-specific learned adjustments
        prompt = get_quote_generation_prompt(
            transcription=transcription,
            contractor_name=contractor.get("business_name", "Contractor"),
            pricing_model=pricing_model,
            pricing_notes=pricing_model.get("pricing_notes"),
            job_types=job_types,
            terms=terms,
            correction_examples=correction_examples,
            detected_category=detected_category,
        )

        # Call Claude with tool calling for structured output
        raw_quote = await self._call_claude_with_tool(prompt)

        # Validate and normalize the response
        quote_data = self._validate_and_normalize_quote(raw_quote)

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

    async def detect_or_create_category(
        self,
        transcription: str,
        pricing_knowledge: Optional[dict] = None,
    ) -> dict:
        """
        Dynamically detect or create a category from the transcription.
        Uses AI to match against existing user categories or create new ones.

        DISC-068: Now returns confidence score to detect when a new category
        should be created vs. forcing into an existing (wrong) category.

        Args:
            transcription: The transcribed voice note
            pricing_knowledge: User's pricing_knowledge dict with categories

        Returns:
            dict with:
            - category: The category name (snake_case)
            - is_new: Whether this is a newly created category
            - display_name: Human-readable name (for new categories)
            - category_confidence: 0-100 confidence score for the match
            - suggested_new_category: If confidence < 70, suggested new category name
        """
        # Get existing categories from user's pricing model
        existing_categories = []
        category_display_names = {}
        if pricing_knowledge and "categories" in pricing_knowledge:
            existing_categories = list(pricing_knowledge["categories"].keys())
            # Also get display names for context
            for cat_key, cat_data in pricing_knowledge["categories"].items():
                if isinstance(cat_data, dict):
                    category_display_names[cat_key] = cat_data.get("display_name", cat_key.replace("_", " ").title())

        # Build the detection prompt with confidence scoring
        if existing_categories:
            categories_list = "\n".join(f"- {cat} ({category_display_names.get(cat, cat)})" for cat in existing_categories)
            detection_prompt = f"""Categorize this work description. Rate your confidence in the match.

Description: "{transcription}"

Existing categories for this business:
{categories_list}

IMPORTANT: Be HONEST about confidence. If this work doesn't clearly fit an existing category, say so.

Confidence scoring guide:
- 90-100: Perfect match (same type of work, clear fit)
- 70-89: Good match (related work, reasonable fit)
- 50-69: Weak match (some similarity but different enough to warrant a new category)
- 0-49: Poor match (should definitely be a new category)

If confidence is BELOW 70, also suggest what new category this should be.

Return JSON only:
{{
  "category": "category_name",
  "is_new": false,
  "display_name": "Human Readable Name",
  "category_confidence": 85,
  "suggested_new_category": null
}}

OR if it doesn't fit well:
{{
  "category": "closest_existing_category",
  "is_new": false,
  "display_name": "Closest Match",
  "category_confidence": 45,
  "suggested_new_category": "new_category_name"
}}

OR if no existing categories are close at all:
{{
  "category": "new_snake_case_name",
  "is_new": true,
  "display_name": "Human Readable Name",
  "category_confidence": 95,
  "suggested_new_category": null
}}"""
        else:
            # No existing categories - create the first one
            detection_prompt = f"""Analyze this work description and create a category for it.

Description: "{transcription}"

Create a short snake_case category name for this type of work:
- Keep it general (e.g., "brand_strategy" not "full_brand_identity_package")
- 2-3 words max

Return JSON only:
{{
  "category": "category_name",
  "is_new": true,
  "display_name": "Human Readable Name",
  "category_confidence": 95,
  "suggested_new_category": null
}}"""

        try:
            # Use haiku for speed and cost - this is just classification
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": detection_prompt}],
            )
            response_text = message.content[0].text.strip()

            # Parse JSON response - handle multi-line JSON
            import json
            # Find JSON in response (including multi-line)
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                # Ensure snake_case and lowercase
                result["category"] = result["category"].lower().replace(" ", "_").replace("-", "_")
                # Ensure confidence is present
                if "category_confidence" not in result:
                    result["category_confidence"] = 70 if not result.get("is_new") else 95
                if "suggested_new_category" not in result:
                    result["suggested_new_category"] = None
                return result

            # Fallback if JSON parsing fails
            return {
                "category": "general",
                "is_new": True,
                "display_name": "General",
                "category_confidence": 50,
                "suggested_new_category": None
            }

        except Exception as e:
            # On error, return general - don't block quote generation
            print(f"[CATEGORY DETECTION ERROR] {e}")
            return {
                "category": "general",
                "is_new": True,
                "display_name": "General",
                "category_confidence": 50,
                "suggested_new_category": None
            }

    async def detect_job_type(
        self,
        transcription: str,
        pricing_knowledge: Optional[dict] = None,
    ) -> str:
        """
        Wrapper for backwards compatibility.
        Calls detect_or_create_category and returns just the category name.
        """
        result = await self.detect_or_create_category(transcription, pricing_knowledge)
        return result["category"]

    async def _call_claude_with_tool(self, prompt: str) -> dict:
        """
        Make a call to Claude API using tool calling for structured output.

        This replaces the old regex-based JSON extraction with Claude's
        native structured outputs, guaranteeing valid JSON matching our schema.
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                tools=[QUOTE_GENERATION_TOOL],
                tool_choice={"type": "tool", "name": "generate_quote"},
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extract the tool call result
            for block in message.content:
                if block.type == "tool_use" and block.name == "generate_quote":
                    return block.input

            # Fallback if no tool call (shouldn't happen with tool_choice)
            raise ValueError("No tool call found in response")

        except anthropic.BadRequestError as e:
            # Handle cases where tool calling fails
            raise Exception(f"Claude tool calling error: {str(e)}")
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def _validate_and_normalize_quote(self, raw_quote: dict) -> dict:
        """
        Validate raw quote data against Pydantic schema and normalize.

        This provides a second layer of validation after Claude's tool schema,
        ensuring data types, recalculating subtotals, and handling edge cases.
        """
        try:
            # Validate through Pydantic model
            validated = QuoteOutput(**raw_quote)

            # Convert to dict and recalculate subtotal from line items
            quote_dict = validated.dict()

            # Ensure subtotal matches sum of line items
            calculated_subtotal = sum(
                item.get("amount", 0) for item in quote_dict.get("line_items", [])
            )
            quote_dict["subtotal"] = round(calculated_subtotal)

            # Convert confidence enum to string
            if isinstance(quote_dict.get("confidence"), ConfidenceLevel):
                quote_dict["confidence"] = quote_dict["confidence"].value

            return quote_dict

        except Exception as e:
            # If validation fails, return with error flag
            return {
                "error": f"Quote validation failed: {str(e)}",
                "raw_data": raw_quote,
                "job_description": raw_quote.get("job_description", "Please review and edit manually"),
                "line_items": raw_quote.get("line_items", []),
                "subtotal": raw_quote.get("subtotal", 0),
                "confidence": "low",
                "questions": ["Quote validation had issues - please review manually"],
            }

    # =========================================================================
    # Enhancement 3: Confidence Sampling - Multi-sample variance estimation
    # =========================================================================

    async def generate_quote_with_confidence(
        self,
        transcription: str,
        contractor: dict,
        pricing_model: dict,
        job_types: Optional[list] = None,
        terms: Optional[dict] = None,
        correction_examples: Optional[list] = None,
        detected_category: Optional[str] = None,
        num_samples: int = 3,
    ) -> Tuple[dict, VarianceConfidence]:
        """
        Generate a quote with data-driven confidence from multi-sample variance.

        Calls Claude N times (default 3), calculates variance across line items,
        returns the median quote with variance-based confidence metrics.

        Args:
            transcription: The transcribed voice note
            contractor: Contractor data
            pricing_model: Pricing model
            job_types: Job types
            terms: Terms and conditions
            correction_examples: Past corrections for learning
            detected_category: Detected category
            num_samples: Number of samples to generate (default 3)

        Returns:
            Tuple of (median_quote, variance_confidence_metrics)
        """
        # Build the prompt once
        prompt = get_quote_generation_prompt(
            transcription=transcription,
            contractor_name=contractor.get("business_name", "Contractor"),
            pricing_model=pricing_model,
            pricing_notes=pricing_model.get("pricing_notes"),
            job_types=job_types,
            terms=terms,
            correction_examples=correction_examples,
            detected_category=detected_category,
        )

        # Generate multiple samples concurrently
        samples = await self._generate_multiple_samples(prompt, num_samples)

        if not samples:
            # Fallback: generate single quote
            single_quote = await self.generate_quote(
                transcription, contractor, pricing_model,
                job_types, terms, correction_examples, detected_category
            )
            fallback_confidence = VarianceConfidence(
                num_samples=1,
                total_variance=0,
                total_std_dev=0,
                coefficient_of_variation=0,
                confidence_score=0.5,
                confidence_level=ConfidenceLevel.LOW,
                line_item_variances={},
                sample_totals=[single_quote.get("subtotal", 0)],
                notes="Single sample only - multi-sample generation failed"
            )
            return single_quote, fallback_confidence

        # Calculate variance-based confidence
        confidence_metrics = self._calculate_variance_confidence(samples)

        # Select the median quote (by total)
        median_quote = self._select_median_quote(samples)

        # Override the AI's self-reported confidence with our data-driven confidence
        median_quote["confidence"] = confidence_metrics.confidence_level.value
        median_quote["variance_confidence"] = confidence_metrics.dict()

        # Add metadata
        median_quote["generated_at"] = datetime.utcnow().isoformat()
        median_quote["transcription"] = transcription
        median_quote["ai_generated_total"] = median_quote.get("subtotal", 0)
        median_quote["num_samples"] = num_samples

        return median_quote, confidence_metrics

    async def _generate_multiple_samples(
        self,
        prompt: str,
        num_samples: int = 3,
    ) -> List[dict]:
        """
        Generate multiple quote samples concurrently.

        Uses asyncio.gather to parallelize API calls for efficiency.
        """
        async def generate_one() -> Optional[dict]:
            try:
                raw_quote = await self._call_claude_with_tool(prompt)
                return self._validate_and_normalize_quote(raw_quote)
            except Exception as e:
                print(f"Sample generation failed: {e}")
                return None

        # Create tasks for concurrent execution
        tasks = [generate_one() for _ in range(num_samples)]
        results = await asyncio.gather(*tasks)

        # Filter out failed samples
        valid_samples = [r for r in results if r is not None and "error" not in r]

        return valid_samples

    def _calculate_variance_confidence(
        self,
        samples: List[dict],
    ) -> VarianceConfidence:
        """
        Calculate variance-based confidence from multiple samples.

        Key insight: High variance across samples = low confidence.
        The model is uncertain when it gives different answers for the same input.
        """
        if not samples:
            return VarianceConfidence(
                num_samples=0,
                total_variance=0,
                total_std_dev=0,
                coefficient_of_variation=1.0,
                confidence_score=0.0,
                confidence_level=ConfidenceLevel.LOW,
                line_item_variances={},
                sample_totals=[],
                notes="No valid samples"
            )

        # Calculate total variance
        totals = [s.get("subtotal", 0) for s in samples]
        mean_total = statistics.mean(totals) if totals else 0

        if len(totals) >= 2:
            total_variance = statistics.variance(totals)
            total_std_dev = statistics.stdev(totals)
        else:
            total_variance = 0
            total_std_dev = 0

        # Coefficient of variation (normalized std dev)
        cv = (total_std_dev / mean_total) if mean_total > 0 else 0

        # Calculate per-line-item variance
        line_item_variances = self._calculate_line_item_variances(samples)

        # Derive confidence score from CV
        # CV < 0.05 (5%) = HIGH confidence
        # CV 0.05-0.15 (5-15%) = MEDIUM confidence
        # CV > 0.15 (15%+) = LOW confidence
        if cv < 0.05:
            confidence_score = 0.9 + (0.05 - cv) * 2  # 0.9-1.0
            confidence_level = ConfidenceLevel.HIGH
            notes = f"High agreement across {len(samples)} samples (CV={cv:.1%})"
        elif cv < 0.15:
            confidence_score = 0.6 + (0.15 - cv) * 3  # 0.6-0.9
            confidence_level = ConfidenceLevel.MEDIUM
            notes = f"Moderate variance across {len(samples)} samples (CV={cv:.1%})"
        else:
            confidence_score = max(0.1, 0.6 - (cv - 0.15) * 2)  # 0.1-0.6
            confidence_level = ConfidenceLevel.LOW
            notes = f"High variance across {len(samples)} samples (CV={cv:.1%}) - review carefully"

        # Add details about high-variance line items
        high_variance_items = [
            k for k, v in line_item_variances.items()
            if v.get("cv", 0) > 0.2  # 20% CV threshold
        ]
        if high_variance_items:
            notes += f". High variance items: {', '.join(high_variance_items)}"

        return VarianceConfidence(
            num_samples=len(samples),
            total_variance=round(total_variance, 2),
            total_std_dev=round(total_std_dev, 2),
            coefficient_of_variation=round(cv, 4),
            confidence_score=round(min(1.0, max(0.0, confidence_score)), 2),
            confidence_level=confidence_level,
            line_item_variances=line_item_variances,
            sample_totals=totals,
            notes=notes
        )

    def _calculate_line_item_variances(
        self,
        samples: List[dict],
    ) -> dict:
        """
        Calculate variance for each line item across samples.
        """
        # Collect amounts by line item name
        item_amounts: dict = {}
        for sample in samples:
            for item in sample.get("line_items", []):
                name = item.get("name", "Unknown")
                amount = item.get("amount", 0)
                if name not in item_amounts:
                    item_amounts[name] = []
                item_amounts[name].append(amount)

        # Calculate variance for each
        variances = {}
        for name, amounts in item_amounts.items():
            if len(amounts) >= 2:
                mean_amt = statistics.mean(amounts)
                std_dev = statistics.stdev(amounts)
                cv = (std_dev / mean_amt) if mean_amt > 0 else 0
                variances[name] = {
                    "mean": round(mean_amt, 2),
                    "std_dev": round(std_dev, 2),
                    "cv": round(cv, 4),
                    "samples": len(amounts),
                }
            elif len(amounts) == 1:
                variances[name] = {
                    "mean": amounts[0],
                    "std_dev": 0,
                    "cv": 0,
                    "samples": 1,
                }

        return variances

    def _select_median_quote(
        self,
        samples: List[dict],
    ) -> dict:
        """
        Select the median quote by total amount.

        The median is more robust to outliers than the mean.
        """
        if not samples:
            return {}

        if len(samples) == 1:
            return samples[0]

        # Sort by subtotal
        sorted_samples = sorted(
            samples,
            key=lambda s: s.get("subtotal", 0)
        )

        # Pick the middle one (or lower-middle for even counts)
        median_idx = len(sorted_samples) // 2
        return sorted_samples[median_idx]

    # =========================================================================
    # End Enhancement 3
    # =========================================================================

    # =========================================================================
    # Enhancement 5: Active Learning - Clarifying Questions
    # =========================================================================

    async def generate_clarifying_questions(
        self,
        transcription: str,
        contractor: dict,
        pricing_model: dict,
        confidence_level: str = "low",
        max_questions: int = 3,
    ) -> dict:
        """
        Generate clarifying questions when confidence is low.

        Used for Active Learning: Instead of guessing, ask the user
        for critical information that would improve estimate accuracy.

        Args:
            transcription: The original transcription
            contractor: Contractor data
            pricing_model: Pricing model
            confidence_level: Current confidence ("low" triggers most questions)
            max_questions: Maximum number of questions to generate

        Returns:
            dict with:
            - questions: List of question dicts with id, question, type, options
            - reasoning: Why these questions are important
            - missing_info: What specific info is missing
        """
        prompt = f"""You are a quote estimation expert for a {contractor.get('primary_trade', 'contractor')}.

The following job description has {confidence_level} confidence for accurate estimation.

## Job Description:
"{transcription}"

## Your Task:
Identify the TOP {max_questions} most critical pieces of missing information that would
significantly improve the accuracy of the estimate.

For each question:
1. Make it specific and answerable
2. Explain why this information matters for pricing
3. Provide options if applicable (makes it easier to answer)
4. Prioritize by impact on estimate accuracy

Categories to consider:
- **Scope**: Size, dimensions, quantities
- **Materials**: Brand/quality level, existing conditions
- **Access**: Site accessibility, working conditions
- **Timeline**: Urgency, scheduling constraints
- **Existing conditions**: Demo required, repairs needed, complications

Output a JSON object with this structure:
{{
    "questions": [
        {{
            "id": "q1",
            "question": "What is the approximate deck size in square feet?",
            "type": "select|text|number",
            "options": ["Under 200 sq ft", "200-400 sq ft", "400-600 sq ft", "Over 600 sq ft"],
            "impact": "Size directly affects material quantities and labor hours",
            "default_assumption": "Assuming 300 sq ft if not specified"
        }}
    ],
    "reasoning": "Why these questions were chosen",
    "missing_info": ["deck size", "material grade", "...]
}}

Generate exactly {max_questions} high-impact questions."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text.strip()

            # Parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())

            return {
                "questions": [],
                "reasoning": "Failed to generate questions",
                "missing_info": [],
            }

        except Exception as e:
            return {
                "questions": [],
                "reasoning": f"Error generating questions: {e}",
                "missing_info": [],
            }

    async def generate_quote_with_clarifications(
        self,
        transcription: str,
        clarifications: List[dict],
        contractor: dict,
        pricing_model: dict,
        job_types: Optional[list] = None,
        terms: Optional[dict] = None,
    ) -> dict:
        """
        Generate a quote incorporating user's answers to clarifying questions.

        Args:
            transcription: Original job description
            clarifications: List of {question_id, question, answer} dicts
            contractor: Contractor data
            pricing_model: Pricing model
            job_types: Job types
            terms: Terms

        Returns:
            Quote dict with improved accuracy from clarifications
        """
        # Build enhanced transcription with clarifications
        clarification_text = "\n".join([
            f"- {c.get('question', 'Question')}: {c.get('answer', 'No answer')}"
            for c in clarifications
        ])

        enhanced_transcription = f"""{transcription}

ADDITIONAL CLARIFICATIONS FROM CUSTOMER:
{clarification_text}"""

        # Generate quote with enhanced context
        return await self.generate_quote(
            transcription=enhanced_transcription,
            contractor=contractor,
            pricing_model=pricing_model,
            job_types=job_types,
            terms=terms,
        )

    def should_request_clarifications(
        self,
        quote_data: dict,
        confidence_threshold: str = "low",
    ) -> bool:
        """
        Determine if we should request clarifications based on confidence.

        Returns True if confidence is at or below threshold.
        """
        confidence = quote_data.get("confidence", "medium")
        confidence_order = {"low": 0, "medium": 1, "high": 2}

        current = confidence_order.get(confidence, 1)
        threshold = confidence_order.get(confidence_threshold, 0)

        return current <= threshold

    # =========================================================================
    # End Enhancement 5
    # =========================================================================

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
