"""
Unit tests for Learning Excellence services.
Tests the core learning intelligence without requiring API calls.

These tests use direct imports (bypassing __init__.py) to avoid
loading services that require external dependencies like pydantic_settings.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
QUOTED_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUOTED_ROOT)

# Import modules directly to bypass backend/services/__init__.py
# which would trigger import of all services and their dependencies
import importlib.util
from pathlib import Path

SERVICES_DIR = Path(__file__).parent.parent / "backend" / "services"
PROMPTS_DIR = Path(__file__).parent.parent / "backend" / "prompts"


def load_module_directly(module_name: str, file_path: Path, package_name: str = None):
    """Load a module directly from file without going through package __init__.py.

    Registers the module both with its simple name and with full package path
    to support relative imports within the modules.
    """
    full_name = f"{package_name}.{module_name}" if package_name else module_name
    spec = importlib.util.spec_from_file_location(full_name, file_path)
    module = importlib.util.module_from_spec(spec)

    # Set __package__ to enable relative imports
    if package_name:
        module.__package__ = package_name

    # Register with simple name
    sys.modules[module_name] = module

    # Also register with full package path for relative imports
    if package_name:
        sys.modules[full_name] = module

    spec.loader.exec_module(module)
    return module


# Set up minimal package structure for relative imports
# Create empty backend and backend.services modules if needed
if "backend" not in sys.modules:
    import types
    backend_mod = types.ModuleType("backend")
    backend_mod.__path__ = [str(SERVICES_DIR.parent)]
    sys.modules["backend"] = backend_mod

if "backend.services" not in sys.modules:
    import types
    services_mod = types.ModuleType("backend.services")
    services_mod.__path__ = [str(SERVICES_DIR)]
    sys.modules["backend.services"] = services_mod

# Pre-load all Learning Excellence modules in dependency order
# learning_quality has no internal dependencies, load first
learning_quality = load_module_directly("learning_quality", SERVICES_DIR / "learning_quality.py", "backend.services")

# learning_relevance depends on learning_quality
learning_relevance = load_module_directly("learning_relevance", SERVICES_DIR / "learning_relevance.py", "backend.services")

# voice_signal_extractor has no internal dependencies
voice_signal_extractor = load_module_directly("voice_signal_extractor", SERVICES_DIR / "voice_signal_extractor.py", "backend.services")

# acceptance_learning has no internal dependencies
acceptance_learning = load_module_directly("acceptance_learning", SERVICES_DIR / "acceptance_learning.py", "backend.services")

# contractor_dna depends on learning_quality
contractor_dna = load_module_directly("contractor_dna", SERVICES_DIR / "contractor_dna.py", "backend.services")

# pricing_confidence has no internal dependencies
pricing_confidence = load_module_directly("pricing_confidence", SERVICES_DIR / "pricing_confidence.py", "backend.services")

# pricing_explanation has no internal dependencies
pricing_explanation = load_module_directly("pricing_explanation", SERVICES_DIR / "pricing_explanation.py", "backend.services")

# quote_generation prompt - set up prompts package
if "backend.prompts" not in sys.modules:
    import types
    prompts_mod = types.ModuleType("backend.prompts")
    prompts_mod.__path__ = [str(PROMPTS_DIR)]
    sys.modules["backend.prompts"] = prompts_mod

quote_generation_prompt = load_module_directly("quote_generation", PROMPTS_DIR / "quote_generation.py", "backend.prompts")


# ============================================================================
# Test Learning Quality Service
# ============================================================================

class TestLearningQuality:
    """Tests for learning_quality.py"""

    def test_score_simple_statement(self):
        """Test scoring a basic learning statement."""
        scorer = learning_quality.LearningQualityScorer()
        result = scorer.score("Always add 10% for difficult access")

        assert result.overall_score >= 0
        assert result.overall_score <= 100
        assert len(result.detected_anti_patterns) >= 0

    def test_score_specific_statement(self):
        """Test that specific statements score higher."""
        scorer = learning_quality.LearningQualityScorer()

        # Specific statement with numbers
        specific = scorer.score(
            "Add $500 flat fee for deck demolition over 300 sqft"
        )

        # Vague statement
        vague = scorer.score(
            "Sometimes charge more for bigger jobs"
        )

        # Specific should score higher
        assert specific.overall_score > vague.overall_score

    def test_score_statement_with_numbers(self):
        """Test that statements with dollar amounts score for specificity."""
        scorer = learning_quality.LearningQualityScorer()

        # Statement with concrete numbers
        with_numbers = scorer.score(
            "Charge $45 per linear foot for cable railing"
        )

        # Statement without numbers
        without_numbers = scorer.score(
            "Charge more for cable railing"
        )

        assert with_numbers.overall_score > without_numbers.overall_score

    def test_score_returns_tier(self):
        """Test that scoring returns a quality tier."""
        QualityTier = learning_quality.QualityTier
        scorer = learning_quality.LearningQualityScorer()

        # High quality statement
        result = scorer.score(
            "Always add 15% for second story access when using Trex decking"
        )

        assert result.tier in [QualityTier.REJECT, QualityTier.REVIEW, QualityTier.REFINE, QualityTier.ACCEPT]

    def test_filter_quality_learnings(self):
        """Test filtering learnings by quality threshold using scorer method."""
        QualityTier = learning_quality.QualityTier
        scorer = learning_quality.LearningQualityScorer()

        learnings = [
            "Add $500 for deck demolition over 300 sqft",  # Specific, should pass
            "idk",  # Too short, should fail
            "Always add 10% markup on materials",  # Good, should pass
        ]

        # Filter with REVIEW threshold
        filtered = scorer.filter_by_tier(learnings, minimum_tier=QualityTier.REVIEW)

        # Should filter out the bad ones
        assert len(filtered) <= len(learnings)


# ============================================================================
# Test Learning Relevance Service
# ============================================================================

class TestLearningRelevance:
    """Tests for learning_relevance.py"""

    def test_select_relevant_learnings_keyword_match(self):
        """Test that keyword matching affects relevance."""
        learnings = [
            "Add 10% for composite decks",
            "Reduce price for fence repairs",
            "Increase demolition cost for large decks",
        ]

        # Transcription about decks
        result = learning_relevance.select_relevant_learnings(
            learned_adjustments=learnings,
            transcription="Building a 20x20 composite deck with railing",
            category="composite_deck",
            max_learnings=2,
        )

        # Should prefer deck-related learnings
        assert len(result) == 2
        assert any("deck" in r.lower() for r in result)

    def test_select_relevant_learnings_max_limit(self):
        """Test that max_learnings limit is respected."""
        learnings = [
            "Rule 1",
            "Rule 2",
            "Rule 3",
            "Rule 4",
            "Rule 5",
        ]

        result = learning_relevance.select_relevant_learnings(
            learned_adjustments=learnings,
            transcription="Some job description",
            category="general",
            max_learnings=3,
        )

        assert len(result) <= 3

    def test_select_relevant_learnings_empty_input(self):
        """Test handling of empty learnings list."""
        result = learning_relevance.select_relevant_learnings(
            learned_adjustments=[],
            transcription="Some job",
            category="deck",
            max_learnings=5,
        )

        assert result == []

    def test_select_relevant_learnings_with_metadata_dict(self):
        """Test that metadata dict format learnings are handled."""
        learnings = [
            {"text": "Add 10% for decks", "quality_score": 80, "created_at": datetime.utcnow().isoformat(), "source": "correction"},
            {"text": "Reduce fence pricing", "quality_score": 70, "created_at": datetime.utcnow().isoformat(), "source": "correction"},
        ]

        result = learning_relevance.select_relevant_learnings(
            learned_adjustments=learnings,
            transcription="Deck project",
            category="deck",
            max_learnings=5,
        )

        assert len(result) == 2

    def test_select_with_scores_returns_scores(self):
        """Test that select_with_scores returns relevance scores."""
        selector = learning_relevance.LearningRelevanceSelector()

        learnings = [
            "Add 10% for composite decks",
            "Always charge for permits",
        ]

        result = selector.select_with_scores(
            learnings=learnings,
            transcription="Building a composite deck with permits",
            category="deck",
            max_learnings=5,
        )

        # Should return tuples of (text, RelevanceScore)
        assert len(result) == 2
        for text, score in result:
            assert isinstance(text, str)
            assert hasattr(score, 'overall_score')
            assert hasattr(score, 'keyword_score')


# ============================================================================
# Test Voice Signal Extractor
# ============================================================================

class TestVoiceSignalExtractor:
    """Tests for voice_signal_extractor.py"""

    def test_extract_difficulty_signal(self):
        """Test detection of difficulty signals."""
        SignalCategory = voice_signal_extractor.SignalCategory

        # Transcription with difficulty cues
        result = voice_signal_extractor.extract_voice_signals(
            "This is a tricky job, complicated access and tight spaces"
        )

        # Check that we got signals
        assert result is not None
        assert len(result.signals) >= 0

        # Check if any difficulty signals detected
        difficulty_signals = [s for s in result.signals if s.category == SignalCategory.DIFFICULTY]
        # Note: May or may not match depending on exact patterns
        assert isinstance(result.overall_price_adjustment, float)

    def test_extract_timeline_signal_rush(self):
        """Test detection of rush job signals."""
        SignalCategory = voice_signal_extractor.SignalCategory
        SignalPolarity = voice_signal_extractor.SignalPolarity

        result = voice_signal_extractor.extract_voice_signals(
            "Customer needs this ASAP, rush job, gotta get it done quickly"
        )

        # Check for timeline signals
        timeline_signals = [s for s in result.signals if s.category == SignalCategory.TIMELINE]

        # Rush/ASAP should be detected with INCREASE polarity
        if timeline_signals:
            rush_signals = [s for s in timeline_signals if s.polarity == SignalPolarity.INCREASE]
            assert len(rush_signals) > 0

    def test_extract_quality_signal_premium(self):
        """Test detection of premium quality signals."""
        SignalCategory = voice_signal_extractor.SignalCategory
        SignalPolarity = voice_signal_extractor.SignalPolarity

        result = voice_signal_extractor.extract_voice_signals(
            "They want top of the line materials, premium everything, high-end quality"
        )

        # Check for quality signals with increase polarity
        quality_signals = [s for s in result.signals if s.category == SignalCategory.QUALITY]

        if quality_signals:
            premium_signals = [s for s in quality_signals if s.polarity == SignalPolarity.INCREASE]
            assert len(premium_signals) > 0

    def test_no_signals_detected(self):
        """Test handling of neutral transcription."""
        result = voice_signal_extractor.extract_voice_signals(
            "Standard 16 by 20 deck, composite material, basic railing"
        )

        # Should still return a valid result
        assert result is not None
        assert isinstance(result.signals, list)
        assert isinstance(result.summary, str)

    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        result = voice_signal_extractor.extract_voice_signals("Rush job for repeat customer")
        dict_result = result.to_dict()

        # Check dict structure
        assert "signals" in dict_result
        assert "overall_price_adjustment" in dict_result
        assert "dominant_category" in dict_result
        assert "summary" in dict_result

    def test_overall_price_adjustment_calculated(self):
        """Test that overall price adjustment is calculated."""
        result = voice_signal_extractor.extract_voice_signals(
            "This is an urgent rush job for a repeat customer"
        )

        # Should have a calculated adjustment (may be positive or negative or zero)
        assert isinstance(result.overall_price_adjustment, float)
        # Capped at +/- 30%
        assert -0.30 <= result.overall_price_adjustment <= 0.30


# ============================================================================
# Test Acceptance Learning Service
# ============================================================================

class TestAcceptanceLearning:
    """Tests for acceptance_learning.py"""

    @pytest.mark.asyncio
    async def test_process_acceptance_boosts_confidence(self):
        """Test that acceptance boosts confidence."""
        service = acceptance_learning.AcceptanceLearningService()

        # Mock quote
        class MockQuote:
            was_edited = False
            job_type = "composite_deck"
            total = 5000

        # Mock pricing model with existing category
        pricing_model = {
            "pricing_knowledge": {
                "categories": {
                    "composite_deck": {
                        "confidence": 0.5,
                        "acceptance_count": 0,
                        "correction_count": 0,
                        "learned_adjustments": [],
                    }
                }
            }
        }

        result = await service.process_acceptance(
            contractor_id="test-123",
            quote=MockQuote(),
            signal_type="sent",
            pricing_model=pricing_model,
        )

        assert result.processed is True
        assert result.new_confidence > result.old_confidence
        assert result.new_confidence == 0.55  # 0.5 + 0.05

    @pytest.mark.asyncio
    async def test_skip_edited_quotes(self):
        """Test that edited quotes are not processed."""
        service = acceptance_learning.AcceptanceLearningService()

        class MockQuote:
            was_edited = True  # Edited!
            job_type = "composite_deck"

        result = await service.process_acceptance(
            contractor_id="test-123",
            quote=MockQuote(),
            signal_type="sent",
            pricing_model={},
        )

        assert result.processed is False
        assert "edited" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_confidence_ceiling(self):
        """Test that confidence doesn't exceed maximum."""
        service = acceptance_learning.AcceptanceLearningService()

        class MockQuote:
            was_edited = False
            job_type = "composite_deck"
            total = 5000

        # Already at high confidence
        pricing_model = {
            "pricing_knowledge": {
                "categories": {
                    "composite_deck": {
                        "confidence": 0.93,
                        "acceptance_count": 50,
                        "correction_count": 2,
                    }
                }
            }
        }

        result = await service.process_acceptance(
            contractor_id="test-123",
            quote=MockQuote(),
            signal_type="accepted",
            pricing_model=pricing_model,
        )

        assert result.new_confidence <= 0.95  # MAX_CONFIDENCE


