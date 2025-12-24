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
    normalized_email = Column(String(255), nullable=True, index=True)  # DISC-017: For duplicate detection
    hashed_password = Column(String(255), nullable=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification

    # Billing
    stripe_customer_id = Column(String(255), unique=True, nullable=True, index=True)
    subscription_id = Column(String(255), unique=True, nullable=True)
    plan_tier = Column(String(50), default="trial")  # trial, starter, pro, team
    quotes_used = Column(Integer, default=0)  # Quotes used in current billing cycle
    billing_cycle_start = Column(DateTime, nullable=True)  # Start of current billing period
    trial_ends_at = Column(DateTime, nullable=True)  # When trial expires
    grace_quotes_used = Column(Integer, default=0)  # DISC-018: Grace quotes used after trial limit (max 3)

    # Referrals (GROWTH-002)
    referral_code = Column(String(20), unique=True, nullable=True, index=True)  # User's unique referral code (e.g., JOHN-A3X9)
    referred_by_code = Column(String(20), nullable=True, index=True)  # Referral code used when signing up
    referral_count = Column(Integer, default=0)  # Number of successful referrals (referees who subscribed)
    referral_credits = Column(Integer, default=0)  # Months of credit earned from referrals

    # Onboarding (DISC-007)
    onboarding_path = Column(String(20), nullable=True)  # "interview" or "quick_setup"
    onboarding_completed_at = Column(DateTime, nullable=True)  # When onboarding was completed

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
    logo_data = Column(Text)  # Base64-encoded logo image (DISC-016)

    # What they do
    primary_trade = Column(String(100))  # e.g., "deck_builder", "painter", "landscaper"
    services = Column(JSON)  # List of services they offer

    # PDF Template Settings (DISC-028)
    pdf_template = Column(String(50), default="modern")  # Template style key
    pdf_accent_color = Column(String(50), nullable=True)  # Hex color or preset name

    # Subscription
    plan = Column(String(50), default="starter")  # starter, team
    is_active = Column(Boolean, default=True)

    # Relationships - all scoped to this contractor
    user = relationship("User", back_populates="contractor")
    pricing_model = relationship("PricingModel", back_populates="contractor", uselist=False)
    terms = relationship("ContractorTerms", back_populates="contractor", uselist=False)
    job_types = relationship("JobType", back_populates="contractor")
    quotes = relationship("Quote", back_populates="contractor")
    invoices = relationship("Invoice", back_populates="contractor")  # DISC-071
    customers = relationship("Customer", back_populates="contractor")  # DISC-086
    tasks = relationship("Task", back_populates="contractor")  # DISC-092


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

    # Global pricing philosophy - the contractor's overall pricing DNA
    # Generated during onboarding, updated when fundamental changes are learned
    pricing_philosophy = Column(Text)
    """
    Example: "You're a premium residential contractor in Austin specializing in
    high-end deck and outdoor living projects. You price labor at $85/hour because
    you do meticulous finish work. Materials are marked up 25% - you handle all
    procurement and delivery. You always include a 10% contingency buffer because
    scope creep is common. Your minimums are $1,500 because quality costs more.
    You prefer to quote slightly high and come in under budget."
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

    # DISC-067: Default timeline and terms text for quotes
    default_timeline_text = Column(Text)  # Default timeline description for quotes
    default_terms_text = Column(Text)  # Default terms/conditions text for quotes

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
    # INFRA-005: Index on contractor_id for frequent queries
    contractor_id = Column(String, ForeignKey("contractors.id"), nullable=False, index=True)
    # INFRA-005: Index on created_at for sorting/filtering
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Customer info (optional - might not have it for budgetary quotes)
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    customer_address = Column(Text)

    # DISC-086: Link to Customer record (CRM)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True, index=True)

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

    # DISC-067: Per-quote timeline and terms text (overrides contractor defaults)
    timeline_text = Column(Text)  # Free-form timeline description for this quote
    terms_text = Column(Text)  # Free-form terms/conditions for this quote

    # Status - INFRA-005: Index for filtering by status
    status = Column(String(50), default="draft", index=True)  # draft, sent, won, lost, expired
    sent_at = Column(DateTime)
    is_grace_quote = Column(Boolean, default=False)  # DISC-018: True if generated during grace period

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

    # Sharing (GROWTH-003)
    share_token = Column(String(32), unique=True, nullable=True, index=True)  # For public access
    shared_at = Column(DateTime, nullable=True)  # When first shared
    share_count = Column(Integer, default=0)  # Track total shares

    # Duplication (DISC-038)
    duplicate_source_quote_id = Column(String(36), nullable=True)  # Quote this was duplicated from

    # Relationship
    contractor = relationship("Contractor", back_populates="quotes")
    feedback = relationship("QuoteFeedback", back_populates="quote", uselist=False)
    invoices = relationship("Invoice", back_populates="quote")  # DISC-071: One quote can have multiple invoices
    customer = relationship("Customer", back_populates="quotes")  # DISC-086: CRM customer link


class QuoteFeedback(Base):
    """
    User feedback on a generated quote (Enhancement 4).

    Allows users to rate quotes and provide explicit feedback without editing.
    This powers the learning loop - feedback is used to improve future quotes.

    Captures:
    - Overall satisfaction rating (1-5 stars)
    - Aspect ratings (pricing accuracy, description quality, etc.)
    - Specific issues (checkboxes for common problems)
    - Actual values if known (for calibration)
    - Free-form text feedback
    """
    __tablename__ = "quote_feedback"

    id = Column(String, primary_key=True, default=generate_uuid)
    quote_id = Column(String, ForeignKey("quotes.id"), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Overall rating (1-5 stars)
    overall_rating = Column(Integer)  # 1 = very poor, 5 = excellent

    # Aspect ratings (1-5 each, null if not rated)
    pricing_accuracy = Column(Integer)  # How accurate was the pricing?
    description_quality = Column(Integer)  # Was the job description good?
    line_item_completeness = Column(Integer)  # Were all items included?
    timeline_accuracy = Column(Integer)  # Was the timeline realistic?

    # Issue flags (specific problems, can select multiple)
    issues = Column(JSON, default=list)
    """
    Example:
    ["price_too_high", "price_too_low", "missing_items", "wrong_quantities",
     "unclear_description", "wrong_job_type", "timeline_unrealistic"]
    """

    # Pricing direction feedback (quick one-click feedback)
    pricing_direction = Column(String(20))  # "too_high", "too_low", "about_right"
    pricing_off_by_percent = Column(Float)  # Optional: how far off? e.g., 15.0 = 15% too high/low

    # Actual values (if user knows the correct amounts)
    actual_total = Column(Float)  # What should the total have been?
    actual_line_items = Column(JSON)  # Corrected line items if provided
    """
    Example:
    [
        {"name": "Demolition", "actual_amount": 1200, "original_amount": 1100},
        {"name": "Decking", "actual_amount": 4500, "original_amount": 4160}
    ]
    """

    # Free-form feedback
    feedback_text = Column(Text)  # Detailed notes from user
    improvement_suggestions = Column(Text)  # What would make future quotes better?

    # Context at time of feedback
    quote_was_sent = Column(Boolean)  # Had they sent this quote to customer?
    quote_outcome = Column(String(20))  # won, lost, pending (if known)

    # Learning status
    processed_for_learning = Column(Boolean, default=False)
    processed_at = Column(DateTime)

    # Relationship
    quote = relationship("Quote", back_populates="feedback")


# DISC-071: Invoice model for quote-to-invoice conversion
class Invoice(Base):
    """
    Invoice generated from a quote.
    Supports the quote-to-invoice workflow where contractors can convert
    accepted quotes into invoices for billing.

    One quote can have multiple invoices (for progress billing).
    """
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=generate_uuid)
    # INFRA-005: Index on contractor_id for frequent queries
    contractor_id = Column(String, ForeignKey("contractors.id"), nullable=False, index=True)
    # INFRA-005: Index on quote_id for joins
    quote_id = Column(String, ForeignKey("quotes.id"), nullable=True, index=True)  # Can create standalone invoices
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Invoice number (auto-generated per contractor)
    invoice_number = Column(String(50), nullable=False, index=True)

    # Customer info (copied from quote or entered manually)
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    customer_address = Column(Text)

    # Invoice details
    description = Column(Text)  # Job/project description
    line_items = Column(JSON)  # Same format as Quote line items
    """
    Example:
    [
        {"name": "Demolition", "description": "Remove existing deck", "amount": 1100},
        {"name": "Framing", "description": "PT frame and joists", "amount": 2800},
        ...
    ]
    """
    subtotal = Column(Float)
    tax_percent = Column(Float, default=0)  # Optional tax
    tax_amount = Column(Float, default=0)
    total = Column(Float)

    # Dates
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)  # When payment is due

    # Payment terms
    terms_text = Column(Text)  # Payment terms
    notes = Column(Text)  # Additional notes

    # Status tracking
    status = Column(String(50), default="draft")
    """
    Status flow:
    - draft: Just created, not sent
    - sent: Emailed to customer
    - viewed: Customer opened the link
    - paid: Marked as paid
    - overdue: Past due date, not paid
    - cancelled: Cancelled/voided
    """
    sent_at = Column(DateTime)
    paid_at = Column(DateTime)
    payment_method = Column(String(50))  # check, credit_card, cash, zelle, etc.
    payment_reference = Column(String(255))  # Check number, transaction ID, etc.

    # PDF storage
    pdf_url = Column(String(500))

    # Sharing
    share_token = Column(String(32), unique=True, nullable=True, index=True)

    # Relationships
    contractor = relationship("Contractor", back_populates="invoices")
    quote = relationship("Quote", back_populates="invoices")


# DISC-086: CRM Customer Model
class Customer(Base):
    """
    Customer record aggregated from quotes.
    Part of the voice-operated CRM system (DISC-085).

    Customers are auto-created from quote data and can be managed via voice/UI.
    """
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=generate_uuid)
    contractor_id = Column(String, ForeignKey("contractors.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Core Info (aggregated from quotes)
    name = Column(String(255), nullable=False)
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(Text)

    # Computed fields (updated on quote changes)
    total_quoted = Column(Float, default=0)  # Sum of all quotes
    total_won = Column(Float, default=0)  # Sum of won quotes
    quote_count = Column(Integer, default=0)  # Number of quotes
    first_quote_at = Column(DateTime)  # First interaction
    last_quote_at = Column(DateTime)  # Most recent interaction

    # CRM-specific fields
    status = Column(String(50), default="active")  # active, inactive, lead, vip
    notes = Column(Text)  # Free-form notes
    tags = Column(JSON, default=list)  # User-defined tags

    # Source tracking
    source = Column(String(100))  # How they found us (optional)

    # Deduplication - normalized values for matching
    normalized_name = Column(String(255), index=True)  # Lowercase, no punctuation
    normalized_phone = Column(String(20), index=True)  # Digits only

    # Relationships
    contractor = relationship("Contractor", back_populates="customers")
    quotes = relationship("Quote", back_populates="customer")
    tasks = relationship("Task", back_populates="customer")  # DISC-092


# DISC-092: CRM Task & Reminder Model
class Task(Base):
    """
    Task/reminder record for CRM workflow management.
    Supports both manual tasks and auto-generated reminders.

    Linked optionally to customers and quotes for context.
    """
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    contractor_id = Column(String, ForeignKey("contractors.id"), nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True, index=True)
    quote_id = Column(String, ForeignKey("quotes.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Task details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    task_type = Column(String(50), default="other")  # follow_up, quote, call, site_visit, material_order, reminder, other

    # Scheduling
    due_date = Column(DateTime, index=True)  # When task is due
    reminder_time = Column(DateTime)  # When to send reminder notification
    completed_at = Column(DateTime)  # When task was completed

    # Status
    status = Column(String(50), default="pending")  # pending, completed, snoozed, cancelled

    # Recurrence (optional)
    recurrence = Column(String(50))  # one_time, daily, weekly, monthly
    recurrence_end_date = Column(DateTime)  # When recurrence ends

    # Auto-generation tracking
    auto_generated = Column(Boolean, default=False)  # True if system-created
    trigger_type = Column(String(100))  # What triggered auto-creation (e.g., "quote_no_response_7d")
    trigger_entity_id = Column(String)  # ID of quote/customer that triggered this

    # Notification tracking
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime)

    # Snooze tracking
    snoozed_until = Column(DateTime)
    snooze_count = Column(Integer, default=0)

    # Relationships
    contractor = relationship("Contractor", back_populates="tasks")
    customer = relationship("Customer", back_populates="tasks")
    quote = relationship("Quote")  # One-way relationship, quote doesn't need back-ref


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


class RefreshToken(Base):
    """
    Refresh tokens for JWT authentication (SEC-003).

    Workflow:
    1. On login/register, generate both access token (15 min) and refresh token (7 days)
    2. Store refresh token hash in database
    3. When access token expires, client uses refresh token to get new access token
    4. On logout, revoke all refresh tokens for user

    Security features:
    - Tokens stored as hashes (bcrypt), not plaintext
    - Each token has unique jti (JWT ID) for revocation
    - Tokens can be revoked individually or all at once
    - Family-based rotation prevents token theft attacks
    """
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)

    # Token identification
    jti = Column(String(36), unique=True, nullable=False, index=True)  # JWT ID for revocation
    token_hash = Column(String(255), nullable=False)  # bcrypt hash of the token

    # Device/session tracking (optional)
    device_info = Column(String(255))  # Browser/device identifier
    ip_address = Column(String(45))  # IPv4 or IPv6

    # Revocation
    revoked = Column(Boolean, default=False, index=True)
    revoked_at = Column(DateTime)
    revoked_reason = Column(String(100))  # logout, token_rotation, security, expired

    # Token family for rotation (prevents reuse of old tokens)
    family_id = Column(String(36), index=True)  # All tokens in rotation share this


class Testimonial(Base):
    """
    User testimonials collected from beta users.

    Workflow:
    1. After user generates 3rd quote, testimonial collection modal appears
    2. User submits rating + testimonial text
    3. Stored as pending (approved=False)
    4. Admin manually reviews and approves for landing page display
    """
    __tablename__ = "testimonials"

    id = Column(String, primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Who submitted it
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Testimonial content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    quote_text = Column(Text, nullable=False)  # What they said about Quoted

    # Optional attribution
    name = Column(String(255), nullable=True)  # Full name (optional)
    company = Column(String(255), nullable=True)  # Company name (optional)

    # Approval status
    approved = Column(Boolean, default=False)  # Needs admin approval before showing on landing
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(255), nullable=True)


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

    # Run migrations for existing tables (add missing columns)
    await run_migrations(engine)
    return engine


async def run_migrations(engine):
    """
    Add missing columns to existing tables.
    SQLAlchemy's create_all doesn't add columns to existing tables,
    so we need to handle that manually.
    """
    from sqlalchemy import text

    # Column additions
    column_migrations = [
        # Add session_data column to setup_conversations if missing
        {
            "table": "setup_conversations",
            "column": "session_data",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'setup_conversations' AND column_name = 'session_data'
            """,
            "alter_sql": "ALTER TABLE setup_conversations ADD COLUMN session_data JSON"
        },
        # Add extracted_data column if missing (was also added later)
        {
            "table": "setup_conversations",
            "column": "extracted_data",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'setup_conversations' AND column_name = 'extracted_data'
            """,
            "alter_sql": "ALTER TABLE setup_conversations ADD COLUMN extracted_data JSON"
        },
        # Billing columns for users table
        {
            "table": "users",
            "column": "stripe_customer_id",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'stripe_customer_id'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR"
        },
        {
            "table": "users",
            "column": "subscription_id",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'subscription_id'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN subscription_id VARCHAR"
        },
        {
            "table": "users",
            "column": "plan_tier",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'plan_tier'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN plan_tier VARCHAR DEFAULT 'trial'"
        },
        {
            "table": "users",
            "column": "quotes_used",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'quotes_used'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN quotes_used INTEGER DEFAULT 0"
        },
        {
            "table": "users",
            "column": "billing_cycle_start",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'billing_cycle_start'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN billing_cycle_start TIMESTAMP"
        },
        {
            "table": "users",
            "column": "trial_ends_at",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'trial_ends_at'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN trial_ends_at TIMESTAMP"
        },
        # Referral columns (GROWTH-002)
        {
            "table": "users",
            "column": "referral_code",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'referral_code'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN referral_code VARCHAR(20)"
        },
        {
            "table": "users",
            "column": "referred_by_code",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'referred_by_code'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN referred_by_code VARCHAR(20)"
        },
        {
            "table": "users",
            "column": "referral_count",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'referral_count'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN referral_count INTEGER DEFAULT 0"
        },
        {
            "table": "users",
            "column": "referral_credits",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'referral_credits'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN referral_credits INTEGER DEFAULT 0"
        },
        # Onboarding path tracking (DISC-007)
        {
            "table": "users",
            "column": "onboarding_path",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'onboarding_path'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN onboarding_path VARCHAR(20)"
        },
        {
            "table": "users",
            "column": "onboarding_completed_at",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'onboarding_completed_at'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN onboarding_completed_at TIMESTAMP"
        },
        # Share Quote columns (GROWTH-003)
        {
            "table": "quotes",
            "column": "share_token",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'quotes' AND column_name = 'share_token'
            """,
            "alter_sql": "ALTER TABLE quotes ADD COLUMN share_token VARCHAR(32)"
        },
        {
            "table": "quotes",
            "column": "shared_at",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'quotes' AND column_name = 'shared_at'
            """,
            "alter_sql": "ALTER TABLE quotes ADD COLUMN shared_at TIMESTAMP"
        },
        {
            "table": "quotes",
            "column": "share_count",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'quotes' AND column_name = 'share_count'
            """,
            "alter_sql": "ALTER TABLE quotes ADD COLUMN share_count INTEGER DEFAULT 0"
        },
        # Logo data column (DISC-016)
        {
            "table": "contractors",
            "column": "logo_data",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'contractors' AND column_name = 'logo_data'
            """,
            "alter_sql": "ALTER TABLE contractors ADD COLUMN logo_data TEXT"
        },
        # Normalized email column for trial abuse prevention (DISC-017)
        {
            "table": "users",
            "column": "normalized_email",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'normalized_email'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN normalized_email VARCHAR(255)"
        },
        # Grace period columns (DISC-018)
        {
            "table": "users",
            "column": "grace_quotes_used",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'grace_quotes_used'
            """,
            "alter_sql": "ALTER TABLE users ADD COLUMN grace_quotes_used INTEGER DEFAULT 0"
        },
        {
            "table": "quotes",
            "column": "is_grace_quote",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'quotes' AND column_name = 'is_grace_quote'
            """,
            "alter_sql": "ALTER TABLE quotes ADD COLUMN is_grace_quote BOOLEAN DEFAULT FALSE"
        },
        # PDF Template columns (DISC-028)
        {
            "table": "contractors",
            "column": "pdf_template",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'contractors' AND column_name = 'pdf_template'
            """,
            "alter_sql": "ALTER TABLE contractors ADD COLUMN pdf_template VARCHAR(50) DEFAULT 'modern'"
        },
        {
            "table": "contractors",
            "column": "pdf_accent_color",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'contractors' AND column_name = 'pdf_accent_color'
            """,
            "alter_sql": "ALTER TABLE contractors ADD COLUMN pdf_accent_color VARCHAR(50)"
        },
        # Duplicate source tracking (DISC-038)
        {
            "table": "quotes",
            "column": "duplicate_source_quote_id",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'quotes' AND column_name = 'duplicate_source_quote_id'
            """,
            "alter_sql": "ALTER TABLE quotes ADD COLUMN duplicate_source_quote_id VARCHAR(36)"
        },
        # Three-layer pricing architecture - global pricing philosophy
        {
            "table": "pricing_models",
            "column": "pricing_philosophy",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'pricing_models' AND column_name = 'pricing_philosophy'
            """,
            "alter_sql": "ALTER TABLE pricing_models ADD COLUMN pricing_philosophy TEXT"
        },
        # DISC-067: Timeline and terms text fields
        {
            "table": "quotes",
            "column": "timeline_text",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'quotes' AND column_name = 'timeline_text'
            """,
            "alter_sql": "ALTER TABLE quotes ADD COLUMN timeline_text TEXT"
        },
        {
            "table": "quotes",
            "column": "terms_text",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'quotes' AND column_name = 'terms_text'
            """,
            "alter_sql": "ALTER TABLE quotes ADD COLUMN terms_text TEXT"
        },
        {
            "table": "contractor_terms",
            "column": "default_timeline_text",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'contractor_terms' AND column_name = 'default_timeline_text'
            """,
            "alter_sql": "ALTER TABLE contractor_terms ADD COLUMN default_timeline_text TEXT"
        },
        {
            "table": "contractor_terms",
            "column": "default_terms_text",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'contractor_terms' AND column_name = 'default_terms_text'
            """,
            "alter_sql": "ALTER TABLE contractor_terms ADD COLUMN default_terms_text TEXT"
        },
        # DISC-086: CRM customer_id FK on quotes
        {
            "table": "quotes",
            "column": "customer_id",
            "check_sql": """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'quotes' AND column_name = 'customer_id'
            """,
            "alter_sql": "ALTER TABLE quotes ADD COLUMN customer_id VARCHAR"
        },
    ]

    # Constraint changes (PostgreSQL only - SQLite doesn't support these)
    constraint_migrations = [
        # Make contractor_id nullable in setup_conversations (for pre-signup interviews)
        {
            "description": "Make setup_conversations.contractor_id nullable",
            "check_sql": """
                SELECT is_nullable FROM information_schema.columns
                WHERE table_name = 'setup_conversations' AND column_name = 'contractor_id'
            """,
            "alter_sql": "ALTER TABLE setup_conversations ALTER COLUMN contractor_id DROP NOT NULL"
        },
    ]

    # INFRA-005: Index migrations for performance
    index_migrations = [
        {
            "name": "ix_quotes_contractor_id",
            "table": "quotes",
            "column": "contractor_id",
            "create_sql": "CREATE INDEX IF NOT EXISTS ix_quotes_contractor_id ON quotes(contractor_id)"
        },
        {
            "name": "ix_quotes_created_at",
            "table": "quotes",
            "column": "created_at",
            "create_sql": "CREATE INDEX IF NOT EXISTS ix_quotes_created_at ON quotes(created_at)"
        },
        {
            "name": "ix_quotes_status",
            "table": "quotes",
            "column": "status",
            "create_sql": "CREATE INDEX IF NOT EXISTS ix_quotes_status ON quotes(status)"
        },
        {
            "name": "ix_invoices_contractor_id",
            "table": "invoices",
            "column": "contractor_id",
            "create_sql": "CREATE INDEX IF NOT EXISTS ix_invoices_contractor_id ON invoices(contractor_id)"
        },
        {
            "name": "ix_invoices_quote_id",
            "table": "invoices",
            "column": "quote_id",
            "create_sql": "CREATE INDEX IF NOT EXISTS ix_invoices_quote_id ON invoices(quote_id)"
        },
        {
            "name": "ix_invoices_created_at",
            "table": "invoices",
            "column": "created_at",
            "create_sql": "CREATE INDEX IF NOT EXISTS ix_invoices_created_at ON invoices(created_at)"
        },
    ]

    async with engine.connect() as conn:
        # Run column additions
        for migration in column_migrations:
            try:
                result = await conn.execute(text(migration["check_sql"]))
                exists = result.fetchone() is not None

                if not exists:
                    print(f"Migration: Adding {migration['column']} column to {migration['table']}")
                    await conn.execute(text(migration["alter_sql"]))
                    await conn.commit()
                    print(f"Migration: Successfully added {migration['column']}")
            except Exception as e:
                # SQLite uses different syntax, try SQLite version
                if "information_schema" in str(e).lower() or "no such table" in str(e).lower():
                    try:
                        sqlite_check = f"PRAGMA table_info({migration['table']})"
                        result = await conn.execute(text(sqlite_check))
                        columns = [row[1] for row in result.fetchall()]

                        if migration["column"] not in columns:
                            print(f"Migration (SQLite): Adding {migration['column']} to {migration['table']}")
                            await conn.execute(text(migration["alter_sql"]))
                            await conn.commit()
                            print(f"Migration (SQLite): Successfully added {migration['column']}")
                    except Exception as sqlite_err:
                        print(f"Migration warning: Could not check/add {migration['column']}: {sqlite_err}")
                else:
                    print(f"Migration warning: {e}")

        # Data migrations (backfill existing records)
        data_migrations = [
            {
                "description": "Backfill onboarding_completed_at for existing users",
                "check_sql": """
                    SELECT COUNT(*) FROM users
                    WHERE onboarding_completed_at IS NULL AND created_at IS NOT NULL
                """,
                "update_sql": """
                    UPDATE users
                    SET onboarding_completed_at = COALESCE(created_at, CURRENT_TIMESTAMP)
                    WHERE onboarding_completed_at IS NULL
                """
            },
        ]

        # DISC-098: One-time migration to clear test-mode Stripe customer IDs
        # Triggered by CLEAR_STRIPE_TEST_CUSTOMERS=true environment variable
        from ..config import settings
        if settings.clear_stripe_test_customers:
            try:
                result = await conn.execute(text(
                    "SELECT COUNT(*) FROM users WHERE stripe_customer_id IS NOT NULL"
                ))
                row = result.fetchone()
                count = row[0] if row else 0

                if count > 0:
                    print(f"DISC-098 Migration: Clearing {count} test-mode Stripe customer IDs")
                    await conn.execute(text("""
                        UPDATE users
                        SET stripe_customer_id = NULL, subscription_id = NULL
                        WHERE stripe_customer_id IS NOT NULL
                    """))
                    await conn.commit()
                    print(f"DISC-098 Migration: Successfully cleared Stripe customer IDs for {count} users")
                    print("IMPORTANT: Remove CLEAR_STRIPE_TEST_CUSTOMERS env var after this deploy!")
            except Exception as e:
                print(f"DISC-098 Migration warning: {e}")

        for migration in data_migrations:
            try:
                result = await conn.execute(text(migration["check_sql"]))
                row = result.fetchone()
                count = row[0] if row else 0

                if count > 0:
                    print(f"Data migration: {migration['description']} ({count} records)")
                    await conn.execute(text(migration["update_sql"]))
                    await conn.commit()
                    print(f"Data migration: Successfully updated {count} records")
            except Exception as e:
                print(f"Data migration warning: {e}")

        # Run constraint changes (PostgreSQL only)
        for migration in constraint_migrations:
            try:
                result = await conn.execute(text(migration["check_sql"]))
                row = result.fetchone()
                if row and row[0] == 'NO':  # Currently NOT NULL
                    print(f"Migration: {migration['description']}")
                    await conn.execute(text(migration["alter_sql"]))
                    await conn.commit()
                    print(f"Migration: Successfully completed - {migration['description']}")
            except Exception as e:
                # SQLite doesn't support ALTER COLUMN, skip these migrations
                if "information_schema" not in str(e).lower():
                    print(f"Migration warning (constraint): {e}")

        # INFRA-005: Run index migrations
        for migration in index_migrations:
            try:
                await conn.execute(text(migration["create_sql"]))
                await conn.commit()
            except Exception as e:
                # Index might already exist or table doesn't exist yet
                if "already exists" not in str(e).lower():
                    print(f"Index migration warning ({migration['name']}): {e}")


def init_db_sync():
    """Synchronous database initialization for scripts."""
    from ..config import settings
    engine = create_engine(settings.sync_database_url)
    Base.metadata.create_all(engine)
    return engine
