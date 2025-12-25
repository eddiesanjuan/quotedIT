# Phase 5: Contractor DNA - Cross-Category Intelligence System

*Agent: contractor-dna-designer | Completed: 2025-12-24*

---

## Executive Summary

**What**: A cross-category intelligence system that identifies transferable pricing patterns within a single contractor's profile, creating a "Contractor DNA" that accelerates learning for new categories.

**Why**: A contractor who adds 15% for "second story" deck access will likely apply similar premiums across ALL job types (roofing, painting, siding). Currently, each category learns in isolation. This wastes the contractor's time re-teaching the same patterns.

**Impact**:
- **Cold start acceleration**: New categories bootstrap from existing DNA at 40-60% confidence
- **Consistency enforcement**: Prevents "I charge 15% for second story decks but forgot about roofing"
- **Faster convergence**: Reach 80% confidence in 3-5 quotes instead of 10-15

**Key Principle**: Patterns transfer at LOWER confidence. Each new category validates or overrides transferred patterns through its own corrections.

---

## 1. Contractor Pricing Profile Schema

### 1.1 Core Data Structure

```python
from typing import TypedDict, List, Optional, Literal
from datetime import datetime

class TransferablePattern(TypedDict):
    """A single pattern that can transfer between categories."""
    pattern_id: str  # Unique ID (UUID)
    pattern_type: str  # "access_modifier", "relationship_discount", "rush_premium", etc.
    statement: str  # The actual learning statement

    # Source tracking
    source_category: str  # Where this originated
    source_confidence: float  # Confidence in source category
    source_quote_count: int  # How many quotes validated this in source

    # Pattern metadata
    keywords: List[str]  # ["second story", "access", "difficult"]
    numeric_value: Optional[float]  # Extracted % or $ if applicable
    transferability: Literal["universal", "partial", "specific"]  # How broadly it transfers

    # History
    created_at: str  # ISO timestamp
    last_validated_at: str  # Most recent confirmation


class ContractorDNA(TypedDict):
    """Complete DNA profile for a contractor."""
    contractor_id: str

    # Universal patterns (transfer to ALL categories)
    universal_patterns: List[TransferablePattern]
    # Examples: "Repeat customer -5%", "ASAP +20%", "Second story +15%"

    # Partial patterns (transfer to SOME categories)
    partial_patterns: List[TransferablePattern]
    # Examples: "Premium materials +20%" (material quality orientation)

    # Pricing style profile
    pricing_style: dict
    """
    {
        "overall_tendency": "conservative" | "aggressive" | "balanced",
        "avg_markup": 0.25,  # Calculated from all categories
        "quality_orientation": "premium" | "budget" | "mid_range",
        "confidence_in_profile": 0.75  # How much data we have
    }
    """

    # Common modifiers across categories
    common_modifiers: List[dict]
    """
    [
        {
            "trigger_keyword": "second story",
            "modifier_type": "percentage_increase",
            "avg_modifier": 0.15,
            "category_count": 3,  # Applied in 3 categories
            "categories": ["deck", "roofing", "painting"]
        }
    ]
    """

    # Timing patterns
    timing_patterns: List[dict]
    """
    [
        {
            "trigger": "ASAP",
            "premium": 0.20,
            "category_count": 5
        },
        {
            "trigger": "winter",
            "adjustment": -0.10,  # Winter discount
            "category_count": 2
        }
    ]
    """

    # Relationship patterns
    relationship_patterns: List[dict]
    """
    [
        {
            "trigger": "repeat customer",
            "discount": 0.05,
            "category_count": 4
        }
    ]
    """

    # Metadata
    total_categories: int  # How many categories have data
    total_corrections: int  # Total corrections across all categories
    dna_confidence: float  # Overall DNA quality (0.0-1.0)
    last_updated_at: str  # ISO timestamp
```

### 1.2 Database Integration

**Add to `PricingModel` table** (`backend/models/database.py` line 136):

```python
# Contractor DNA (cross-category intelligence)
contractor_dna = Column(JSON, default=dict)
"""
Stores ContractorDNA TypedDict as JSON.
Updated after each correction to extract transferable patterns.
"""
```

**No schema changes needed** - this is a pure JSON blob addition to existing `pricing_models` table.

---

## 2. Pattern Transfer Algorithm

### 2.1 Core Transfer Logic

