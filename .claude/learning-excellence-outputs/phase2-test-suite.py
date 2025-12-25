"""
Acceptance Learning - Test Suite

Tests for LEARNING-EXCELLENCE Phase 2: Acceptance signal processing.

Run with: pytest backend/tests/test_acceptance_learning.py -v
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from backend.services.learning import LearningService
from backend.models.database import Quote, Contractor, PricingModel


@pytest.fixture
def learning_service():
    """Fixture for LearningService instance."""
    return LearningService()


@pytest.fixture
def mock_contractor():
    """Mock contractor with ID."""
    contractor = Mock(spec=Contractor)
    contractor.id = "contractor-123"
    return contractor


@pytest.fixture
def mock_pricing_model():
    """Mock pricing model with empty categories."""
    model = Mock(spec=PricingModel)
    model.pricing_knowledge = {
        "categories": {}
    }
    return model


@pytest.fixture
def mock_quote():
    """Mock quote for testing."""
    quote = Mock(spec=Quote)
    quote.id = "quote-123"
    quote.job_type = "deck_composite"
    quote.total = 8500.0
    quote.subtotal = 8500.0
    quote.was_edited = False
    quote.contractor_id = "contractor-123"
    return quote


# ============================================================================
# TEST 1: Basic Acceptance (Sent Signal)
# ============================================================================

@pytest.mark.asyncio
async def test_basic_acceptance_sent_signal(learning_service, mock_quote, mock_contractor, mock_pricing_model):
    """
    Test basic acceptance signal when quote sent without edit.

    Expected:
    - Confidence: 0.50 → 0.55 (+0.05)
    - acceptance_count: 0 → 1
    - accepted_totals: 1 entry
    - learned_adjustments: unchanged
    """
    with patch('backend.services.learning.get_db_service') as mock_db:
        # Setup mocks
        mock_db.return_value.get_contractor_by_id = AsyncMock(return_value=mock_contractor)
        mock_db.return_value.get_pricing_model = AsyncMock(return_value=mock_pricing_model)
        mock_db.return_value.update_pricing_model = AsyncMock()

        # Process acceptance
        result = await learning_service.process_acceptance_learning(
            contractor_id="contractor-123",
            quote=mock_quote,
            signal_type="sent",
        )

        # Assertions
        assert result["processed"] is True
        assert result["signal_type"] == "sent"
        assert result["category"] == "deck_composite"
        assert result["confidence_boost"] == 0.05
        assert result["new_confidence"] == 0.55  # 0.50 + 0.05

        # Check category data
        cat_data = mock_pricing_model.pricing_knowledge["categories"]["deck_composite"]
        assert cat_data["acceptance_count"] == 1
        assert cat_data["confidence"] == 0.55
        assert len(cat_data["accepted_totals"]) == 1
        assert cat_data["accepted_totals"][0]["total"] == 8500.0
        assert cat_data["accepted_totals"][0]["signal_type"] == "sent"
        assert len(cat_data["learned_adjustments"]) == 0  # NO NEW RULES


# ============================================================================
# TEST 2: Acceptance After Acceptance (Confidence Accumulation)
# ============================================================================

@pytest.mark.asyncio
async def test_confidence_accumulation(learning_service, mock_contractor, mock_pricing_model):
    """
    Test confidence accumulation after multiple acceptances.

    Scenario:
    - First quote: $8,500, sent → confidence 0.50 → 0.55
    - Second quote: $9,200, sent → confidence 0.55 → 0.60

    Expected:
    - acceptance_count: 2
    - confidence: 0.60
    - accepted_totals: 2 entries
    """
    # Pre-populate first acceptance
    mock_pricing_model.pricing_knowledge["categories"] = {
        "deck_composite": {
            "display_name": "Deck Composite",
            "tailored_prompt": None,
            "learned_adjustments": [],
            "samples": 1,
            "confidence": 0.55,
            "correction_count": 0,
            "acceptance_count": 1,
            "accepted_totals": [
                {"total": 8500.0, "signal_type": "sent", "quote_id": "quote-1"}
            ],
        }
    }

    # Create second quote
    quote_2 = Mock(spec=Quote)
    quote_2.id = "quote-2"
    quote_2.job_type = "deck_composite"
    quote_2.total = 9200.0
    quote_2.was_edited = False
    quote_2.contractor_id = "contractor-123"

    with patch('backend.services.learning.get_db_service') as mock_db:
        mock_db.return_value.get_contractor_by_id = AsyncMock(return_value=mock_contractor)
        mock_db.return_value.get_pricing_model = AsyncMock(return_value=mock_pricing_model)
        mock_db.return_value.update_pricing_model = AsyncMock()

        # Process second acceptance
        result = await learning_service.process_acceptance_learning(
            contractor_id="contractor-123",
            quote=quote_2,
            signal_type="sent",
        )

        # Assertions
        assert result["processed"] is True
        assert result["new_confidence"] == 0.60  # 0.55 + 0.05

        cat_data = mock_pricing_model.pricing_knowledge["categories"]["deck_composite"]
        assert cat_data["acceptance_count"] == 2
        assert cat_data["confidence"] == 0.60
        assert len(cat_data["accepted_totals"]) == 2
        assert cat_data["accepted_totals"][1]["total"] == 9200.0


# ============================================================================
# TEST 3: Acceptance vs Correction (Mixed Signals)
# ============================================================================

@pytest.mark.asyncio
async def test_mixed_signals_accuracy_ratio(learning_service, mock_contractor, mock_pricing_model):
    """
    Test accuracy ratio calculation with mixed acceptance/correction signals.

    Scenario:
    - 2 acceptances, 1 correction
    - Accuracy ratio: 2/3 = 0.667

    Expected:
    - acceptance_count: 2
    - correction_count: 1
    - accuracy_ratio: 0.667
    """
    # Pre-populate mixed signals
    mock_pricing_model.pricing_knowledge["categories"] = {
        "deck_composite": {
            "display_name": "Deck Composite",
            "tailored_prompt": None,
            "learned_adjustments": ["Some correction learning"],
            "samples": 2,
            "confidence": 0.57,
            "correction_count": 1,
            "acceptance_count": 1,
            "accepted_totals": [
                {"total": 8500.0, "signal_type": "sent", "quote_id": "quote-1"}
            ],
        }
    }

    # Create third quote (acceptance)
    quote_3 = Mock(spec=Quote)
    quote_3.id = "quote-3"
    quote_3.job_type = "deck_composite"
    quote_3.total = 8800.0
    quote_3.was_edited = False
    quote_3.contractor_id = "contractor-123"

    with patch('backend.services.learning.get_db_service') as mock_db:
        mock_db.return_value.get_contractor_by_id = AsyncMock(return_value=mock_contractor)
        mock_db.return_value.get_pricing_model = AsyncMock(return_value=mock_pricing_model)
        mock_db.return_value.update_pricing_model = AsyncMock()

        # Process third acceptance
        result = await learning_service.process_acceptance_learning(
            contractor_id="contractor-123",
            quote=quote_3,
            signal_type="sent",
        )

        # Assertions
        assert result["processed"] is True
        assert result["acceptance_count"] == 2
        assert result["accuracy_ratio"] == pytest.approx(0.667, rel=0.01)

        cat_data = mock_pricing_model.pricing_knowledge["categories"]["deck_composite"]
        assert cat_data["acceptance_count"] == 2
        assert cat_data["correction_count"] == 1
        # learned_adjustments should still have the correction learning (unchanged by acceptance)
        assert len(cat_data["learned_adjustments"]) == 1


# ============================================================================
# TEST 4: Confidence Calibration (Preventing Inflation)
# ============================================================================

@pytest.mark.asyncio
async def test_confidence_calibration_caps_inflation(learning_service):
    """
    Test confidence calibration prevents inflation.

    Scenario:
    - 3 acceptances, 7 corrections (30% accuracy)
    - Current confidence: 0.75 (inflated)
    - Calibration should cap at: 0.30 + 0.15 = 0.45

    Expected:
    - Calibrated confidence: 0.45
    """
    calibrated = learning_service._calculate_calibrated_confidence(
        acceptance_count=3,
        correction_count=7,
        current_confidence=0.75,
    )

    assert calibrated == 0.45


@pytest.mark.asyncio
async def test_confidence_calibration_allows_optimism(learning_service):
    """
    Test calibration allows 15% optimism buffer.

    Scenario:
    - 7 acceptances, 3 corrections (70% accuracy)
    - Current confidence: 0.80
    - Ceiling: 0.70 + 0.15 = 0.85
    - 0.80 < 0.85 → No capping needed

    Expected:
    - Calibrated confidence: 0.80 (unchanged)
    """
    calibrated = learning_service._calculate_calibrated_confidence(
        acceptance_count=7,
        correction_count=3,
        current_confidence=0.80,
    )

    assert calibrated == 0.80  # No change


@pytest.mark.asyncio
async def test_confidence_calibration_requires_minimum_samples(learning_service):
    """
    Test calibration requires at least 5 signals.

    Scenario:
    - 2 acceptances, 1 correction (only 3 signals)
    - Confidence: 0.90
    - Should NOT calibrate (need 5+ signals)

    Expected:
    - Calibrated confidence: 0.90 (unchanged)
    """
    calibrated = learning_service._calculate_calibrated_confidence(
        acceptance_count=2,
        correction_count=1,
        current_confidence=0.90,
    )

    assert calibrated == 0.90  # No change (not enough samples)


# ============================================================================
# TEST 5: Accepted by Customer (Stronger Signal)
# ============================================================================

@pytest.mark.asyncio
async def test_customer_acceptance_signal(learning_service, mock_contractor, mock_pricing_model):
    """
    Test customer acceptance signal (signal_type="accepted").

    Expected:
    - Same confidence boost as "sent"
    - signal_type: "accepted" stored in accepted_totals
    """
    quote = Mock(spec=Quote)
    quote.id = "quote-123"
    quote.job_type = "deck_composite"
    quote.total = 12000.0
    quote.was_edited = False
    quote.contractor_id = "contractor-123"

    with patch('backend.services.learning.get_db_service') as mock_db:
        mock_db.return_value.get_contractor_by_id = AsyncMock(return_value=mock_contractor)
        mock_db.return_value.get_pricing_model = AsyncMock(return_value=mock_pricing_model)
        mock_db.return_value.update_pricing_model = AsyncMock()

        # Process customer acceptance
        result = await learning_service.process_acceptance_learning(
            contractor_id="contractor-123",
            quote=quote,
            signal_type="accepted",
        )

        # Assertions
        assert result["processed"] is True
        assert result["signal_type"] == "accepted"

        cat_data = mock_pricing_model.pricing_knowledge["categories"]["deck_composite"]
        assert cat_data["accepted_totals"][0]["signal_type"] == "accepted"


# ============================================================================
# TEST 6: Edge Case - Quote Edited Then Accepted
# ============================================================================

@pytest.mark.asyncio
async def test_edited_quote_rejected(learning_service):
    """
    Test that edited quotes do NOT trigger acceptance learning.

    Scenario:
    - Quote edited by contractor (was_edited = True)
    - Customer accepts the edited quote
    - Acceptance learning should NOT run

    Expected:
    - processed: False
    - reason: "Quote was edited - not an acceptance signal"
    """
    quote = Mock(spec=Quote)
    quote.id = "quote-123"
    quote.job_type = "deck_composite"
    quote.total = 11000.0
    quote.was_edited = True  # EDITED
    quote.contractor_id = "contractor-123"

    # Process should reject
    result = await learning_service.process_acceptance_learning(
        contractor_id="contractor-123",
        quote=quote,
        signal_type="accepted",
    )

    # Assertions
    assert result["processed"] is False
    assert "edited" in result["reason"].lower()


# ============================================================================
# TEST 7: High-Volume Category (10+ Acceptances)
# ============================================================================

@pytest.mark.asyncio
async def test_accepted_totals_capped_at_ten(learning_service, mock_contractor, mock_pricing_model):
    """
    Test accepted_totals list is capped at 10 entries (FIFO).

    Scenario:
    - 15 acceptances total
    - accepted_totals should only store last 10

    Expected:
    - acceptance_count: 15
    - len(accepted_totals): 10
    - Oldest 5 discarded
    """
    # Pre-populate 10 accepted totals
    existing_totals = [
        {"total": 8000 + (i * 100), "signal_type": "sent", "quote_id": f"quote-{i}"}
        for i in range(10)
    ]

    mock_pricing_model.pricing_knowledge["categories"] = {
        "deck_composite": {
            "display_name": "Deck Composite",
            "tailored_prompt": None,
            "learned_adjustments": [],
            "samples": 10,
            "confidence": 0.75,
            "correction_count": 0,
            "acceptance_count": 10,
            "accepted_totals": existing_totals.copy(),
        }
    }

    # Add 5 more quotes
    for i in range(11, 16):
        quote = Mock(spec=Quote)
        quote.id = f"quote-{i}"
        quote.job_type = "deck_composite"
        quote.total = 8000 + (i * 100)
        quote.was_edited = False
        quote.contractor_id = "contractor-123"

        with patch('backend.services.learning.get_db_service') as mock_db:
            mock_db.return_value.get_contractor_by_id = AsyncMock(return_value=mock_contractor)
            mock_db.return_value.get_pricing_model = AsyncMock(return_value=mock_pricing_model)
            mock_db.return_value.update_pricing_model = AsyncMock()

            await learning_service.process_acceptance_learning(
                contractor_id="contractor-123",
                quote=quote,
                signal_type="sent",
            )

    # Assertions
    cat_data = mock_pricing_model.pricing_knowledge["categories"]["deck_composite"]
    assert cat_data["acceptance_count"] == 15
    assert len(cat_data["accepted_totals"]) == 10  # Capped

    # Verify FIFO: First entry should be quote-6 (quote-1 to quote-5 discarded)
    assert cat_data["accepted_totals"][0]["quote_id"] == "quote-6"
    assert cat_data["accepted_totals"][-1]["quote_id"] == "quote-15"


# ============================================================================
# TEST 8: Analytics Event Tracking
# ============================================================================

@pytest.mark.asyncio
async def test_analytics_event_tracked(learning_service, mock_quote, mock_contractor, mock_pricing_model):
    """
    Test that analytics event is tracked on acceptance.

    Expected:
    - Event: acceptance_signal_processed
    - Properties include: contractor_id, category, signal_type, accuracy_ratio
    """
    with patch('backend.services.learning.get_db_service') as mock_db, \
         patch('backend.services.learning.analytics_service') as mock_analytics:

        mock_db.return_value.get_contractor_by_id = AsyncMock(return_value=mock_contractor)
        mock_db.return_value.get_pricing_model = AsyncMock(return_value=mock_pricing_model)
        mock_db.return_value.update_pricing_model = AsyncMock()

        # Process acceptance
        await learning_service.process_acceptance_learning(
            contractor_id="contractor-123",
            quote=mock_quote,
            signal_type="sent",
        )

        # Verify analytics called
        mock_analytics.track_event.assert_called_once()
        call_args = mock_analytics.track_event.call_args

        assert call_args[1]["event_name"] == "acceptance_signal_processed"
        props = call_args[1]["properties"]
        assert props["contractor_id"] == "contractor-123"
        assert props["category"] == "deck_composite"
        assert props["signal_type"] == "sent"
        assert "accuracy_ratio" in props


# ============================================================================
# TEST 9: No Job Type (Error Case)
# ============================================================================

@pytest.mark.asyncio
async def test_no_job_type_rejected(learning_service):
    """
    Test that quotes without job_type are rejected.

    Expected:
    - processed: False
    - reason: "No job_type on quote - cannot apply learning"
    """
    quote = Mock(spec=Quote)
    quote.id = "quote-123"
    quote.job_type = None  # NO JOB TYPE
    quote.total = 8500.0
    quote.was_edited = False
    quote.contractor_id = "contractor-123"

    result = await learning_service.process_acceptance_learning(
        contractor_id="contractor-123",
        quote=quote,
        signal_type="sent",
    )

    assert result["processed"] is False
    assert "job_type" in result["reason"].lower()


# ============================================================================
# TEST 10: Backward Compatibility (Missing Fields)
# ============================================================================

@pytest.mark.asyncio
async def test_backward_compatibility_missing_fields(learning_service, mock_contractor, mock_pricing_model):
    """
    Test backward compatibility with old pricing models missing acceptance fields.

    Scenario:
    - Category exists but has no acceptance_count, accepted_totals fields
    - Processing should initialize them

    Expected:
    - acceptance_count: 0 → 1
    - accepted_totals: [] → [entry]
    """
    # Old category data (missing acceptance fields)
    mock_pricing_model.pricing_knowledge["categories"] = {
        "deck_composite": {
            "display_name": "Deck Composite",
            "tailored_prompt": None,
            "learned_adjustments": [],
            "samples": 5,
            "confidence": 0.65,
            "correction_count": 3,
            # NO acceptance_count, accepted_totals, last_accepted_at
        }
    }

    quote = Mock(spec=Quote)
    quote.id = "quote-123"
    quote.job_type = "deck_composite"
    quote.total = 8500.0
    quote.was_edited = False
    quote.contractor_id = "contractor-123"

    with patch('backend.services.learning.get_db_service') as mock_db:
        mock_db.return_value.get_contractor_by_id = AsyncMock(return_value=mock_contractor)
        mock_db.return_value.get_pricing_model = AsyncMock(return_value=mock_pricing_model)
        mock_db.return_value.update_pricing_model = AsyncMock()

        # Process acceptance
        result = await learning_service.process_acceptance_learning(
            contractor_id="contractor-123",
            quote=quote,
            signal_type="sent",
        )

        # Assertions
        assert result["processed"] is True

        cat_data = mock_pricing_model.pricing_knowledge["categories"]["deck_composite"]
        assert cat_data["acceptance_count"] == 1  # Initialized and incremented
        assert len(cat_data["accepted_totals"]) == 1
        assert "last_accepted_at" in cat_data


# ============================================================================
# RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