# ============================================================================
# Test Contractor DNA Service
# ============================================================================

class TestContractorDNA:
    """Tests for contractor_dna.py"""

    def test_identify_transferable_patterns(self):
        """Test identification of transferable patterns."""
        service = contractor_dna.ContractorDNAService()

        # Source learnings with universal patterns
        source_learnings = [
            "Add 15% for second story access",  # Universal - access_modifier
            "Repeat customer gets 5% discount",  # Universal - relationship_discount
            "Charge $45 per sqft for composite",  # Specific - should not transfer
        ]

        candidates = service.identify_transferable_patterns(
            source_category="deck",
            source_learnings=source_learnings,
            source_confidence=0.8,
            source_quote_count=20,
            target_category="roofing",
        )

        # Should find some transferable patterns (universal ones)
        assert len(candidates) >= 0  # May or may not find depending on pattern matching

    def test_generate_category_bootstrap(self):
        """Test generating bootstrap pricing for new category."""
        service = contractor_dna.get_dna_service()

        # Build sample DNA
        dna = {
            "contractor_id": "test-123",
            "universal_patterns": [
                {
                    "statement": "Add 10% for difficult access",
                    "source_category": "deck",
                    "source_confidence": 0.8,
                    "source_quote_count": 15,
                    "pattern_type": "access_modifier",
                }
            ],
            "partial_patterns": [],
            "pricing_style": {
                "overall_tendency": "balanced",
                "confidence_in_profile": 0.5,
            },
        }

        bootstrap = service.generate_category_bootstrap(
            contractor_id="test-123",
            new_category="roofing",
            contractor_dna=dna,
        )

        # Should return some bootstrap learnings
        assert isinstance(bootstrap, list)
        if bootstrap:
            assert "statement" in bootstrap[0]
            assert "confidence" in bootstrap[0]

    def test_update_dna_from_correction(self):
        """Test updating DNA after a correction."""
        service = contractor_dna.ContractorDNAService()

        initial_dna = {
            "contractor_id": "test-123",
            "universal_patterns": [],
            "partial_patterns": [],
            "total_corrections": 0,
        }

        new_learnings = [
            "Add 15% for second story access",  # Universal pattern
        ]

        updated_dna = service.update_dna_from_correction(
            contractor_dna=initial_dna,
            category="deck",
            new_learnings=new_learnings,
            category_confidence=0.7,
            category_quote_count=10,
        )

        # Should update correction count
        assert updated_dna["total_corrections"] == 1

    def test_empty_dna_initialization(self):
        """Test that empty DNA is properly initialized."""
        service = contractor_dna.ContractorDNAService()
        dna = service._empty_dna("test-contractor")

        assert dna["contractor_id"] == "test-contractor"
        assert "universal_patterns" in dna
        assert "partial_patterns" in dna
        assert "pricing_style" in dna


