"""
Backfill Existing Quotes to Customer Records (DISC-091).

This script processes all existing quotes and creates Customer records,
linking quotes to their respective customers using the CustomerService
deduplication logic.

Can be run:
1. During deployment: python -m backend.scripts.backfill_customers
2. From API endpoint: POST /api/customers/backfill (admin only)
3. During database init: Called from init_db()

Safe to run multiple times - uses find_or_create_customer which handles
deduplication automatically.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings
from backend.models.database import Quote, Customer, Contractor
from backend.services.customer_service import CustomerService


async def backfill_customers_for_contractor(
    db: AsyncSession,
    contractor_id: str,
    verbose: bool = False
) -> dict:
    """
    Backfill customers for a single contractor.

    Args:
        db: Database session
        contractor_id: Contractor ID to process
        verbose: Print progress messages

    Returns:
        Dict with stats: quotes_processed, customers_created, customers_updated
    """
    stats = {
        "quotes_processed": 0,
        "customers_created": 0,
        "customers_linked": 0,
        "errors": 0
    }

    # Get all quotes for this contractor that have customer info
    result = await db.execute(
        select(Quote).where(
            Quote.contractor_id == contractor_id,
            Quote.customer_name.isnot(None),
            Quote.customer_name != ""
        ).order_by(Quote.created_at.asc())  # Process oldest first for accurate stats
    )
    quotes = result.scalars().all()

    if verbose:
        print(f"  Found {len(quotes)} quotes with customer data")

    for quote in quotes:
        try:
            # Check if quote already linked to a customer
            if quote.customer_id:
                stats["quotes_processed"] += 1
                continue

            # Use the service to find or create customer
            customer = await CustomerService.find_or_create_customer(
                db=db,
                contractor_id=contractor_id,
                name=quote.customer_name,
                phone=quote.customer_phone,
                email=quote.customer_email,
                address=quote.customer_address
            )

            if customer:
                # Check if this was a new customer (no quotes yet linked)
                was_new = customer.quote_count == 0 or not quote.customer_id

                # Link quote to customer
                quote.customer_id = customer.id

                # Update stats
                await CustomerService.update_customer_stats(db, customer)

                if was_new and customer.quote_count == 1:
                    stats["customers_created"] += 1

                stats["customers_linked"] += 1

            stats["quotes_processed"] += 1

        except Exception as e:
            if verbose:
                print(f"  Error processing quote {quote.id}: {e}")
            stats["errors"] += 1

    # Commit all changes for this contractor
    await db.commit()

    return stats


async def backfill_all_customers(verbose: bool = True) -> dict:
    """
    Backfill customers for all contractors.

    Args:
        verbose: Print progress messages

    Returns:
        Dict with total stats across all contractors
    """
    # Create database engine
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    total_stats = {
        "contractors_processed": 0,
        "quotes_processed": 0,
        "customers_created": 0,
        "customers_linked": 0,
        "errors": 0
    }

    async with async_session() as db:
        # Get all contractors
        result = await db.execute(select(Contractor))
        contractors = result.scalars().all()

        if verbose:
            print(f"\n=== Customer Backfill (DISC-091) ===")
            print(f"Processing {len(contractors)} contractors...")

        for contractor in contractors:
            if verbose:
                print(f"\nContractor: {contractor.business_name or contractor.id}")

            stats = await backfill_customers_for_contractor(
                db=db,
                contractor_id=contractor.id,
                verbose=verbose
            )

            total_stats["contractors_processed"] += 1
            total_stats["quotes_processed"] += stats["quotes_processed"]
            total_stats["customers_created"] += stats["customers_created"]
            total_stats["customers_linked"] += stats["customers_linked"]
            total_stats["errors"] += stats["errors"]

            if verbose:
                print(f"  → {stats['customers_created']} new customers, {stats['customers_linked']} quotes linked")

    await engine.dispose()

    if verbose:
        print(f"\n=== Backfill Complete ===")
        print(f"Contractors: {total_stats['contractors_processed']}")
        print(f"Quotes processed: {total_stats['quotes_processed']}")
        print(f"Customers created: {total_stats['customers_created']}")
        print(f"Quotes linked: {total_stats['customers_linked']}")
        if total_stats["errors"]:
            print(f"Errors: {total_stats['errors']}")

    return total_stats


async def check_backfill_status() -> dict:
    """
    Check how many quotes still need backfill.

    Returns:
        Dict with counts of linked vs unlinked quotes
    """
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Count total quotes with customer name
        total_result = await db.execute(
            select(func.count(Quote.id)).where(
                Quote.customer_name.isnot(None),
                Quote.customer_name != ""
            )
        )
        total_with_name = total_result.scalar() or 0

        # Count quotes already linked
        linked_result = await db.execute(
            select(func.count(Quote.id)).where(
                Quote.customer_id.isnot(None)
            )
        )
        linked = linked_result.scalar() or 0

        # Count total customers
        customers_result = await db.execute(
            select(func.count(Customer.id))
        )
        total_customers = customers_result.scalar() or 0

    await engine.dispose()

    return {
        "total_quotes_with_customer": total_with_name,
        "quotes_linked": linked,
        "quotes_pending": total_with_name - linked,
        "total_customers": total_customers,
        "backfill_complete": (total_with_name - linked) == 0
    }


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backfill customer records from quotes")
    parser.add_argument("--status", action="store_true", help="Check backfill status only")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    if args.status:
        status = asyncio.run(check_backfill_status())
        print(f"\nBackfill Status:")
        print(f"  Quotes with customer data: {status['total_quotes_with_customer']}")
        print(f"  Already linked: {status['quotes_linked']}")
        print(f"  Pending: {status['quotes_pending']}")
        print(f"  Total customers: {status['total_customers']}")
        print(f"  Complete: {'Yes' if status['backfill_complete'] else 'No'}")
    else:
        asyncio.run(backfill_all_customers(verbose=not args.quiet))