```python
# backend/services/contractor_dna.py (NEW FILE)

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class TransferCandidate:
    """A pattern being considered for transfer."""
    pattern: TransferablePattern
    target_category: str
    inherited_confidence: float
    transfer_reason: str  # Why we think this transfers


class ContractorDNAService:
    """Manages contractor DNA patterns and cross-category intelligence."""

    def identify_transferable_patterns(
        self,
        source_category: str,
        source_learnings: List[str],
        source_confidence: float,
        source_quote_count: int,
        target_category: str,
    ) -> List[TransferCandidate]:
        """
        Identify which learnings from source category should transfer to target.

        Pattern transferability tiers:
        1. UNIVERSAL: Transfers to ALL categories at 60% source confidence
           - Access difficulty ("second story +15%")
           - Relationship discounts ("repeat customer -5%")
           - Rush premiums ("ASAP +20%")
           - Timeline modifiers ("winter work +10%")

        2. PARTIAL: Transfers to RELATED categories at 40% source confidence
           - Material quality preferences ("premium materials +20%")
           - Job size scaling ("small jobs +15% minimum")

        3. SPECIFIC: DO NOT transfer (category-specific pricing)
           - Absolute prices ("deck framing $2,800")
           - Material costs ("Trex composite $6.50/sqft")
           - Labor hours ("3-day timeline")
        """
        candidates = []

        for learning in source_learnings:
            # Classify pattern
            pattern_type, transferability = self._classify_pattern(learning)

            if transferability == "specific":
                continue  # Don't transfer category-specific patterns

            # Check if pattern applies to target category
            if transferability == "universal":
                # Always transfer
                inherited_conf = source_confidence * 0.60
                reason = f"Universal pattern from {source_category}"

            elif transferability == "partial":
                # Transfer only if categories are related
                if self._categories_related(source_category, target_category):
                    inherited_conf = source_confidence * 0.40
                    reason = f"Partial pattern from related category {source_category}"
                else:
                    continue  # Skip unrelated categories
            else:
                continue

            # Create transfer candidate
            pattern = TransferablePattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type=pattern_type,
                statement=learning,
                source_category=source_category,
                source_confidence=source_confidence,
                source_quote_count=source_quote_count,
                keywords=self._extract_keywords(learning),
                numeric_value=self._extract_numeric_value(learning),
                transferability=transferability,
                created_at=datetime.utcnow().isoformat(),
                last_validated_at=datetime.utcnow().isoformat(),
            )

            candidates.append(TransferCandidate(
                pattern=pattern,
                target_category=target_category,
                inherited_confidence=inherited_conf,
                transfer_reason=reason,
            ))

        return candidates


    def _classify_pattern(self, statement: str) -> tuple[str, str]:
        """
        Classify a learning statement into pattern type and transferability.

        Returns: (pattern_type, transferability)
        """
        statement_lower = statement.lower()

        # UNIVERSAL PATTERNS (transfer to all categories)
        if any(kw in statement_lower for kw in ["second story", "difficult access", "steep", "ladder"]):
            return ("access_modifier", "universal")

        if any(kw in statement_lower for kw in ["repeat customer", "returning", "previous client"]):
            return ("relationship_discount", "universal")

        if any(kw in statement_lower for kw in ["asap", "rush", "urgent", "emergency"]):
            return ("rush_premium", "universal")

        if any(kw in statement_lower for kw in ["winter", "summer", "rainy season", "off-season"]):
            return ("seasonal_adjustment", "universal")

        if any(kw in statement_lower for kw in ["permit", "inspection"]):
            return ("permit_handling", "universal")

        # PARTIAL PATTERNS (transfer to related categories)
        if any(kw in statement_lower for kw in ["premium", "high-end", "luxury", "top quality"]):
            return ("quality_preference", "partial")

        if any(kw in statement_lower for kw in ["small job", "minimum", "trip charge"]):
            return ("minimum_pricing", "partial")

        if any(kw in statement_lower for kw in ["material markup", "markup on materials"]):
            return ("material_markup", "partial")

        # SPECIFIC PATTERNS (do not transfer)
        if any(kw in statement_lower for kw in ["deck", "railing", "composite", "pt lumber"]):
            return ("category_specific_material", "specific")

        if re.search(r'\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*per|\s*/)', statement):
            # Contains absolute pricing (e.g., "$45/sqft", "$2,800 per deck")
            return ("absolute_pricing", "specific")

        if any(kw in statement_lower for kw in ["sqft", "linear foot", "lf", "square"]):
            # Contains unit-based pricing
            return ("unit_pricing", "specific")

        # Default to partial (conservative)
        return ("general_adjustment", "partial")


    def _categories_related(self, cat1: str, cat2: str) -> bool:
        """Check if two categories are related (for partial pattern transfer)."""
        # Define category relationships
        RELATED_GROUPS = [
            {"deck", "fence", "pergola", "gazebo"},  # Outdoor structures
            {"roofing", "siding", "gutters"},  # Exterior
            {"painting_interior", "painting_exterior", "staining"},  # Coatings
            {"flooring", "tile", "carpet"},  # Flooring
            {"landscaping", "irrigation", "hardscaping"},  # Outdoor
        ]

        for group in RELATED_GROUPS:
            if cat1 in group and cat2 in group:
                return True

        return False


    def _extract_keywords(self, statement: str) -> List[str]:
        """Extract key terms from learning statement."""
        # Simple keyword extraction (can be enhanced with NLP)
        keywords = []

        # Common pricing trigger words
        triggers = [
            "second story", "difficult access", "repeat customer", "asap",
            "rush", "premium", "winter", "summer", "permit", "steep"
        ]

        statement_lower = statement.lower()
        for trigger in triggers:
            if trigger in statement_lower:
                keywords.append(trigger)

        return keywords


    def _extract_numeric_value(self, statement: str) -> Optional[float]:
        """Extract percentage or dollar amount from statement."""
        import re

        # Try to extract percentage
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', statement)
        if pct_match:
            return float(pct_match.group(1)) / 100.0  # Convert to decimal

        # Try to extract dollar amount
        dollar_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', statement)
        if dollar_match:
            return float(dollar_match.group(1).replace(',', ''))

        return None
```

