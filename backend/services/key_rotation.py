"""
Key Rotation Service for Quoted (SEC-006).

Provides secure key rotation for JWT tokens without invalidating
existing sessions. Supports multiple active keys during rotation.
"""

import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..config import settings

logger = logging.getLogger("quoted.key_rotation")


@dataclass
class SigningKey:
    """A JWT signing key with metadata."""
    key_id: str
    key: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_primary: bool = False

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def age_days(self) -> int:
        return (datetime.utcnow() - self.created_at).days


class KeyRotationService:
    """
    Manages JWT signing keys with support for rotation.

    Features:
    - Multiple active keys (primary for signing, all for verification)
    - Key ID (kid) in JWT header for key selection
    - Graceful rotation without invalidating existing tokens
    - Key expiration and cleanup
    """

    def __init__(self):
        self._keys: Dict[str, SigningKey] = {}
        self._initialize_from_config()

    def _initialize_from_config(self):
        """Initialize with the key from settings."""
        # Use the configured JWT secret as the initial key
        if settings.jwt_secret_key:
            key_id = self._generate_key_id(settings.jwt_secret_key)
            self._keys[key_id] = SigningKey(
                key_id=key_id,
                key=settings.jwt_secret_key,
                created_at=datetime.utcnow(),
                is_primary=True,
            )
            logger.info(f"Initialized with key: {key_id[:8]}...")

    @staticmethod
    def _generate_key_id(key: str) -> str:
        """Generate a key ID from a key (first 16 chars of SHA256)."""
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    @staticmethod
    def _generate_key() -> str:
        """Generate a new cryptographically secure key."""
        return secrets.token_urlsafe(32)

    def get_primary_key(self) -> Tuple[str, str]:
        """
        Get the primary signing key.

        Returns:
            Tuple of (key_id, key)
        """
        for key in self._keys.values():
            if key.is_primary and not key.is_expired:
                return key.key_id, key.key

        # No primary key found - use first non-expired key
        for key in self._keys.values():
            if not key.is_expired:
                return key.key_id, key.key

        raise ValueError("No valid signing keys available")

    def get_key_by_id(self, key_id: str) -> Optional[str]:
        """
        Get a key by its ID for token verification.

        Returns:
            The key if found and not expired, None otherwise
        """
        key = self._keys.get(key_id)
        if key and not key.is_expired:
            return key.key
        return None

    def get_all_valid_keys(self) -> Dict[str, str]:
        """
        Get all valid (non-expired) keys for verification.

        Returns:
            Dict of key_id -> key for all valid keys
        """
        return {
            k.key_id: k.key
            for k in self._keys.values()
            if not k.is_expired
        }

    def rotate_key(
        self,
        expiration_days: int = 7,
    ) -> str:
        """
        Create a new primary key and schedule expiration of old keys.

        Args:
            expiration_days: Days until old keys expire

        Returns:
            The new key ID
        """
        # Generate new key
        new_key = self._generate_key()
        new_key_id = self._generate_key_id(new_key)

        # Demote current primary and set expiration
        for key in self._keys.values():
            if key.is_primary:
                key.is_primary = False
                key.expires_at = datetime.utcnow() + timedelta(days=expiration_days)

        # Add new primary key
        self._keys[new_key_id] = SigningKey(
            key_id=new_key_id,
            key=new_key,
            created_at=datetime.utcnow(),
            is_primary=True,
        )

        logger.info(
            f"Rotated to new key: {new_key_id[:8]}..., "
            f"old keys expire in {expiration_days} days"
        )

        return new_key_id

    def cleanup_expired_keys(self) -> int:
        """
        Remove expired keys.

        Returns:
            Number of keys removed
        """
        expired = [k.key_id for k in self._keys.values() if k.is_expired]
        for key_id in expired:
            del self._keys[key_id]
            logger.info(f"Removed expired key: {key_id[:8]}...")
        return len(expired)

    def get_status(self) -> Dict:
        """Get status of all keys."""
        return {
            "total_keys": len(self._keys),
            "keys": [
                {
                    "key_id": k.key_id[:8] + "...",
                    "is_primary": k.is_primary,
                    "age_days": k.age_days,
                    "is_expired": k.is_expired,
                    "expires_at": k.expires_at.isoformat() if k.expires_at else None,
                }
                for k in self._keys.values()
            ],
        }


# Singleton instance
key_rotation_service = KeyRotationService()


# =============================================================================
# JWT Integration Functions
# =============================================================================

def get_signing_key() -> Tuple[str, str]:
    """
    Get the current signing key for creating tokens.

    Returns:
        Tuple of (key_id, key)
    """
    return key_rotation_service.get_primary_key()


def get_verification_key(key_id: str) -> Optional[str]:
    """
    Get a key for verifying tokens.

    Args:
        key_id: The key ID from the JWT header

    Returns:
        The key if valid, None otherwise
    """
    return key_rotation_service.get_key_by_id(key_id)


def get_all_verification_keys() -> Dict[str, str]:
    """
    Get all valid keys for token verification.

    Useful when key_id is not available (legacy tokens).
    """
    return key_rotation_service.get_all_valid_keys()