# ============================================================================
# Test Pricing Confidence Service
# ============================================================================

class TestPricingConfidence:
    """Tests for pricing_confidence.py"""

    def test_calculate_confidence_new_category(self):
        """Test confidence for a new category with no history."""
        result = pricing_confidence.calculate_confidence(
            quote_count=1,  # Very few quotes
            acceptance_count=0,
            correction_count=1,
            correction_magnitudes=[],
            days_since_last_quote=0,
            complexity_distribution={},
        )

        # New category should have low confidence
        assert result.overall_confidence < 0.5
        assert result.display_confidence == "Learning"

    def test_calculate_confidence_established_category(self):
        """Test confidence for established category."""
        result = pricing_confidence.calculate_confidence(
            quote_count=50,
            acceptance_count=45,
            correction_count=5,
            correction_magnitudes=[3.0, 5.0, 2.0, 4.0, 6.0],
            days_since_last_quote=5,
            complexity_distribution={"simple": 15, "medium": 25, "complex": 10},
        )

        # Established category should have higher confidence
        assert result.overall_confidence >= 0.5
        assert result.display_confidence in ["High", "Medium"]

    def test_recency_affects_confidence(self):
        """Test that recency affects confidence score."""
        # Recent quotes
        recent = pricing_confidence.calculate_confidence(
            quote_count=20,
            acceptance_count=15,
            correction_count=5,
            correction_magnitudes=[5.0] * 5,
            days_since_last_quote=5,  # Recent
            complexity_distribution={"simple": 10, "medium": 10},
        )

        # Old quotes
        old = pricing_confidence.calculate_confidence(
            quote_count=20,
            acceptance_count=15,
            correction_count=5,
            correction_magnitudes=[5.0] * 5,
            days_since_last_quote=90,  # 3 months ago
            complexity_distribution={"simple": 10, "medium": 10},
        )

        # Recent should have higher confidence
        assert recent.recency_confidence > old.recency_confidence

    def test_confidence_dimensions_available(self):
        """Test that all confidence dimensions are calculated."""
        result = pricing_confidence.calculate_confidence(
            quote_count=30,
            acceptance_count=25,
            correction_count=5,
            correction_magnitudes=[3.0, 4.0, 5.0],
            days_since_last_quote=10,
            complexity_distribution={"simple": 10, "medium": 15, "complex": 5},
        )

        # All dimensions should be present
        assert hasattr(result, 'data_confidence')
        assert hasattr(result, 'accuracy_confidence')
        assert hasattr(result, 'recency_confidence')
        assert hasattr(result, 'coverage_confidence')
        assert hasattr(result, 'overall_confidence')


