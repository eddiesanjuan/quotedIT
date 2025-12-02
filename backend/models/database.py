"""
Database models for Quoted.
Critical: Each contractor has completely isolated data and learning.
No cross-contamination between customers.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime,
    Boolean, ForeignKey, JSON, create_engine
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """
    User account for authentication.
    Each user has exactly one contractor profile.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification

    # Relationship to contractor (one-to-one)
    contractor = relationship("Contractor", back_populates="user", uselist=False)


class Contractor(Base):
    """
    The core customer entity. All other data is scoped to a contractor.
    This is the isolation boundary - everything below belongs to ONE contractor.
    """
    __tablename__ = "contractors"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=True)  # nullable for migration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Business Info
    business_name = Column(String(255), nullable=False)
    owner_name = Column(String(255))
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    address = Column(Text)
    service_area = Column(String(255))
    logo_url = Column(String(500))

    # What they do
    primary_trade = Column(String(100))  # e.g., "deck_builder", "painter", "landscaper"
    services = Column(JSON)  # List of services they offer

    # Subscription
    plan = Column(String(50), default="starter")  # starter, team
    is_active = Column(Boolean, default=True)

    # Relationships - all scoped to this contractor
    user = relationship("User", back_populates="contractor")
    pricing_model = relationship("PricingModel", back_populates="contractor", uselist=False)
    terms = relationship("ContractorTerms", back_populates="contractor", uselist=False)
    job_types = relationship("JobType", back_populates="contractor")
    quotes = relationship("Quote", back_populates="contractor")


