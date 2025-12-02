"""
Configuration for Quoted application.
Uses environment variables for secrets.
"""

import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Quoted"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"  # development, production

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""  # For Whisper transcription
    resend_api_key: str = ""  # For transactional emails

    # Database - supports both SQLite (dev) and PostgreSQL (prod)
    database_url: str = "sqlite+aiosqlite:///./data/quoted.db"

    # JWT Authentication
    jwt_secret_key: str = secrets.token_urlsafe(32)  # Auto-generate if not set
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

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

    # Stripe Product IDs
    stripe_starter_product_id: str = "prod_TWyp6aH4vMY7A8"
    stripe_pro_product_id: str = "prod_TWyzygs71MWNeQ"
    stripe_team_product_id: str = "prod_TWz0uN0EAbgPKI"

    # Pricing Configuration
    trial_days: int = 7
    trial_quote_limit: int = 75

    # Plan limits and pricing
    starter_monthly_quotes: int = 75
    starter_price_monthly: int = 2900  # $29.00 in cents
    starter_overage_price: int = 50  # $0.50 in cents

    pro_monthly_quotes: int = 200
    pro_price_monthly: int = 4900  # $49.00 in cents
    pro_overage_price: int = 35  # $0.35 in cents

    team_monthly_quotes: int = 500
    team_price_monthly: int = 7900  # $79.00 in cents
    team_overage_price: int = 25  # $0.25 in cents

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience access
settings = get_settings()