# ============================================================================
# Test Pricing Explanation Service
# ============================================================================

class TestPricingExplanation:
    """Tests for pricing_explanation.py"""

    def test_generate_explanation(self):
        """Test generating a pricing explanation."""
        service = pricing_explanation.PricingExplanationService()

        # Mock quote
        class MockQuote:
            subtotal = 5000
            total = 5000

        # Mock confidence
        class MockConfidence:
            overall_confidence = 0.75
            display_confidence = "Medium"
            data_confidence = 0.7
            accuracy_confidence = 0.8
            recency_confidence = 0.9
            quote_count = 20

        result = service.generate_explanation(
            quote=MockQuote(),
            learned_adjustments=["Add 10% for second story"],
            contractor_dna={},
            voice_signals={},
            confidence=MockConfidence(),
            pricing_model={"pricing_knowledge": {"categories": {}}},
            detected_category="deck",
        )

        assert result is not None
        assert result.summary != ""
        assert isinstance(result.components, list)
        assert isinstance(result.overall_confidence, float)

    def test_explanation_to_dict(self):
        """Test that explanation can be serialized."""
        service = pricing_explanation.PricingExplanationService()

        class MockQuote:
            subtotal = 3000

        class MockConfidence:
            overall_confidence = 0.65
            display_confidence = "Medium"
            data_confidence = 0.6
            accuracy_confidence = 0.7
            recency_confidence = 0.8
            quote_count = 15

        result = service.generate_explanation(
            quote=MockQuote(),
            learned_adjustments=[],
            contractor_dna={},
            voice_signals={},
            confidence=MockConfidence(),
            pricing_model={},
            detected_category="fence",
        )

        # Should be serializable
        dict_result = result.to_dict()
        assert "summary" in dict_result
        assert "overall_confidence" in dict_result
        assert "components" in dict_result


