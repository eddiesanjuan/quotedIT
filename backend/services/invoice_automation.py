"""
Invoice Automation Service for Quoted (INNOV-6).

Automates invoice generation and payment tracking:
- Auto-create invoice when quote is accepted
- Send invoice notification to customer
- Payment reminder scheduling
- Overdue invoice tracking
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .logging import get_logger

logger = get_logger("quoted.invoice_automation")


@dataclass
class InvoiceGenerationResult:
    """Result of auto-generating an invoice."""
    success: bool
    invoice_id: Optional[str]
    invoice_number: Optional[str]
    message: str
    sent_to_customer: bool = False


class InvoiceAutomationService:
    """
    Handles automatic invoice generation and payment tracking.
    """

    # Default days until invoice is due
    DEFAULT_DUE_DAYS = 30

    # Days before due date to send first reminder
    FIRST_REMINDER_DAYS_BEFORE = 7

    # Days after due date to send overdue reminders
    OVERDUE_REMINDER_DAYS = [1, 7, 14, 30]

    @staticmethod
    async def _get_next_invoice_number(db: AsyncSession, contractor_id: str) -> str:
        """Generate the next invoice number for a contractor."""
        from ..models.database import Invoice

        result = await db.execute(
            select(Invoice).where(Invoice.contractor_id == contractor_id)
        )
        count = len(result.scalars().all())
        return f"INV-{count + 1:04d}"

    @staticmethod
    async def auto_generate_from_quote(
        db: AsyncSession,
        quote_id: str,
        send_to_customer: bool = False,
        due_days: int = 30,
    ) -> InvoiceGenerationResult:
        """
        Automatically generate an invoice from an accepted quote.

        Called when a quote is marked as 'won' or 'accepted'.

        Args:
            db: Database session
            quote_id: ID of the quote to convert
            send_to_customer: Whether to send invoice email immediately
            due_days: Days until invoice is due

        Returns:
            InvoiceGenerationResult with invoice details
        """
        from ..models.database import Quote, Invoice, Contractor, ContractorTerms

        # Get the quote
        result = await db.execute(
            select(Quote).where(Quote.id == quote_id)
        )
        quote = result.scalar_one_or_none()

        if not quote:
            return InvoiceGenerationResult(
                success=False,
                invoice_id=None,
                invoice_number=None,
                message="Quote not found"
            )

        # Check if invoice already exists for this quote
        existing_result = await db.execute(
            select(Invoice).where(Invoice.quote_id == quote_id)
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            return InvoiceGenerationResult(
                success=False,
                invoice_id=existing.id,
                invoice_number=existing.invoice_number,
                message="Invoice already exists for this quote"
            )

        # Get contractor and terms
        contractor_result = await db.execute(
            select(Contractor).where(Contractor.id == quote.contractor_id)
        )
        contractor = contractor_result.scalar_one_or_none()

        if not contractor:
            return InvoiceGenerationResult(
                success=False,
                invoice_id=None,
                invoice_number=None,
                message="Contractor not found"
            )

        # Get terms for defaults
        terms_result = await db.execute(
            select(ContractorTerms).where(ContractorTerms.contractor_id == contractor.id)
        )
        terms = terms_result.scalar_one_or_none()

        # Generate invoice number
        invoice_number = await InvoiceAutomationService._get_next_invoice_number(db, contractor.id)

        # Calculate amounts (same as quote)
        subtotal = quote.subtotal or 0
        tax_percent = 0  # Could be configured per contractor
        tax_amount = subtotal * (tax_percent / 100)
        total = quote.total or subtotal + tax_amount

        # Generate dates
        invoice_date = datetime.utcnow()
        due_date = invoice_date + timedelta(days=due_days)

        # Get default terms text
        terms_text = None
        if terms:
            terms_text = f"Payment due within {due_days} days."
            if terms.accepted_payments:
                payments = terms.accepted_payments
                if isinstance(payments, list):
                    terms_text += f" Accepted payments: {', '.join(payments)}."

        # Generate share token
        share_token = secrets.token_urlsafe(24)[:32]

        # Create invoice
        invoice = Invoice(
            contractor_id=contractor.id,
            quote_id=quote.id,
            invoice_number=invoice_number,
            customer_name=quote.customer_name,
            customer_email=quote.customer_email,
            customer_phone=quote.customer_phone,
            customer_address=quote.customer_address,
            description=quote.job_description or quote.job_type,
            line_items=quote.line_items or [],
            subtotal=subtotal,
            tax_percent=tax_percent,
            tax_amount=tax_amount,
            total=total,
            invoice_date=invoice_date,
            due_date=due_date,
            terms_text=terms_text,
            status="draft",
            share_token=share_token,
            auto_generated=True,  # Mark as auto-generated
        )

        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)

        logger.info(
            f"Auto-generated invoice {invoice_number} from quote {quote_id}",
            extra={
                "invoice_id": invoice.id,
                "quote_id": quote_id,
                "contractor_id": contractor.id,
                "total": total,
            }
        )

        # Send to customer if requested
        sent = False
        if send_to_customer and quote.customer_email:
            try:
                sent = await InvoiceAutomationService.send_invoice_email(
                    db=db,
                    invoice_id=invoice.id
                )
            except Exception as e:
                logger.error(f"Failed to send invoice email: {e}")

        return InvoiceGenerationResult(
            success=True,
            invoice_id=invoice.id,
            invoice_number=invoice_number,
            message="Invoice created successfully",
            sent_to_customer=sent
        )

    @staticmethod
    async def send_invoice_email(
        db: AsyncSession,
        invoice_id: str,
    ) -> bool:
        """
        Send invoice notification email to customer.

        Returns True if sent successfully.
        """
        from ..models.database import Invoice, Contractor
        from .email import EmailService

        # Get invoice
        result = await db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        invoice = result.scalar_one_or_none()

        if not invoice or not invoice.customer_email:
            return False

        # Get contractor
        contractor_result = await db.execute(
            select(Contractor).where(Contractor.id == invoice.contractor_id)
        )
        contractor = contractor_result.scalar_one_or_none()

        if not contractor:
            return False

        # Send email
        email_service = EmailService()
        business_name = contractor.business_name or "Your Contractor"

        try:
            await email_service.send_invoice_email(
                to_email=invoice.customer_email,
                customer_name=invoice.customer_name or "Customer",
                business_name=business_name,
                invoice_number=invoice.invoice_number,
                amount=invoice.total,
                due_date=invoice.due_date,
                invoice_link=f"https://quoted.it.com/invoice/{invoice.share_token}",
            )

            # Update invoice status
            invoice.status = "sent"
            invoice.sent_at = datetime.utcnow()
            await db.commit()

            logger.info(f"Sent invoice {invoice.invoice_number} to {invoice.customer_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send invoice email: {e}")
            return False

    @staticmethod
    async def check_payment_reminders(db: AsyncSession) -> int:
        """
        Check for invoices needing payment reminders.

        Returns count of reminders sent.
        """
        from ..models.database import Invoice, Contractor
        from .email import EmailService

        now = datetime.utcnow()
        reminders_sent = 0

        # Find invoices due soon (7 days before)
        reminder_date = now + timedelta(days=InvoiceAutomationService.FIRST_REMINDER_DAYS_BEFORE)

        result = await db.execute(
            select(Invoice)
            .where(
                Invoice.status == "sent",
                Invoice.due_date <= reminder_date,
                Invoice.due_date > now,
                Invoice.reminder_sent.is_(None)  # Haven't sent reminder yet
            )
        )
        due_soon = result.scalars().all()

        email_service = EmailService()

        for invoice in due_soon:
            try:
                # Get contractor
                contractor_result = await db.execute(
                    select(Contractor).where(Contractor.id == invoice.contractor_id)
                )
                contractor = contractor_result.scalar_one_or_none()
                business_name = contractor.business_name if contractor else "Your Contractor"

                if invoice.customer_email:
                    await email_service.send_payment_reminder_email(
                        to_email=invoice.customer_email,
                        customer_name=invoice.customer_name or "Customer",
                        business_name=business_name,
                        invoice_number=invoice.invoice_number,
                        amount=invoice.total,
                        due_date=invoice.due_date,
                        invoice_link=f"https://quoted.it.com/invoice/{invoice.share_token}",
                        is_overdue=False,
                    )

                    invoice.reminder_sent = now
                    invoice.reminder_count = (invoice.reminder_count or 0) + 1
                    reminders_sent += 1

                    logger.info(f"Sent payment reminder for invoice {invoice.invoice_number}")

            except Exception as e:
                logger.error(f"Failed to send reminder for invoice {invoice.id}: {e}")

        # Find overdue invoices
        for days_overdue in InvoiceAutomationService.OVERDUE_REMINDER_DAYS:
            overdue_date = now - timedelta(days=days_overdue)

            result = await db.execute(
                select(Invoice)
                .where(
                    Invoice.status == "sent",
                    Invoice.due_date <= overdue_date,
                    Invoice.due_date > overdue_date - timedelta(days=1),  # Just passed this threshold
                )
            )
            overdue = result.scalars().all()

            for invoice in overdue:
                try:
                    contractor_result = await db.execute(
                        select(Contractor).where(Contractor.id == invoice.contractor_id)
                    )
                    contractor = contractor_result.scalar_one_or_none()
                    business_name = contractor.business_name if contractor else "Your Contractor"

                    if invoice.customer_email:
                        await email_service.send_payment_reminder_email(
                            to_email=invoice.customer_email,
                            customer_name=invoice.customer_name or "Customer",
                            business_name=business_name,
                            invoice_number=invoice.invoice_number,
                            amount=invoice.total,
                            due_date=invoice.due_date,
                            invoice_link=f"https://quoted.it.com/invoice/{invoice.share_token}",
                            is_overdue=True,
                            days_overdue=days_overdue,
                        )

                        invoice.reminder_sent = now
                        invoice.reminder_count = (invoice.reminder_count or 0) + 1
                        invoice.status = "overdue"
                        reminders_sent += 1

                        logger.info(
                            f"Sent overdue reminder ({days_overdue} days) for invoice {invoice.invoice_number}"
                        )

                except Exception as e:
                    logger.error(f"Failed to send overdue reminder for invoice {invoice.id}: {e}")

        await db.commit()
        return reminders_sent

    @staticmethod
    async def get_outstanding_invoices(
        db: AsyncSession,
        contractor_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get all outstanding (unpaid) invoices for a contractor.
        """
        from ..models.database import Invoice

        result = await db.execute(
            select(Invoice)
            .where(
                Invoice.contractor_id == contractor_id,
                Invoice.status.in_(["sent", "overdue", "viewed"])
            )
            .order_by(Invoice.due_date)
        )
        invoices = result.scalars().all()

        now = datetime.utcnow()

        return [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "customer_name": inv.customer_name,
                "total": inv.total,
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
                "status": inv.status,
                "days_until_due": (inv.due_date - now).days if inv.due_date else None,
                "is_overdue": inv.due_date < now if inv.due_date else False,
                "share_token": inv.share_token,
            }
            for inv in invoices
        ]

    @staticmethod
    async def get_contractor_invoice_settings(
        db: AsyncSession,
        contractor_id: str,
    ) -> Dict[str, Any]:
        """
        Get contractor's invoice automation settings.
        """
        from ..models.database import Contractor

        result = await db.execute(
            select(Contractor).where(Contractor.id == contractor_id)
        )
        contractor = result.scalar_one_or_none()

        if not contractor:
            return {
                "auto_generate_invoices": False,
                "auto_send_invoices": False,
                "default_due_days": 30,
                "send_reminders": True,
            }

        # Return settings from contractor model (INNOV-6 fields)
        return {
            "auto_generate_invoices": contractor.auto_generate_invoices or False,
            "auto_send_invoices": contractor.auto_send_invoices or False,
            "default_due_days": contractor.invoice_due_days or 30,
            "send_reminders": contractor.send_invoice_reminders if contractor.send_invoice_reminders is not None else True,
        }


# Singleton instance
invoice_automation = InvoiceAutomationService()