### 2.2 Bootstrap Algorithm (Cold Start Acceleration)

```python
class ContractorDNAService:
    # ... (continued)

    def generate_category_bootstrap(
        self,
        contractor_id: str,
        new_category: str,
        contractor_dna: ContractorDNA,
    ) -> List[dict]:
        """
        Generate bootstrap pricing for a new category using DNA.

        Returns list of learnings to inject with inherited confidence.
        """
        bootstrap_learnings = []

        # 1. ALWAYS inject universal patterns
        for pattern in contractor_dna["universal_patterns"]:
            inherited_conf = self._calculate_inherited_confidence(
                source_confidence=pattern["source_confidence"],
                source_quote_count=pattern["source_quote_count"],
                pattern_type="universal",
            )

            bootstrap_learnings.append({
                "statement": pattern["statement"],
                "confidence": inherited_conf,
                "source": f"DNA from {pattern['source_category']}",
                "pattern_type": pattern["pattern_type"],
                "transferred": True,  # Flag as transferred
            })

        # 2. Inject partial patterns if categories are related
        for pattern in contractor_dna["partial_patterns"]:
            if self._categories_related(pattern["source_category"], new_category):
                inherited_conf = self._calculate_inherited_confidence(
                    source_confidence=pattern["source_confidence"],
                    source_quote_count=pattern["source_quote_count"],
                    pattern_type="partial",
                )

                bootstrap_learnings.append({
                    "statement": pattern["statement"],
                    "confidence": inherited_conf,
                    "source": f"DNA from {pattern['source_category']}",
                    "pattern_type": pattern["pattern_type"],
                    "transferred": True,
                })

        # 3. Add pricing style guidelines
        style = contractor_dna["pricing_style"]
        if style["overall_tendency"] == "conservative":
            bootstrap_learnings.append({
                "statement": "You tend to price conservatively - better to quote high and come in under budget",
                "confidence": style["confidence_in_profile"],
                "source": "DNA pricing style",
                "pattern_type": "pricing_philosophy",
                "transferred": True,
            })

        return bootstrap_learnings


    def _calculate_inherited_confidence(
        self,
        source_confidence: float,
        source_quote_count: int,
        pattern_type: str,
    ) -> float:
        """
        Calculate confidence for inherited pattern.

        Rules:
        - Universal patterns: inherit at 60% of source confidence
        - Partial patterns: inherit at 40% of source confidence
        - Minimum confidence: 0.30 (even weak signals are useful)
        - Maximum confidence: 0.70 (never 100% confident on transfer)
        """
        if pattern_type == "universal":
            base_inheritance = 0.60
        elif pattern_type == "partial":
            base_inheritance = 0.40
        else:
            base_inheritance = 0.30

        inherited = source_confidence * base_inheritance

        # Adjust for source data quality
        if source_quote_count < 3:
            inherited *= 0.7  # Penalize weak source data
        elif source_quote_count > 10:
            inherited *= 1.1  # Boost well-validated patterns

        # Clamp to safe range
        return max(0.30, min(0.70, inherited))
```

---

## 3. DNA Building from Corrections

### 3.1 Update DNA After Each Correction

**Integration point**: `backend/services/learning.py` line 117

```python
# backend/services/learning.py

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
    """Process correction and update THREE-LAYER + DNA."""

    # ... existing correction processing ...

    # NEW: Update contractor DNA
    if contractor_id and category:
        from .contractor_dna import get_dna_service
        dna_service = get_dna_service()

        await dna_service.update_dna_from_correction(
            contractor_id=contractor_id,
            category=category,
            new_learnings=learnings.get("learning_statements", []),
            category_confidence=existing_category_confidence,  # From pricing_knowledge
            category_quote_count=existing_quote_count,
        )

    return {
        "has_changes": True,
        "corrections": corrections,
        "learnings": learnings,
        "processed_at": datetime.utcnow().isoformat(),
    }
```

### 3.2 DNA Update Service