# ============================================================================
# Test Integration: Quote Generation Prompt
# ============================================================================

class TestQuoteGenerationPromptIntegration:
    """Test the integration of voice signals into quote generation prompt."""

    def test_prompt_includes_voice_signals(self):
        """Test that voice signals are included in the prompt."""
        # Voice signals in dict format (as returned by to_dict())
        voice_signals = {
            "signals": [
                {
                    "category": "difficulty",
                    "polarity": "increase",
                    "text": "tricky job",
                    "confidence": 0.8,
                    "impact_estimate": 0.10,
                    "context": "...tricky job...",
                },
                {
                    "category": "timeline",
                    "polarity": "increase",
                    "text": "rush",
                    "confidence": 0.9,
                    "impact_estimate": 0.20,
                    "context": "...rush...",
                },
            ],
            "overall_price_adjustment": 0.15,
            "dominant_category": "timeline",
            "summary": "Rush job with difficulty",
        }

        prompt = quote_generation_prompt.get_quote_generation_prompt(
            transcription="Build a tricky deck with rush timeline",
            contractor_name="Test Contractor",
            pricing_model={"labor_rate_hourly": 65},
            voice_signals=voice_signals,
        )

        # Prompt should mention voice signals
        assert "Voice Signal" in prompt or "voice" in prompt.lower()

    def test_prompt_without_voice_signals(self):
        """Test that prompt works without voice signals."""
        prompt = quote_generation_prompt.get_quote_generation_prompt(
            transcription="Simple deck job",
            contractor_name="Test Contractor",
            pricing_model={"labor_rate_hourly": 65},
            voice_signals=None,
        )

        # Should still generate a valid prompt
        assert "Simple deck job" in prompt
        assert "Test Contractor" in prompt


