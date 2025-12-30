"""
AI Company Event Model.

Stores incoming events from webhooks (Stripe, Resend, Railway, etc.)
for processing by the AI Civilization agents.

Part of the AI Company autonomous operations system.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSON
import uuid
import enum

from .database import Base


def generate_uuid():
    return str(uuid.uuid4())


class EventUrgency(enum.Enum):
    """Event urgency levels for prioritization."""
    CRITICAL = "critical"  # Immediate attention required
    HIGH = "high"          # Process within 1 hour
    MEDIUM = "medium"      # Process in next loop
    LOW = "low"            # Can wait for batch processing


class AIEvent(Base):
    """
    Incoming event from external services.

    Events are received via webhooks and queued for processing
    by the appropriate AI agent (Support, Ops, Code, Growth).
    """
    __tablename__ = "ai_company_events"

    id = Column(String, primary_key=True, default=generate_uuid)

    # Source information
    source = Column(String(50), nullable=False, index=True)  # stripe, resend, railway, manual, github
    event_type = Column(String(100), nullable=False)  # e.g., payment_failed, email.bounced

    # Classification
    urgency = Column(SQLEnum(EventUrgency), default=EventUrgency.MEDIUM)
    target_agent = Column(String(50), nullable=True, index=True)  # support, ops, code, growth

    # Content
    payload = Column(JSON, nullable=False)  # Full event payload
    headers = Column(JSON, nullable=True)   # Request headers for verification
    raw_body = Column(Text, nullable=True)  # Original request body

    # Processing state
    received_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    processing_result = Column(JSON, nullable=True)  # What the agent did

    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(String(10), default="0")  # Number of processing attempts

    # Linking
    related_event_id = Column(String, nullable=True)  # Link to related events

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "source": self.source,
            "event_type": self.event_type,
            "urgency": self.urgency.value if self.urgency else "medium",
            "target_agent": self.target_agent,
            "payload": self.payload,
            "received_at": self.received_at.isoformat() if self.received_at else None,
            "processed": self.processed,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }

    def __repr__(self):
        return f"<AIEvent {self.id[:8]} {self.source}/{self.event_type} urgency={self.urgency.value if self.urgency else 'medium'}>"


class AIDecision(Base):
    """
    Decisions made by AI agents that require human approval.

    The decision queue - items pending Eddie's review.
    """
    __tablename__ = "ai_company_decisions"

    id = Column(String, primary_key=True, default=generate_uuid)

    # Source
    agent = Column(String(50), nullable=False)  # Which agent created this
    event_id = Column(String, nullable=True)    # Triggering event if any

    # Classification
    category = Column(String(50), nullable=False)  # support, ops, growth, finance
    urgency = Column(SQLEnum(EventUrgency), default=EventUrgency.MEDIUM)

    # Content
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    context = Column(JSON, nullable=False)      # Full context for decision
    options = Column(JSON, nullable=False)      # Available choices
    recommendation = Column(JSON, nullable=True) # AI's recommendation with reasoning

    # Status
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution = Column(String(50), nullable=True)  # approved, rejected, custom
    resolution_details = Column(JSON, nullable=True)
    resolved_by = Column(String(100), nullable=True)  # "eddie" or "system"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "agent": self.agent,
            "category": self.category,
            "urgency": self.urgency.value if self.urgency else "medium",
            "title": self.title,
            "summary": self.summary,
            "context": self.context,
            "options": self.options,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved": self.resolved_at is not None,
        }


class AIActionLog(Base):
    """
    Audit log of all AI agent actions.

    Every action is logged for transparency and debugging.
    """
    __tablename__ = "ai_company_action_logs"

    id = Column(String, primary_key=True, default=generate_uuid)

    # Who
    agent = Column(String(50), nullable=False)

    # What
    action_type = Column(String(50), nullable=False)  # autonomous, approved, escalated
    action = Column(String(255), nullable=False)      # Description
    reasoning = Column(Text, nullable=True)           # Why this action

    # Context
    event_id = Column(String, nullable=True)
    decision_id = Column(String, nullable=True)
    confidence = Column(String(10), nullable=True)  # 0.0-1.0

    # Inputs/Outputs
    inputs = Column(JSON, nullable=True)    # What information was used
    outputs = Column(JSON, nullable=True)   # What was produced

    # Result
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    outcome = Column(String(50), nullable=True)  # success, failure, pending
    error_message = Column(Text, nullable=True)

    # Reversibility
    reversible = Column(Boolean, default=True)
    reversed_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "agent": self.agent,
            "action_type": self.action_type,
            "action": self.action,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "outcome": self.outcome,
        }