```python
# backend/services/contractor_dna.py (continued)

class ContractorDNAService:
    # ... (continued)

    async def update_dna_from_correction(
        self,
        contractor_id: str,
        category: str,
        new_learnings: List[str],
        category_confidence: float,
        category_quote_count: int,
    ):
        """
        Update contractor DNA after a correction is processed.

        Workflow:
        1. Extract transferable patterns from new learnings
        2. Merge with existing DNA (avoid duplicates)
        3. Recalculate DNA confidence
        4. Save updated DNA to pricing_model
        """
        from ..models.database import PricingModel
        from ..db import get_db

        async with get_db() as db:
            # Get current pricing model
            pricing_model = await db.query(PricingModel).filter(
                PricingModel.contractor_id == contractor_id
            ).first()

            if not pricing_model:
                return

            # Get current DNA
            current_dna = pricing_model.contractor_dna or self._empty_dna(contractor_id)

            # Extract transferable patterns from new learnings
            new_patterns = []
            for learning in new_learnings:
                pattern_type, transferability = self._classify_pattern(learning)

                if transferability in ["universal", "partial"]:
                    pattern = TransferablePattern(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type=pattern_type,
                        statement=learning,
                        source_category=category,
                        source_confidence=category_confidence,
                        source_quote_count=category_quote_count,
                        keywords=self._extract_keywords(learning),
                        numeric_value=self._extract_numeric_value(learning),
                        transferability=transferability,
                        created_at=datetime.utcnow().isoformat(),
                        last_validated_at=datetime.utcnow().isoformat(),
                    )
                    new_patterns.append(pattern)

            # Merge with existing DNA (avoid duplicates)
            updated_dna = self._merge_patterns(current_dna, new_patterns, category)

            # Recalculate DNA confidence
            updated_dna["dna_confidence"] = self._calculate_dna_confidence(updated_dna)
            updated_dna["last_updated_at"] = datetime.utcnow().isoformat()

            # Save
            pricing_model.contractor_dna = updated_dna
            await db.commit()


    def _merge_patterns(
        self,
        current_dna: ContractorDNA,
        new_patterns: List[TransferablePattern],
        source_category: str,
    ) -> ContractorDNA:
        """Merge new patterns into existing DNA, avoiding duplicates."""

        for new_pattern in new_patterns:
            # Check for duplicates (same statement + pattern_type)
            is_duplicate = False

            if new_pattern["transferability"] == "universal":
                target_list = current_dna["universal_patterns"]
            else:
                target_list = current_dna["partial_patterns"]

            for existing in target_list:
                if (existing["statement"] == new_pattern["statement"] and
                    existing["pattern_type"] == new_pattern["pattern_type"]):
                    # Update existing pattern (increase confidence if validated in new category)
                    existing["last_validated_at"] = new_pattern["last_validated_at"]
                    is_duplicate = True
                    break

            if not is_duplicate:
                target_list.append(new_pattern)

        # Update metadata
        current_dna["total_corrections"] += 1

        # Track unique categories
        categories_with_data = set()
        for pattern in current_dna["universal_patterns"] + current_dna["partial_patterns"]:
            categories_with_data.add(pattern["source_category"])
        current_dna["total_categories"] = len(categories_with_data)

        return current_dna


    def _calculate_dna_confidence(self, dna: ContractorDNA) -> float:
        """
        Calculate overall DNA quality score.

        Based on:
        - Number of categories with data
        - Number of universal patterns
        - Average source confidence
        """
        category_count = dna["total_categories"]
        universal_count = len(dna["universal_patterns"])

        # More categories = better DNA
        category_score = min(1.0, category_count / 5.0)  # Max at 5 categories

        # More universal patterns = better DNA
        pattern_score = min(1.0, universal_count / 10.0)  # Max at 10 patterns

        # Average confidence of patterns
        all_patterns = dna["universal_patterns"] + dna["partial_patterns"]
        if all_patterns:
            avg_confidence = sum(p["source_confidence"] for p in all_patterns) / len(all_patterns)
        else:
            avg_confidence = 0.5

        # Weighted combination
        dna_confidence = (
            category_score * 0.4 +
            pattern_score * 0.3 +
            avg_confidence * 0.3
        )

        return round(dna_confidence, 2)


    def _empty_dna(self, contractor_id: str) -> ContractorDNA:
        """Create empty DNA structure."""
        return {
            "contractor_id": contractor_id,
            "universal_patterns": [],
            "partial_patterns": [],
            "pricing_style": {
                "overall_tendency": "balanced",
                "avg_markup": 0.20,
                "quality_orientation": "mid_range",
                "confidence_in_profile": 0.0,
            },
            "common_modifiers": [],
            "timing_patterns": [],
            "relationship_patterns": [],
            "total_categories": 0,
            "total_corrections": 0,
            "dna_confidence": 0.0,
            "last_updated_at": datetime.utcnow().isoformat(),
        }


# Singleton
_dna_service: Optional[ContractorDNAService] = None

def get_dna_service() -> ContractorDNAService:
    global _dna_service
    if _dna_service is None:
        _dna_service = ContractorDNAService()
    return _dna_service
```

---

## 4. Integration with Quote Generation

### 4.1 Inject DNA Patterns for New Categories

**Integration point**: `backend/prompts/quote_generation.py` line 59