class PricingModel(Base):
    """
    The learned pricing model for ONE contractor.
    This is their 'brain' - how they price jobs.
    Updated every time they correct a quote.

    CRITICAL: This is per-contractor. Never shared.
    """
    __tablename__ = "pricing_models"

    id = Column(String, primary_key=True, default=generate_uuid)
    contractor_id = Column(String, ForeignKey("contractors.id"), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Core pricing parameters (learned from setup + corrections)
    labor_rate_hourly = Column(Float)  # $/hour for owner
    helper_rate_hourly = Column(Float)  # $/hour for helpers
    labor_rate_daily = Column(Float)  # $/day alternative
    material_markup_percent = Column(Float, default=20.0)  # % markup on materials
    minimum_job_amount = Column(Float)  # Won't take jobs under this

    # The flexible learned pricing knowledge
    # This JSON blob stores everything the AI has learned about their pricing
    pricing_knowledge = Column(JSON, default=dict)
    """
    Example pricing_knowledge structure:
    {
        "deck_composite": {
            "base_per_sqft": 58.0,
            "confidence": 0.85,
            "samples": 23,
            "notes": "Trex Select baseline, adjust +10% for Transcend"
        },
        "deck_wood": {
            "base_per_sqft": 42.0,
            "confidence": 0.90,
            "samples": 31
        },
        "demolition": {
            "base_rate": 800,
            "per_sqft_adder": 2.5,
            "notes": "Add 50% for second story"
        },
        "railings": {
            "per_linear_foot": 35.0,
            "cable_rail_multiplier": 1.8
        },
        "adjustments": {
            "difficult_access": 1.10,
            "second_story": 1.25,
            "winter_work": 1.15
        }
    }
    """

    # General pricing notes (natural language, used in prompts)
    pricing_notes = Column(Text)
    """
    Example: "I usually add 10% for jobs in the Heights neighborhood because
    parking is a pain. For repeat customers I knock off 5%."
    """

    # Relationship
    contractor = relationship("Contractor", back_populates="pricing_model")


class ContractorTerms(Base):
    """
    Standard terms and conditions for ONE contractor.
    Goes on every quote they send.
    """
    __tablename__ = "contractor_terms"

    id = Column(String, primary_key=True, default=generate_uuid)
    contractor_id = Column(String, ForeignKey("contractors.id"), unique=True, nullable=False)

    # Payment terms
    deposit_percent = Column(Float, default=50.0)
    deposit_description = Column(String(255), default="50% deposit to schedule")
    final_payment_terms = Column(String(255), default="Balance due upon completion")
    accepted_payment_methods = Column(JSON, default=["check", "credit_card"])
    credit_card_fee_percent = Column(Float, default=3.0)

    # Timeline
    quote_valid_days = Column(Integer, default=30)
    typical_scheduling_weeks = Column(Integer, default=2)  # "Available within X weeks"

    # Warranty
    labor_warranty_years = Column(Integer, default=2)
    labor_warranty_text = Column(Text)

    # Custom terms (free-form, appended to quote)
    custom_terms = Column(Text)

    # Relationship
    contractor = relationship("Contractor", back_populates="terms")


class JobType(Base):
    """
    Types of jobs this contractor does, with their specific pricing patterns.
    Learned and refined over time.
    """
    __tablename__ = "job_types"

    id = Column(String, primary_key=True, default=generate_uuid)
    contractor_id = Column(String, ForeignKey("contractors.id"), nullable=False)

    name = Column(String(100), nullable=False)  # e.g., "composite_deck", "fence_wood"
    display_name = Column(String(100))  # e.g., "Composite Deck"

    # Pricing pattern for this job type
    pricing_pattern = Column(JSON)
    """
    Example for a deck:
    {
        "unit": "sqft",
        "base_rate": 58.0,
        "typical_range": [45.0, 75.0],
        "line_items": [
            {"name": "Framing", "percent_of_total": 0.20},
            {"name": "Decking", "percent_of_total": 0.35},
            {"name": "Railing", "unit": "linear_ft", "rate": 35.0},
            {"name": "Stairs", "unit": "each", "rate": 650}
        ],
        "common_adders": [
            {"name": "Demolition", "trigger": "demo", "rate": 800},
            {"name": "Permit", "trigger": "permit", "rate": 250}
        ]
    }
    """

    # Stats from actual quotes
    quote_count = Column(Integer, default=0)
    average_quote_amount = Column(Float)
    win_rate = Column(Float)  # If they track wins/losses

    # Relationship
    contractor = relationship("Contractor", back_populates="job_types")


class Quote(Base):
    """
    A generated quote. Stores both the input (voice/text) and output (generated quote).
    Used for learning and history.
    """
    __tablename__ = "quotes"

    id = Column(String, primary_key=True, default=generate_uuid)
    contractor_id = Column(String, ForeignKey("contractors.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Customer info (optional - might not have it for budgetary quotes)
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    customer_address = Column(Text)

    # Input
    original_voice_url = Column(String(500))  # S3 URL to audio file
    transcription = Column(Text)  # What they said

    # Generated output
    job_type = Column(String(100))  # Detected job type
    job_description = Column(Text)  # Parsed description
    line_items = Column(JSON)  # The itemized quote
    """
    Example:
    [
        {"name": "Demolition", "description": "Remove existing deck", "amount": 1100},
        {"name": "Framing", "description": "PT frame and joists", "amount": 2800},
        {"name": "Decking", "description": "Trex Select, 320 sqft", "amount": 4160},
        ...
    ]
    """
    subtotal = Column(Float)
    total = Column(Float)

    # What the AI generated (before any edits)
    ai_generated_total = Column(Float)

    # Timeline
    estimated_days = Column(Integer)
    estimated_crew_size = Column(Integer)

    # Status
    status = Column(String(50), default="draft")  # draft, sent, won, lost, expired
    sent_at = Column(DateTime)

    # Corrections (for learning)
    was_edited = Column(Boolean, default=False)
    edit_details = Column(JSON)  # What changed
    """
    Example:
    {
        "total_change": 400,
        "total_change_percent": 3.2,
        "line_item_changes": [
            {"item": "Decking", "original": 4160, "final": 4400, "reason": "Premium boards"}
        ],
        "learning_note": "Customer wanted Trex Transcend, not Select"
    }
    """

    # Outcome (for learning what wins)
    outcome = Column(String(50))  # won, lost, pending
    outcome_notes = Column(Text)

    # The full generated PDF/document
    pdf_url = Column(String(500))

    # Relationship
    contractor = relationship("Contractor", back_populates="quotes")


class SetupConversation(Base):
    """
    Stores the setup/onboarding conversation for a contractor.
    This is how we initially learn their pricing model.

    Can be created before a contractor record exists (during onboarding flow).
    """
    __tablename__ = "setup_conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    contractor_id = Column(String, ForeignKey("contractors.id"), nullable=True)  # Nullable for pre-signup interviews
    created_at = Column(DateTime, default=datetime.utcnow)

    # Session metadata (contractor_name, primary_trade, initial_message, etc.)
    session_data = Column(JSON)

    # The full conversation
    messages = Column(JSON)  # List of {role, content} messages

    # Extracted data (intermediate, before pricing model is built)
    extracted_data = Column(JSON)

    # Status
    status = Column(String(50), default="in_progress")  # in_progress, completed
    completed_at = Column(DateTime)


class UserIssue(Base):
    """
    User-reported issues for autonomous Claude Code resolution.

    Workflow:
    1. User reports issue via app (creates record with status='new')
    2. Polling script detects new issues
    3. Claude Code agent attempts to fix
    4. Status updated to 'in_progress', 'resolved', or 'needs_human'
    5. Resolution details stored for user review
    """
    __tablename__ = "user_issues"

    id = Column(String, primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Who reported it (nullable for anonymous/pre-auth issues)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Issue details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100))  # bug, feature_request, ui_issue, pricing_issue, etc.
    severity = Column(String(50), default="medium")  # low, medium, high, critical

    # Context for Claude Code
    page_url = Column(String(500))  # Where the issue occurred
    browser_info = Column(String(255))
    error_message = Column(Text)  # Any JS errors captured
    screenshot_url = Column(String(500))  # Optional screenshot
    steps_to_reproduce = Column(Text)

    # Processing status
    status = Column(String(50), default="new")
    """
    Status flow:
    - new: Just reported, awaiting pickup
    - queued: Picked up by autonomous agent, waiting to process
    - in_progress: Claude Code actively working on it
    - resolved: Successfully fixed
    - needs_human: Claude couldn't fix, needs human review
    - wont_fix: Intentional behavior or out of scope
    - duplicate: Duplicate of another issue
    """

    # Resolution tracking
    picked_up_at = Column(DateTime)  # When autonomous agent started
    resolved_at = Column(DateTime)

    # Claude Code's work
    agent_analysis = Column(Text)  # Claude's understanding of the issue
    agent_solution = Column(Text)  # What Claude did to fix it
    files_modified = Column(JSON)  # List of files changed
    commit_hash = Column(String(64))  # Git commit if changes were made

    # Human review
    human_notes = Column(Text)
    verified_by = Column(String)  # Admin who verified the fix
    verified_at = Column(DateTime)


# Database initialization
def get_database_url(async_mode: bool = True) -> str:
    """Get database URL from config. Supports SQLite and PostgreSQL."""
    from ..config import settings
    if async_mode:
        return settings.async_database_url
    return settings.sync_database_url


async def init_db():
    """Initialize the database and create tables."""
    from ..config import settings
    engine = create_async_engine(settings.async_database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


def init_db_sync():
    """Synchronous database initialization for scripts."""
    from ..config import settings
    engine = create_engine(settings.sync_database_url)
    Base.metadata.create_all(engine)
    return engine