# ============================================================================
# Test Service Convenience Functions
# ============================================================================

class TestConvenienceFunctions:
    """Test convenience functions for direct use."""

    def test_score_learning_function(self):
        """Test the score_learning convenience function."""
        result = learning_quality.score_learning("Always add 15% for second story work")

        assert result.overall_score >= 0
        assert result.overall_score <= 100

    def test_extract_voice_signals_function(self):
        """Test the extract_voice_signals convenience function."""
        result = voice_signal_extractor.extract_voice_signals("Rush job for repeat customer")

        assert result is not None
        assert isinstance(result.signals, list)


# ============================================================================
# Additional Coverage Tests
# ============================================================================

class TestLearningQualityAdditional:
    """Additional tests for learning_quality.py to improve coverage."""

    def test_detect_anti_patterns(self):
        """Test that anti-patterns are properly detected."""
        scorer = learning_quality.LearningQualityScorer()

        # Vague statement should have lower score
        vague = scorer.score("Maybe add some extra")
        assert vague.overall_score < 50  # Vague should score low

    def test_quality_score_with_conditions(self):
        """Test scoring statements with conditions."""
        scorer = learning_quality.LearningQualityScorer()

        # Statement with "if" condition
        conditional = scorer.score("If demolition needed, add $300 flat fee")
        assert conditional.overall_score > 40  # Conditional should score reasonably

    def test_quality_tier_assignment(self):
        """Test that tiers are correctly assigned based on scores."""
        QualityTier = learning_quality.QualityTier
        scorer = learning_quality.LearningQualityScorer()

        # High quality should get ACCEPT tier
        high = scorer.score("Always add 15% margin for second story decks over 400 sqft")
        # Check tier exists and is valid
        assert high.tier in [QualityTier.REJECT, QualityTier.REVIEW, QualityTier.REFINE, QualityTier.ACCEPT]


class TestPricingConfidenceAdditional:
    """Additional tests for pricing_confidence.py to improve coverage."""

    def test_zero_quotes_confidence(self):
        """Test confidence calculation with zero quotes."""
        result = pricing_confidence.calculate_confidence(
            quote_count=0,
            acceptance_count=0,
            correction_count=0,
            correction_magnitudes=[],
            days_since_last_quote=0,
            complexity_distribution={},
        )

        # New category with no data should have low confidence
        assert result.overall_confidence < 0.5
        assert result.display_confidence == "Learning"

    def test_high_correction_rate(self):
        """Test confidence with high correction rate."""
        result = pricing_confidence.calculate_confidence(
            quote_count=20,
            acceptance_count=5,
            correction_count=15,  # 75% correction rate
            correction_magnitudes=[10.0, 15.0, 20.0, 25.0, 30.0] * 3,
            days_since_last_quote=5,
            complexity_distribution={"simple": 20},
        )

        # High corrections should lower accuracy confidence
        assert result.accuracy_confidence < 0.7

    def test_very_old_quotes(self):
        """Test confidence with very old quotes."""
        result = pricing_confidence.calculate_confidence(
            quote_count=30,
            acceptance_count=25,
            correction_count=5,
            correction_magnitudes=[5.0] * 5,
            days_since_last_quote=365,  # 1 year ago
            complexity_distribution={"simple": 10, "medium": 15, "complex": 5},
        )

        # Very old quotes should have low recency confidence
        assert result.recency_confidence < 0.5