```python
# backend/prompts/quote_generation.py

def get_quote_generation_prompt(
    transcription: str,
    contractor_name: str,
    pricing_model: dict,
    pricing_notes: Optional[str] = None,
    job_types: Optional[list] = None,
    terms: Optional[dict] = None,
    correction_examples: Optional[list] = None,
    detected_category: Optional[str] = None,
) -> str:
    """Generate quote prompt with DNA bootstrapping for new categories."""

    pricing_knowledge = pricing_model.get("pricing_knowledge", {})

    # Check if this is a NEW category (no learnings yet)
    is_new_category = False
    if detected_category and "categories" in pricing_knowledge:
        cat_data = pricing_knowledge["categories"].get(detected_category, {})
        learned_adjustments = cat_data.get("learned_adjustments", [])

        if len(learned_adjustments) == 0:
            is_new_category = True

    # If new category, bootstrap from DNA
    dna_bootstrap_str = ""
    if is_new_category and pricing_model.get("contractor_dna"):
        from backend.services.contractor_dna import get_dna_service
        dna_service = get_dna_service()

        contractor_dna = pricing_model["contractor_dna"]
        bootstrap_learnings = dna_service.generate_category_bootstrap(
            contractor_id=pricing_model.get("contractor_id"),
            new_category=detected_category,
            contractor_dna=contractor_dna,
        )

        if bootstrap_learnings:
            dna_statements = []
            for learning in bootstrap_learnings:
                conf = learning["confidence"]
                statement = learning["statement"]
                source = learning["source"]
                dna_statements.append(
                    f"- {statement} (Confidence: {conf:.0%}, {source})"
                )

            dna_bootstrap_str = f"""
## 🧬 DNA Bootstrap for New Category "{detected_category}"

This is your first quote in this category. We've identified patterns from your other work:

{chr(10).join(dna_statements)}

**IMPORTANT**: These are TRANSFERRED patterns from other categories. Apply them as starting points, but be ready to adjust. Each category will build its own specific learnings over time.
"""

    # ... rest of prompt generation ...

    return f"""You are a quoting assistant for {contractor_name}, a professional contractor.

Your job is to take the contractor's voice notes about a job and produce a professional budgetary quote.

IMPORTANT: This is a BUDGETARY quote - a ballpark estimate to help the customer understand general pricing. It is NOT a detailed takeoff or binding contract. Make this clear in the quote.

## Voice Note Transcription

"{transcription}"
{philosophy_str}
{dna_bootstrap_str}
{category_context_str}

## Contractor's Base Pricing Information
...
"""
```

---

## 5. Pattern Confidence Inheritance Rules

### 5.1 Confidence Calculation Matrix

| Source Confidence | Source Quotes | Pattern Type | Inherited Confidence | Rationale |
|------------------|---------------|--------------|---------------------|-----------|
| 0.85 | 15 | Universal | **0.51** (0.85 * 0.6) | High source + universal = strong transfer |
| 0.85 | 15 | Partial | **0.34** (0.85 * 0.4) | High source but partial = moderate transfer |
| 0.60 | 5 | Universal | **0.25** (0.60 * 0.6 * 0.7) | Medium source + few quotes = weak transfer |
| 0.90 | 25 | Universal | **0.59** (0.90 * 0.6 * 1.1) | Very high source = boosted transfer |
| 0.70 | 2 | Partial | **0.20** (0.70 * 0.4 * 0.7) | Partial + very few quotes = minimal transfer |

### 5.2 Validation & Override Rules

```python
# backend/services/contractor_dna.py

class ContractorDNAService:
    # ... (continued)

    def validate_or_override_transferred_pattern(
        self,
        category: str,
        transferred_pattern: dict,
        new_correction_learnings: List[str],
    ) -> str:
        """
        After a correction in target category, check if it validates or overrides
        the transferred pattern.

        Returns: "validated", "overridden", or "neutral"
        """
        pattern_statement = transferred_pattern["statement"]
        pattern_keywords = set(transferred_pattern["keywords"])

        # Check if new learnings mention same keywords
        for new_learning in new_correction_learnings:
            new_keywords = set(self._extract_keywords(new_learning))

            # High keyword overlap = related to transferred pattern
            overlap = len(pattern_keywords & new_keywords)
            if overlap >= 2:
                # Check if new learning contradicts or confirms
                if self._are_contradictory(pattern_statement, new_learning):
                    return "overridden"
                else:
                    return "validated"

        return "neutral"  # Correction didn't address this pattern


    def _are_contradictory(self, statement1: str, statement2: str) -> bool:
        """Check if two statements contradict each other."""
        # Extract numeric values
        val1 = self._extract_numeric_value(statement1)
        val2 = self._extract_numeric_value(statement2)

        # If both have numbers and keywords overlap, check if numbers conflict
        if val1 and val2:
            keywords1 = set(self._extract_keywords(statement1))
            keywords2 = set(self._extract_keywords(statement2))

            if len(keywords1 & keywords2) >= 1:
                # Same keywords, different numbers = contradiction
                if abs(val1 - val2) > 0.05:  # More than 5% difference
                    return True

        return False
```

---

## 6. Example Flow: Complete Walkthrough

### Scenario: Contractor with 50 Deck Quotes, First Roofing Quote

