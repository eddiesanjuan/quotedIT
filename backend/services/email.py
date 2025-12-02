"""
Email service for Quoted using Resend.
Handles all transactional emails with branded dark premium design.
"""

from typing import Optional, Dict, Any
import resend
from datetime import datetime

from ..config import settings


# Initialize Resend with API key
resend.api_key = settings.resend_api_key


class EmailService:
    """Service for sending transactional emails via Resend."""

    FROM_EMAIL = "Quoted <hello@quoted.it>"

    @staticmethod
    def _get_base_template() -> str:
        """
        Get the base HTML template for all emails.
        Dark premium aesthetic matching the brand.
        """
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

        body {
            margin: 0;
            padding: 0;
            background-color: #0a0a0a;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #ffffff;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #141414;
        }

        .header {
            padding: 40px 40px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .logo {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 28px;
            font-weight: 600;
            font-style: italic;
            color: #ffffff;
            margin: 0;
        }

        .tagline {
            font-size: 13px;
            color: #a0a0a0;
            margin: 8px 0 0;
            letter-spacing: 0.5px;
        }

        .content {
            padding: 40px;
        }

        .content h1 {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 32px;
            font-weight: 600;
            margin: 0 0 24px;
            color: #ffffff;
            line-height: 1.2;
        }

        .content p {
            font-size: 16px;
            line-height: 1.6;
            color: #e0e0e0;
            margin: 0 0 16px;
        }

        .content .muted {
            color: #a0a0a0;
            font-size: 14px;
        }

        .button {
            display: inline-block;
            padding: 14px 32px;
            background-color: #ffffff;
            color: #0a0a0a;
            text-decoration: none;
            font-weight: 600;
            font-size: 15px;
            border-radius: 4px;
            margin: 24px 0;
            transition: opacity 0.2s;
        }

        .button:hover {
            opacity: 0.9;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin: 24px 0;
        }

        .stat-box {
            background-color: #1a1a1a;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 20px;
        }

        .stat-value {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 28px;
            font-weight: 600;
            color: #ffffff;
            margin: 0 0 4px;
        }

        .stat-label {
            font-size: 13px;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .feature-list {
            list-style: none;
            padding: 0;
            margin: 24px 0;
        }

        .feature-list li {
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            color: #e0e0e0;
            font-size: 15px;
        }

        .feature-list li:last-child {
            border-bottom: none;
        }

        .feature-list li:before {
            content: "✓ ";
            color: #a0a0a0;
            font-weight: 600;
            margin-right: 8px;
        }

        .footer {
            padding: 32px 40px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }

        .footer p {
            font-size: 13px;
            color: #666666;
            margin: 8px 0;
        }

        .footer a {
            color: #a0a0a0;
            text-decoration: none;
        }

        .footer a:hover {
            color: #ffffff;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">quoted.it</h1>
            <p class="tagline">Qualify faster. Close more.</p>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            <p>&copy; 2025 Quoted. All rights reserved.</p>
            <p>
                <a href="https://quoted.it/terms">Terms</a> •
                <a href="https://quoted.it/privacy">Privacy</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

    @staticmethod
    async def send_welcome_email(
        to_email: str,
        business_name: str,
        owner_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send welcome email after successful registration.

        Args:
            to_email: Recipient email address
            business_name: Name of the business
            owner_name: Optional owner name for personalization

        Returns:
            Resend API response
        """
        name = owner_name if owner_name else business_name

        content = f"""
            <h1>Welcome to Quoted, {name}</h1>

            <p>You're all set up and ready to start turning voice notes into professional quotes.</p>

            <p>Here's what you can do now:</p>

            <ul class="feature-list">
                <li>Record a voice note describing any job</li>
                <li>Get a professional budget quote in seconds</li>
                <li>Edit and send quotes directly to customers</li>
                <li>Watch Quoted learn your pricing style</li>
            </ul>

            <a href="https://quoted.it/app" class="button">Start Quoting</a>

            <p class="muted">Your 7-day trial starts now. No credit card required.</p>
        """

        html = EmailService._get_base_template().format(content=content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": f"Welcome to Quoted, {name}",
                "html": html,
            })
            return response
        except Exception as e:
            print(f"Failed to send welcome email to {to_email}: {e}")
            raise

    @staticmethod
    async def send_trial_starting_email(
        to_email: str,
        business_name: str,
        trial_end_date: str
    ) -> Dict[str, Any]:
        """
        Send email when trial officially starts (first quote generated).

        Args:
            to_email: Recipient email address
            business_name: Name of the business
            trial_end_date: Date when trial ends (formatted string)

        Returns:
            Resend API response
        """
        content = f"""
            <h1>Your Trial Has Started</h1>

            <p>Great! You just generated your first quote. Your 7-day free trial is now active.</p>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">7 Days</div>
                    <div class="stat-label">Trial Period</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{trial_end_date}</div>
                    <div class="stat-label">Ends On</div>
                </div>
            </div>

            <p>During your trial, you have unlimited access to:</p>

            <ul class="feature-list">
                <li>Unlimited voice-to-quote conversions</li>
                <li>AI-powered pricing that learns from you</li>
                <li>Professional PDF quote generation</li>
                <li>Quote history and editing</li>
            </ul>

            <a href="https://quoted.it/app" class="button">Continue Quoting</a>

            <p class="muted">We'll send you a reminder before your trial ends.</p>
        """

        html = EmailService._get_base_template().format(content=content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Your Quoted trial has started",
                "html": html,
            })
            return response
        except Exception as e:
            print(f"Failed to send trial starting email to {to_email}: {e}")
            raise

    @staticmethod
    async def send_trial_ending_reminder(
        to_email: str,
        business_name: str,
        days_left: int,
        quotes_generated: int
    ) -> Dict[str, Any]:
        """
        Send reminder email when trial is ending (typically day 5 of 7).

        Args:
            to_email: Recipient email address
            business_name: Name of the business
            days_left: Number of days remaining in trial
            quotes_generated: Total quotes generated during trial

        Returns:
            Resend API response
        """
        content = f"""
            <h1>Your Trial Ends in {days_left} Days</h1>

            <p>You've generated {quotes_generated} quote{"s" if quotes_generated != 1 else ""} during your trial. Nice work!</p>

            <p>To keep using Quoted after your trial ends, choose a plan:</p>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">$29</div>
                    <div class="stat-label">Per Month</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">Unlimited</div>
                    <div class="stat-label">Quotes</div>
                </div>
            </div>

            <a href="https://quoted.it/app?upgrade=true" class="button">Choose Your Plan</a>

            <p class="muted">Cancel anytime. No questions asked.</p>
        """

        html = EmailService._get_base_template().format(content=content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": f"Your trial ends in {days_left} days",
                "html": html,
            })
            return response
        except Exception as e:
            print(f"Failed to send trial ending reminder to {to_email}: {e}")
            raise

    @staticmethod
    async def send_subscription_confirmation(
        to_email: str,
        business_name: str,
        plan_name: str,
        amount: float,
        billing_date: str
    ) -> Dict[str, Any]:
        """
        Send confirmation email after successful subscription payment.

        Args:
            to_email: Recipient email address
            business_name: Name of the business
            plan_name: Name of the subscribed plan
            amount: Amount charged
            billing_date: Next billing date (formatted string)

        Returns:
            Resend API response
        """
        content = f"""
            <h1>Subscription Confirmed</h1>

            <p>Thanks for subscribing to Quoted! Your payment has been processed.</p>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">{plan_name}</div>
                    <div class="stat-label">Plan</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${amount:.2f}</div>
                    <div class="stat-label">Per Month</div>
                </div>
            </div>

            <p>Your next billing date is {billing_date}.</p>

            <p>You now have unlimited access to:</p>

            <ul class="feature-list">
                <li>Unlimited voice-to-quote conversions</li>
                <li>AI that learns your pricing patterns</li>
                <li>Professional quote PDFs</li>
                <li>Quote history and analytics</li>
                <li>Priority support</li>
            </ul>

            <a href="https://quoted.it/app" class="button">Go to Dashboard</a>

            <p class="muted">Need help? Reply to this email anytime.</p>
        """

        html = EmailService._get_base_template().format(content=content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Your Quoted subscription is active",
                "html": html,
            })
            return response
        except Exception as e:
            print(f"Failed to send subscription confirmation to {to_email}: {e}")
            raise

    @staticmethod
    async def send_payment_failed_notification(
        to_email: str,
        business_name: str,
        retry_date: str
    ) -> Dict[str, Any]:
        """
        Send notification when a payment fails.

        Args:
            to_email: Recipient email address
            business_name: Name of the business
            retry_date: Date when payment will be retried (formatted string)

        Returns:
            Resend API response
        """
        content = f"""
            <h1>Payment Failed</h1>

            <p>We couldn't process your payment for this month's subscription.</p>

            <p>This can happen if:</p>

            <ul class="feature-list">
                <li>Your card has expired</li>
                <li>There are insufficient funds</li>
                <li>Your bank declined the charge</li>
            </ul>

            <p>We'll automatically retry on {retry_date}. To avoid service interruption, please update your payment method.</p>

            <a href="https://quoted.it/app?billing=true" class="button">Update Payment Method</a>

            <p class="muted">Questions? Reply to this email and we'll help sort it out.</p>
        """

        html = EmailService._get_base_template().format(content=content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Payment failed - action required",
                "html": html,
            })
            return response
        except Exception as e:
            print(f"Failed to send payment failed notification to {to_email}: {e}")
            raise


# Convenience instance
email_service = EmailService()
