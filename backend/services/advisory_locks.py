"""
Advisory lock helpers for preventing duplicate scheduled job execution.

P0-1 Fix: When running with multiple workers (--workers 4), each worker
independently starts the scheduler. The env var guard races because workers
check/set SCHEDULER_STARTED simultaneously.

Solution: Use Postgres advisory locks at the job level. Each job acquires
a non-blocking lock before execution. If another worker is already running
the job, we skip this execution.

Advisory locks are:
- Session-scoped (auto-released on disconnect)
- Non-blocking with pg_try_advisory_lock (returns immediately)
- Perfect for preventing duplicate cron job execution

Usage:
    @with_job_lock("task_reminders")
    async def check_task_reminders():
        # Job code here - only one worker will execute at a time
        ...
"""

import functools
from typing import Callable, Optional
from sqlalchemy import text

from .logging import get_logger

logger = get_logger("quoted.advisory_locks")


def _job_name_to_lock_id(job_name: str) -> int:
    """
    Convert a job name to a Postgres advisory lock ID.

    Advisory lock IDs are 64-bit integers. We use the hash of the job name
    modulo 2^31 to fit in a signed 32-bit integer range (Postgres accepts both
    32-bit and 64-bit lock IDs).

    Args:
        job_name: Unique identifier for the scheduled job

    Returns:
        Integer lock ID for use with pg_try_advisory_lock
    """
    # Use Python's built-in hash and constrain to positive 32-bit range
    # The modulo ensures we stay within Postgres's int4 range
    return abs(hash(job_name)) % (2**31)


async def acquire_job_lock(job_name: str, db_session) -> bool:
    """
    Try to acquire an advisory lock for a scheduled job.

    Uses pg_try_advisory_lock which is non-blocking - returns immediately
    with True if lock acquired, False if another process holds it.

    Args:
        job_name: Unique identifier for the scheduled job
        db_session: SQLAlchemy async session

    Returns:
        True if lock acquired, False if job is already running elsewhere
    """
    lock_id = _job_name_to_lock_id(job_name)

    try:
        result = await db_session.execute(
            text(f"SELECT pg_try_advisory_lock({lock_id})")
        )
        acquired = result.scalar()

        if acquired:
            logger.debug(f"Acquired lock for job '{job_name}' (lock_id={lock_id})")
        else:
            logger.debug(f"Lock unavailable for job '{job_name}' - another worker is running it")

        return bool(acquired)

    except Exception as e:
        # If advisory locks fail (e.g., SQLite in dev), log and allow execution
        # This maintains backward compatibility with SQLite development
        logger.warning(f"Advisory lock check failed for '{job_name}': {e} - proceeding with execution")
        return True


async def release_job_lock(job_name: str, db_session) -> None:
    """
    Release an advisory lock for a scheduled job.

    Uses pg_advisory_unlock. Should be called in a finally block.
    Note: Advisory locks are automatically released when the session ends,
    so explicit release is optional but good practice.

    Args:
        job_name: Unique identifier for the scheduled job
        db_session: SQLAlchemy async session
    """
    lock_id = _job_name_to_lock_id(job_name)

    try:
        await db_session.execute(
            text(f"SELECT pg_advisory_unlock({lock_id})")
        )
        logger.debug(f"Released lock for job '{job_name}' (lock_id={lock_id})")

    except Exception as e:
        # Log but don't raise - lock will be released on session close anyway
        logger.warning(f"Advisory lock release failed for '{job_name}': {e}")


def with_job_lock(job_name: str):
    """
    Decorator that wraps a scheduled job with advisory lock acquisition.

    If the lock cannot be acquired (another worker is running the job),
    the decorated function returns early without executing.

    Usage:
        @with_job_lock("task_reminders")
        async def check_task_reminders():
            # This code only runs in one worker at a time
            ...

    Args:
        job_name: Unique identifier for the scheduled job

    Returns:
        Decorated function with advisory lock protection
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            from .database import async_session_factory

            async with async_session_factory() as db:
                # Try to acquire lock
                if not await acquire_job_lock(job_name, db):
                    logger.info(f"Skipping job '{job_name}' - already running in another worker")
                    return None

                try:
                    # Execute the job
                    return await func(*args, **kwargs)
                finally:
                    # Always release the lock
                    await release_job_lock(job_name, db)

        return wrapper
    return decorator


def wrap_with_lock(job_name: str, func: Callable) -> Callable:
    """
    Wrap a job function with advisory lock protection.

    This is an alternative to the @with_job_lock decorator that can be used
    at job registration time rather than function definition time.

    Usage in start_scheduler():
        scheduler.add_job(
            wrap_with_lock("task_reminders", check_task_reminders),
            trigger=IntervalTrigger(minutes=5),
            ...
        )

    Args:
        job_name: Unique identifier for the scheduled job
        func: The async job function to wrap

    Returns:
        Wrapped function with advisory lock protection
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        from .database import async_session_factory

        async with async_session_factory() as db:
            # Try to acquire lock
            if not await acquire_job_lock(job_name, db):
                logger.info(f"Skipping job '{job_name}' - already running in another worker")
                return None

            try:
                # Execute the job
                return await func(*args, **kwargs)
            finally:
                # Always release the lock
                await release_job_lock(job_name, db)

    return wrapper