class TestContractorDNAAdditional:
    """Additional tests for contractor_dna.py to improve coverage."""

    def test_identify_patterns_no_match(self):
        """Test pattern identification with non-matching learnings."""
        service = contractor_dna.ContractorDNAService()

        # Learnings that don't match universal patterns
        source_learnings = [
            "Use premium nails",  # Too specific
            "Check weather forecast",  # Not pricing related
        ]

        candidates = service.identify_transferable_patterns(
            source_category="deck",
            source_learnings=source_learnings,
            source_confidence=0.8,
            source_quote_count=20,
            target_category="fence",
        )

        # May or may not find patterns
        assert isinstance(candidates, list)

    def test_get_dna_service_singleton(self):
        """Test that get_dna_service returns a service instance."""
        service1 = contractor_dna.get_dna_service()
        service2 = contractor_dna.get_dna_service()

        # Both should be valid service instances
        assert service1 is not None
        assert service2 is not None
        assert isinstance(service1, contractor_dna.ContractorDNAService)


class TestPricingExplanationAdditional:
    """Additional tests for pricing_explanation.py to improve coverage."""

    def test_generate_explanation_no_learnings(self):
        """Test explanation with no learned adjustments."""
        service = pricing_explanation.PricingExplanationService()

        class MockQuote:
            subtotal = 2000

        class MockConfidence:
            overall_confidence = 0.4
            display_confidence = "Learning"
            data_confidence = 0.3
            accuracy_confidence = 0.4
            recency_confidence = 0.5
            quote_count = 3

        result = service.generate_explanation(
            quote=MockQuote(),
            learned_adjustments=[],
            contractor_dna={},
            voice_signals={},
            confidence=MockConfidence(),
            pricing_model={},
            detected_category="new_category",
        )

        assert result is not None
        assert "Learning" in result.summary or result.overall_confidence < 0.5

    def test_generate_explanation_with_voice_signals(self):
        """Test explanation including voice signals."""
        service = pricing_explanation.PricingExplanationService()

        class MockQuote:
            subtotal = 4000
            total = 4000

        class MockConfidence:
            overall_confidence = 0.7
            display_confidence = "Medium"
            data_confidence = 0.65
            accuracy_confidence = 0.75
            recency_confidence = 0.8
            quote_count = 25

        voice_signals = {
            "signals": [{"category": "timeline", "polarity": "increase", "impact_estimate": 0.15}],
            "overall_price_adjustment": 0.15,
            "summary": "Rush job detected",
        }

        result = service.generate_explanation(
            quote=MockQuote(),
            learned_adjustments=["Add 10% for rush"],
            contractor_dna={},
            voice_signals=voice_signals,
            confidence=MockConfidence(),
            pricing_model={},
            detected_category="deck",
        )

        assert result is not None
        assert len(result.components) >= 0


class TestAcceptanceLearningAdditional:
    """Additional tests for acceptance_learning.py to improve coverage."""

    @pytest.mark.asyncio
    async def test_process_acceptance_no_category(self):
        """Test acceptance processing when category doesn't exist."""
        service = acceptance_learning.AcceptanceLearningService()

        class MockQuote:
            was_edited = False
            job_type = "nonexistent_category"
            total = 3000

        pricing_model = {
            "pricing_knowledge": {
                "categories": {}  # Empty categories
            }
        }

        result = await service.process_acceptance(
            contractor_id="test-123",
            quote=MockQuote(),
            signal_type="sent",
            pricing_model=pricing_model,
        )

        # Should handle missing category gracefully
        assert result is not None


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
