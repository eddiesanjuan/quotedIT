"""
Health Check Service for Quoted (INFRA-007).

Provides health checks for all external services including:
- Database
- OpenAI (Whisper)
- Anthropic (Claude)
- Stripe
- Resend (Email)
- Redis (if configured)
- S3 (if configured)
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..config import settings
from .resilience import get_circuit_breaker_status

logger = logging.getLogger("quoted.health")


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ServiceHealth:
    """Health check result for a single service."""
    name: str
    status: HealthStatus
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "status": self.status.value,
        }
        if self.latency_ms is not None:
            result["latency_ms"] = round(self.latency_ms, 2)
        if self.message:
            result["message"] = self.message
        if self.details:
            result["details"] = self.details
        return result


async def check_database_health() -> ServiceHealth:
    """Check database connectivity."""
    try:
        from sqlalchemy import text
        from ..models.database import get_db_session

        start = time.time()
        async with get_db_session() as db:
            await db.execute(text("SELECT 1"))
        latency = (time.time() - start) * 1000

        return ServiceHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            latency_ms=latency,
        )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return ServiceHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def check_openai_health() -> ServiceHealth:
    """Check OpenAI API connectivity."""
    if not settings.openai_api_key:
        return ServiceHealth(
            name="openai",
            status=HealthStatus.DEGRADED,
            message="API key not configured",
        )

    try:
        import httpx
        start = time.time()

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Use models endpoint as a lightweight health check
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            )
        latency = (time.time() - start) * 1000

        if response.status_code == 200:
            return ServiceHealth(
                name="openai",
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
            )
        elif response.status_code == 429:
            return ServiceHealth(
                name="openai",
                status=HealthStatus.DEGRADED,
                latency_ms=latency,
                message="Rate limited",
            )
        else:
            return ServiceHealth(
                name="openai",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency,
                message=f"HTTP {response.status_code}",
            )
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        return ServiceHealth(
            name="openai",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def check_anthropic_health() -> ServiceHealth:
    """Check Anthropic API connectivity."""
    if not settings.anthropic_api_key:
        return ServiceHealth(
            name="anthropic",
            status=HealthStatus.DEGRADED,
            message="API key not configured",
        )

    try:
        import httpx
        start = time.time()

        # Anthropic doesn't have a dedicated health endpoint,
        # so we'll make a lightweight request
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                },
            )
        latency = (time.time() - start) * 1000

        if response.status_code in (200, 401):  # 401 means API is up but auth issue
            status = HealthStatus.HEALTHY if response.status_code == 200 else HealthStatus.DEGRADED
            return ServiceHealth(
                name="anthropic",
                status=status,
                latency_ms=latency,
                message="Auth issue" if response.status_code == 401 else None,
            )
        elif response.status_code == 429:
            return ServiceHealth(
                name="anthropic",
                status=HealthStatus.DEGRADED,
                latency_ms=latency,
                message="Rate limited",
            )
        else:
            return ServiceHealth(
                name="anthropic",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency,
                message=f"HTTP {response.status_code}",
            )
    except Exception as e:
        logger.error(f"Anthropic health check failed: {e}")
        return ServiceHealth(
            name="anthropic",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def check_stripe_health() -> ServiceHealth:
    """Check Stripe API connectivity."""
    if not settings.stripe_secret_key:
        return ServiceHealth(
            name="stripe",
            status=HealthStatus.DEGRADED,
            message="API key not configured",
        )

    try:
        import httpx
        start = time.time()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.stripe.com/v1/balance",
                auth=(settings.stripe_secret_key, ""),
            )
        latency = (time.time() - start) * 1000

        if response.status_code == 200:
            return ServiceHealth(
                name="stripe",
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
            )
        elif response.status_code == 401:
            return ServiceHealth(
                name="stripe",
                status=HealthStatus.DEGRADED,
                latency_ms=latency,
                message="Invalid API key",
            )
        else:
            return ServiceHealth(
                name="stripe",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency,
                message=f"HTTP {response.status_code}",
            )
    except Exception as e:
        logger.error(f"Stripe health check failed: {e}")
        return ServiceHealth(
            name="stripe",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def check_resend_health() -> ServiceHealth:
    """Check Resend API connectivity."""
    if not settings.resend_api_key:
        return ServiceHealth(
            name="resend",
            status=HealthStatus.DEGRADED,
            message="API key not configured",
        )

    try:
        import httpx
        start = time.time()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.resend.com/domains",
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            )
        latency = (time.time() - start) * 1000

        if response.status_code == 200:
            return ServiceHealth(
                name="resend",
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
            )
        elif response.status_code == 401:
            return ServiceHealth(
                name="resend",
                status=HealthStatus.DEGRADED,
                latency_ms=latency,
                message="Invalid API key",
            )
        else:
            return ServiceHealth(
                name="resend",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency,
                message=f"HTTP {response.status_code}",
            )
    except Exception as e:
        logger.error(f"Resend health check failed: {e}")
        return ServiceHealth(
            name="resend",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def check_all_health(
    include_external: bool = True,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """
    Run all health checks and return aggregated status.

    Args:
        include_external: If True, check external APIs (slower)
        timeout: Max time to wait for all checks

    Returns:
        Dict with overall status and individual service statuses
    """
    checks = [check_database_health()]

    if include_external:
        checks.extend([
            check_openai_health(),
            check_anthropic_health(),
            check_stripe_health(),
            check_resend_health(),
        ])

    # Run all checks concurrently with timeout
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*checks, return_exceptions=True),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        results = []
        for check in checks:
            results.append(ServiceHealth(
                name="unknown",
                status=HealthStatus.UNHEALTHY,
                message="Health check timed out",
            ))

    # Process results
    services = {}
    overall_status = HealthStatus.HEALTHY

    for result in results:
        if isinstance(result, Exception):
            service = ServiceHealth(
                name="unknown",
                status=HealthStatus.UNHEALTHY,
                message=str(result),
            )
        else:
            service = result

        services[service.name] = service.to_dict()

        # Update overall status
        if service.status == HealthStatus.UNHEALTHY:
            overall_status = HealthStatus.UNHEALTHY
        elif service.status == HealthStatus.DEGRADED and overall_status != HealthStatus.UNHEALTHY:
            overall_status = HealthStatus.DEGRADED

    # Add circuit breaker status
    circuit_breakers = get_circuit_breaker_status()

    return {
        "status": overall_status.value,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": services,
        "circuit_breakers": circuit_breakers,
    }


async def get_quick_health() -> Dict[str, Any]:
    """
    Quick health check - database only.
    For use by load balancers that need fast response.
    """
    db_health = await check_database_health()

    return {
        "status": db_health.status.value,
        "database": db_health.to_dict(),
    }
