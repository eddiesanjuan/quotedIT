"""
Tests for Support Agent webhook endpoint (DISC-160).

Tests the Resend webhook endpoint that receives incoming customer emails
and queues them for the Support Agent to process.
"""

import sys
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
from datetime import datetime
from unittest.mock import MagicMock

# Mock database to avoid SQLite pool configuration during test collection
sys.modules['backend.services.database'] = MagicMock()

from backend.main import app
from backend.services.support import support_service


client = TestClient(app)


class TestResendWebhook:
    """Test the Resend webhook endpoint."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clean up inbox.md if it exists
        inbox_path = Path(".ai-company/agents/support/inbox.md")
        if inbox_path.exists():
            inbox_path.unlink()

    def teardown_method(self):
        """Clean up after tests."""
        # Clean up inbox.md
        inbox_path = Path(".ai-company/agents/support/inbox.md")
        if inbox_path.exists():
            inbox_path.unlink()

    def test_webhook_accepts_email_received_event(self):
        """Test that webhook accepts email.received events."""
        payload = {
            "type": "email.received",
            "data": {
                "from": {
                    "email": "customer@example.com",
                    "name": "Test Customer"
                },
                "to": [{
                    "email": "support@quoted.it.com",
                    "name": "Quoted Support"
                }],
                "subject": "Help with my quote",
                "text": "I need help creating a quote for a bathroom remodel.",
                "message_id": "test-msg-123",
                "created_at": datetime.utcnow().isoformat()
            }
        }

        response = client.post("/api/webhooks/resend", json=payload)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["type"] == "email.received"

    def test_webhook_creates_inbox_entry(self):
        """Test that webhook creates an entry in inbox.md."""
        payload = {
            "type": "email.received",
            "data": {
                "from": {
                    "email": "customer@example.com",
                    "name": "Test Customer"
                },
                "to": [{
                    "email": "support@quoted.it.com",
                    "name": "Quoted Support"
                }],
                "subject": "Test Subject",
                "text": "Test body content.",
                "message_id": "test-msg-456",
                "created_at": datetime.utcnow().isoformat()
            }
        }

        response = client.post("/api/webhooks/resend", json=payload)
        assert response.status_code == 200

        # Check that inbox.md was created
        inbox_path = Path(".ai-company/agents/support/inbox.md")
        assert inbox_path.exists()

        # Check content
        inbox_content = inbox_path.read_text()
        assert "Test Customer" in inbox_content
        assert "customer@example.com" in inbox_content
        assert "Test Subject" in inbox_content
        assert "test-msg-456" in inbox_content
        assert "UNPROCESSED" in inbox_content

    def test_webhook_handles_delivered_events(self):
        """Test that webhook handles email.delivered events."""
        payload = {
            "type": "email.delivered",
            "data": {
                "message_id": "outbound-msg-789"
            }
        }

        response = client.post("/api/webhooks/resend", json=payload)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["type"] == "email.delivered"

    def test_webhook_handles_bounced_events(self):
        """Test that webhook handles email.bounced events."""
        payload = {
            "type": "email.bounced",
            "data": {
                "message_id": "bounced-msg-101",
                "email": "invalid@example.com"
            }
        }

        response = client.post("/api/webhooks/resend", json=payload)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["type"] == "email.bounced"

    def test_webhook_handles_complained_events(self):
        """Test that webhook handles email.complained events."""
        payload = {
            "type": "email.complained",
            "data": {
                "message_id": "spam-msg-202",
                "email": "complainer@example.com"
            }
        }

        response = client.post("/api/webhooks/resend", json=payload)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["type"] == "email.complained"

    def test_webhook_rejects_invalid_json(self):
        """Test that webhook rejects invalid JSON payloads."""
        response = client.post(
            "/api/webhooks/resend",
            data="invalid json{",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400
        assert "Invalid JSON" in response.json()["detail"]

    def test_webhook_handles_unknown_event_types(self):
        """Test that webhook gracefully handles unknown event types."""
        payload = {
            "type": "email.unknown_type",
            "data": {}
        }

        response = client.post("/api/webhooks/resend", json=payload)

        # Should succeed (log and continue)
        assert response.status_code == 200
        assert response.json()["type"] == "email.unknown_type"


class TestSupportService:
    """Test the SupportService classification methods."""

    def test_should_escalate_very_negative_sentiment(self):
        """Test that very negative sentiment triggers escalation."""
        classification = {
            "sentiment": -0.6,
            "urgency": "normal",
            "type": "question",
            "confidence": 0.9
        }

        should_escalate, reason = support_service.should_escalate(classification)

        assert should_escalate is True
        assert "Very negative sentiment" in reason

    def test_should_escalate_negative_sentiment(self):
        """Test that negative sentiment triggers escalation."""
        classification = {
            "sentiment": -0.4,
            "urgency": "normal",
            "type": "question",
            "confidence": 0.9
        }

        should_escalate, reason = support_service.should_escalate(classification)

        assert should_escalate is True
        assert "Negative sentiment" in reason

    def test_should_escalate_refund_requests(self):
        """Test that refund requests always escalate."""
        classification = {
            "sentiment": 0.5,
            "urgency": "normal",
            "type": "refund",
            "confidence": 0.9
        }

        should_escalate, reason = support_service.should_escalate(classification)

        assert should_escalate is True
        assert "Refund request" in reason

    def test_should_escalate_critical_urgency(self):
        """Test that critical urgency triggers escalation."""
        classification = {
            "sentiment": 0.0,
            "urgency": "critical",
            "type": "bug_report",
            "confidence": 0.9
        }

        should_escalate, reason = support_service.should_escalate(classification)

        assert should_escalate is True
        assert "Critical urgency" in reason

    def test_should_escalate_low_confidence(self):
        """Test that low confidence triggers escalation."""
        classification = {
            "sentiment": 0.0,
            "urgency": "normal",
            "type": "question",
            "confidence": 0.5
        }

        should_escalate, reason = support_service.should_escalate(classification)

        assert should_escalate is True
        assert "Low confidence" in reason

    def test_should_not_escalate_normal_email(self):
        """Test that normal emails don't trigger escalation."""
        classification = {
            "sentiment": 0.2,
            "urgency": "normal",
            "type": "question",
            "confidence": 0.85
        }

        should_escalate, reason = support_service.should_escalate(classification)

        assert should_escalate is False
        assert "Normal processing" in reason
