"""
AI Company Event Gateway.

Receives webhooks from external services (Stripe, Resend, Railway, etc.)
and queues them for processing by AI agents.

This is the entry point for all AI Civilization operations.

Security: All routes are gated by the ai_company_enabled feature flag.
"""

import json
import hmac
import hashlib
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.database import get_session
from ..models.ai_event import AIEvent, AIDecision, AIActionLog, EventUrgency
from ..services.feature_flags import is_feature_enabled


router = APIRouter(prefix="/api/ai-company", tags=["ai-company"])


async def check_ai_company_enabled():
    """Dependency to check if AI Company is enabled."""
    if not is_feature_enabled("ai_company_enabled"):
        raise HTTPException(status_code=404, detail="Not found")


def classify_event(source: str, event_type: str, payload: dict) -> tuple[EventUrgency, str]:
    """
    Classify event urgency and target agent.

    Returns (urgency, target_agent)
    """
    event_lower = event_type.lower()

    # Critical patterns - immediate attention
    critical_patterns = {
        "stripe": ["charge.dispute", "payment_intent.payment_failed", "invoice.payment_failed"],
        "resend": ["email.bounced", "email.complained"],
        "railway": ["error", "crash", "down", "failed"],
        "github": ["security_alert"],
    }

    for pattern in critical_patterns.get(source, []):
        if pattern in event_lower:
            agent = "ops" if source in ["railway", "github"] else "support"
            return EventUrgency.CRITICAL, agent

    # High priority patterns
    high_patterns = {
        "stripe": ["subscription.deleted", "customer.subscription.updated"],
        "resend": ["email.failed"],
        "github": ["issue.opened", "pull_request.opened"],
    }

    for pattern in high_patterns.get(source, []):
        if pattern in event_lower:
            return EventUrgency.HIGH, _get_target_agent(source)

    # Default routing
    return EventUrgency.MEDIUM, _get_target_agent(source)


def _get_target_agent(source: str) -> str:
    """Get the default target agent for a source."""
    routing = {
        "stripe": "support",
        "resend": "support",
        "railway": "ops",
        "github": "code",
        "posthog": "growth",
        "manual": "ops",
    }
    return routing.get(source, "ops")


@router.post("/webhook/{source}")
async def receive_webhook(
    source: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    _enabled: None = Depends(check_ai_company_enabled)
):
    """
    Receive webhooks from external services.

    Supported sources:
    - stripe: Payment events
    - resend: Email delivery events
    - railway: Deployment and log events
    - github: Repository events
    - manual: Manual triggers for testing
    """
    # Get raw body for signature verification
    body = await request.body()
    headers = dict(request.headers)

    # Verify signatures based on source
    if source == "stripe":
        # Stripe signature verification
        sig = headers.get("stripe-signature", "")
        if sig and not _verify_stripe_signature(body, sig):
            raise HTTPException(status_code=400, detail="Invalid signature")

    # Parse payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {"raw": body.decode("utf-8", errors="replace")}

    # Extract event type
    event_type = payload.get("type", payload.get("event", "unknown"))

    # Classify event
    urgency, target_agent = classify_event(source, event_type, payload)

    # Store event
    event = AIEvent(
        source=source,
        event_type=event_type,
        urgency=urgency,
        target_agent=target_agent,
        payload=payload,
        headers=headers,
        raw_body=body.decode("utf-8", errors="replace")
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)

    # Dispatch critical events immediately
    if urgency == EventUrgency.CRITICAL:
        from ..services.ai_dispatcher import dispatch_to_agent_async
        background_tasks.add_task(
            dispatch_to_agent_async,
            "urgent",
            {"event_id": event.id, "event": event.to_dict()}
        )

    return {
        "status": "received",
        "event_id": event.id,
        "urgency": urgency.value,
        "target_agent": target_agent
    }


def _verify_stripe_signature(payload: bytes, sig_header: str) -> bool:
    """Verify Stripe webhook signature."""
    import os
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret:
        # No secret configured - skip verification in dev
        return True

    try:
        import stripe
        stripe.Webhook.construct_event(payload, sig_header, secret)
        return True
    except Exception:
        return False


