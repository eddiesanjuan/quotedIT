"""
Configuration for Quoted application.
Uses environment variables for secrets.
"""

import secrets
import sys
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


# Generate a stable default for development only
# In production, JWT_SECRET_KEY MUST be set as environment variable
_DEV_JWT_SECRET = "dev-only-secret-key-do-not-use-in-production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Quoted"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"  # development, production
    frontend_url: str = "https://quoted.it.com"  # For generating shareable referral links

    # Founder Notifications (DISC-128)
    founder_email: str = "eddie@granular.tools"  # Receives signup & demo usage alerts

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""  # For Whisper transcription
    resend_api_key: str = ""  # For transactional emails

    # Database - supports both SQLite (dev) and PostgreSQL (prod)
    database_url: str = "sqlite+aiosqlite:///./data/quoted.db"

    # JWT Authentication (SEC-003: Short-lived access + refresh tokens)
    # CRITICAL: In production, JWT_SECRET_KEY MUST be set as environment variable
    # If not set, all tokens will be invalidated on each deploy!
    jwt_secret_key: str = _DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 15  # Access token: 15 minutes (security best practice)
    jwt_refresh_expire_days: int = 7  # Refresh token: 7 days

    @property
    def async_database_url(self) -> str:
        """Convert database URL to async version."""
        url = self.database_url
        if url.startswith("postgres://"):
            # Railway uses postgres://, but SQLAlchemy needs postgresql+asyncpg://
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def sync_database_url(self) -> str:
        """Convert database URL to sync version."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        elif "asyncpg" in url:
            url = url.replace("+asyncpg", "", 1)
        elif "aiosqlite" in url:
            url = url.replace("+aiosqlite", "", 1)
        return url

    # Redis Cache (INFRA-004)
    redis_url: str = ""  # e.g., redis://localhost:6379 or Railway Redis URL
    cache_ttl_default: int = 300  # 5 minutes default TTL
    cache_ttl_contractor: int = 600  # 10 minutes for contractor profiles
    cache_ttl_pricing: int = 1800  # 30 minutes for pricing categories

    # File Storage (S3 or local for MVP)
    storage_type: str = "local"  # "local" or "s3"
    storage_path: str = "./data/uploads"
    s3_bucket: str = ""
    aws_access_key: str = ""
    aws_secret_key: str = ""

    # Transcription
    transcription_provider: str = "openai"  # "openai" (Whisper) or "deepgram"
    deepgram_api_key: str = ""

    # Claude model settings
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096

    # Stripe Payment Settings
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    # Stripe Product IDs (production)
    # Legacy tiers (deprecated, kept for existing subscriber webhook handling)
    stripe_starter_product_id: str = "prod_TXB6SKP96LAlcM"
    stripe_pro_product_id: str = "prod_TXB6du0ylntvVV"
    stripe_team_product_id: str = "prod_TXB6aO5kvAD4uV"

    # New single-tier pricing (DISC-098)
    stripe_unlimited_product_id: str = "prod_TapBB8ff0tCan0"

    # Analytics & Monitoring
    posthog_api_key: str = ""  # PostHog analytics
    sentry_dsn: str = ""  # Sentry error tracking

    # Pricing Configuration
    trial_days: int = 7
    trial_quote_limit: int = 75

    # Single-tier pricing (DISC-098) - $9/month or $59/year unlimited quotes
    # Replaces legacy 3-tier pricing
    unlimited_monthly_quotes: int = 999999  # Unlimited
    unlimited_price_monthly: int = 900  # $9.00 in cents
    unlimited_price_annual: int = 5900  # $59.00 in cents
    unlimited_overage_price: int = 0  # No overage - unlimited plan

    # Legacy plan limits and pricing (deprecated, kept for existing subscribers)
    # Note: New signups use unlimited tier only
    starter_monthly_quotes: int = 75
    starter_price_monthly: int = 1900  # $19.00 in cents
    starter_overage_price: int = 50  # $0.50 in cents

    pro_monthly_quotes: int = 200
    pro_price_monthly: int = 3900  # $39.00 in cents
    pro_overage_price: int = 35  # $0.35 in cents

    team_monthly_quotes: int = 999999  # Effectively unlimited
    team_price_monthly: int = 7900  # $79.00 in cents
    team_overage_price: int = 0  # No overage - unlimited plan

    # One-time migration flags (DISC-098)
    # Set CLEAR_STRIPE_TEST_CUSTOMERS=true when switching from test to live Stripe
    clear_stripe_test_customers: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def _validate_jwt_secret(s: Settings) -> None:
    """
    Validate JWT secret key configuration.

    CRITICAL: In production, JWT_SECRET_KEY MUST be set as an environment variable.
    Without this, a new secret is generated on each deploy, invalidating all tokens
    and causing the "quotes not visible" bug.
    """
    # Check if JWT_SECRET_KEY was explicitly set via environment variable
    jwt_from_env = os.environ.get("JWT_SECRET_KEY")

    if s.environment == "production":
        if jwt_from_env is None:
            # JWT_SECRET_KEY not set - this is a CRITICAL issue
            print("\n" + "=" * 80)
            print("🚨 CRITICAL: JWT_SECRET_KEY not set in environment!")
            print("=" * 80)
            print("\nThis causes ALL user sessions to be invalidated on each deploy!")
            print("Users will appear logged out with no quotes visible.")
            print("\n📋 FIX THIS NOW:")
            print("1. Go to Railway Dashboard → quoted project → Variables")
            print("2. Add: JWT_SECRET_KEY = <paste the key below>")
            print("\n🔑 Use this key (save it securely):")
            print(f"   {secrets.token_urlsafe(32)}")
            print("\n⚠️  After adding the variable, redeploy the service.")
            print("=" * 80 + "\n")
        elif len(s.jwt_secret_key) < 32:
            print("\n" + "=" * 80)
            print("⚠️  WARNING: JWT_SECRET_KEY is too short (< 32 characters)")
            print("For security, use at least 32 characters.")
            print("=" * 80 + "\n")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    s = Settings()
    _validate_jwt_secret(s)
    return s


# Convenience access
settings = get_settings()
