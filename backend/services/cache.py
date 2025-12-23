"""
Redis Caching Service for Quoted (INFRA-004).

Provides caching with graceful fallback when Redis is unavailable.
All operations are non-blocking and won't fail the request if cache is down.
"""

import json
from typing import Any, Optional
from datetime import timedelta

from ..config import settings
from .logging import get_logger

logger = get_logger("quoted.cache")

# Global Redis client (initialized lazily)
_redis_client = None
_redis_available = None  # None = not checked, True/False after check


async def _get_redis():
    """Get Redis client, initializing if needed."""
    global _redis_client, _redis_available

    # Already determined Redis is not available
    if _redis_available is False:
        return None

    # Already have a working client
    if _redis_client is not None:
        return _redis_client

    # No Redis URL configured
    if not settings.redis_url:
        _redis_available = False
        logger.info("Redis not configured - caching disabled")
        return None

    # Try to connect
    try:
        import redis.asyncio as redis
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
        # Test connection
        await _redis_client.ping()
        _redis_available = True
        logger.info("Redis connected successfully")
        return _redis_client
    except ImportError:
        _redis_available = False
        logger.warning("Redis package not installed - caching disabled")
        return None
    except Exception as e:
        _redis_available = False
        logger.warning(f"Redis connection failed - caching disabled: {e}")
        return None


class CacheService:
    """
    Async Redis cache service with graceful degradation.

    All methods are safe to call even when Redis is unavailable -
    they will simply return None/False without raising exceptions.
    """

    # Key prefixes for namespacing
    PREFIX_CONTRACTOR = "contractor:"
    PREFIX_PRICING = "pricing:"
    PREFIX_TEMPLATE = "template:"
    PREFIX_QUOTE = "quote:"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Returns None if key doesn't exist or cache is unavailable.
        """
        try:
            client = await _get_redis()
            if not client:
                return None

            value = await client.get(key)
            if value is None:
                return None

            return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get failed for {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache with optional TTL.

        Returns True on success, False on failure.
        TTL defaults to cache_ttl_default from settings.
        """
        try:
            client = await _get_redis()
            if not client:
                return False

            ttl = ttl or settings.cache_ttl_default
            serialized = json.dumps(value)
            await client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Returns True on success, False on failure.
        """
        try:
            client = await _get_redis()
            if not client:
                return False

            await client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Returns count of deleted keys, 0 on failure.
        Use with caution - SCAN can be slow on large datasets.
        """
        try:
            client = await _get_redis()
            if not client:
                return 0

            deleted = 0
            async for key in client.scan_iter(match=pattern):
                await client.delete(key)
                deleted += 1
            return deleted
        except Exception as e:
            logger.warning(f"Cache delete_pattern failed for {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            client = await _get_redis()
            if not client:
                return False

            return await client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Cache exists check failed for {key}: {e}")
            return False

    # =========================================================================
    # Contractor Profile Caching
    # =========================================================================

    def contractor_key(self, contractor_id: str) -> str:
        """Generate cache key for contractor profile."""
        return f"{self.PREFIX_CONTRACTOR}{contractor_id}"

    async def get_contractor(self, contractor_id: str) -> Optional[dict]:
        """Get cached contractor profile."""
        return await self.get(self.contractor_key(contractor_id))

    async def set_contractor(self, contractor_id: str, data: dict) -> bool:
        """Cache contractor profile."""
        return await self.set(
            self.contractor_key(contractor_id),
            data,
            ttl=settings.cache_ttl_contractor,
        )

    async def invalidate_contractor(self, contractor_id: str) -> bool:
        """Invalidate cached contractor profile."""
        return await self.delete(self.contractor_key(contractor_id))

    # =========================================================================
    # Pricing Category Caching
    # =========================================================================

    def pricing_key(self, contractor_id: str) -> str:
        """Generate cache key for pricing categories."""
        return f"{self.PREFIX_PRICING}{contractor_id}"

    async def get_pricing(self, contractor_id: str) -> Optional[list]:
        """Get cached pricing categories for contractor."""
        return await self.get(self.pricing_key(contractor_id))

    async def set_pricing(self, contractor_id: str, categories: list) -> bool:
        """Cache pricing categories for contractor."""
        return await self.set(
            self.pricing_key(contractor_id),
            categories,
            ttl=settings.cache_ttl_pricing,
        )

    async def invalidate_pricing(self, contractor_id: str) -> bool:
        """Invalidate cached pricing categories."""
        return await self.delete(self.pricing_key(contractor_id))

    # =========================================================================
    # Quote Template Caching
    # =========================================================================

    def template_key(self, contractor_id: str, template_name: str = "default") -> str:
        """Generate cache key for quote template."""
        return f"{self.PREFIX_TEMPLATE}{contractor_id}:{template_name}"

    async def get_template(
        self, contractor_id: str, template_name: str = "default"
    ) -> Optional[dict]:
        """Get cached quote template."""
        return await self.get(self.template_key(contractor_id, template_name))

    async def set_template(
        self,
        contractor_id: str,
        template: dict,
        template_name: str = "default",
    ) -> bool:
        """Cache quote template."""
        return await self.set(
            self.template_key(contractor_id, template_name),
            template,
            ttl=settings.cache_ttl_default,
        )

    async def invalidate_template(
        self, contractor_id: str, template_name: str = "default"
    ) -> bool:
        """Invalidate cached quote template."""
        return await self.delete(self.template_key(contractor_id, template_name))

    # =========================================================================
    # Health Check
    # =========================================================================

    async def health_check(self) -> dict:
        """
        Check Redis health status.

        Returns dict with 'available' bool and optional 'latency_ms'.
        """
        try:
            client = await _get_redis()
            if not client:
                return {"available": False, "reason": "not_configured"}

            import time
            start = time.time()
            await client.ping()
            latency = (time.time() - start) * 1000

            info = await client.info("memory")
            return {
                "available": True,
                "latency_ms": round(latency, 2),
                "used_memory": info.get("used_memory_human", "unknown"),
            }
        except Exception as e:
            return {"available": False, "reason": str(e)}


# Singleton instance
cache_service = CacheService()
