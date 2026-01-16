"""
Webhook endpoints for external services.
Handles incoming events from Resend, and other services.
"""

import base64
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr

from ..config import settings
from ..services.support import support_service

logger = logging.getLogger(__name__)

# Svix signature verification constants
SVIX_TIMESTAMP_TOLERANCE_SECONDS = 300  # 5 minutes tolerance for timestamp drift


def verify_svix_signature(
    payload: bytes,
    svix_id: str,
    svix_timestamp: str,
    svix_signature: str,
    secret: str
) -> bool:
    """
    Verify Svix webhook signature (used by Resend).

    Svix signatures follow this pattern:
    1. Construct signed content: "{svix_id}.{svix_timestamp}.{payload}"
    2. Compute HMAC-SHA256 using the webhook secret (after decoding from base64)
    3. Compare against the signature(s) in the header

    The svix-signature header format is: "v1,<base64_signature>" or
    "v1,<sig1> v1,<sig2>" for multiple signatures (key rotation).

    Args:
        payload: Raw request body bytes
        svix_id: Value of svix-id header
        svix_timestamp: Value of svix-timestamp header
        svix_signature: Value of svix-signature header
        secret: Webhook signing secret (may have "whsec_" prefix)

    Returns:
        True if signature is valid, False otherwise
    """
    # Validate timestamp to prevent replay attacks
    try:
        timestamp_int = int(svix_timestamp)
        current_time = int(time.time())
        if abs(current_time - timestamp_int) > SVIX_TIMESTAMP_TOLERANCE_SECONDS:
            logger.warning(
                f"Svix timestamp too old or in future: {timestamp_int}, current: {current_time}"
            )
            return False
    except ValueError:
        logger.warning(f"Invalid svix-timestamp format: {svix_timestamp}")
        return False

    # Prepare the secret - Svix secrets may have "whsec_" prefix
    # The actual secret is base64 encoded after the prefix
    if secret.startswith("whsec_"):
        secret_bytes = base64.b64decode(secret[6:])
    else:
        # Try to decode as base64, fallback to raw bytes
        try:
            secret_bytes = base64.b64decode(secret)
        except Exception:
            secret_bytes = secret.encode("utf-8")

    # Construct the signed content
    signed_content = f"{svix_id}.{svix_timestamp}.".encode("utf-8") + payload

    # Compute expected signature
    expected_signature = base64.b64encode(
        hmac.new(secret_bytes, signed_content, hashlib.sha256).digest()
    ).decode("utf-8")

    # Parse signatures from header - format: "v1,<sig1> v1,<sig2> ..."
    # Split by space to handle multiple signatures (key rotation)
    signature_parts = svix_signature.split(" ")

    for part in signature_parts:
        if part.startswith("v1,"):
            provided_signature = part[3:]  # Remove "v1," prefix
            if hmac.compare_digest(expected_signature, provided_signature):
                return True

    logger.warning("No valid signature found in svix-signature header")
    return False


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
    - Svix signature verification (cryptographic, not just presence check)
    - Timestamp validation to prevent replay attacks
    - Rate limiting at infrastructure level

    Flow:
    1. Receive and validate webhook payload
    2. Verify Svix signature cryptographically
    3. Append to support agent inbox (.ai-company/agents/support/inbox.md)
    4. Return 200 immediately (async processing)

    Returns:
        Dict with status confirmation
    """
    try:
        # Get raw payload for signature verification (must be done before .json())
        payload_bytes = await request.body()

        # Verify webhook signature if secret is configured
        # Resend uses Svix for webhook signing with these headers:
        # - svix-id: Unique message ID
        # - svix-timestamp: Unix timestamp
        # - svix-signature: HMAC-SHA256 signature
        if settings.resend_webhook_secret:
            svix_id = request.headers.get("svix-id")
            svix_timestamp = request.headers.get("svix-timestamp")
            svix_signature = request.headers.get("svix-signature")

            # All three headers are required for verification
            if not svix_id or not svix_timestamp or not svix_signature:
                logger.warning(
                    f"Resend webhook missing required Svix headers: "
                    f"id={bool(svix_id)}, ts={bool(svix_timestamp)}, sig={bool(svix_signature)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing webhook signature headers"
                )

            # Cryptographically verify the signature
            if not verify_svix_signature(
                payload=payload_bytes,
                svix_id=svix_id,
                svix_timestamp=svix_timestamp,
                svix_signature=svix_signature,
                secret=settings.resend_webhook_secret
            ):
                logger.warning(
                    f"Invalid Resend webhook signature for svix-id={svix_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid webhook signature"
                )

            logger.debug(f"Svix signature verified for webhook {svix_id}")
        else:
            # No secret configured - log warning in production
            if settings.environment == "production":
                logger.warning(
                    "SECURITY: Resend webhook received without signature verification. "
                    "Set RESEND_WEBHOOK_SECRET environment variable to enable verification."
                )

        # Parse the payload
        payload = json.loads(payload_bytes)

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
