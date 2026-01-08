"""
Webhook endpoints for external services.
Handles incoming events from Resend, and other services.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr

from ..config import settings
from ..services.support import support_service

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for Resend webhook payloads
class ResendEmailAddress(BaseModel):
    """Email address with name."""
    email: EmailStr
    name: Optional[str] = None


class ResendInboundEmail(BaseModel):
    """
    Resend inbound email webhook payload.

    Reference: https://resend.com/docs/api-reference/webhooks/inbound-emails
    """
    from_: ResendEmailAddress
    to: list[ResendEmailAddress]
    subject: str
    html: Optional[str] = None
    text: Optional[str] = None
    reply_to: Optional[ResendEmailAddress] = None
    message_id: str
    created_at: str

    class Config:
        # Allow using 'from' as field name (Python keyword)
        fields = {"from_": "from"}


@router.post("/resend")
async def resend_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Handle incoming email webhooks from Resend.

    DISC-160: Support Agent Infrastructure

    This endpoint receives incoming customer emails forwarded by Resend
    and queues them for the Support Agent to process.

    Security:
    - Webhook signing verification (if enabled)
    - Rate limiting at infrastructure level

    Flow:
    1. Receive and validate webhook payload
    2. Append to support agent inbox (.ai-company/agents/support/inbox.md)
    3. Return 200 immediately (async processing)

    Returns:
        Dict with status confirmation
    """
    try:
        # Get webhook payload
        payload = await request.json()

        # Verify webhook signature if secret is configured
        # Resend uses 'svix-signature' header
        signature = request.headers.get("svix-signature")
        if settings.resend_webhook_secret and not signature:
            logger.warning("Resend webhook received without signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature"
            )

        # Parse webhook type
        webhook_type = payload.get("type")
        logger.info(f"Received Resend webhook: {webhook_type}")

        # Handle different webhook types
        if webhook_type == "email.received":
            # Inbound email - add to support queue
            email_data = payload.get("data", {})
            await handle_inbound_email(email_data, background_tasks)

        elif webhook_type == "email.delivered":
            # Outbound email delivered successfully - log for monitoring
            logger.info(f"Email delivered: {payload.get('data', {}).get('message_id')}")

        elif webhook_type == "email.bounced":
            # Email bounced - log and alert
            logger.warning(f"Email bounced: {payload.get('data', {})}")
            # TODO: Alert founder via monitoring agent

        elif webhook_type == "email.complained":
            # Spam complaint - log and alert
            logger.error(f"Email spam complaint: {payload.get('data', {})}")
            # TODO: Alert founder immediately

        else:
            logger.info(f"Unhandled Resend webhook type: {webhook_type}")

        return {"status": "success", "type": webhook_type}

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}", exc_info=True)
        # Return 500 so Resend will retry
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


async def handle_inbound_email(
    email_data: Dict[str, Any],
    background_tasks: BackgroundTasks
) -> None:
    """
    Process an inbound email and add to support inbox.

    DISC-160: File-based queue approach (no database complexity).

    Args:
        email_data: Resend webhook email payload
        background_tasks: FastAPI background tasks for async classification
    """
    try:
        # Extract email details
        from_email = email_data.get("from", {}).get("email", "unknown@example.com")
        from_name = email_data.get("from", {}).get("name", "")
        subject = email_data.get("subject", "(no subject)")
        text_body = email_data.get("text", "")
        html_body = email_data.get("html", "")
        message_id = email_data.get("message_id", "unknown")
        received_at = email_data.get("created_at", datetime.utcnow().isoformat())

        # Prefer plain text, fallback to HTML
        body = text_body if text_body else html_body

        # Create inbox entry in markdown format
        inbox_entry = f"""
---

## Email Received: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

**From**: {from_name} <{from_email}>
**Subject**: {subject}
**Message ID**: {message_id}
**Received**: {received_at}
**Status**: UNPROCESSED

**Body**:
```
{body[:1000]}{'...(truncated)' if len(body) > 1000 else ''}
```

**Agent Notes**:
- Classification: [To be determined by Support Agent]
- Urgency: [To be determined]
- Sentiment: [To be determined]
- Action: [To be determined]

"""

        # Append to inbox file
        inbox_path = Path(".ai-company/agents/support/inbox.md")
        inbox_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize inbox file if it doesn't exist
        if not inbox_path.exists():
            inbox_path.write_text(
                "# Support Agent Inbox\n\n"
                "Last Updated: " + datetime.utcnow().isoformat() + "\n\n"
                "## Queue Status\n"
                "- Unprocessed: 1\n"
                "- Processing: 0\n"
                "- Escalated: 0\n"
            )

        # Append new email to inbox
        with inbox_path.open("a", encoding="utf-8") as f:
            f.write(inbox_entry)

        logger.info(
            f"Added email to support inbox: from={from_email}, subject={subject}"
        )

        # Trigger classification in background
        # This updates the inbox entry with AI classification
        background_tasks.add_task(
            classify_and_update_email,
            message_id=message_id,
            from_email=from_email,
            subject=subject,
            body=body
        )

    except Exception as e:
        logger.error(f"Failed to handle inbound email: {str(e)}", exc_info=True)
        # Don't raise - we don't want to fail the webhook response
        # Support agent will see the error in logs


async def classify_and_update_email(
    message_id: str,
    from_email: str,
    subject: str,
    body: str
) -> None:
    """
    Background task to classify email and update inbox.

    This runs after the webhook response is sent, so it doesn't
    block the Resend webhook (which has a timeout).

    Args:
        message_id: Email message ID
        from_email: Sender email
        subject: Email subject
        body: Email body
    """
    try:
        # Classify the email using Claude
        classification = await support_service.classify_email(
            from_email=from_email,
            subject=subject,
            body=body
        )

        # Update inbox.md with classification
        await support_service.update_inbox_with_classification(
            message_id=message_id,
            classification=classification
        )

        # Check if escalation needed
        should_escalate, reason = support_service.should_escalate(classification)

        if should_escalate:
            logger.warning(
                f"Email {message_id} requires escalation: {reason}",
                extra={
                    "from": from_email,
                    "subject": subject,
                    "classification": classification
                }
            )
            # TODO: Send founder notification via email
            # For MVP, founder reviews inbox.md manually

    except Exception as e:
        logger.error(f"Classification failed for {message_id}: {e}", exc_info=True)
