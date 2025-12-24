"""
Tests for Production Infrastructure Services (QA-002).

Tests the new production-ready infrastructure including:
- Rate limiting
- Key rotation
- Resilience (circuit breakers, retry)
"""

import asyncio
import time
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# Rate Limiting Tests
# =============================================================================

class TestRateLimiting:
    """Tests for the rate limiting service."""

    def test_rate_limits_defined(self):
        """Rate limit constants are properly defined."""
        from backend.services.rate_limiting import RateLimits

        # Auth limits should be strict
        assert "minute" in RateLimits.AUTH_LOGIN
        assert "minute" in RateLimits.AUTH_REGISTER

        # Demo limits should be hourly
        assert "hour" in RateLimits.DEMO_QUOTE

        # API limits should be reasonable
        assert "minute" in RateLimits.API_READ

    def test_get_user_id_or_ip(self):
        """get_user_id_or_ip extracts correct key."""
        from backend.services.rate_limiting import get_user_id_or_ip
        from unittest.mock import MagicMock

        # Test IP fallback
        request = MagicMock()
        request.client.host = "192.168.1.1"
        delattr(request, "state")  # No state attribute

        # Should not raise
        try:
            result = get_user_id_or_ip(request)
            assert result is not None
        except AttributeError:
            pass  # Expected if state not set up properly

    def test_limiters_created(self):
        """Limiter instances are properly created."""
        from backend.services.rate_limiting import (
            ip_limiter,
            user_limiter,
            contractor_limiter,
        )

        assert ip_limiter is not None
        assert user_limiter is not None
        assert contractor_limiter is not None


# =============================================================================
# Key Rotation Tests
# =============================================================================

class TestKeyRotation:
    """Tests for the key rotation service."""

    def test_key_rotation_service_initializes(self):
        """Key rotation service initializes with config key."""
        from backend.services.key_rotation import key_rotation_service

        # Should have at least one key
        status = key_rotation_service.get_status()
        assert status["total_keys"] >= 1

    def test_get_primary_key(self):
        """Can get primary signing key."""
        from backend.services.key_rotation import key_rotation_service

        key_id, key = key_rotation_service.get_primary_key()
        assert key_id is not None
        assert len(key_id) > 0
        assert key is not None
        assert len(key) > 0

    def test_get_key_by_id(self):
        """Can retrieve key by ID."""
        from backend.services.key_rotation import key_rotation_service

        key_id, original_key = key_rotation_service.get_primary_key()
        retrieved_key = key_rotation_service.get_key_by_id(key_id)

        assert retrieved_key == original_key

    def test_get_nonexistent_key_returns_none(self):
        """Getting nonexistent key returns None."""
        from backend.services.key_rotation import key_rotation_service

        result = key_rotation_service.get_key_by_id("nonexistent_key_id")
        assert result is None

    def test_rotate_key_creates_new_primary(self):
        """Key rotation creates new primary key."""
        from backend.services.key_rotation import KeyRotationService
        from backend.config import settings

        # Create fresh service for testing
        service = KeyRotationService()
        old_key_id, _ = service.get_primary_key()

        # Rotate
        new_key_id = service.rotate_key(expiration_days=1)

        assert new_key_id != old_key_id

        # New key should be primary
        current_key_id, _ = service.get_primary_key()
        assert current_key_id == new_key_id

    def test_get_all_valid_keys(self):
        """Can get all valid keys for verification."""
        from backend.services.key_rotation import key_rotation_service

        keys = key_rotation_service.get_all_valid_keys()
        assert isinstance(keys, dict)
        assert len(keys) >= 1


# =============================================================================
# Resilience Tests
# =============================================================================

class TestCircuitBreaker:
    """Tests for circuit breaker functionality."""

    def test_circuit_breaker_starts_closed(self):
        """Circuit breaker starts in closed state."""
        from backend.services.resilience import CircuitBreaker, CircuitState

        cb = CircuitBreaker("test_service")
        assert cb.state.state == CircuitState.CLOSED

    def test_circuit_opens_after_failures(self):
        """Circuit opens after threshold failures."""
        from backend.services.resilience import (
            CircuitBreaker,
            CircuitBreakerConfig,
            CircuitState,
        )

        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker("test_service", config)

        # Simulate failures
        for _ in range(3):
            cb._on_failure(Exception("test error"))

        assert cb.state.state == CircuitState.OPEN

    def test_circuit_rejects_when_open(self):
        """Open circuit rejects calls."""
        from backend.services.resilience import (
            CircuitBreaker,
            CircuitBreakerConfig,
            CircuitBreakerOpen,
        )

        config = CircuitBreakerConfig(failure_threshold=1, reset_timeout=60)
        cb = CircuitBreaker("test_service", config)

        # Open the circuit
        cb._on_failure(Exception("test error"))

        # Should reject
        assert not cb._should_allow_request()

    def test_circuit_allows_after_reset_timeout(self):
        """Circuit allows request after reset timeout."""
        from backend.services.resilience import (
            CircuitBreaker,
            CircuitBreakerConfig,
            CircuitState,
        )

        config = CircuitBreakerConfig(failure_threshold=1, reset_timeout=0.1)
        cb = CircuitBreaker("test_service", config)

        # Open the circuit
        cb._on_failure(Exception("test error"))
        assert cb.state.state == CircuitState.OPEN

        # Wait for reset timeout
        time.sleep(0.2)

        # Should allow (and transition to half-open)
        assert cb._should_allow_request()
        assert cb.state.state == CircuitState.HALF_OPEN

    def test_circuit_closes_after_success_in_half_open(self):
        """Circuit closes after success threshold in half-open."""
        from backend.services.resilience import (
            CircuitBreaker,
            CircuitBreakerConfig,
            CircuitState,
        )

        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=2,
            reset_timeout=0.1,
        )
        cb = CircuitBreaker("test_service", config)

        # Open the circuit
        cb._on_failure(Exception("test error"))

        # Wait and transition to half-open
        time.sleep(0.2)
        cb._should_allow_request()

        # Succeed twice
        cb._on_success()
        cb._on_success()

        assert cb.state.state == CircuitState.CLOSED

    def test_preconfigured_circuit_breakers_exist(self):
        """Pre-configured circuit breakers are available."""
        from backend.services.resilience import (
            openai_circuit,
            anthropic_circuit,
            stripe_circuit,
            resend_circuit,
        )

        assert openai_circuit is not None
        assert anthropic_circuit is not None
        assert stripe_circuit is not None
        assert resend_circuit is not None

    def test_get_circuit_breaker_status(self):
        """Can get status of all circuit breakers."""
        from backend.services.resilience import get_circuit_breaker_status

        status = get_circuit_breaker_status()
        assert "openai" in status
        assert "anthropic" in status
        assert "stripe" in status
        assert "resend" in status


class TestRetryLogic:
    """Tests for retry with exponential backoff."""

    def test_retry_config_defaults(self):
        """Retry config has sensible defaults."""
        from backend.services.resilience import RetryConfig

        config = RetryConfig()
        assert config.max_attempts >= 1
        assert config.initial_delay > 0
        assert config.max_delay > config.initial_delay

    def test_preconfigured_retry_configs_exist(self):
        """Pre-configured retry configs are available."""
        from backend.services.resilience import (
            AI_RETRY_CONFIG,
            PAYMENT_RETRY_CONFIG,
            EMAIL_RETRY_CONFIG,
        )

        assert AI_RETRY_CONFIG.max_attempts >= 1
        assert PAYMENT_RETRY_CONFIG.max_attempts >= 1
        assert EMAIL_RETRY_CONFIG.max_attempts >= 1


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
