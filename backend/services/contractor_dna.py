"""
Contractor DNA Service for Quoted.

Cross-category intelligence system that identifies transferable pricing patterns
within a single contractor's profile, creating a "Contractor DNA" that accelerates
learning for new categories.

Key insight: A contractor who adds 15% for "second story" deck access will likely
apply similar premiums across ALL job types (roofing, painting, siding).

Design source: .claude/learning-excellence-outputs/phase5-contractor-dna.md
"""

import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Literal


@dataclass
class TransferablePattern:
    """A single pattern that can transfer between categories."""
    pattern_id: str
    pattern_type: str  # "access_modifier", "relationship_discount", etc.
    statement: str  # The actual learning statement
    source_category: str
    source_confidence: float
    source_quote_count: int
    keywords: List[str]
    numeric_value: Optional[float]
    transferability: Literal["universal", "partial", "specific"]
    created_at: str
    last_validated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "statement": self.statement,
            "source_category": self.source_category,
            "source_confidence": self.source_confidence,
            "source_quote_count": self.source_quote_count,
            "keywords": self.keywords,
            "numeric_value": self.numeric_value,
            "transferability": self.transferability,
            "created_at": self.created_at,
            "last_validated_at": self.last_validated_at,
        }


@dataclass
class TransferCandidate:
    """A pattern being considered for transfer to a new category."""
    pattern: TransferablePattern
    target_category: str
    inherited_confidence: float
    transfer_reason: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern": self.pattern.to_dict() if hasattr(self.pattern, 'to_dict') else self.pattern,
            "target_category": self.target_category,
            "inherited_confidence": self.inherited_confidence,
            "transfer_reason": self.transfer_reason,
        }