@router.get("/events/pending")
async def get_pending_events(
    limit: int = 50,
    agent: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    _enabled: None = Depends(check_ai_company_enabled)
):
    """
    Get pending events for processing.

    Used by GitHub Actions to fetch work for agents.
    """
    from sqlalchemy import select

    query = select(AIEvent).where(AIEvent.processed == False)

    if agent:
        query = query.where(AIEvent.target_agent == agent)

    # Order by urgency (critical first), then by age (oldest first)
    query = query.order_by(
        AIEvent.urgency.desc(),
        AIEvent.received_at.asc()
    ).limit(limit)

    result = await session.execute(query)
    events = result.scalars().all()

    return {"events": [e.to_dict() for e in events]}


@router.post("/events/{event_id}/mark-processed")
async def mark_processed(
    event_id: str,
    result: dict,
    session: AsyncSession = Depends(get_session),
    _enabled: None = Depends(check_ai_company_enabled)
):
    """Mark an event as processed with its result."""
    from sqlalchemy import select

    query = select(AIEvent).where(AIEvent.id == event_id)
    db_result = await session.execute(query)
    event = db_result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.processed = True
    event.processed_at = datetime.utcnow()
    event.processing_result = result
    await session.commit()

    return {"status": "marked", "event_id": event_id}


@router.get("/decisions/pending")
async def get_pending_decisions(
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
    _enabled: None = Depends(check_ai_company_enabled)
):
    """
    Get pending decisions for Eddie to review.

    Returns decisions that need human approval.
    """
    from sqlalchemy import select

    query = select(AIDecision).where(
        AIDecision.resolved_at == None
    ).order_by(
        AIDecision.urgency.desc(),
        AIDecision.created_at.asc()
    ).limit(limit)

    result = await session.execute(query)
    decisions = result.scalars().all()

    return {"decisions": [d.to_dict() for d in decisions]}


@router.post("/decisions/{decision_id}/resolve")
async def resolve_decision(
    decision_id: str,
    resolution: str,
    details: Optional[dict] = None,
    session: AsyncSession = Depends(get_session),
    _enabled: None = Depends(check_ai_company_enabled)
):
    """
    Resolve a pending decision.

    resolution: "approved", "rejected", or "custom"
    details: Additional information about the resolution
    """
    from sqlalchemy import select

    query = select(AIDecision).where(AIDecision.id == decision_id)
    result = await session.execute(query)
    decision = result.scalar_one_or_none()

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    decision.resolved_at = datetime.utcnow()
    decision.resolution = resolution
    decision.resolution_details = details
    decision.resolved_by = "eddie"
    await session.commit()

    return {"status": "resolved", "decision_id": decision_id}


@router.get("/logs")
async def get_action_logs(
    agent: Optional[str] = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    _enabled: None = Depends(check_ai_company_enabled)
):
    """
    Get recent action logs for audit.

    Shows what AI agents have done.
    """
    from sqlalchemy import select

    query = select(AIActionLog)

    if agent:
        query = query.where(AIActionLog.agent == agent)

    query = query.order_by(AIActionLog.timestamp.desc()).limit(limit)

    result = await session.execute(query)
    logs = result.scalars().all()

    return {"logs": [log.to_dict() for log in logs]}


@router.get("/health")
async def health(_enabled: None = Depends(check_ai_company_enabled)):
    """Health check for AI Company system."""
    return {
        "status": "healthy",
        "feature": "ai_company",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def get_status(
    session: AsyncSession = Depends(get_session),
    _enabled: None = Depends(check_ai_company_enabled)
):
    """
    Get overall AI Company status.

    Summary of pending events, decisions, and recent activity.
    """
    from sqlalchemy import select, func

    # Count pending events
    events_query = select(func.count()).select_from(AIEvent).where(AIEvent.processed == False)
    events_result = await session.execute(events_query)
    pending_events = events_result.scalar()

    # Count pending decisions
    decisions_query = select(func.count()).select_from(AIDecision).where(AIDecision.resolved_at == None)
    decisions_result = await session.execute(decisions_query)
    pending_decisions = decisions_result.scalar()

    # Recent activity count (last 24h)
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=24)
    activity_query = select(func.count()).select_from(AIActionLog).where(AIActionLog.timestamp > cutoff)
    activity_result = await session.execute(activity_query)
    recent_actions = activity_result.scalar()

    return {
        "status": "operational",
        "pending_events": pending_events,
        "pending_decisions": pending_decisions,
        "recent_actions_24h": recent_actions,
        "timestamp": datetime.utcnow().isoformat()
    }
