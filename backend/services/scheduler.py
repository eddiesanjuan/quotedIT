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
    from ..models.database import get_async_session, Task, Contractor
    from .email import EmailService
    from .logging import get_logger
    job_logger = get_logger("quoted.scheduler.task_reminders")

    logger.info("Running task reminder check")

    try:
        async with get_async_session() as db:
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


async def check_quote_followups():
    """
    Check for quotes needing follow-up.
    Creates auto-tasks for:
    - Sent quotes not viewed after 3 days
    - Viewed quotes not accepted/rejected after 7 days

    Runs daily at 9am UTC.
    """
    from ..models.database import get_async_session, Quote, Task, Customer

    logger.info("Running quote follow-up check")

    try:
        async with get_async_session() as db:
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

    scheduler.start()
    logger.info("Background scheduler started with jobs: task_reminders (5min), quote_followups (daily 9am UTC)")


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
