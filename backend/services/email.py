"""
Email service for Quoted using Resend.
Handles all transactional emails with branded dark premium design.
"""

import re
from typing import Optional, Dict, Any
import resend
import asyncio
from functools import partial
from datetime import datetime

from ..config import settings
from .logging import get_email_logger

logger = get_email_logger()


def format_phone_number(phone: Optional[str]) -> str:
    """
    Format a phone number to a clean (XXX) XXX-XXXX format.

    Handles various input formats:
    - 5551234567 -> (555) 123-4567
    - 15551234567 -> (555) 123-4567
    - +15551234567 -> (555) 123-4567
    - 555-123-4567 -> (555) 123-4567
    - (555) 123-4567 -> (555) 123-4567 (already formatted)

    Returns "N/A" if phone is None/empty or doesn't contain enough digits.
    """
    if not phone:
        return "N/A"

    # Extract only digits
    digits = re.sub(r'\D', '', phone)

    # Handle country code (1 for US)
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]

    # Format as (XXX) XXX-XXXX for 10-digit numbers
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    # If not 10 digits, return original (cleaned) or N/A
    if digits:
        return phone.strip()  # Return original if we can't parse it
    return "N/A"


# Initialize Resend with API key
resend.api_key = settings.resend_api_key

# Validate API key is configured
if not settings.resend_api_key or settings.resend_api_key == "":
    import warnings
    warnings.warn(
        "RESEND_API_KEY not configured. Email sending will fail. "
        "Set RESEND_API_KEY in your .env file."
    )