```
STEP 1: User speaks roofing quote
Input: "15 square roofing repair, second story, asap"
Category: roofing (NEW - 0 prior quotes)

STEP 2: System checks DNA
- Contractor has 50 deck quotes
- DNA contains:
  - "Add 15% for second story access" (universal, 0.85 confidence, deck)
  - "Add 20% for ASAP/rush jobs" (universal, 0.78 confidence, deck)
  - "Repeat customer gets 5% discount" (universal, 0.82 confidence, deck)

STEP 3: Bootstrap from DNA
Transferred patterns:
  1. "Add 15% for second story access" → 0.51 confidence (0.85 * 0.6)
  2. "Add 20% for ASAP/rush jobs" → 0.47 confidence (0.78 * 0.6)
  3. "Repeat customer gets 5% discount" → 0.49 confidence (0.82 * 0.6)

STEP 4: Quote generation
Claude prompt includes:
"""
🧬 DNA Bootstrap for New Category "roofing"

This is your first quote in this category. We've identified patterns from your other work:

- Add 15% for second story access (Confidence: 51%, DNA from deck)
- Add 20% for ASAP/rush jobs (Confidence: 47%, DNA from deck)
- Repeat customer gets 5% discount (Confidence: 49%, DNA from deck)

IMPORTANT: These are TRANSFERRED patterns from other categories.
"""

STEP 5: Generated quote
AI applies:
- Base roofing repair: $3,500
- Second story +15%: +$525
- ASAP +20%: +$700
- Total: $4,725

STEP 6A: Contractor sends WITHOUT edit
- Acceptance learning: roofing confidence +0.05 → 0.56
- DNA patterns VALIDATED (implicit confirmation)

STEP 6B: Contractor EDITS to $4,200
- Correction learning triggered
- New learning: "Roofing repairs: be more aggressive, second story only +10%"
- DNA pattern OVERRIDDEN for roofing category
- Roofing now has its own "second story +10%" rule at 0.55 confidence
- Deck keeps "second story +15%" at 0.85 confidence

STEP 7: Next roofing quote
- Uses roofing-specific "+10%" rule (0.60 confidence after 2nd correction)
- DNA patterns remain as fallback for new aspects
```

---

## 7. Test Scenarios

### Test 1: Basic DNA Transfer

```python
# Given
contractor = {
    "categories": {
        "deck": {
            "learned_adjustments": [
                "Add 15% for second story access",
                "Composite decking is $6.50/sqft",
            ],
            "confidence": 0.85,
            "correction_count": 20,
        }
    }
}

# When
dna_service.identify_transferable_patterns(
    source_category="deck",
    source_learnings=contractor["categories"]["deck"]["learned_adjustments"],
    source_confidence=0.85,
    source_quote_count=20,
    target_category="roofing",
)

# Then
assert len(candidates) == 1  # Only "second story" transfers
assert candidates[0].pattern.statement == "Add 15% for second story access"
assert candidates[0].inherited_confidence == 0.51  # 0.85 * 0.6
assert candidates[0].pattern.transferability == "universal"
# "Composite decking" does NOT transfer (category-specific)
```

### Test 2: Cold Start Acceleration

```python
# Given
contractor_dna = {
    "universal_patterns": [
        {
            "statement": "Add 15% for second story",
            "source_confidence": 0.85,
            "source_quote_count": 20,
            "source_category": "deck",
            "pattern_type": "access_modifier",
        }
    ],
    "partial_patterns": [],
}

# When
bootstrap = dna_service.generate_category_bootstrap(
    contractor_id="test-contractor",
    new_category="roofing",
    contractor_dna=contractor_dna,
)

# Then
assert len(bootstrap) >= 1
assert bootstrap[0]["statement"] == "Add 15% for second story"
assert bootstrap[0]["confidence"] == 0.51
assert bootstrap[0]["transferred"] == True
assert "DNA from deck" in bootstrap[0]["source"]
```

### Test 3: Pattern Override After Correction

```python
# Given
transferred_pattern = {
    "statement": "Add 15% for second story",
    "keywords": ["second story", "access"],
    "numeric_value": 0.15,
}
new_learnings = ["Roofing: second story only needs +10%"]

# When
result = dna_service.validate_or_override_transferred_pattern(
    category="roofing",
    transferred_pattern=transferred_pattern,
    new_correction_learnings=new_learnings,
)

# Then
assert result == "overridden"
# Roofing category will use +10%, deck keeps +15%
```

### Test 4: Accumulation Across 5 Categories

```python
# Given
categories = ["deck", "roofing", "siding", "painting", "fencing"]
for cat in categories:
    # Contractor learns "second story +15%" in each category
    dna_service.update_dna_from_correction(
        contractor_id="test",
        category=cat,
        new_learnings=["Add 15% for second story access"],
        category_confidence=0.80,
        category_quote_count=10,
    )

# When
final_dna = pricing_model.contractor_dna

# Then
assert final_dna["total_categories"] == 5
assert len(final_dna["universal_patterns"]) == 1  # Merged, not duplicated
assert final_dna["universal_patterns"][0]["source_quote_count"] == 10  # From first category
assert final_dna["dna_confidence"] >= 0.80  # High confidence across categories
```

