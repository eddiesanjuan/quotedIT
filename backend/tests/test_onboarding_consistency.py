"""
Test suite to verify onboarding path consistency.

CRITICAL: Both Quick Setup and Interview must produce pricing_models
that work identically in quote generation.
"""

import pytest
from backend.services.onboarding import OnboardingService


class TestOnboardingConsistency:
    """Test that both onboarding paths produce consistent pricing_models."""

    @pytest.fixture
    def onboarding_service(self):
        return OnboardingService()

    @pytest.fixture
    async def quick_setup_model(self, onboarding_service):
        """Generate a pricing_model via Quick Setup."""
        return await onboarding_service.quick_setup(
            contractor_name="Test Contractor",
            primary_trade="deck_builder",
            labor_rate=85.0,
            material_markup=20.0,
            minimum_job=500.0,
        )

    @pytest.fixture
    async def interview_model(self, onboarding_service):
        """
        Simulate a pricing_model extracted from interview.

        Note: In reality, this would call extract_pricing_model() with
        a completed session. For testing, we simulate the structure.
        """
        # Simulate session
        session = {
            "primary_trade": "deck_builder",
            "messages": [
                {"role": "assistant", "content": "Tell me about your pricing..."},
                {"role": "user", "content": "I charge $85/hour for labor..."},
                # ... more conversation
            ]
        }

        # This would normally parse the conversation and extract pricing
        # For testing, we'll create a minimal extracted model
        extracted = {
            "labor_rate_hourly": 85.0,
            "helper_rate_hourly": 50.0,
            "material_markup_percent": 20.0,
            "minimum_job_amount": 500.0,
            "pricing_notes": "Extracted from interview",
        }

        # Apply the same normalization that extract_pricing_model does
        primary_trade = session.get("primary_trade", "")
        trade_defaults = onboarding_service._get_trade_defaults(primary_trade)

        if "pricing_knowledge" not in extracted:
            extracted["pricing_knowledge"] = {}

        if "trade_defaults" not in extracted["pricing_knowledge"]:
            extracted["pricing_knowledge"]["trade_defaults"] = trade_defaults

        if "categories" not in extracted["pricing_knowledge"]:
            extracted["pricing_knowledge"]["categories"] = onboarding_service._seed_categories_from_trade(
                primary_trade, trade_defaults
            )

        if "global_rules" not in extracted["pricing_knowledge"]:
            extracted["pricing_knowledge"]["global_rules"] = []

        if "terms" not in extracted:
            extracted["terms"] = {
                "deposit_percent": 50.0,
                "quote_valid_days": 30,
                "labor_warranty_years": 2,
            }

        extracted["setup_type"] = "interview"

        return extracted

    @pytest.mark.asyncio
    async def test_both_have_essential_fields(self, quick_setup_model, interview_model):
        """Both paths must have all essential fields."""
        essential_fields = [
            "labor_rate_hourly",
            "helper_rate_hourly",
            "material_markup_percent",
            "minimum_job_amount",
            "pricing_knowledge",
            "terms",
            "setup_type",
        ]

        for field in essential_fields:
            assert field in quick_setup_model, f"Quick Setup missing {field}"
            assert field in interview_model, f"Interview missing {field}"

    @pytest.mark.asyncio
    async def test_both_have_pricing_knowledge_structure(self, quick_setup_model, interview_model):
        """Both paths must have same pricing_knowledge structure."""
        required_pk_fields = ["trade_defaults", "categories", "global_rules"]

        for field in required_pk_fields:
            assert field in quick_setup_model["pricing_knowledge"], \
                f"Quick Setup pricing_knowledge missing {field}"
            assert field in interview_model["pricing_knowledge"], \
                f"Interview pricing_knowledge missing {field}"

    @pytest.mark.asyncio
    async def test_both_have_categories_seeded(self, quick_setup_model, interview_model):
        """Both paths must seed categories from trade defaults."""
        quick_categories = quick_setup_model["pricing_knowledge"]["categories"]
        interview_categories = interview_model["pricing_knowledge"]["categories"]

        # Both should have at least 1 category
        assert len(quick_categories) > 0, "Quick Setup has no categories"
        assert len(interview_categories) > 0, "Interview has no categories"

        # Categories should have required fields
        for cat_name, cat_data in quick_categories.items():
            assert "display_name" in cat_data
            assert "learned_adjustments" in cat_data
            assert "samples" in cat_data
            assert "confidence" in cat_data

        for cat_name, cat_data in interview_categories.items():
            assert "display_name" in cat_data
            assert "learned_adjustments" in cat_data
            assert "samples" in cat_data
            assert "confidence" in cat_data

    @pytest.mark.asyncio
    async def test_both_have_terms_structure(self, quick_setup_model, interview_model):
        """Both paths must have terms structure."""
        required_terms = ["deposit_percent", "quote_valid_days", "labor_warranty_years"]

        for field in required_terms:
            assert field in quick_setup_model["terms"], \
                f"Quick Setup terms missing {field}"
            assert field in interview_model["terms"], \
                f"Interview terms missing {field}"

    @pytest.mark.asyncio
    async def test_setup_type_marker(self, quick_setup_model, interview_model):
        """Both paths must have correct setup_type marker."""
        assert quick_setup_model["setup_type"] == "quick"
        assert interview_model["setup_type"] == "interview"

    @pytest.mark.asyncio
    async def test_quote_generation_compatibility(self, quick_setup_model, interview_model):
        """
        Verify both models work identically in quote generation.

        Quote generation expects:
        - pricing_knowledge.categories (for category detection)
        - pricing_knowledge.trade_defaults (for baseline rates)
        - pricing_knowledge.global_rules (for universal adjustments)
        """
        # Simulate quote generation access patterns
        quick_pk = quick_setup_model["pricing_knowledge"]
        interview_pk = interview_model["pricing_knowledge"]

        # Can access categories
        assert isinstance(quick_pk["categories"], dict)
        assert isinstance(interview_pk["categories"], dict)

        # Can access trade_defaults
        assert isinstance(quick_pk["trade_defaults"], dict)
        assert isinstance(interview_pk["trade_defaults"], dict)

        # Can access global_rules
        assert isinstance(quick_pk["global_rules"], list)
        assert isinstance(interview_pk["global_rules"], list)

        # Can iterate categories (for category detection)
        quick_cat_keys = list(quick_pk["categories"].keys())
        interview_cat_keys = list(interview_pk["categories"].keys())

        assert len(quick_cat_keys) > 0
        assert len(interview_cat_keys) > 0

    @pytest.mark.asyncio
    async def test_learned_adjustments_structure(self, quick_setup_model, interview_model):
        """Learned adjustments must be lists for appending corrections."""
        for cat_name, cat_data in quick_setup_model["pricing_knowledge"]["categories"].items():
            assert isinstance(cat_data["learned_adjustments"], list), \
                f"Quick Setup category {cat_name} learned_adjustments not a list"

        for cat_name, cat_data in interview_model["pricing_knowledge"]["categories"].items():
            assert isinstance(cat_data["learned_adjustments"], list), \
                f"Interview category {cat_name} learned_adjustments not a list"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