class EmailService:
    """Service for sending transactional emails via Resend."""

    FROM_EMAIL = "Quoted <hello@quoted.it.com>"

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
                <a href="https://quoted.it.com/terms">Terms</a> •
                <a href="https://quoted.it.com/privacy">Privacy</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        body: str,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generic email sending method for any HTML content.
        Used by follow-up service and other features that generate custom emails.
        (P0-05 fix)

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: HTML body content (will be wrapped in base template)
            reply_to: Optional reply-to email address

        Returns:
            Resend API response
        """
        html = EmailService._get_base_template().format(content=body)

        try:
            email_params = {
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": subject,
                "html": html,
            }
            if reply_to:
                email_params["reply_to"] = reply_to

            # Use run_in_executor to avoid blocking event loop (P1-04 pattern)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(resend.Emails.send, email_params)
            )
            logger.info(f"Sent email to {to_email}: {subject}")
            return response
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {subject}", exc_info=True)
            raise

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

            <a href="https://quoted.it.com/app" class="button">Start Quoting</a>

            <p class="muted">Your 7-day trial starts now. No credit card required.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": f"Welcome to Quoted, {name}",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send welcome email to {to_email}", exc_info=True)
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

            <a href="https://quoted.it.com/app" class="button">Continue Quoting</a>

            <p class="muted">We'll send you a reminder before your trial ends.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Your Quoted trial has started",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send trial starting email to {to_email}", exc_info=True)
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

            <a href="https://quoted.it.com/app?upgrade=true" class="button">Choose Your Plan</a>

            <p class="muted">Cancel anytime. No questions asked.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": f"Your trial ends in {days_left} days",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send trial ending reminder to {to_email}", exc_info=True)
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

            <a href="https://quoted.it.com/app" class="button">Go to Dashboard</a>

            <p class="muted">Need help? Reply to this email anytime.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Your Quoted subscription is active",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send subscription confirmation to {to_email}", exc_info=True)
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

            <a href="https://quoted.it.com/app?billing=true" class="button">Update Payment Method</a>

            <p class="muted">Questions? Reply to this email and we'll help sort it out.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Payment failed - action required",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send payment failed notification to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_quote_email(
        to_email: str,
        contractor_name: str,
        contractor_phone: str,
        customer_name: Optional[str],
        job_description: str,
        total: float,
        message: Optional[str] = None,
        pdf_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send quote via email to customer (GROWTH-003).

        Args:
            to_email: Customer's email address
            contractor_name: Name of the contractor/business
            contractor_phone: Contractor's phone number
            customer_name: Customer's name (optional)
            job_description: Brief job description
            total: Quote total amount
            message: Optional personal message from contractor
            pdf_path: Optional path to PDF attachment

        Returns:
            Resend API response
        """
        greeting = f"Hi {customer_name}" if customer_name else "Hello"
        personal_msg = f"<p>{message}</p>" if message else ""

        # Format the total amount and phone number
        formatted_total = f"${total:,.2f}"
        formatted_phone = format_phone_number(contractor_phone)

        content = f"""
            <h1>Quote from {contractor_name}</h1>

            <p>{greeting},</p>

            <p>Thank you for your interest. Here's your quote:</p>

            {personal_msg}

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #a0a0a0; font-size: 13px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Project
                </div>
                <div style="color: #e0e0e0; font-size: 16px; margin-bottom: 16px;">
                    {job_description}
                </div>
                <div style="color: #a0a0a0; font-size: 13px; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Total Investment
                </div>
                <div class="stat-value" style="font-family: 'Playfair Display', Georgia, serif; font-size: 32px; font-weight: 600; color: #ffffff;">
                    {formatted_total}
                </div>
            </div>

            <p>Please review the attached PDF for complete details.</p>

            <p>Questions? Give me a call at <strong>{formatted_phone}</strong></p>

            <p class="muted" style="margin-top: 32px; padding-top: 24px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                This quote was generated with Quoted - Voice-to-quote for contractors.<br>
                <a href="https://quoted.it.com" style="color: #a0a0a0;">Learn more</a>
            </p>
        """

        # Escape curly braces in content to prevent format() from interpreting them
        # This fixes the '\n margin' error when job_description contains CSS-like syntax
        content = content.replace('{', '{{').replace('}', '}}')

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            email_data = {
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": f"Quote from {contractor_name}",
                "html": html,
            }

            # Attach PDF if provided
            if pdf_path:
                import base64
                with open(pdf_path, "rb") as f:
                    pdf_content = base64.b64encode(f.read()).decode()
                    email_data["attachments"] = [{
                        "filename": "quote.pdf",
                        "content": pdf_content,
                    }]

            # Resend SDK is synchronous, so run it in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(resend.Emails.send, email_data)
            )

            logger.info(f"Quote email sent successfully to {to_email}")
            return response
        except Exception as e:
            logger.error(f"Failed to send quote email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_post_first_quote_email(
        to_email: str,
        contractor_name: str,
        quote_id: str
    ) -> Dict[str, Any]:
        """
        Send congratulations email after first quote (Day 1).
        Part of RETAIN-001 engagement series.

        Args:
            to_email: Recipient email address
            contractor_name: Name of the contractor/business
            quote_id: ID of the first quote generated

        Returns:
            Resend API response
        """
        content = f"""
            <h1>Your first quote is ready! 🎉</h1>

            <p>Congratulations, {contractor_name}! You just created your first quote with Quoted.</p>

            <p>Here's a quick tip to help you get even more from the platform:</p>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 12px;">
                    💡 Pro Tip: Edit Anytime
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6;">
                    Your quotes aren't set in stone. You can edit pricing, add notes, or adjust details before sending to customers.
                    Just go to "My Quotes" and click any quote to refine it.
                </div>
            </div>

            <a href="https://quoted.it.com/app" class="button">Generate Another Quote</a>

            <p class="muted" style="margin-top: 32px; padding-top: 24px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                <strong>Love Quoted? Spread the word!</strong><br>
                Share your referral link and earn rewards when other contractors join.
                <a href="https://quoted.it.com/app?tab=referral" style="color: #a0a0a0;">Get your referral code</a>
            </p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Your first quote is ready! 🎉",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send post-first-quote email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_pro_tips_email(
        to_email: str,
        contractor_name: str
    ) -> Dict[str, Any]:
        """
        Send pro tips email (Day 3).
        Part of RETAIN-001 engagement series.

        Args:
            to_email: Recipient email address
            contractor_name: Name of the contractor/business

        Returns:
            Resend API response
        """
        content = f"""
            <h1>Pro tip: Rush job pricing in Quoted</h1>

            <p>Hey {contractor_name},</p>

            <p>We wanted to share a couple pro tips to help you quote smarter:</p>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 12px;">
                    ⚡ Handling Rush Jobs
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6; margin-bottom: 16px;">
                    When a customer needs it fast, mention "rush" or "ASAP" in your voice note. Quoted will adjust pricing automatically.
                    Standard rush markup: 15-25% depending on timeline.
                </div>
            </div>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 12px;">
                    📊 Material Markup Best Practices
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6;">
                    Industry standard: 10-20% markup on materials for handling/warranty.
                    Quoted learns your markup preferences over time as you edit quotes, so your pricing gets smarter with every job.
                </div>
            </div>

            <a href="https://quoted.it.com/app" class="button">Create a Quote</a>

            <p class="muted" style="margin-top: 32px; padding-top: 24px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                <strong>Know other contractors who'd love this?</strong><br>
                Share your referral link and we'll hook you both up with rewards.
                <a href="https://quoted.it.com/app?tab=referral" style="color: #a0a0a0;">Get your referral code</a>
            </p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Pro tip: Rush job pricing in Quoted",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send pro tips email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_feature_reminder_email(
        to_email: str,
        contractor_name: str
    ) -> Dict[str, Any]:
        """
        Send feature reminder email (Day 5).
        Part of RETAIN-001 engagement series.

        Args:
            to_email: Recipient email address
            contractor_name: Name of the contractor/business

        Returns:
            Resend API response
        """
        content = f"""
            <h1>Did you know? Edit quotes anytime</h1>

            <p>Hey {contractor_name},</p>

            <p>Just a quick reminder about two powerful features you might not be using yet:</p>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 12px;">
                    ✏️ Quote Editing
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6;">
                    Every quote you generate can be edited before sending. Adjust pricing, add notes, tweak line items—whatever you need.
                    Go to "My Quotes" and click any quote to make changes.
                </div>
            </div>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 12px;">
                    🧠 Pricing Brain Learning
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6;">
                    Every time you edit a quote, Quoted learns from it. Your Pricing Brain adapts to YOUR style—rush markups, material preferences, labor rates.
                    The more you use it, the smarter it gets.
                </div>
            </div>

            <a href="https://quoted.it.com/app?tab=pricing-brain" class="button">Check Your Pricing Brain</a>

            <p class="muted">Want to see what Quoted has learned about your pricing style? Check your Pricing Brain dashboard.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Did you know? Edit quotes anytime",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send feature reminder email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_milestone_email(
        to_email: str,
        contractor_name: str,
        quote_count: int,
        referral_code: str
    ) -> Dict[str, Any]:
        """
        Send milestone celebration email (Day 10).
        Part of RETAIN-001 engagement series.

        Args:
            to_email: Recipient email address
            contractor_name: Name of the contractor/business
            quote_count: Number of quotes generated
            referral_code: User's referral code

        Returns:
            Resend API response
        """
        content = f"""
            <h1>You've generated {quote_count} quotes! 📊</h1>

            <p>Amazing work, {contractor_name}!</p>

            <p>You've created {quote_count} quote{"s" if quote_count != 1 else ""} with Quoted. That's {quote_count} potential jobs that you quoted faster and more professionally.</p>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">{quote_count}</div>
                    <div class="stat-label">Total Quotes</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">⚡</div>
                    <div class="stat-label">Getting Smarter</div>
                </div>
            </div>

            <p>Your Pricing Brain is learning fast. With {quote_count} quote{"s" if quote_count != 1 else ""} under its belt, it's already adapting to your pricing style.</p>

            <a href="https://quoted.it.com/app" class="button">Keep the Momentum Going</a>

            <div style="background-color: #1a1a1a; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 24px; margin: 32px 0;">
                <div style="color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 12px;">
                    💰 Share the Love, Earn Rewards
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6; margin-bottom: 16px;">
                    Know contractors who waste time on quotes? Share your referral code and you'll both get rewarded when they sign up.
                </div>
                <div style="background-color: #0a0a0a; border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 4px; padding: 16px; text-align: center; font-family: 'Courier New', monospace; font-size: 20px; font-weight: 600; color: #ffffff; letter-spacing: 2px;">
                    {referral_code}
                </div>
                <div style="margin-top: 16px; text-align: center;">
                    <a href="https://quoted.it.com/app?tab=referral" style="color: #a0a0a0; font-size: 14px;">View your referral dashboard →</a>
                </div>
            </div>

            <p class="muted">Questions or feedback? Hit reply—we read every message.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": f"You've generated {quote_count} quotes! 📊",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send milestone email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_check_in_email(
        to_email: str,
        contractor_name: str
    ) -> Dict[str, Any]:
        """
        Send Day 7 check-in email for inactive users.
        Part of RETAIN-002 dormancy re-engagement series.

        Args:
            to_email: Recipient email address
            contractor_name: Name of the contractor/business

        Returns:
            Resend API response
        """
        content = f"""
            <h1>Quick check-in—everything okay?</h1>

            <p>Hey {contractor_name},</p>

            <p>We noticed you haven't created a quote in a little while. Just wanted to check in and make sure everything's going smoothly.</p>

            <p>Sometimes contractors get stuck or have questions about the platform. If that's you, we're here to help. Just hit reply to this email.</p>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 12px;">
                    💡 Quick Tip: Speed Up Job Walks
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6;">
                    Use Quoted during job walks to quote on the spot. Just record a quick voice note while you're there, and you can send a professional quote before you leave.
                    Customers love the fast turnaround.
                </div>
            </div>

            <a href="https://quoted.it.com/app" class="button">Generate a Quote</a>

            <p class="muted">Your pricing data is still here waiting for you whenever you're ready.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "Quick check-in—everything okay with Quoted?",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send check-in email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_improvements_email(
        to_email: str,
        contractor_name: str
    ) -> Dict[str, Any]:
        """
        Send Day 14 improvements email for inactive users.
        Part of RETAIN-002 dormancy re-engagement series.

        Args:
            to_email: Recipient email address
            contractor_name: Name of the contractor/business

        Returns:
            Resend API response
        """
        content = f"""
            <h1>We've made some improvements</h1>

            <p>Hey {contractor_name},</p>

            <p>While you've been away, we've been busy improving Quoted. Here are a few updates you might like:</p>

            <ul class="feature-list">
                <li><strong>Smarter Pricing Brain</strong> - Now learns faster from your edits and adapts to seasonal pricing changes</li>
                <li><strong>Faster Quote Generation</strong> - We cut processing time in half—quotes now generate in seconds, not minutes</li>
                <li><strong>Enhanced PDF Exports</strong> - More professional layouts with better mobile viewing</li>
            </ul>

            <div class="stat-box" style="margin: 24px 0; background-color: #1a1a1a; border: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="color: #a0a0a0; font-size: 13px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Your Data is Safe
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6;">
                    All your pricing data and quote history is still here waiting. Pick up right where you left off.
                </div>
            </div>

            <a href="https://quoted.it.com/app" class="button">Come Back and Try It</a>

            <p class="muted" style="margin-top: 32px; padding-top: 24px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                <strong>Know other contractors?</strong><br>
                Share your referral link and earn rewards when they join.
                <a href="https://quoted.it.com/app?tab=referral" style="color: #a0a0a0;">Get your referral code</a>
            </p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "We've made some improvements you might like",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send improvements email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_win_back_email(
        to_email: str,
        contractor_name: str
    ) -> Dict[str, Any]:
        """
        Send Day 30 win-back email for inactive users.
        Part of RETAIN-002 dormancy re-engagement series.

        Args:
            to_email: Recipient email address
            contractor_name: Name of the contractor/business

        Returns:
            Resend API response
        """
        content = f"""
            <h1>We miss you!</h1>

            <p>Hey {contractor_name},</p>

            <p>It's been about a month since we've seen you on Quoted. We genuinely miss having you as part of our community.</p>

            <p>We'd love to know what would bring you back. Was there something that didn't work for you? A feature you needed? Just hit reply and let us know—we read every message.</p>

            <div class="stat-box" style="margin: 24px 0; background-color: #1a1a1a; border: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 12px;">
                    🎁 Special Welcome Back Offer
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6; margin-bottom: 12px;">
                    If you'd like to give Quoted another shot, we'll extend your trial by 7 days—no strings attached. Just reply to this email and we'll set it up.
                </div>
                <div style="color: #a0a0a0; font-size: 13px;">
                    Offer expires in 7 days
                </div>
            </div>

            <a href="https://quoted.it.com/app" class="button">Reactivate My Account</a>

            <p style="margin-top: 32px; color: #e0e0e0;">Whether you come back or not, thanks for giving Quoted a try. We wish you all the best with your business.</p>

            <p class="muted" style="margin-top: 16px;">
                If you don't want to receive these emails anymore, you can <a href="https://quoted.it.com/unsubscribe" style="color: #a0a0a0;">unsubscribe here</a>.
            </p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            response = resend.Emails.send({
                "from": EmailService.FROM_EMAIL,
                "to": to_email,
                "subject": "We miss you! Here's something special",
                "html": html,
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send win-back email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_task_reminder_email(
        to_email: str,
        contractor_name: str,
        task_title: str,
        task_description: Optional[str],
        due_date: Optional[datetime],
        customer_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send task reminder notification (Wave 3 - Background Jobs).

        Args:
            to_email: Recipient email address
            contractor_name: Name of the contractor/business
            task_title: Title of the task
            task_description: Optional task description
            due_date: Optional due date for the task
            customer_name: Optional related customer name

        Returns:
            Resend API response
        """
        due_info = ""
        if due_date:
            due_info = f"""
                <div class="stat-box" style="margin: 16px 0;">
                    <div style="color: #a0a0a0; font-size: 13px; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">
                        Due Date
                    </div>
                    <div style="color: #ffffff; font-size: 18px; font-weight: 600;">
                        {due_date.strftime('%B %d, %Y')}
                    </div>
                </div>
            """

        customer_info = ""
        if customer_name:
            customer_info = f"""
                <div style="color: #a0a0a0; font-size: 14px; margin-bottom: 8px;">
                    Related to: <strong style="color: #e0e0e0;">{customer_name}</strong>
                </div>
            """

        description_html = ""
        if task_description:
            description_html = f"""
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6; margin: 16px 0; padding: 16px; background-color: #1a1a1a; border-radius: 8px;">
                    {task_description}
                </div>
            """

        content = f"""
            <h1>Task Reminder ⏰</h1>

            <p>Hey {contractor_name},</p>

            <p>Just a friendly reminder about this task:</p>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 20px; font-weight: 600; margin-bottom: 12px;">
                    {task_title}
                </div>
                {customer_info}
                {description_html}
            </div>

            {due_info}

            <a href="https://quoted.it.com/app?tab=tasks" class="button">View My Tasks</a>

            <p class="muted">You can manage your task reminders in the Tasks section of your dashboard.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(resend.Emails.send, {
                    "from": EmailService.FROM_EMAIL,
                    "to": to_email,
                    "subject": f"⏰ Reminder: {task_title}",
                    "html": html,
                })
            )
            logger.info(f"Task reminder email sent successfully to {to_email}")
            return response
        except Exception as e:
            logger.error(f"Failed to send task reminder email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_quote_first_view_email(
        to_email: str,
        contractor_name: str,
        customer_name: Optional[str],
        quote_total: float,
        quote_token: str
    ) -> Dict[str, Any]:
        """
        Send notification when a quote is viewed for the first time (Wave 3).

        Args:
            to_email: Contractor's email address
            contractor_name: Name of the contractor/business
            customer_name: Customer's name who viewed the quote
            quote_total: Quote total amount
            quote_token: Token for the shared quote link

        Returns:
            Resend API response
        """
        customer_display = customer_name if customer_name else "Your customer"
        formatted_total = f"${quote_total:,.2f}"

        content = f"""
            <h1>Your quote was just viewed! 👀</h1>

            <p>Hey {contractor_name},</p>

            <p><strong>{customer_display}</strong> just opened and viewed your quote.</p>

            <div class="stats-grid" style="margin: 24px 0;">
                <div class="stat-box">
                    <div class="stat-value">{formatted_total}</div>
                    <div class="stat-label">Quote Total</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">Just Now</div>
                    <div class="stat-label">First Viewed</div>
                </div>
            </div>

            <p>This is a great sign! They're actively reviewing your proposal. Consider following up if you don't hear back soon.</p>

            <a href="https://quoted.it.com/app" class="button">View Quote Details</a>

            <p class="muted" style="margin-top: 24px;">
                <a href="https://quoted.it.com/shared/{quote_token}" style="color: #a0a0a0;">View the quote as your customer sees it →</a>
            </p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(resend.Emails.send, {
                    "from": EmailService.FROM_EMAIL,
                    "to": to_email,
                    "subject": f"👀 {customer_display} just viewed your quote!",
                    "html": html,
                })
            )
            logger.info(f"Quote first-view email sent successfully to {to_email}")
            return response
        except Exception as e:
            logger.error(f"Failed to send quote first-view email to {to_email}", exc_info=True)
            raise

    @staticmethod
    async def send_invoice_email(
        to_email: str,
        contractor_name: str,
        invoice_number: str,
        total: float,
        due_date: Optional[str] = None,
        share_url: Optional[str] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send invoice via email to customer (DISC-071).

        Args:
            to_email: Customer's email address
            contractor_name: Name of the contractor/business
            invoice_number: Invoice number (e.g., INV-0001)
            total: Invoice total amount
            due_date: Optional due date string
            share_url: URL to view invoice online
            message: Optional personal message from contractor

        Returns:
            Resend API response
        """
        formatted_total = f"${total:,.2f}"
        personal_msg = f"<p>{message}</p>" if message else ""
        due_info = f"<p><strong>Due:</strong> {due_date}</p>" if due_date else ""

        content = f"""
            <h1>Invoice from {contractor_name}</h1>

            <p>Hello,</p>

            <p>You have received an invoice from {contractor_name}.</p>

            {personal_msg}

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #a0a0a0; font-size: 13px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Invoice #{invoice_number}
                </div>
                <div class="stat-value" style="font-family: 'Playfair Display', Georgia, serif; font-size: 32px; font-weight: 600; color: #ffffff; margin-bottom: 12px;">
                    {formatted_total}
                </div>
                {due_info}
            </div>

            <a href="{share_url}" class="button">View Invoice</a>

            <p class="muted" style="margin-top: 32px;">Thank you for your business!</p>

            <p class="muted" style="padding-top: 24px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                This invoice was sent via Quoted.<br>
                <a href="https://quoted.it.com" style="color: #a0a0a0;">Learn more</a>
            </p>
        """

        # Escape curly braces in content to prevent format() issues
        content = content.replace('{', '{{').replace('}', '}}')
        html = EmailService._get_base_template().replace('{content}', content)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(resend.Emails.send, {
                    "from": EmailService.FROM_EMAIL,
                    "to": to_email,
                    "subject": f"Invoice {invoice_number} from {contractor_name}",
                    "html": html,
                })
            )
            logger.info(f"Invoice email sent successfully to {to_email}")
            return response
        except Exception as e:
            logger.error(f"Failed to send invoice email to {to_email}", exc_info=True)
            raise

    # =========================================================================
    # Founder Notifications (DISC-128)
    # Internal notifications for signups and demo usage
    # =========================================================================

    @staticmethod
    async def send_founder_signup_notification(
        user_email: str,
        business_name: str,
        owner_name: Optional[str],
        primary_trade: Optional[str],
        referral_code: Optional[str] = None,
        used_referral: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send notification to founder when a new user signs up (DISC-128).

        Args:
            user_email: New user's email address
            business_name: Name of the business
            owner_name: Owner's name
            primary_trade: Primary trade/category
            referral_code: New user's referral code
            used_referral: Referral code they used (if any)

        Returns:
            Resend API response
        """
        referral_info = ""
        if used_referral:
            referral_info = f"""
                <div style="color: #22c55e; font-size: 14px; margin-top: 12px;">
                    🎉 Used referral code: <strong>{used_referral}</strong>
                </div>
            """

        content = f"""
            <h1>🎉 New Signup!</h1>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 20px; font-weight: 600; margin-bottom: 16px;">
                    {business_name}
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.8;">
                    <strong>Owner:</strong> {owner_name or 'Not provided'}<br>
                    <strong>Email:</strong> {user_email}<br>
                    <strong>Trade:</strong> {primary_trade or 'Not specified'}<br>
                    <strong>Their Referral Code:</strong> {referral_code or 'None'}
                </div>
                {referral_info}
            </div>

            <p class="muted">This is an automated notification from Quoted.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(resend.Emails.send, {
                    "from": EmailService.FROM_EMAIL,
                    "to": settings.founder_email,
                    "subject": f"[Quoted] New Signup: {business_name}",
                    "html": html,
                    "text": f"New Signup: {business_name}\n\nOwner: {owner_name or 'Not provided'}\nEmail: {user_email}\nTrade: {primary_trade or 'Not specified'}\n\nThis is an automated notification from Quoted.",
                })
            )
            logger.info(f"Founder signup notification sent for {user_email}")
            return response
        except Exception as e:
            logger.error(f"Failed to send founder signup notification for {user_email}", exc_info=True)
            raise

    @staticmethod
    async def send_founder_demo_notification(
        job_description: str,
        quote_total: float,
        line_item_count: int,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send notification to founder when demo quote is generated (DISC-128).

        Args:
            job_description: The job description used
            quote_total: Generated quote total
            line_item_count: Number of line items
            ip_address: Visitor's IP address (optional)

        Returns:
            Resend API response
        """
        formatted_total = f"${quote_total:,.2f}"
        ip_info = f"<br><strong>IP:</strong> {ip_address}" if ip_address else ""

        # Truncate long job descriptions
        job_display = job_description[:200] + "..." if len(job_description) > 200 else job_description

        content = f"""
            <h1>👀 Demo Quote Generated</h1>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #a0a0a0; font-size: 13px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Job Description
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.6; margin-bottom: 16px;">
                    {job_display}
                </div>
            </div>

            <div class="stats-grid" style="margin: 24px 0;">
                <div class="stat-box">
                    <div class="stat-value">{formatted_total}</div>
                    <div class="stat-label">Quote Total</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{line_item_count}</div>
                    <div class="stat-label">Line Items</div>
                </div>
            </div>

            <p class="muted" style="font-size: 13px;">
                Visitor info{ip_info}
            </p>

            <p class="muted">This is an automated notification from Quoted demo page.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(resend.Emails.send, {
                    "from": EmailService.FROM_EMAIL,
                    "to": settings.founder_email,
                    "subject": f"[Quoted] Demo: {formatted_total} quote generated",
                    "html": html,
                    "text": f"Demo Quote Generated\n\nJob: {job_display}\nTotal: {formatted_total}\nLine Items: {line_item_count}\nIP: {ip_address or 'Unknown'}\n\nThis is an automated notification from Quoted.",
                })
            )
            logger.info(f"Founder demo notification sent for {formatted_total} quote")
            return response
        except Exception as e:
            logger.error(f"Failed to send founder demo notification", exc_info=True)
            raise

    @staticmethod
    async def send_founder_quote_notification(
        business_name: str,
        user_email: str,
        quote_total: float,
        customer_name: Optional[str],
        job_type: Optional[str],
        line_item_count: int
    ) -> Dict[str, Any]:
        """
        Send notification to founder when a real user creates a quote (DISC-146).

        Args:
            business_name: User's business name
            user_email: User's email address
            quote_total: Quote total amount
            customer_name: Customer name on the quote
            job_type: Type of job
            line_item_count: Number of line items

        Returns:
            Resend API response
        """
        formatted_total = f"${quote_total:,.2f}"

        content = f"""
            <h1>Quote Created</h1>

            <div class="stat-box" style="margin: 24px 0;">
                <div style="color: #ffffff; font-size: 20px; font-weight: 600; margin-bottom: 16px;">
                    {business_name}
                </div>
                <div style="color: #e0e0e0; font-size: 15px; line-height: 1.8;">
                    <strong>For:</strong> {customer_name or 'Not specified'}<br>
                    <strong>Job:</strong> {job_type or 'Not specified'}<br>
                </div>
            </div>

            <div class="stats-grid" style="margin: 24px 0;">
                <div class="stat-box">
                    <div class="stat-value">{formatted_total}</div>
                    <div class="stat-label">Quote Total</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{line_item_count}</div>
                    <div class="stat-label">Line Items</div>
                </div>
            </div>

            <p class="muted">This is an automated notification from Quoted.</p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        plain_text = f"Quote Created by {business_name}\n\nFor: {customer_name or 'Not specified'}\nJob: {job_type or 'Not specified'}\nTotal: {formatted_total}\nLine Items: {line_item_count}\n\nThis is an automated notification from Quoted."

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(resend.Emails.send, {
                    "from": EmailService.FROM_EMAIL,
                    "to": settings.founder_email,
                    "subject": f"[Quoted] Quote: {formatted_total} by {business_name}",
                    "html": html,
                    "text": plain_text,
                })
            )
            logger.info(f"Founder quote notification sent for {user_email}: {formatted_total}")
            return response
        except Exception as e:
            logger.error(f"Failed to send founder quote notification for {user_email}", exc_info=True)
            raise

    @staticmethod
    async def send_feedback_request(
        to_email: str,
        owner_name: Optional[str],
        business_name: str,
        days_since_signup: int
    ) -> Dict[str, Any]:
        """
        Send thoughtful feedback request to users (DISC-147).

        Part of automated follow-up pulse for gathering product feedback.

        Args:
            to_email: User's email
            owner_name: User's name
            business_name: Business name
            days_since_signup: Days since they signed up

        Returns:
            Resend API response
        """
        greeting = f"Hi {owner_name}," if owner_name else "Hi there,"

        if days_since_signup <= 3:
            # Early feedback - first impressions
            subject = "Quick question about your first Quoted experience"
            body_intro = "You've had a few days to try Quoted, and I'd love to hear your honest first impressions."
            questions = """
                <ul style="color: #e0e0e0; line-height: 2;">
                    <li>Was the setup process smooth?</li>
                    <li>Did the AI understand your pricing well?</li>
                    <li>Any features you wish existed?</li>
                </ul>
            """
        elif days_since_signup <= 7:
            # Week-in feedback - usage patterns
            subject = "How's Quoted working for your workflow?"
            body_intro = "You've been using Quoted for about a week now. I'm curious how it's fitting into your daily workflow."
            questions = """
                <ul style="color: #e0e0e0; line-height: 2;">
                    <li>How many quotes have you generated?</li>
                    <li>Is the AI getting better at your pricing?</li>
                    <li>What's the biggest time-saver so far?</li>
                </ul>
            """
        else:
            # Deeper feedback - value assessment
            subject = "Is Quoted delivering value for you?"
            body_intro = "You've been with us for a few weeks now. I want to make sure Quoted is genuinely helping your business."
            questions = """
                <ul style="color: #e0e0e0; line-height: 2;">
                    <li>Has Quoted changed how you handle quotes?</li>
                    <li>What would make it indispensable?</li>
                    <li>Would you recommend it to other contractors?</li>
                </ul>
            """

        content = f"""
            <p style="color: #e0e0e0; font-size: 16px; line-height: 1.7;">
                {greeting}
            </p>

            <p style="color: #e0e0e0; font-size: 16px; line-height: 1.7;">
                {body_intro}
            </p>

            {questions}

            <p style="color: #e0e0e0; font-size: 16px; line-height: 1.7;">
                Just hit reply - I read every response personally. Your feedback directly shapes what we build next.
            </p>

            <p style="color: #a0a0a0; font-size: 14px; margin-top: 32px;">
                Thanks for being an early user,<br>
                <strong style="color: #ffffff;">Eddie</strong><br>
                Founder, Quoted
            </p>
        """

        html = EmailService._get_base_template().replace('{content}', content)

        plain_text = f"{greeting}\n\n{body_intro}\n\nJust hit reply - I read every response personally.\n\nThanks,\nEddie\nFounder, Quoted"

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(resend.Emails.send, {
                    "from": "Eddie from Quoted <hello@quoted.it.com>",
                    "to": to_email,
                    "reply_to": "eddie@granular.tools",
                    "subject": subject,
                    "html": html,
                    "text": plain_text,
                })
            )
            logger.info(f"Feedback request sent to {to_email} (day {days_since_signup})")
            return response
        except Exception as e:
            logger.error(f"Failed to send feedback request to {to_email}", exc_info=True)
            raise


# Convenience instance
email_service = EmailService()
