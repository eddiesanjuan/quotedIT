"""
Resilience Service for Quoted (INFRA-006, INFRA-009).

Provides retry logic with exponential backoff and circuit breakers
for external service calls.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger("quoted.resilience")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    reset_timeout: float = 30.0  # Seconds before trying again
    excluded_exceptions: tuple = ()  # Exceptions that don't count as failures


@dataclass
class CircuitBreakerState:
    """State tracking for circuit breaker."""
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    opened_at: Optional[float] = None

    def record_failure(self):
        self.failures += 1
        self.successes = 0
        self.last_failure_time = time.time()

    def record_success(self):
        self.successes += 1
        self.last_success_time = time.time()

    def reset(self):
        self.failures = 0
        self.successes = 0
        self.state = CircuitState.CLOSED
        self.opened_at = None


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""
    def __init__(self, service_name: str, retry_after: float):
        self.service_name = service_name
        self.retry_after = retry_after
        super().__init__(f"Circuit breaker open for {service_name}. Retry after {retry_after:.1f}s")


class CircuitBreaker:
    """
    Circuit breaker implementation for external services.

    Prevents cascading failures by temporarily blocking calls to failing services.
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState()

    def _should_allow_request(self) -> bool:
        """Check if request should be allowed based on circuit state."""
        if self.state.state == CircuitState.CLOSED:
            return True

        if self.state.state == CircuitState.OPEN:
            # Check if reset timeout has passed
            if self.state.opened_at:
                elapsed = time.time() - self.state.opened_at
                if elapsed >= self.config.reset_timeout:
                    self.state.state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit {self.name} transitioning to HALF_OPEN")
                    return True
            return False

        # HALF_OPEN - allow request for testing
        return True

    def _on_success(self):
        """Handle successful call."""
        self.state.record_success()

        if self.state.state == CircuitState.HALF_OPEN:
            if self.state.successes >= self.config.success_threshold:
                self.state.reset()
                logger.info(f"Circuit {self.name} CLOSED after recovery")

    def _on_failure(self, exc: Exception):
        """Handle failed call."""
        # Check if exception is excluded
        if isinstance(exc, self.config.excluded_exceptions):
            return

        self.state.record_failure()

        if self.state.state == CircuitState.HALF_OPEN:
            # Immediately reopen on failure during half-open
            self.state.state = CircuitState.OPEN
            self.state.opened_at = time.time()
            logger.warning(f"Circuit {self.name} reopened after HALF_OPEN failure")
        elif self.state.failures >= self.config.failure_threshold:
            self.state.state = CircuitState.OPEN
            self.state.opened_at = time.time()
            logger.warning(
                f"Circuit {self.name} OPENED after {self.state.failures} failures"
            )

    def get_retry_after(self) -> float:
        """Get seconds until retry is allowed."""
        if self.state.state != CircuitState.OPEN or not self.state.opened_at:
            return 0.0
        elapsed = time.time() - self.state.opened_at
        return max(0.0, self.config.reset_timeout - elapsed)

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.state.value,
            "failures": self.state.failures,
            "successes": self.state.successes,
            "retry_after": self.get_retry_after() if self.state.state == CircuitState.OPEN else None,
        }

    def __call__(self, func: Callable) -> Callable:
        """Decorator for wrapping functions with circuit breaker."""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not self._should_allow_request():
                raise CircuitBreakerOpen(self.name, self.get_retry_after())
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure(e)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not self._should_allow_request():
                raise CircuitBreakerOpen(self.name, self.get_retry_after())
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure(e)
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 30.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = ()


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
):
    """
    Decorator for retry with exponential backoff.

    Args:
        config: Retry configuration
        on_retry: Callback called before each retry (attempt, exception, wait_time)
    """
    config = config or RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except config.non_retryable_exceptions as e:
                    # Don't retry these
                    raise
                except config.retryable_exceptions as e:
                    last_exception = e

                    if attempt >= config.max_attempts:
                        logger.warning(
                            f"Retry exhausted for {func.__name__} after {attempt} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.initial_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay,
                    )

                    # Add jitter
                    if config.jitter:
                        import random
                        delay *= (0.5 + random.random())

                    logger.info(
                        f"Retry {attempt}/{config.max_attempts} for {func.__name__} "
                        f"after {delay:.2f}s: {e}"
                    )

                    if on_retry:
                        on_retry(attempt, e, delay)

                    await asyncio.sleep(delay)

            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except config.non_retryable_exceptions as e:
                    raise
                except config.retryable_exceptions as e:
                    last_exception = e

                    if attempt >= config.max_attempts:
                        logger.warning(
                            f"Retry exhausted for {func.__name__} after {attempt} attempts: {e}"
                        )
                        raise

                    delay = min(
                        config.initial_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay,
                    )

                    if config.jitter:
                        import random
                        delay *= (0.5 + random.random())

                    logger.info(
                        f"Retry {attempt}/{config.max_attempts} for {func.__name__} "
                        f"after {delay:.2f}s: {e}"
                    )

                    if on_retry:
                        on_retry(attempt, e, delay)

                    time.sleep(delay)

            raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# =============================================================================
# Pre-configured Circuit Breakers for External Services
# =============================================================================

# OpenAI (Whisper) - longer timeout, more failures allowed
openai_circuit = CircuitBreaker(
    "openai",
    CircuitBreakerConfig(
        failure_threshold=5,
        success_threshold=2,
        reset_timeout=60.0,  # Wait longer before retry
    ),
)

# Anthropic (Claude) - critical service, faster recovery
anthropic_circuit = CircuitBreaker(
    "anthropic",
    CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=1,
        reset_timeout=30.0,
    ),
)

# Stripe - payment critical, moderate thresholds
stripe_circuit = CircuitBreaker(
    "stripe",
    CircuitBreakerConfig(
        failure_threshold=5,
        success_threshold=2,
        reset_timeout=45.0,
    ),
)

# Resend (email) - less critical, higher threshold
resend_circuit = CircuitBreaker(
    "resend",
    CircuitBreakerConfig(
        failure_threshold=10,
        success_threshold=2,
        reset_timeout=60.0,
    ),
)


# =============================================================================
# Pre-configured Retry Configs
# =============================================================================

# For AI API calls (Whisper, Claude)
AI_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=2.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True,
)

# For payment APIs (Stripe)
PAYMENT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True,
)

# For email (Resend)
EMAIL_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
)


# =============================================================================
# Combined Decorator for Production Use
# =============================================================================

def resilient(
    circuit_breaker: Optional[CircuitBreaker] = None,
    retry_config: Optional[RetryConfig] = None,
):
    """
    Combined decorator applying circuit breaker and retry logic.

    Usage:
        @resilient(circuit_breaker=anthropic_circuit, retry_config=AI_RETRY_CONFIG)
        async def call_claude(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        wrapped = func

        # Apply retry first (inner decorator)
        if retry_config:
            wrapped = retry_with_backoff(retry_config)(wrapped)

        # Apply circuit breaker second (outer decorator)
        if circuit_breaker:
            wrapped = circuit_breaker(wrapped)

        return wrapped

    return decorator


# =============================================================================
# Health Check for All Circuit Breakers
# =============================================================================

def get_circuit_breaker_status() -> Dict[str, Any]:
    """Get status of all circuit breakers."""
    return {
        "openai": openai_circuit.get_status(),
        "anthropic": anthropic_circuit.get_status(),
        "stripe": stripe_circuit.get_status(),
        "resend": resend_circuit.get_status(),
    }
