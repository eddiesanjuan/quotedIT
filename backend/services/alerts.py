"""
Alerts & Monitoring Service for Quoted (INFRA-010).

Provides centralized alerting and monitoring including:
- Sentry integration for error reporting
- Structured event logging for observability
- Circuit breaker state change alerts
- Business metric alerts
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from ..config import settings

logger = logging.getLogger("quoted.alerts")


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertCategory(Enum):
    """Alert categories for routing."""
    SYSTEM = "system"
    SECURITY = "security"
    PAYMENT = "payment"
    EXTERNAL_SERVICE = "external_service"
    BUSINESS = "business"


@dataclass
class Alert:
    """Structured alert data."""
    title: str
    message: str
    severity: AlertSeverity
    category: AlertCategory
    timestamp: datetime
    context: Dict[str, Any]
    user_id: Optional[str] = None
    contractor_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.timestamp.isoformat() + "Z",
            "context": self.context,
            "user_id": self.user_id,
            "contractor_id": self.contractor_id,
        }


class AlertService:
    """
    Centralized alerting service.

    Sends alerts to:
    - Sentry (errors and critical issues)
    - Structured logs (all alerts)
    - Future: Slack, PagerDuty, etc.
    """

    def __init__(self):
        self._sentry_initialized = False
        self._init_sentry()

    def _init_sentry(self):
        """Initialize Sentry if configured."""
        if settings.sentry_dsn:
            try:
                import sentry_sdk
                self._sentry_initialized = True
            except ImportError:
                logger.warning("Sentry SDK not installed")

    def _send_to_sentry(self, alert: Alert):
        """Send alert to Sentry."""
        if not self._sentry_initialized:
            return

        try:
            import sentry_sdk
            from sentry_sdk import set_context, set_tag, set_user

            # Set context
            set_context("alert", alert.to_dict())

            if alert.user_id:
                set_user({"id": alert.user_id})

            # Set tags for filtering
            set_tag("alert.category", alert.category.value)
            set_tag("alert.severity", alert.severity.value)

            # Capture based on severity
            if alert.severity in (AlertSeverity.ERROR, AlertSeverity.CRITICAL):
                sentry_sdk.capture_message(
                    f"[{alert.severity.value.upper()}] {alert.title}",
                    level="error" if alert.severity == AlertSeverity.ERROR else "fatal",
                )
            elif alert.severity == AlertSeverity.WARNING:
                sentry_sdk.capture_message(
                    f"[WARNING] {alert.title}",
                    level="warning",
                )
        except Exception as e:
            logger.error(f"Failed to send alert to Sentry: {e}")

    def _log_alert(self, alert: Alert):
        """Log alert with structured data."""
        log_data = alert.to_dict()

        if alert.severity == AlertSeverity.CRITICAL:
            logger.critical(alert.message, extra=log_data)
        elif alert.severity == AlertSeverity.ERROR:
            logger.error(alert.message, extra=log_data)
        elif alert.severity == AlertSeverity.WARNING:
            logger.warning(alert.message, extra=log_data)
        else:
            logger.info(alert.message, extra=log_data)

    def send(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        category: AlertCategory = AlertCategory.SYSTEM,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        contractor_id: Optional[str] = None,
    ):
        """Send an alert."""
        alert = Alert(
            title=title,
            message=message,
            severity=severity,
            category=category,
            timestamp=datetime.utcnow(),
            context=context or {},
            user_id=user_id,
            contractor_id=contractor_id,
        )

        # Always log
        self._log_alert(alert)

        # Send to Sentry for warnings and above
        if severity in (AlertSeverity.WARNING, AlertSeverity.ERROR, AlertSeverity.CRITICAL):
            self._send_to_sentry(alert)

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def circuit_breaker_opened(
        self,
        service_name: str,
        failure_count: int,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Alert when a circuit breaker opens."""
        self.send(
            title=f"Circuit Breaker Opened: {service_name}",
            message=f"Circuit breaker for {service_name} opened after {failure_count} failures",
            severity=AlertSeverity.WARNING,
            category=AlertCategory.EXTERNAL_SERVICE,
            context={
                "service": service_name,
                "failure_count": failure_count,
                **(context or {}),
            },
        )

    def circuit_breaker_closed(
        self,
        service_name: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Alert when a circuit breaker closes (recovery)."""
        self.send(
            title=f"Circuit Breaker Closed: {service_name}",
            message=f"Circuit breaker for {service_name} closed - service recovered",
            severity=AlertSeverity.INFO,
            category=AlertCategory.EXTERNAL_SERVICE,
            context={
                "service": service_name,
                **(context or {}),
            },
        )

    def payment_failed(
        self,
        error: str,
        contractor_id: Optional[str] = None,
        amount_cents: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Alert on payment failure."""
        self.send(
            title="Payment Failed",
            message=f"Payment processing failed: {error}",
            severity=AlertSeverity.ERROR,
            category=AlertCategory.PAYMENT,
            contractor_id=contractor_id,
            context={
                "error": error,
                "amount_cents": amount_cents,
                **(context or {}),
            },
        )

    def subscription_event(
        self,
        event_type: str,
        contractor_id: str,
        plan: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Track subscription events."""
        self.send(
            title=f"Subscription: {event_type}",
            message=f"Subscription event: {event_type} for contractor {contractor_id}",
            severity=AlertSeverity.INFO,
            category=AlertCategory.BUSINESS,
            contractor_id=contractor_id,
            context={
                "event_type": event_type,
                "plan": plan,
                **(context or {}),
            },
        )

    def security_event(
        self,
        event_type: str,
        message: str,
        user_id: Optional[str] = None,
        severity: AlertSeverity = AlertSeverity.WARNING,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Alert on security-related events."""
        self.send(
            title=f"Security: {event_type}",
            message=message,
            severity=severity,
            category=AlertCategory.SECURITY,
            user_id=user_id,
            context={
                "event_type": event_type,
                **(context or {}),
            },
        )

    def external_service_error(
        self,
        service_name: str,
        error: str,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Alert on external service errors."""
        self.send(
            title=f"External Service Error: {service_name}",
            message=f"{service_name} error during {operation or 'operation'}: {error}",
            severity=AlertSeverity.ERROR,
            category=AlertCategory.EXTERNAL_SERVICE,
            context={
                "service": service_name,
                "operation": operation,
                "error": error,
                **(context or {}),
            },
        )

    def quote_generated(
        self,
        contractor_id: str,
        quote_id: str,
        total: float,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Track quote generation for business metrics."""
        self.send(
            title="Quote Generated",
            message=f"Quote {quote_id} generated for ${total:.2f}",
            severity=AlertSeverity.INFO,
            category=AlertCategory.BUSINESS,
            contractor_id=contractor_id,
            context={
                "quote_id": quote_id,
                "total": total,
                **(context or {}),
            },
        )

    def high_error_rate(
        self,
        service_name: str,
        error_rate: float,
        threshold: float,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Alert when error rate exceeds threshold."""
        self.send(
            title=f"High Error Rate: {service_name}",
            message=f"{service_name} error rate {error_rate:.1%} exceeds threshold {threshold:.1%}",
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.SYSTEM,
            context={
                "service": service_name,
                "error_rate": error_rate,
                "threshold": threshold,
                **(context or {}),
            },
        )


# Singleton instance
alert_service = AlertService()
