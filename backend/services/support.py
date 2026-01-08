"""
Support agent service for automated customer communication handling.

DISC-160: Support Agent Infrastructure

This service provides:
1. Email classification (type, urgency, sentiment)
2. FAQ matching and response drafting
3. Escalation queue management
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

import anthropic

from ..config import settings

logger = logging.getLogger(__name__)


class SupportService:
    """Service for automated support operations."""

    def __init__(self):
        """Initialize Claude API client."""
        if not settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured - support classification disabled")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def classify_email(
        self,
        from_email: str,
        subject: str,
        body: str
    ) -> Dict[str, Any]:
        """
        Classify an incoming support email.

        Uses Claude to analyze the email and determine:
        - Type: question, bug_report, feedback, complaint, refund, other
        - Urgency: critical, high, normal, low
        - Sentiment: -1.0 to 1.0 scale
        - Summary: Brief description of the issue

        Args:
            from_email: Sender email address
            subject: Email subject line
            body: Email body text

        Returns:
            Dict with classification results:
            {
                "type": str,
                "urgency": str,
                "sentiment": float,
                "summary": str,
                "suggested_response": Optional[str],
                "confidence": float
            }
        """
        if not self.client:
            # Fallback classification when API not available
            return {
                "type": "other",
                "urgency": "normal",
                "sentiment": 0.0,
                "summary": subject,
                "suggested_response": None,
                "confidence": 0.0,
                "error": "Claude API not configured"
            }

        try:
            # Build classification prompt
            prompt = f"""Analyze this customer support email and provide structured classification.

From: {from_email}
Subject: {subject}

Body:
{body[:2000]}

Classify the email using these categories:

TYPE (choose one):
- question: Customer asking how to do something
- bug_report: Something isn't working correctly
- feedback: General feedback or feature request
- complaint: Customer is upset or dissatisfied
- refund: Requesting a refund or cancellation
- other: Doesn't fit other categories

URGENCY (choose one):
- critical: Service down, data loss, urgent business need
- high: Blocking work, time-sensitive issue
- normal: Standard inquiry or issue
- low: Nice-to-have, general question

SENTIMENT (scale -1.0 to 1.0):
- 1.0: Very positive, happy customer
- 0.5: Somewhat positive
- 0.0: Neutral
- -0.3: Slightly frustrated
- -0.5: Upset or disappointed
- -1.0: Very angry or hostile

Respond in JSON format:
{{
    "type": "...",
    "urgency": "...",
    "sentiment": 0.0,
    "summary": "One sentence summary of the issue",
    "suggested_response": "Draft response if this matches a common FAQ, or null",
    "confidence": 0.85,
    "reasoning": "Brief explanation of classification"
}}"""

            # Call Claude API
            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            response_text = response.content[0].text.strip()

            # Extract JSON from response (handle code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            classification = json.loads(response_text)

            logger.info(
                f"Classified email: type={classification['type']}, "
                f"urgency={classification['urgency']}, "
                f"sentiment={classification['sentiment']}"
            )

            return classification

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            return {
                "type": "other",
                "urgency": "normal",
                "sentiment": 0.0,
                "summary": subject,
                "suggested_response": None,
                "confidence": 0.0,
                "error": "JSON parse error"
            }
        except Exception as e:
            logger.error(f"Email classification failed: {e}", exc_info=True)
            return {
                "type": "other",
                "urgency": "normal",
                "sentiment": 0.0,
                "summary": subject,
                "suggested_response": None,
                "confidence": 0.0,
                "error": str(e)
            }

    def should_escalate(self, classification: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Determine if an email should be escalated to founder.

        Based on Support Agent spec (AGENT.md):
        - Very negative sentiment (< -0.5): Immediate escalation
        - Negative sentiment (-0.5 to -0.3): Queue for human review
        - Refund requests: Always escalate
        - Critical urgency: Always escalate
        - Low confidence (<0.7): Escalate to be safe

        Args:
            classification: Email classification dict

        Returns:
            Tuple of (should_escalate: bool, reason: str)
        """
        sentiment = classification.get("sentiment", 0.0)
        urgency = classification.get("urgency", "normal")
        email_type = classification.get("type", "other")
        confidence = classification.get("confidence", 0.0)

        # Very negative sentiment - immediate escalation
        if sentiment <= -0.5:
            return True, "Very negative sentiment - immediate founder notification"

        # Negative sentiment - queue for review
        if sentiment < -0.3:
            return True, "Negative sentiment - requires human review"

        # Refund requests always escalate
        if email_type == "refund":
            return True, "Refund request - requires founder approval"

        # Critical urgency always escalates
        if urgency == "critical":
            return True, "Critical urgency - immediate attention needed"

        # Low confidence - escalate to be safe
        if confidence < 0.7:
            return True, f"Low confidence ({confidence:.2f}) - human review recommended"

        # Otherwise, can attempt automated response
        return False, "Normal processing"

    async def update_inbox_with_classification(
        self,
        message_id: str,
        classification: Dict[str, Any]
    ) -> None:
        """
        Update inbox.md with classification results.

        Finds the email entry by message_id and adds classification info.

        Args:
            message_id: Email message ID
            classification: Classification results from classify_email()
        """
        try:
            inbox_path = Path(".ai-company/agents/support/inbox.md")

            if not inbox_path.exists():
                logger.warning("inbox.md does not exist - cannot update classification")
                return

            # Read current inbox
            content = inbox_path.read_text(encoding="utf-8")

            # Find the email entry
            if f"**Message ID**: {message_id}" not in content:
                logger.warning(f"Message ID {message_id} not found in inbox")
                return

            # Build classification text
            classification_text = f"""
**Agent Notes**:
- Classification: {classification['type']}
- Urgency: {classification['urgency']}
- Sentiment: {classification['sentiment']:.2f}
- Summary: {classification['summary']}
- Confidence: {classification.get('confidence', 0.0):.2f}
- Escalate: {self.should_escalate(classification)}
"""

            # Replace placeholder notes with actual classification
            # The webhook creates a placeholder "Agent Notes" section
            content = content.replace(
                "**Agent Notes**:\n- Classification: [To be determined by Support Agent]\n"
                "- Urgency: [To be determined]\n"
                "- Sentiment: [To be determined]\n"
                "- Action: [To be determined]",
                classification_text
            )

            # Write back
            inbox_path.write_text(content, encoding="utf-8")

            logger.info(f"Updated inbox with classification for message {message_id}")

        except Exception as e:
            logger.error(f"Failed to update inbox with classification: {e}", exc_info=True)


# Singleton instance
support_service = SupportService()
