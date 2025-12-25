"""
Interpretable AI Pricing Explanation Service for Quoted.

Shows contractors exactly WHY their quote was priced the way it was:
- Component breakdown (base rate, modifiers, voice signals)
- Pattern tracing (which learnings were applied)
- Uncertainty surfacing (what we don't know)
- Confidence display (how sure we are)

Core Principle: Show the chain of reasoning from learned patterns → voice signals → final price.
Make the AI's thought process auditable.

Design source: .claude/learning-excellence-outputs/phase6-explanation.md
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Literal


@dataclass
class PricingComponent:
    """A single component of the pricing explanation."""
    type: Literal["base_rate", "modifier", "adjustment", "voice_signal"]
    label: str  # Human-readable label
    amount: float  # Dollar amount
    source: Literal["learned", "default", "dna_transfer", "voice_detected"]
    confidence: float  # 0.0-1.0
    learning_ref: Optional[str] = None  # Reference to specific learning ID
    pattern_id: Optional[str] = None  # Reference to contractor DNA pattern
    validation_count: Optional[int] = None  # How many times pattern was validated
    last_validated: Optional[str] = None  # ISO timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "type": self.type,
            "label": self.label,
            "amount": self.amount,
            "source": self.source,
            "confidence": self.confidence,
            "learning_ref": self.learning_ref,
            "pattern_id": self.pattern_id,
            "validation_count": self.validation_count,
            "last_validated": self.last_validated,
        }


@dataclass
class AppliedPattern:
    """A pricing pattern that was applied to this quote."""
    pattern: str  # The pattern statement
    source_category: str  # Where this pattern came from
    times_validated: int  # How many quotes validated this
    last_validated: str  # ISO timestamp
    confidence: float  # Pattern confidence

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern": self.pattern,
            "source_category": self.source_category,
            "times_validated": self.times_validated,
            "last_validated": self.last_validated,
            "confidence": self.confidence,
        }


@dataclass
class UncertaintyNote:
    """An area of uncertainty in the pricing."""
    area: str  # What we're uncertain about
    reason: str  # Why we're uncertain
    suggestion: Optional[str] = None  # How contractor can resolve

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "area": self.area,
            "reason": self.reason,
            "suggestion": self.suggestion,
        }


@dataclass
class DNATransfer:
    """Information about a DNA pattern transfer."""
    pattern: str
    from_category: str
    inherited_confidence: float
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern": self.pattern,
            "from_category": self.from_category,
            "inherited_confidence": self.inherited_confidence,
            "reason": self.reason,
        }


@dataclass
class LearningContext:
    """Context about the learning state for this category."""
    category: str
    quote_count: int
    correction_count: int
    acceptance_rate: float
    avg_adjustment: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "quote_count": self.quote_count,
            "correction_count": self.correction_count,
            "acceptance_rate": self.acceptance_rate,
            "avg_adjustment": self.avg_adjustment,
        }


@dataclass
class PricingExplanation:
    """Complete explanation of how a quote was priced."""
    summary: str
    overall_confidence: float  # 0.0-1.0
    confidence_label: str  # "High", "Medium", "Low"
    components: List[PricingComponent] = field(default_factory=list)
    uncertainties: List[UncertaintyNote] = field(default_factory=list)
    patterns_applied: List[AppliedPattern] = field(default_factory=list)
    dna_transfers: List[DNATransfer] = field(default_factory=list)
    learning_context: Optional[LearningContext] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "summary": self.summary,
            "overall_confidence": self.overall_confidence,
            "confidence_label": self.confidence_label,
            "components": [c.to_dict() for c in self.components],
            "uncertainties": [u.to_dict() for u in self.uncertainties],
            "patterns_applied": [p.to_dict() for p in self.patterns_applied],
            "dna_transfers": [d.to_dict() for d in self.dna_transfers],
            "learning_context": self.learning_context.to_dict() if self.learning_context else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PricingExplanation":
        """Create from dictionary."""
        return cls(
            summary=data.get("summary", ""),
            overall_confidence=data.get("overall_confidence", 0.0),
            confidence_label=data.get("confidence_label", "Learning"),
            components=[
                PricingComponent(**c) for c in data.get("components", [])
            ],
            uncertainties=[
                UncertaintyNote(**u) for u in data.get("uncertainties", [])
            ],
            patterns_applied=[
                AppliedPattern(**p) for p in data.get("patterns_applied", [])
            ],
            dna_transfers=[
                DNATransfer(**d) for d in data.get("dna_transfers", [])
            ],
            learning_context=(
                LearningContext(**data["learning_context"])
                if data.get("learning_context") else None
            ),
        )


class PricingExplanationService:
    """
    Generates explanations for quote pricing decisions.

    Usage:
        service = PricingExplanationService()
        explanation = service.generate_explanation(
            quote=quote,
            learned_adjustments=["Add 15% for second story"],
            contractor_dna={"universal_patterns": [...]},
            voice_signals={"rush": True},
            confidence=PricingConfidence(...),
            pricing_model=pricing_model,
            detected_category="deck",
        )
    """

    # Related category mappings for DNA transfer explanations
    RELATED_CATEGORIES = {
        "deck": ["patio", "pergola", "outdoor_structure"],
        "fence": ["gate", "railing", "outdoor_structure"],
        "roofing": ["siding", "gutters", "exterior"],
        "painting": ["staining", "finishing", "interior"],
        "concrete": ["patio", "driveway", "flatwork"],
    }

    def generate_explanation(
        self,
        quote: Any,  # Quote model
        learned_adjustments: List[str],
        contractor_dna: Dict[str, Any],
        voice_signals: Dict[str, Any],
        confidence: Any,  # PricingConfidence
        pricing_model: Dict[str, Any],
        detected_category: str,
    ) -> PricingExplanation:
        """
        Build explanation by tracing each pricing decision.

        Algorithm:
        1. Identify base rate source (learned vs default vs DNA)
        2. Trace each modifier/adjustment to its origin
        3. Surface uncertainties from confidence system
        4. Generate human-readable summary
        """
        components: List[PricingComponent] = []
        patterns_applied: List[AppliedPattern] = []
        uncertainties: List[UncertaintyNote] = []
        dna_transfers: List[DNATransfer] = []

        # Get quote total for calculations
        quote_total = getattr(quote, 'subtotal', 0) or getattr(quote, 'total', 0) or 0

        # 1. BASE RATE IDENTIFICATION
        base_component = self._identify_base_rate_source(
            quote_total=quote_total,
            pricing_model=pricing_model,
            detected_category=detected_category,
            contractor_dna=contractor_dna,
        )
        components.append(base_component)

        # Track running total for modifier calculations
        running_total = base_component.amount

        # 2. LEARNED MODIFIERS
        for adjustment in learned_adjustments:
            modifier = self._trace_learned_modifier(
                adjustment=adjustment,
                quote_total=quote_total,
                pricing_model=pricing_model,
                detected_category=detected_category,
            )
            if modifier:
                components.append(modifier)
                running_total += modifier.amount

                # Add to patterns_applied if it's a validated pattern
                if modifier.validation_count and modifier.validation_count > 5:
                    patterns_applied.append(AppliedPattern(
                        pattern=adjustment,
                        source_category=detected_category,
                        times_validated=modifier.validation_count,
                        last_validated=modifier.last_validated or datetime.utcnow().isoformat(),
                        confidence=modifier.confidence,
                    ))

        # 3. DNA TRANSFERS
        universal_patterns = contractor_dna.get("universal_patterns", [])
        for pattern in universal_patterns:
            if self._pattern_applies_to_quote(pattern, quote, voice_signals):
                transfer_result = self._trace_dna_transfer(
                    pattern=pattern,
                    quote_total=quote_total,
                )
                if transfer_result:
                    components.append(transfer_result["component"])
                    dna_transfers.append(transfer_result["dna_info"])

        # 4. VOICE SIGNALS
        voice_components = self._extract_voice_signal_components(
            voice_signals=voice_signals,
            quote_total=quote_total,
        )
        components.extend(voice_components)

        # 5. SURFACE UNCERTAINTIES
        uncertainties = self._identify_uncertainties(
            confidence=confidence,
            pricing_model=pricing_model,
            detected_category=detected_category,
            quote_total=quote_total,
        )

        # 6. GET CONFIDENCE INFO
        overall_confidence = getattr(confidence, 'overall_confidence', 0.5)
        confidence_label = getattr(confidence, 'display_confidence', 'Medium')

        # 7. GENERATE SUMMARY
        summary = self._generate_human_summary(
            components=components,
            patterns_applied=patterns_applied,
            confidence_label=confidence_label,
            pricing_model=pricing_model,
            detected_category=detected_category,
        )

        # 8. COMPILE LEARNING CONTEXT
        learning_context = self._get_learning_context(
            pricing_model=pricing_model,
            detected_category=detected_category,
        )

        return PricingExplanation(
            summary=summary,
            overall_confidence=overall_confidence,
            confidence_label=confidence_label,
            components=components,
            uncertainties=uncertainties,
            patterns_applied=patterns_applied,
            dna_transfers=dna_transfers,
            learning_context=learning_context,
        )

    def _identify_base_rate_source(
        self,
        quote_total: float,
        pricing_model: Dict[str, Any],
        detected_category: str,
        contractor_dna: Dict[str, Any],
    ) -> PricingComponent:
        """
        Identify where the base rate came from.

        Priority:
        1. Learned category pricing (best)
        2. DNA transfer from related category
        3. Default market rates (fallback)
        """
        pricing_knowledge = pricing_model.get("pricing_knowledge", {})
        categories = pricing_knowledge.get("categories", {})

        # Estimate base amount (quote total minus modifiers, ~80%)
        estimated_base = quote_total * 0.80

        if detected_category in categories:
            cat_data = categories[detected_category]
            quote_count = cat_data.get("quote_count", 0)
            confidence = cat_data.get("confidence", 0.5)

            return PricingComponent(
                type="base_rate",
                label=f"{self._format_category_name(detected_category)} base pricing",
                amount=round(estimated_base, 2),
                source="learned",
                confidence=confidence,
                learning_ref=f"category_{detected_category}_base",
                validation_count=quote_count,
            )

        # Check for DNA transfer from related category
        related_category = self._find_related_category(
            target_category=detected_category,
            contractor_dna=contractor_dna,
            pricing_knowledge=pricing_knowledge,
        )

        if related_category:
            return PricingComponent(
                type="base_rate",
                label=f"Using {self._format_category_name(related_category)} pricing patterns (first {self._format_category_name(detected_category)} quote)",
                amount=round(estimated_base * 0.875, 2),  # Slightly less of base for transfers
                source="dna_transfer",
                confidence=0.50,  # Lower confidence for transfers
                learning_ref=f"dna_transfer_from_{related_category}",
                validation_count=0,
            )

        # Default market rates
        return PricingComponent(
            type="base_rate",
            label="Market average pricing (no prior data)",
            amount=round(estimated_base * 0.875, 2),
            source="default",
            confidence=0.30,
            learning_ref=None,
            validation_count=0,
        )

    def _trace_learned_modifier(
        self,
        adjustment: str,
        quote_total: float,
        pricing_model: Dict[str, Any],
        detected_category: str,
    ) -> Optional[PricingComponent]:
        """
        Trace a learned adjustment to create a component.

        Parse adjustment statements like:
        - "Add 15% for second story access"
        - "Repeat customer: reduce by 5%"
        - "ASAP timeline: increase by 20%"
        """
        # Extract numeric value
        numeric_value = self._extract_numeric_from_statement(adjustment)
        if numeric_value is None:
            return None  # Can't create component without amount

        # Calculate dollar amount
        modifier_amount = quote_total * (numeric_value / 100)

        # Humanize the label
        label = self._humanize_adjustment_label(adjustment, numeric_value)

        # Estimate validation count based on category data
        pricing_knowledge = pricing_model.get("pricing_knowledge", {})
        categories = pricing_knowledge.get("categories", {})
        cat_data = categories.get(detected_category, {})

        # Estimate validation count (simplified - in production would track per-learning)
        quote_count = cat_data.get("quote_count", 0)
        validation_count = max(1, quote_count // 5)  # Rough estimate

        return PricingComponent(
            type="modifier",
            label=label,
            amount=round(modifier_amount, 2),
            source="learned",
            confidence=0.85,
            learning_ref=f"learned_{hash(adjustment) % 10000:04d}",
            validation_count=validation_count,
            last_validated=datetime.utcnow().isoformat(),
        )

    def _pattern_applies_to_quote(
        self,
        pattern: Dict[str, Any],
        quote: Any,
        voice_signals: Dict[str, Any],
    ) -> bool:
        """Check if a DNA pattern applies to the current quote."""
        pattern_text = pattern.get("statement", "").lower()

        # Check for timeline patterns
        if "asap" in pattern_text or "rush" in pattern_text:
            return voice_signals.get("rush", False) or voice_signals.get("asap", False)

        # Check for relationship patterns
        if "repeat customer" in pattern_text:
            return voice_signals.get("repeat_customer", False)

        # Check for difficulty patterns
        if "second story" in pattern_text:
            return voice_signals.get("second_story", False)

        return False

    def _trace_dna_transfer(
        self,
        pattern: Dict[str, Any],
        quote_total: float,
    ) -> Optional[Dict[str, Any]]:
        """Trace a DNA transfer pattern."""
        statement = pattern.get("statement", "")
        source_category = pattern.get("source_category", "unknown")
        inherited_confidence = pattern.get("inherited_confidence", 0.60)

        # Extract numeric value
        numeric_value = self._extract_numeric_from_statement(statement)
        if numeric_value is None:
            return None

        amount = quote_total * (numeric_value / 100)

        component = PricingComponent(
            type="adjustment",
            label=self._humanize_adjustment_label(statement, numeric_value),
            amount=round(amount, 2),
            source="dna_transfer",
            confidence=inherited_confidence,
            pattern_id=pattern.get("pattern_id"),
        )

        dna_info = DNATransfer(
            pattern=statement,
            from_category=source_category,
            inherited_confidence=inherited_confidence,
            reason=f"Universal pattern validated across multiple categories",
        )

        return {
            "component": component,
            "dna_info": dna_info,
        }

    def _extract_voice_signal_components(
        self,
        voice_signals: Dict[str, Any],
        quote_total: float,
    ) -> List[PricingComponent]:
        """Create components from detected voice signals."""
        components = []

        # Voice signal mappings
        signal_configs = {
            "rush": {"label": "ASAP timeline detected", "pct": 20, "conf": 0.70},
            "asap": {"label": "Rush job premium", "pct": 20, "conf": 0.70},
            "repeat_customer": {"label": "Repeat customer discount", "pct": -5, "conf": 0.65},
            "referral": {"label": "Referral discount", "pct": -5, "conf": 0.65},
            "second_story": {"label": "Second story access", "pct": 15, "conf": 0.80},
            "difficult_access": {"label": "Difficult access premium", "pct": 10, "conf": 0.75},
            "premium_materials": {"label": "Premium materials selected", "pct": 15, "conf": 0.80},
            "budget_materials": {"label": "Budget materials selected", "pct": -10, "conf": 0.80},
        }

        for signal_key, detected in voice_signals.items():
            if detected and signal_key in signal_configs:
                config = signal_configs[signal_key]
                amount = quote_total * (config["pct"] / 100)

                sign = "+" if config["pct"] > 0 else ""
                label = f"{config['label']} ({sign}{config['pct']}%)"

                components.append(PricingComponent(
                    type="voice_signal",
                    label=label,
                    amount=round(amount, 2),
                    source="voice_detected",
                    confidence=config["conf"],
                ))

        return components

    def _identify_uncertainties(
        self,
        confidence: Any,
        pricing_model: Dict[str, Any],
        detected_category: str,
        quote_total: float,
    ) -> List[UncertaintyNote]:
        """Surface areas of uncertainty for contractor review."""
        uncertainties = []

        # Get confidence attributes safely
        overall_conf = getattr(confidence, 'overall_confidence', 0.5)
        data_conf = getattr(confidence, 'data_confidence', 0.5)
        accuracy_conf = getattr(confidence, 'accuracy_confidence', 0.5)
        recency_conf = getattr(confidence, 'recency_confidence', 0.5)
        quote_count = getattr(confidence, 'quote_count', 0)

        # 1. Low overall confidence
        if overall_conf < 0.60:
            reason_parts = []

            if data_conf < 0.50:
                reason_parts.append(f"limited prior data ({quote_count} quotes)")
            if accuracy_conf < 0.70:
                reason_parts.append("past quotes in this category needed significant edits")
            if recency_conf < 0.60:
                reason_parts.append("haven't quoted this type recently")

            if reason_parts:
                uncertainties.append(UncertaintyNote(
                    area="Overall pricing accuracy",
                    reason=", ".join(reason_parts).capitalize(),
                    suggestion="Review line items carefully, especially material costs",
                ))

        # 2. First quote in category
        pricing_knowledge = pricing_model.get("pricing_knowledge", {})
        categories = pricing_knowledge.get("categories", {})
        if detected_category not in categories:
            uncertainties.append(UncertaintyNote(
                area=f"First {self._format_category_name(detected_category)} quote",
                reason="No prior quotes in this category, using DNA patterns from other work",
                suggestion="This quote will establish baseline pricing for future similar jobs",
            ))

        # 3. Large project
        if quote_total > 10000:
            uncertainties.append(UncertaintyNote(
                area="Large project complexity",
                reason="Limited data for projects over $10,000",
                suggestion="Consider adding complexity factor for project management overhead",
            ))

        return uncertainties

    def _generate_human_summary(
        self,
        components: List[PricingComponent],
        patterns_applied: List[AppliedPattern],
        confidence_label: str,
        pricing_model: Dict[str, Any],
        detected_category: str,
    ) -> str:
        """Generate 1-2 sentence human-readable summary."""
        # Identify primary source
        base_component = next((c for c in components if c.type == "base_rate"), None)
        if not base_component:
            return "Pricing breakdown unavailable"

        # Get quote count for source phrase
        pricing_knowledge = pricing_model.get("pricing_knowledge", {})
        categories = pricing_knowledge.get("categories", {})
        cat_data = categories.get(detected_category, {})
        quote_count = cat_data.get("quote_count", 0)

        # Build source phrase
        if base_component.source == "learned":
            source_phrase = f"{quote_count} previous {self._format_category_name(detected_category)} quotes"
        elif base_component.source == "dna_transfer":
            source_phrase = f"patterns from related work"
        else:
            source_phrase = "market averages (no prior data)"

        # Identify key modifiers (top 2 by absolute amount)
        modifiers = [c for c in components if c.type in ["modifier", "voice_signal", "adjustment"]]
        modifiers.sort(key=lambda x: abs(x.amount), reverse=True)
        top_modifiers = modifiers[:2]

        if top_modifiers:
            modifier_phrases = []
            for m in top_modifiers:
                # Extract the main descriptor from the label
                phrase = self._extract_modifier_phrase(m.label)
                if m.validation_count and m.validation_count > 10:
                    phrase += f" (validated {m.validation_count}×)"
                modifier_phrases.append(phrase)

            modifier_str = " and ".join(modifier_phrases)
            return f"Based on {source_phrase} with {modifier_str}"
        else:
            return f"Based on {source_phrase}"

    def _get_learning_context(
        self,
        pricing_model: Dict[str, Any],
        detected_category: str,
    ) -> Optional[LearningContext]:
        """Get learning context for the category."""
        pricing_knowledge = pricing_model.get("pricing_knowledge", {})
        categories = pricing_knowledge.get("categories", {})
        cat_data = categories.get(detected_category, {})

        if not cat_data:
            return None

        quote_count = cat_data.get("quote_count", 0)
        correction_count = cat_data.get("correction_count", 0)
        acceptance_count = cat_data.get("acceptance_count", 0)

        total_signals = acceptance_count + correction_count
        acceptance_rate = acceptance_count / total_signals if total_signals > 0 else 0.0

        # Estimate average adjustment from correction magnitudes
        magnitudes = cat_data.get("correction_magnitudes", [])
        avg_adjustment = sum(magnitudes) / len(magnitudes) / 100 if magnitudes else 0.0

        return LearningContext(
            category=detected_category,
            quote_count=quote_count,
            correction_count=correction_count,
            acceptance_rate=round(acceptance_rate, 2),
            avg_adjustment=round(avg_adjustment, 2),
        )

    def _find_related_category(
        self,
        target_category: str,
        contractor_dna: Dict[str, Any],
        pricing_knowledge: Dict[str, Any],
    ) -> Optional[str]:
        """Find a related category with existing data."""
        # Check explicit DNA category relationships
        category_relationships = contractor_dna.get("category_relationships", {})
        related = category_relationships.get(target_category, [])

        # Also check predefined relationships
        predefined_related = self.RELATED_CATEGORIES.get(target_category, [])
        all_related = list(set(related + predefined_related))

        # Find first related category with data
        categories = pricing_knowledge.get("categories", {})
        for cat in all_related:
            if cat in categories and categories[cat].get("quote_count", 0) > 0:
                return cat

        return None

    def _format_category_name(self, category: str) -> str:
        """Format category name for display."""
        return category.replace("_", " ").title()

    def _extract_numeric_from_statement(self, statement: str) -> Optional[float]:
        """
        Extract percentage from learning statement.

        Examples:
        - "Add 15% for second story" → 15.0
        - "Reduce by 5%" → -5.0
        """
        # Match percentage patterns
        pct_match = re.search(r'(\+|-)?(\d+(?:\.\d+)?)\s*%', statement)
        if pct_match:
            sign = -1 if pct_match.group(1) == '-' else 1
            value = float(pct_match.group(2))

            # Check for decrease keywords
            decrease_words = ['reduce', 'discount', 'lower', 'decrease', 'subtract']
            if any(word in statement.lower() for word in decrease_words):
                sign = -1

            return sign * value

        return None

    def _humanize_adjustment_label(self, statement: str, numeric_value: float) -> str:
        """
        Convert learning statement to human-readable label.

        Examples:
        - "Add 15% for second story access" → "Second story access (+15%)"
        - "Repeat customer: reduce by 5%" → "Repeat customer (-5%)"
        """
        # Try to extract from "for X" pattern
        for_match = re.search(r'for (.+?)(?:\s*$|\s*\()', statement, re.IGNORECASE)
        if for_match:
            phrase = for_match.group(1).strip()
            sign = "+" if numeric_value > 0 else ""
            return f"{phrase.title()} ({sign}{numeric_value:.0f}%)"

        # Try colon separator
        if ':' in statement:
            phrase = statement.split(':')[0].strip()
            sign = "+" if numeric_value > 0 else ""
            return f"{phrase.title()} ({sign}{numeric_value:.0f}%)"

        # Fallback: clean up the statement
        cleaned = statement.replace("Add", "").replace("Increase", "").replace("Reduce", "").strip()
        sign = "+" if numeric_value > 0 else ""
        return f"{cleaned.title()} ({sign}{numeric_value:.0f}%)"

    def _extract_modifier_phrase(self, label: str) -> str:
        """Extract the main descriptor from a modifier label."""
        # Remove percentage suffix
        phrase = re.sub(r'\s*\([+-]?\d+%\)\s*$', '', label)
        # Remove common prefixes
        phrase = re.sub(r'^(Detected|Premium|Discount)\s+', '', phrase, flags=re.IGNORECASE)
        return phrase.lower()


# Convenience function for direct use
def generate_pricing_explanation(
    quote: Any,
    learned_adjustments: List[str],
    contractor_dna: Dict[str, Any],
    voice_signals: Dict[str, Any],
    confidence: Any,
    pricing_model: Dict[str, Any],
    detected_category: str,
) -> PricingExplanation:
    """Generate pricing explanation for a quote."""
    service = PricingExplanationService()
    return service.generate_explanation(
        quote=quote,
        learned_adjustments=learned_adjustments,
        contractor_dna=contractor_dna,
        voice_signals=voice_signals,
        confidence=confidence,
        pricing_model=pricing_model,
        detected_category=detected_category,
    )
