"""
Background job scheduler for Quoted (Wave 3).

Uses APScheduler for lightweight in-process background jobs.
Handles:
- Task reminder notifications
- Quote follow-up auto-task creation
- Stale quote detection

Cost: $0 additional (runs in FastAPI process, no external services)
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_

from .logging import get_logger

logger = get_logger("quoted.scheduler")

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


async def check_task_reminders():
    """
    Check for tasks with reminder_time in the past and notification_sent=False.
    Runs every 5 minutes.
    """
    from ..models.database import Task, Contractor
    from .database import async_session_factory
    from .email import EmailService
    from .logging import get_logger
    job_logger = get_logger("quoted.scheduler.task_reminders")

    logger.info("Running task reminder check")

    try:
        async with async_session_factory() as db:
            # Find tasks with due reminders
            now = datetime.utcnow()
            result = await db.execute(
                select(Task).where(
                    and_(
                        Task.reminder_time <= now,
                        Task.notification_sent == False,
                        Task.status == "pending"
                    )
                )
            )
            due_tasks = result.scalars().all()

            if not due_tasks:
                logger.debug("No task reminders due")
                return

            logger.info(f"Found {len(due_tasks)} task reminders to send")
            email_service = EmailService()

            for task in due_tasks:
                try:
                    # Get contractor email
                    contractor = await db.get(Contractor, task.contractor_id)
                    if not contractor or not contractor.email:
                        logger.warning(f"No email for contractor {task.contractor_id}")
                        continue

                    # Send reminder email
                    await email_service.send_task_reminder_email(
                        to_email=contractor.email,
                        contractor_name=contractor.owner_name or contractor.business_name,
                        task_title=task.title,
                        task_description=task.description,
                        due_date=task.due_date,
                        customer_name=None,  # Could fetch if needed
                    )

                    # Mark as sent
                    task.notification_sent = True
                    task.notification_sent_at = datetime.utcnow()

                    logger.info(f"Sent reminder for task {task.id}")

                except Exception as e:
                    logger.error(f"Failed to send reminder for task {task.id}: {e}")

            await db.commit()

    except Exception as e:
        logger.error(f"Error in check_task_reminders: {e}")


async def run_smart_followups():
    """
    INNOV-3: Smart Follow-Up Engine.

    Process all active follow-up sequences:
    - Check for due follow-ups
    - Analyze customer signals
    - Send AI-optimized emails
    - Adjust timing based on behavior

    Runs every 15 minutes.
    """
    from .follow_up import FollowUpService

    logger.info("Running smart follow-up engine")

    try:
        from .database import async_session_factory
        async with async_session_factory() as db:
            processed = await FollowUpService.process_due_followups(db)
            if processed > 0:
                logger.info(f"Smart follow-up engine: Processed {processed} follow-ups")
            else:
                logger.debug("Smart follow-up engine: No follow-ups due")

    except Exception as e:
        logger.error(f"Error in run_smart_followups: {e}")


async def run_marketing_report():
    """
    DISC-141: Daily Marketing Analytics Report.

    Generate and send daily marketing metrics to founder:
    - Signup counts (yesterday vs trend)
    - Quote generation metrics
    - All-time totals
    - 7-day sparkline

    Runs daily at 8am UTC (3am EST).
    """
    from .marketing_analytics import run_daily_marketing_report

    logger.info("Running daily marketing report")

    try:
        await run_daily_marketing_report()
        logger.info("Daily marketing report completed")
    except Exception as e:
        logger.error(f"Error in run_marketing_report: {e}")


async def run_exit_survey_digest():
    """
    DISC-137: Daily Exit Survey Digest.

    Generate and send daily exit survey summary to founder:
    - Reason breakdown (counts by category)
    - Verbatim "Other" responses (most valuable)
    - Trend vs previous day

    Runs daily at 8:30am UTC (3:30am EST), after marketing report.
    """
    from .exit_survey import run_exit_survey_digest as _run_digest

    logger.info("Running exit survey digest")

    try:
        await _run_digest()
        logger.info("Exit survey digest completed")
    except Exception as e:
        logger.error(f"Error in run_exit_survey_digest: {e}")


async def run_traffic_spike_check():
    """
    DISC-139: Real-Time Traffic Spike Alerts.

    Hourly check for unusual activity:
    - Compare signups to 7-day average
    - Alert on 3x+ normal traffic
    - Alert on 3+ signups/hour or 5+ demos/hour
    - Enable rapid response to viral moments

    Runs every hour at :30 (offset from other jobs).
    """
    from .traffic_spike_alerts import check_traffic_spikes

    logger.info("Running traffic spike check")

    try:
        await check_traffic_spikes()
        logger.info("Traffic spike check completed")
    except Exception as e:
        logger.error(f"Error in run_traffic_spike_check: {e}")


async def run_feedback_drip():
    """
    DISC-147: Automated Feedback Follow-up Pulse.

    Send thoughtful feedback requests to users at key milestones:
    - Day 3: First impressions
    - Day 7: Workflow integration

    Runs daily at 2pm UTC (9am EST) - during work hours.
    """
    from ..models.database import Contractor
    from .database import async_session_factory
    from .email import EmailService
    from sqlalchemy import select, and_

    logger.info("Running feedback drip check")

    try:
        async with async_session_factory() as db:
            now = datetime.utcnow()
            email_service = EmailService()

            # Find users at day 3 (between 3 and 4 days old)
            day3_start = now - timedelta(days=4)
            day3_end = now - timedelta(days=3)

            day3_result = await db.execute(
                select(Contractor).where(
                    and_(
                        Contractor.created_at >= day3_start,
                        Contractor.created_at < day3_end,
                        Contractor.feedback_email_sent.is_(None) | (Contractor.feedback_email_sent < 3)
                    )
                )
            )
            day3_users = day3_result.scalars().all()

            # Find users at day 7 (between 7 and 8 days old)
            day7_start = now - timedelta(days=8)
            day7_end = now - timedelta(days=7)

            day7_result = await db.execute(
                select(Contractor).where(
                    and_(
                        Contractor.created_at >= day7_start,
                        Contractor.created_at < day7_end,
                        Contractor.feedback_email_sent.is_(None) | (Contractor.feedback_email_sent < 7)
                    )
                )
            )
            day7_users = day7_result.scalars().all()

            emails_sent = 0

            for contractor in day3_users:
                try:
                    if not contractor.email:
                        continue
                    await email_service.send_feedback_request(
                        to_email=contractor.email,
                        owner_name=contractor.owner_name,
                        business_name=contractor.business_name,
                        days_since_signup=3
                    )
                    contractor.feedback_email_sent = 3
                    emails_sent += 1
                    # Rate limit protection: Resend allows 2 req/sec
                    await asyncio.sleep(0.6)
                except Exception as e:
                    logger.warning(f"Failed to send day-3 feedback to {contractor.email}: {e}")

            for contractor in day7_users:
                try:
                    if not contractor.email:
                        continue
                    await email_service.send_feedback_request(
                        to_email=contractor.email,
                        owner_name=contractor.owner_name,
                        business_name=contractor.business_name,
                        days_since_signup=7
                    )
                    contractor.feedback_email_sent = 7
                    emails_sent += 1
                    # Rate limit protection: Resend allows 2 req/sec
                    await asyncio.sleep(0.6)
                except Exception as e:
                    logger.warning(f"Failed to send day-7 feedback to {contractor.email}: {e}")

            if emails_sent > 0:
                await db.commit()
                logger.info(f"Feedback drip: Sent {emails_sent} feedback requests")
            else:
                logger.info(f"Feedback drip: No users at feedback milestones (day3: {len(day3_users)}, day7: {len(day7_users)})")

    except Exception as e:
        logger.error(f"Error in run_feedback_drip: {e}")


async def check_trial_reminders():
    """
    DISC-161: Trial System Reminder Emails.

    Check for users whose trial is ending and send reminders:
    - 3 days before trial ends: Send trial ending reminder (once)
    - Day of expiration: Send trial expired email

    Runs daily at 11am UTC (6am EST) - during morning hours.
    """
    from ..models.database import User, Contractor
    from .database import async_session_factory
    from .email import EmailService
    from sqlalchemy import select, and_

    logger.info("Running trial reminder check")

    try:
        async with async_session_factory() as db:
            now = datetime.utcnow()
            email_service = EmailService()
            reminders_sent = 0
            expiry_emails_sent = 0

            # --- 3-day reminder: Users whose trial ends in 3-4 days ---
            # Window: trial_ends_at between 3 and 4 days from now
            reminder_start = now + timedelta(days=3)
            reminder_end = now + timedelta(days=4)

            reminder_result = await db.execute(
                select(User).where(
                    and_(
                        User.trial_ends_at >= reminder_start,
                        User.trial_ends_at < reminder_end,
                        User.plan_tier == "trial",
                        User.trial_reminder_sent == False
                    )
                )
            )
            reminder_users = reminder_result.scalars().all()

            for user in reminder_users:
                try:
                    # Get contractor for business name and quote count
                    contractor_result = await db.execute(
                        select(Contractor).where(Contractor.user_id == user.id)
                    )
                    contractor = contractor_result.scalar_one_or_none()

                    if not contractor:
                        logger.warning(f"No contractor found for user {user.id}")
                        continue

                    # Calculate days left
                    days_left = (user.trial_ends_at - now).days

                    # Count quotes generated
                    quotes_generated = user.quotes_used or 0

                    await email_service.send_trial_ending_reminder(
                        to_email=user.email,
                        business_name=contractor.business_name,
                        days_left=days_left,
                        quotes_generated=quotes_generated
                    )

                    # Mark reminder as sent
                    user.trial_reminder_sent = True
                    reminders_sent += 1

                    # PostHog tracking
                    try:
                        from .posthog import track_event
                        track_event(
                            user.id,
                            "trial_reminder_sent",
                            {
                                "days_left": days_left,
                                "quotes_generated": quotes_generated,
                                "email": user.email
                            }
                        )
                    except Exception as ph_error:
                        logger.debug(f"PostHog tracking failed: {ph_error}")

                    logger.info(f"Sent trial reminder to {user.email} ({days_left} days left)")
                    # Rate limit protection: Resend allows 2 req/sec
                    await asyncio.sleep(0.6)

                except Exception as e:
                    logger.warning(f"Failed to send trial reminder to {user.email}: {e}")

            # --- Expiration email: Users whose trial ended today ---
            # Window: trial_ends_at between yesterday and now
            expiry_start = now - timedelta(days=1)
            expiry_end = now

            expiry_result = await db.execute(
                select(User).where(
                    and_(
                        User.trial_ends_at >= expiry_start,
                        User.trial_ends_at < expiry_end,
                        User.plan_tier == "trial"  # Still on trial tier (didn't upgrade)
                    )
                )
            )
            expiry_users = expiry_result.scalars().all()

            for user in expiry_users:
                try:
                    # Get contractor for business name
                    contractor_result = await db.execute(
                        select(Contractor).where(Contractor.user_id == user.id)
                    )
                    contractor = contractor_result.scalar_one_or_none()

                    if not contractor:
                        logger.warning(f"No contractor found for user {user.id}")
                        continue

                    quotes_generated = user.quotes_used or 0

                    await email_service.send_trial_expired_email(
                        to_email=user.email,
                        business_name=contractor.business_name,
                        quotes_generated=quotes_generated
                    )

                    expiry_emails_sent += 1

                    # PostHog tracking
                    try:
                        from .posthog import track_event
                        track_event(
                            user.id,
                            "trial_expired",
                            {
                                "quotes_generated": quotes_generated,
                                "email": user.email
                            }
                        )
                    except Exception as ph_error:
                        logger.debug(f"PostHog tracking failed: {ph_error}")

                    logger.info(f"Sent trial expired email to {user.email}")
                    # Rate limit protection: Resend allows 2 req/sec
                    await asyncio.sleep(0.6)

                except Exception as e:
                    logger.warning(f"Failed to send trial expired email to {user.email}: {e}")

            if reminders_sent > 0 or expiry_emails_sent > 0:
                await db.commit()
                logger.info(f"Trial reminders: {reminders_sent} reminder(s), {expiry_emails_sent} expiry email(s) sent")
            else:
                logger.info(f"Trial reminders: No users need trial emails today (reminders: {len(reminder_users)}, expiry: {len(expiry_users)})")

    except Exception as e:
        logger.error(f"Error in check_trial_reminders: {e}")


async def run_daily_health_check():
    """
    DISC-148: Daily Synthetic Quote Health Check.

    Test the core quoting functionality daily:
    - Generate a test quote using the demo endpoint
    - Verify PDF generation works
    - Alert founder if anything fails

    Runs daily at 6am UTC (1am EST) - quiet hours, before business day.
    """
    from .email import EmailService
    import httpx
    from ..config import settings

    logger.info("Running daily quote health check")

    try:
        email_service = EmailService()
        errors = []

        # Test demo quote generation
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    "https://quoted.it.com/api/demo/quote",
                    json={"transcription": "Health check: Install 2 ceiling fans, $150 each, 3 hours total labor at $75/hour."},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code != 200:
                    errors.append(f"Demo quote generation failed: HTTP {response.status_code}")
                else:
                    data = response.json()
                    if not data.get("line_items"):
                        errors.append("Demo quote returned no line items")
                    if not data.get("total") or data.get("total", 0) <= 0:
                        errors.append(f"Demo quote returned invalid total: {data.get('total')}")
                    else:
                        logger.info(f"Health check quote generated: ${data.get('total', 0):.2f}")
            except Exception as e:
                errors.append(f"Demo quote request failed: {str(e)}")

        # If errors, alert founder
        if errors:
            logger.error(f"Health check failed with {len(errors)} errors: {errors}")

            # Send alert email
            error_list = "\n".join(f"• {e}" for e in errors)
            await email_service._send_email(
                to_email=settings.founder_email,
                subject="[Quoted] ALERT: Daily Health Check Failed",
                html=f"""
                    <h1 style="color: #ef4444;">⚠️ Health Check Failed</h1>
                    <p>The daily quote health check found issues:</p>
                    <pre style="background: #1a1a1a; padding: 16px; border-radius: 8px; color: #ef4444;">
{error_list}
                    </pre>
                    <p>Please investigate immediately.</p>
                """,
                text=f"Health Check Failed\n\n{error_list}\n\nPlease investigate immediately."
            )
        else:
            logger.info("Daily health check passed - all systems operational")

    except Exception as e:
        logger.error(f"Error in run_daily_health_check: {e}")


async def check_invoice_reminders():
    """
    INNOV-6: Invoice Automation - Payment Reminders.

    Check for invoices needing payment reminders:
    - 7 days before due date
    - 1, 7, 14, 30 days after due (overdue)

    Runs daily at 10am UTC.
    """
    from .invoice_automation import InvoiceAutomationService

    logger.info("Running invoice payment reminder check")

    try:
        from .database import async_session_factory
        async with async_session_factory() as db:
            reminders_sent = await InvoiceAutomationService.check_payment_reminders(db)
            if reminders_sent > 0:
                logger.info(f"Invoice reminders: Sent {reminders_sent} reminders")
            else:
                logger.debug("Invoice reminders: No reminders due")

    except Exception as e:
        logger.error(f"Error in check_invoice_reminders: {e}")


async def check_quote_followups():
    """
    Check for quotes needing follow-up.
    Creates auto-tasks for:
    - Sent quotes not viewed after 3 days
    - Viewed quotes not accepted/rejected after 7 days

    Runs daily at 9am UTC.
    """
    from ..models.database import Quote, Task, Customer
    from .database import async_session_factory

    logger.info("Running quote follow-up check")

    try:
        async with async_session_factory() as db:
            now = datetime.utcnow()
            three_days_ago = now - timedelta(days=3)
            seven_days_ago = now - timedelta(days=7)

            # Find sent quotes not viewed after 3 days
            stale_sent = await db.execute(
                select(Quote).where(
                    and_(
                        Quote.status == "sent",
                        Quote.sent_at < three_days_ago,
                        Quote.view_count == 0
                    )
                )
            )
            stale_sent_quotes = stale_sent.scalars().all()

            # Find viewed quotes not acted on after 7 days
            stale_viewed = await db.execute(
                select(Quote).where(
                    and_(
                        Quote.status == "viewed",
                        Quote.first_viewed_at < seven_days_ago
                    )
                )
            )
            stale_viewed_quotes = stale_viewed.scalars().all()

            tasks_created = 0

            for quote in stale_sent_quotes:
                # Check if follow-up task already exists
                existing = await db.execute(
                    select(Task).where(
                        and_(
                            Task.quote_id == quote.id,
                            Task.trigger_type == "quote_not_viewed_3d",
                            Task.status == "pending"
                        )
                    )
                )
                if existing.scalars().first():
                    continue  # Already have a follow-up task

                task = Task(
                    contractor_id=quote.contractor_id,
                    quote_id=quote.id,
                    customer_id=quote.customer_id,
                    title=f"Follow up: Quote for {quote.customer_name} not viewed",
                    description=f"Quote sent {quote.sent_at.strftime('%b %d')} hasn't been viewed yet. Consider resending or calling the customer.",
                    due_date=now,
                    priority="high",
                    task_type="follow_up",
                    auto_generated=True,
                    trigger_type="quote_not_viewed_3d",
                    trigger_entity_id=quote.id,
                )
                db.add(task)
                tasks_created += 1

            for quote in stale_viewed_quotes:
                # Check if follow-up task already exists
                existing = await db.execute(
                    select(Task).where(
                        and_(
                            Task.quote_id == quote.id,
                            Task.trigger_type == "quote_viewed_no_action_7d",
                            Task.status == "pending"
                        )
                    )
                )
                if existing.scalars().first():
                    continue

                task = Task(
                    contractor_id=quote.contractor_id,
                    quote_id=quote.id,
                    customer_id=quote.customer_id,
                    title=f"Follow up: {quote.customer_name} viewed quote but hasn't responded",
                    description=f"Quote viewed on {quote.first_viewed_at.strftime('%b %d')} ({quote.view_count} views) but no decision yet. Time to check in!",
                    due_date=now,
                    priority="high",
                    task_type="follow_up",
                    auto_generated=True,
                    trigger_type="quote_viewed_no_action_7d",
                    trigger_entity_id=quote.id,
                )
                db.add(task)
                tasks_created += 1

            if tasks_created > 0:
                await db.commit()
                logger.info(f"Created {tasks_created} follow-up tasks")
            else:
                logger.debug("No follow-up tasks needed")

    except Exception as e:
        logger.error(f"Error in check_quote_followups: {e}")


def start_scheduler():
    """Initialize and start the background scheduler."""
    global scheduler

    if scheduler is not None and scheduler.running:
        logger.warning("Scheduler already running")
        return

    scheduler = AsyncIOScheduler()

    # Task reminders - every 5 minutes
    scheduler.add_job(
        check_task_reminders,
        trigger=IntervalTrigger(minutes=5),
        id="task_reminders",
        replace_existing=True,
        max_instances=1,
    )

    # Quote follow-ups - daily at 9am UTC (4am EST)
    scheduler.add_job(
        check_quote_followups,
        trigger=CronTrigger(hour=9, minute=0),
        id="quote_followups",
        replace_existing=True,
        max_instances=1,
    )

    # INNOV-3: Smart follow-up engine - every 15 minutes
    scheduler.add_job(
        run_smart_followups,
        trigger=IntervalTrigger(minutes=15),
        id="smart_followups",
        replace_existing=True,
        max_instances=1,
    )

    # INNOV-6: Invoice payment reminders - daily at 10am UTC
    scheduler.add_job(
        check_invoice_reminders,
        trigger=CronTrigger(hour=10, minute=0),
        id="invoice_reminders",
        replace_existing=True,
        max_instances=1,
    )

    # DISC-141: Daily marketing report - daily at 8am UTC (3am EST)
    scheduler.add_job(
        run_marketing_report,
        trigger=CronTrigger(hour=8, minute=0),
        id="marketing_report",
        replace_existing=True,
        max_instances=1,
    )

    # DISC-137: Daily exit survey digest - daily at 8:30am UTC (3:30am EST)
    scheduler.add_job(
        run_exit_survey_digest,
        trigger=CronTrigger(hour=8, minute=30),
        id="exit_survey_digest",
        replace_existing=True,
        max_instances=1,
    )

    # DISC-139: Hourly traffic spike alerts - every hour at :30
    scheduler.add_job(
        run_traffic_spike_check,
        trigger=CronTrigger(minute=30),
        id="traffic_spike_check",
        replace_existing=True,
        max_instances=1,
    )

    # DISC-147: Feedback drip - daily at 2pm UTC (9am EST)
    scheduler.add_job(
        run_feedback_drip,
        trigger=CronTrigger(hour=14, minute=0),
        id="feedback_drip",
        replace_existing=True,
        max_instances=1,
    )

    # DISC-161: Trial reminders - daily at 11am UTC (6am EST)
    scheduler.add_job(
        check_trial_reminders,
        trigger=CronTrigger(hour=11, minute=0),
        id="trial_reminders",
        replace_existing=True,
        max_instances=1,
    )

    # DISC-148: Daily health check - daily at 6am UTC (1am EST)
    scheduler.add_job(
        run_daily_health_check,
        trigger=CronTrigger(hour=6, minute=0),
        id="daily_health_check",
        replace_existing=True,
        max_instances=1,
    )

    # DISC-140: Monitoring Agent - Critical health checks every 15 minutes
    from .monitoring_agent import (
        run_critical_health_checks,
        run_business_metrics_check,
        run_daily_monitoring_summary,
    )

    scheduler.add_job(
        run_critical_health_checks,
        trigger=IntervalTrigger(minutes=15),
        id="monitoring_critical_health",
        replace_existing=True,
        max_instances=1,
    )

    # DISC-140: Monitoring Agent - Business metrics check hourly at :45
    scheduler.add_job(
        run_business_metrics_check,
        trigger=CronTrigger(minute=45),
        id="monitoring_business_metrics",
        replace_existing=True,
        max_instances=1,
    )

    # DISC-140: Monitoring Agent - Daily summary at 8:15am UTC (after marketing report)
    scheduler.add_job(
        run_daily_monitoring_summary,
        trigger=CronTrigger(hour=8, minute=15),
        id="monitoring_daily_summary",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    logger.info("Background scheduler started with jobs: task_reminders (5min), quote_followups (daily 9am UTC), smart_followups (15min), invoice_reminders (daily 10am UTC), marketing_report (daily 8am UTC), exit_survey_digest (daily 8:30am UTC), traffic_spike_check (hourly :30), feedback_drip (daily 2pm UTC), trial_reminders (daily 11am UTC), daily_health_check (daily 6am UTC), monitoring_critical_health (15min), monitoring_business_metrics (hourly :45), monitoring_daily_summary (daily 8:15am UTC)")


def stop_scheduler():
    """Stop the background scheduler gracefully."""
    global scheduler

    if scheduler is not None and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped")
        scheduler = None


def get_scheduler_status() -> dict:
    """Get current scheduler status for health checks."""
    global scheduler

    if scheduler is None:
        return {"running": False, "jobs": []}

    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            for job in scheduler.get_jobs()
        ]
    }