class ContractorDNAService:
    """
    Manages contractor DNA patterns and cross-category intelligence.

    Pattern transferability tiers:
    1. UNIVERSAL: Transfers to ALL categories at 60% source confidence
       - Access difficulty ("second story +15%")
       - Relationship discounts ("repeat customer -5%")
       - Rush premiums ("ASAP +20%")

    2. PARTIAL: Transfers to RELATED categories at 40% source confidence
       - Material quality preferences
       - Job size scaling

    3. SPECIFIC: DO NOT transfer (category-specific pricing)
       - Absolute prices
       - Material costs
    """

    # Related category groups (for partial pattern transfer)
    RELATED_GROUPS = [
        {"deck", "fence", "pergola", "gazebo"},  # Outdoor structures
        {"roofing", "siding", "gutters"},  # Exterior
        {"painting_interior", "painting_exterior", "staining"},  # Coatings
        {"flooring", "tile", "carpet"},  # Flooring
        {"landscaping", "irrigation", "hardscaping"},  # Outdoor
    ]

    # Universal pattern keywords
    UNIVERSAL_KEYWORDS = {
        "access_modifier": ["second story", "difficult access", "steep", "ladder", "elevated"],
        "relationship_discount": ["repeat customer", "returning", "previous client", "referral"],
        "rush_premium": ["asap", "rush", "urgent", "emergency", "expedite"],
        "seasonal_adjustment": ["winter", "summer", "rainy season", "off-season", "holiday"],
        "permit_handling": ["permit", "inspection", "code"],
    }

    # Partial pattern keywords
    PARTIAL_KEYWORDS = {
        "quality_preference": ["premium", "high-end", "luxury", "top quality", "best"],
        "minimum_pricing": ["small job", "minimum", "trip charge", "call out"],
        "material_markup": ["material markup", "markup on materials", "mark up"],
    }

    # Confidence inheritance rates
    UNIVERSAL_INHERITANCE = 0.60
    PARTIAL_INHERITANCE = 0.40
    MIN_INHERITED_CONFIDENCE = 0.30
    MAX_INHERITED_CONFIDENCE = 0.70

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

        Args:
            source_category: Category where patterns originated
            source_learnings: Learning statements from source
            source_confidence: Confidence score in source category
            source_quote_count: Number of quotes in source category
            target_category: Category to potentially transfer to

        Returns:
            List of TransferCandidates
        """
        candidates = []

        for learning in source_learnings:
            pattern_type, transferability = self._classify_pattern(learning)

            if transferability == "specific":
                continue  # Don't transfer category-specific patterns

            # Check if pattern applies to target category
            if transferability == "universal":
                inherited_conf = self._calculate_inherited_confidence(
                    source_confidence=source_confidence,
                    source_quote_count=source_quote_count,
                    pattern_type="universal",
                )
                reason = f"Universal pattern from {source_category}"

            elif transferability == "partial":
                if self._categories_related(source_category, target_category):
                    inherited_conf = self._calculate_inherited_confidence(
                        source_confidence=source_confidence,
                        source_quote_count=source_quote_count,
                        pattern_type="partial",
                    )
                    reason = f"Partial pattern from related category {source_category}"
                else:
                    continue  # Skip unrelated categories for partial patterns

            else:
                continue

            # Create pattern
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

    def generate_category_bootstrap(
        self,
        contractor_id: str,
        new_category: str,
        contractor_dna: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate bootstrap pricing for a new category using DNA.

        Args:
            contractor_id: The contractor's ID
            new_category: The new category being quoted
            contractor_dna: The contractor's DNA profile

        Returns:
            List of learnings to inject with inherited confidence
        """
        bootstrap_learnings = []

        # 1. ALWAYS inject universal patterns
        universal_patterns = contractor_dna.get("universal_patterns", [])
        for pattern in universal_patterns:
            if isinstance(pattern, dict):
                statement = pattern.get("statement", "")
                source_conf = pattern.get("source_confidence", 0.5)
                source_count = pattern.get("source_quote_count", 0)
                source_cat = pattern.get("source_category", "unknown")
            else:
                continue

            inherited_conf = self._calculate_inherited_confidence(
                source_confidence=source_conf,
                source_quote_count=source_count,
                pattern_type="universal",
            )

            bootstrap_learnings.append({
                "statement": statement,
                "confidence": inherited_conf,
                "source": f"DNA from {source_cat}",
                "pattern_type": pattern.get("pattern_type", "unknown"),
                "transferred": True,
            })

        # 2. Inject partial patterns if categories are related
        partial_patterns = contractor_dna.get("partial_patterns", [])
        for pattern in partial_patterns:
            if isinstance(pattern, dict):
                source_cat = pattern.get("source_category", "")
                if self._categories_related(source_cat, new_category):
                    inherited_conf = self._calculate_inherited_confidence(
                        source_confidence=pattern.get("source_confidence", 0.5),
                        source_quote_count=pattern.get("source_quote_count", 0),
                        pattern_type="partial",
                    )

                    bootstrap_learnings.append({
                        "statement": pattern.get("statement", ""),
                        "confidence": inherited_conf,
                        "source": f"DNA from {source_cat}",
                        "pattern_type": pattern.get("pattern_type", "unknown"),
                        "transferred": True,
                    })

        # 3. Add pricing style guidelines
        pricing_style = contractor_dna.get("pricing_style", {})
        tendency = pricing_style.get("overall_tendency", "balanced")
        style_conf = pricing_style.get("confidence_in_profile", 0.5)

        if tendency == "conservative" and style_conf > 0.5:
            bootstrap_learnings.append({
                "statement": "You tend to price conservatively - better to quote high and come in under budget",
                "confidence": style_conf,
                "source": "DNA pricing style",
                "pattern_type": "pricing_philosophy",
                "transferred": True,
            })
        elif tendency == "aggressive" and style_conf > 0.5:
            bootstrap_learnings.append({
                "statement": "You price competitively - focus on winning jobs with tight margins",
                "confidence": style_conf,
                "source": "DNA pricing style",
                "pattern_type": "pricing_philosophy",
                "transferred": True,
            })

        return bootstrap_learnings

    def update_dna_from_correction(
        self,
        contractor_dna: Dict[str, Any],
        category: str,
        new_learnings: List[str],
        category_confidence: float,
        category_quote_count: int,
    ) -> Dict[str, Any]:
        """
        Update contractor DNA after a correction is processed.

        Args:
            contractor_dna: Current DNA profile
            category: Category where correction happened
            new_learnings: New learning statements from correction
            category_confidence: Current confidence in category
            category_quote_count: Number of quotes in category

        Returns:
            Updated DNA profile
        """
        if contractor_dna is None:
            contractor_dna = self._empty_dna("")

        # Extract transferable patterns from new learnings
        for learning in new_learnings:
            pattern_type, transferability = self._classify_pattern(learning)

            if transferability in ["universal", "partial"]:
                pattern = {
                    "pattern_id": str(uuid.uuid4()),
                    "pattern_type": pattern_type,
                    "statement": learning,
                    "source_category": category,
                    "source_confidence": category_confidence,
                    "source_quote_count": category_quote_count,
                    "keywords": self._extract_keywords(learning),
                    "numeric_value": self._extract_numeric_value(learning),
                    "transferability": transferability,
                    "created_at": datetime.utcnow().isoformat(),
                    "last_validated_at": datetime.utcnow().isoformat(),
                }

                # Merge with existing (avoid duplicates)
                contractor_dna = self._merge_pattern(contractor_dna, pattern, category)

        # Update metadata
        contractor_dna["total_corrections"] = contractor_dna.get("total_corrections", 0) + 1
        contractor_dna["dna_confidence"] = self._calculate_dna_confidence(contractor_dna)
        contractor_dna["last_updated_at"] = datetime.utcnow().isoformat()

        return contractor_dna

    def _classify_pattern(self, statement: str) -> Tuple[str, str]:
        """
        Classify a learning statement into pattern type and transferability.

        Returns:
            Tuple of (pattern_type, transferability)
        """
        statement_lower = statement.lower()

        # Check universal patterns
        for pattern_type, keywords in self.UNIVERSAL_KEYWORDS.items():
            if any(kw in statement_lower for kw in keywords):
                return (pattern_type, "universal")

        # Check partial patterns
        for pattern_type, keywords in self.PARTIAL_KEYWORDS.items():
            if any(kw in statement_lower for kw in keywords):
                return (pattern_type, "partial")

        # Check for specific patterns (DO NOT transfer)
        # Contains absolute pricing
        if re.search(r'\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*per|\s*/)', statement):
            return ("absolute_pricing", "specific")

        # Contains unit-based pricing
        if any(kw in statement_lower for kw in ["sqft", "sq ft", "linear foot", "lf", "square"]):
            return ("unit_pricing", "specific")

        # Contains category-specific materials
        category_specific = ["deck", "railing", "composite", "pt lumber", "shingle", "membrane"]
        if any(kw in statement_lower for kw in category_specific):
            return ("category_specific_material", "specific")

        # Default to partial (conservative)
        return ("general_adjustment", "partial")

    def _categories_related(self, cat1: str, cat2: str) -> bool:
        """Check if two categories are related (for partial pattern transfer)."""
        cat1_lower = cat1.lower().replace("-", "_").replace(" ", "_")
        cat2_lower = cat2.lower().replace("-", "_").replace(" ", "_")

        for group in self.RELATED_GROUPS:
            # Check if both categories belong to the same group
            cat1_in = any(g in cat1_lower for g in group)
            cat2_in = any(g in cat2_lower for g in group)
            if cat1_in and cat2_in:
                return True

        return False

    def _calculate_inherited_confidence(
        self,
        source_confidence: float,
        source_quote_count: int,
        pattern_type: str,
    ) -> float:
        """Calculate confidence for inherited pattern."""
        if pattern_type == "universal":
            base_inheritance = self.UNIVERSAL_INHERITANCE
        elif pattern_type == "partial":
            base_inheritance = self.PARTIAL_INHERITANCE
        else:
            base_inheritance = 0.30

        inherited = source_confidence * base_inheritance

        # Adjust for source data quality
        if source_quote_count < 3:
            inherited *= 0.7  # Penalize weak source data
        elif source_quote_count > 10:
            inherited *= 1.1  # Boost well-validated patterns

        # Clamp to safe range
        return max(self.MIN_INHERITED_CONFIDENCE, min(self.MAX_INHERITED_CONFIDENCE, inherited))

    def _extract_keywords(self, statement: str) -> List[str]:
        """Extract key terms from learning statement."""
        keywords = []
        statement_lower = statement.lower()

        # Common pricing trigger words
        triggers = [
            "second story", "difficult access", "repeat customer", "asap",
            "rush", "premium", "winter", "summer", "permit", "steep",
            "referral", "emergency", "minimum", "small job",
        ]

        for trigger in triggers:
            if trigger in statement_lower:
                keywords.append(trigger)

        return keywords

    def _extract_numeric_value(self, statement: str) -> Optional[float]:
        """Extract percentage or dollar amount from statement."""
        # Try to extract percentage
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', statement)
        if pct_match:
            return float(pct_match.group(1)) / 100.0

        # Try to extract dollar amount
        dollar_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', statement)
        if dollar_match:
            return float(dollar_match.group(1).replace(',', ''))

        return None

    def _merge_pattern(
        self,
        dna: Dict[str, Any],
        new_pattern: Dict[str, Any],
        source_category: str,
    ) -> Dict[str, Any]:
        """Merge new pattern into existing DNA, avoiding duplicates."""
        transferability = new_pattern.get("transferability", "partial")

        if transferability == "universal":
            target_list = dna.get("universal_patterns", [])
            list_key = "universal_patterns"
        else:
            target_list = dna.get("partial_patterns", [])
            list_key = "partial_patterns"

        # Check for duplicates
        is_duplicate = False
        for existing in target_list:
            if (existing.get("statement") == new_pattern.get("statement") and
                    existing.get("pattern_type") == new_pattern.get("pattern_type")):
                # Update existing pattern
                existing["last_validated_at"] = new_pattern.get("last_validated_at")
                is_duplicate = True
                break

        if not is_duplicate:
            target_list.append(new_pattern)

        dna[list_key] = target_list

        # Track unique categories
        categories_with_data = set()
        for pattern in dna.get("universal_patterns", []) + dna.get("partial_patterns", []):
            categories_with_data.add(pattern.get("source_category", ""))
        dna["total_categories"] = len(categories_with_data)

        return dna

    def _calculate_dna_confidence(self, dna: Dict[str, Any]) -> float:
        """Calculate overall DNA quality score."""
        category_count = dna.get("total_categories", 0)
        universal_count = len(dna.get("universal_patterns", []))

        # More categories = better DNA
        category_score = min(1.0, category_count / 5.0)

        # More universal patterns = better DNA
        pattern_score = min(1.0, universal_count / 10.0)

        # Average confidence of patterns
        all_patterns = dna.get("universal_patterns", []) + dna.get("partial_patterns", [])
        if all_patterns:
            avg_confidence = sum(
                p.get("source_confidence", 0.5) for p in all_patterns
            ) / len(all_patterns)
        else:
            avg_confidence = 0.5

        # Weighted combination
        dna_confidence = (
            category_score * 0.4 +
            pattern_score * 0.3 +
            avg_confidence * 0.3
        )

        return round(dna_confidence, 2)

    def _empty_dna(self, contractor_id: str) -> Dict[str, Any]:
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


# Singleton instance
_dna_service: Optional[ContractorDNAService] = None


def get_dna_service() -> ContractorDNAService:
    """Get the singleton DNA service instance."""
    global _dna_service
    if _dna_service is None:
        _dna_service = ContractorDNAService()
    return _dna_service