### Test 5: Related vs Unrelated Categories

```python
# Partial pattern: "Premium materials +20%"
# This should transfer deck → fence (related) but NOT deck → painting (unrelated)

# When
related = dna_service._categories_related("deck", "fence")
unrelated = dna_service._categories_related("deck", "painting_interior")

# Then
assert related == True
assert unrelated == False

# Transfer to fence
candidates_fence = dna_service.identify_transferable_patterns(
    source_category="deck",
    source_learnings=["Premium materials +20%"],
    source_confidence=0.80,
    source_quote_count=15,
    target_category="fence",
)
assert len(candidates_fence) == 1  # Transfers

# Don't transfer to painting
candidates_paint = dna_service.identify_transferable_patterns(
    source_category="deck",
    source_learnings=["Premium materials +20%"],
    source_confidence=0.80,
    source_quote_count=15,
    target_category="painting_interior",
)
assert len(candidates_paint) == 0  # Does NOT transfer
```

### Test 6: Confidence Ceiling Prevents Overconfidence

```python
# A pattern with weak source data should inherit LOW confidence

# Given
weak_pattern = {
    "statement": "Add 10% for difficult terrain",
    "source_confidence": 0.55,
    "source_quote_count": 2,  # Very few quotes
}

# When
inherited = dna_service._calculate_inherited_confidence(
    source_confidence=0.55,
    source_quote_count=2,
    pattern_type="universal",
)

# Then
assert inherited < 0.35  # 0.55 * 0.6 * 0.7 (penalty) = 0.23
# Even as universal, weak source = weak transfer
```

### Test 7: No DNA Pollution (Specifics Stay Isolated)

```python
# Given
deck_learnings = [
    "Composite decking is Trex Select at $6.50/sqft",  # SPECIFIC
    "Add 15% for second story",  # UNIVERSAL
    "Deck framing labor is 16 hours",  # SPECIFIC
]

# When
dna_service.update_dna_from_correction(
    contractor_id="test",
    category="deck",
    new_learnings=deck_learnings,
    category_confidence=0.85,
    category_quote_count=20,
)

# Then
dna = pricing_model.contractor_dna
assert len(dna["universal_patterns"]) == 1  # Only "second story"
assert len(dna["partial_patterns"]) == 0
# Specific pricing doesn't pollute DNA
```

---

## 8. Migration Plan

### 8.1 Backfill DNA from Existing Learnings

```python
# backend/scripts/backfill_contractor_dna.py (NEW FILE)

"""
One-time script to build contractor DNA from existing category learnings.

Run after deployment to populate DNA for existing contractors.
"""

import asyncio
from backend.models.database import PricingModel, init_db
from backend.services.contractor_dna import get_dna_service
from sqlalchemy import select


async def backfill_dna():
    """Build DNA for all contractors from existing learnings."""
    engine = await init_db()

    async with engine.begin() as conn:
        # Get all pricing models
        result = await conn.execute(select(PricingModel))
        pricing_models = result.scalars().all()

        dna_service = get_dna_service()

        for pm in pricing_models:
            print(f"Building DNA for contractor {pm.contractor_id}")

            pricing_knowledge = pm.pricing_knowledge or {}
            categories = pricing_knowledge.get("categories", {})

            # Build DNA from all existing categories
            for cat_name, cat_data in categories.items():
                learnings = cat_data.get("learned_adjustments", [])
                confidence = cat_data.get("confidence", 0.5)
                quote_count = cat_data.get("correction_count", 0)

                if learnings:
                    await dna_service.update_dna_from_correction(
                        contractor_id=pm.contractor_id,
                        category=cat_name,
                        new_learnings=learnings,
                        category_confidence=confidence,
                        category_quote_count=quote_count,
                    )

            print(f"  → Built DNA with {len(pm.contractor_dna.get('universal_patterns', []))} universal patterns")


if __name__ == "__main__":
    asyncio.run(backfill_dna())
```

### 8.2 Deployment Steps

```bash
# 1. Deploy code (adds contractor_dna column to pricing_models)
git add backend/services/contractor_dna.py
git add backend/models/database.py  # Added contractor_dna column
git commit -m "Add Contractor DNA cross-category intelligence system"
git push origin main

# 2. Railway auto-deploys (migrations run automatically)

# 3. Backfill DNA for existing contractors
railway run python -m backend.scripts.backfill_contractor_dna

# 4. Verify in production
railway run python -c "
from backend.models.database import PricingModel, init_db
import asyncio

async def check():
    engine = await init_db()
    async with engine.begin() as conn:
        result = await conn.execute('SELECT COUNT(*) FROM pricing_models WHERE contractor_dna IS NOT NULL')
        count = result.scalar()
        print(f'Contractors with DNA: {count}')

asyncio.run(check())
"
```

---

## 9. Success Metrics

### 9.1 DNA Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **DNA coverage** | 80%+ contractors have DNA | `COUNT(contractor_dna IS NOT NULL) / COUNT(*)` |
| **Pattern count** | 5+ universal patterns/contractor | `AVG(len(universal_patterns))` |
| **Category coverage** | 3+ categories/contractor | `AVG(total_categories)` |
| **DNA confidence** | 0.60+ average | `AVG(dna_confidence)` |

### 9.2 Cold Start Improvement

| Scenario | Before DNA | With DNA | Target Improvement |
|----------|-----------|----------|-------------------|
| **Quotes to 80% confidence** | 10-15 quotes | 3-5 quotes | **3x faster** |
| **First quote accuracy** | 65% sent without edit | 80% sent without edit | **+15pp** |
| **Cross-category consistency** | Manual re-teaching | Automatic transfer | **100% consistent** |

### 9.3 PostHog Events

```javascript
// Track DNA usage
posthog.capture('dna_pattern_transferred', {
    contractor_id: contractorId,
    source_category: 'deck',
    target_category: 'roofing',
    pattern_type: 'access_modifier',
    inherited_confidence: 0.51,
});

// Track DNA validation
posthog.capture('dna_pattern_validated', {
    contractor_id: contractorId,
    category: 'roofing',
    pattern: 'Add 15% for second story',
    validation_type: 'sent_without_edit',
});

// Track DNA override
posthog.capture('dna_pattern_overridden', {
    contractor_id: contractorId,
    category: 'roofing',
    original_pattern: 'Add 15% for second story',
    override_pattern: 'Add 10% for second story',
});
```

---

## 10. Files Created/Modified

### New Files

1. **`backend/services/contractor_dna.py`** (NEW)
   - ContractorDNAService class
   - Pattern classification logic
   - Bootstrap generation
   - DNA building/merging
   - ~600 lines

2. **`backend/scripts/backfill_contractor_dna.py`** (NEW)
   - One-time migration script
   - Builds DNA from existing learnings
   - ~100 lines

### Modified Files

1. **`backend/models/database.py`** (line 136)
   - Add `contractor_dna = Column(JSON, default=dict)`
   - 1 line change

2. **`backend/services/learning.py`** (line 117)
   - Call `dna_service.update_dna_from_correction()` after processing
   - ~10 lines added

3. **`backend/prompts/quote_generation.py`** (line 59)
   - Check for new category
   - Generate DNA bootstrap section
   - Inject into prompt
   - ~30 lines added

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **DNA pattern conflicts** | Contractor gets confused seeing contradictory rules | Conflict detection algorithm + clear "TRANSFERRED" labeling |
| **Overconfident transfers** | Wrong patterns applied with high confidence | Conservative inheritance (max 60% for universal, 40% for partial) |
| **Category misclassification** | Pattern transfers to wrong category | Related category groups + transferability tiers |
| **Performance degradation** | DNA building slows down corrections | Async processing + capped pattern list (max 50 universal) |
| **Data corruption** | DNA becomes polluted with bad patterns | Each category validates/overrides independently |

---

## 12. Future Enhancements

### Phase 6 Candidates (Not in Scope)

1. **Network DNA** (Privacy-preserving)
   - Aggregate anonymous patterns across ALL contractors
   - "95% of deck contractors add 15% for second story"
   - Requires differential privacy

2. **Temporal DNA**
   - Detect if contractor's pricing DNA *changes* over time
   - "You used to be aggressive, now you're conservative"

3. **Competitive DNA**
   - Compare contractor DNA to market benchmarks
   - "Your rush premium (20%) is 2x industry average (10%)"

4. **Predictive DNA**
   - "Based on your deck DNA, we predict you'll price roofing conservatively"
   - ML-based pattern prediction

---

## Appendix: Pattern Type Reference

### Universal Patterns (Always Transfer)

| Pattern Type | Example | Trigger Keywords |
|-------------|---------|------------------|
| **access_modifier** | "Add 15% for second story access" | second story, difficult access, steep, ladder |
| **relationship_discount** | "Repeat customer gets 5% off" | repeat customer, returning, previous client |
| **rush_premium** | "ASAP jobs +20%" | asap, rush, urgent, emergency |
| **seasonal_adjustment** | "Winter work +10%" | winter, summer, rainy season, off-season |
| **permit_handling** | "Permit fees pass-through" | permit, inspection |

### Partial Patterns (Transfer to Related Categories)

| Pattern Type | Example | Transfers To |
|-------------|---------|--------------|
| **quality_preference** | "Premium materials +20%" | Related material-based categories |
| **minimum_pricing** | "Small jobs have $800 minimum" | All categories (but varies by category) |
| **material_markup** | "Mark up materials 25%" | All categories with materials |

### Specific Patterns (Never Transfer)

| Pattern Type | Example | Why Not Transfer |
|-------------|---------|------------------|
| **absolute_pricing** | "Deck framing is $2,800" | Category-specific cost |
| **unit_pricing** | "Composite decking $6.50/sqft" | Material-specific |
| **category_material** | "Use Trex Select for standard jobs" | Deck-specific product |

---

**End of Phase 5 Design Document**
