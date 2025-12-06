"""
Migration script: Convert text-based learnings to structured Learning model

DISC-053: Structured Learning Storage

This script:
1. Reads all contractors' pricing_knowledge
2. Extracts learned_adjustments from each category
3. Creates Learning records with metadata
4. Maintains dual-write capability during migration

Usage:
    python -m backend.migrations.migrate_learnings_to_structured [--dry-run]
"""

import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import (
    Contractor,
    PricingModel,
    Learning,
    async_session_factory,
    init_db,
)


def parse_learning_text(text: str, category: str) -> Dict[str, Any]:
    """
    Parse a text learning statement into structured components.

    Examples:
    - "Increase labor by ~20% (customer prefers premium work)"
    - "Reduce materials by ~15%"
    - "Always add 10% for jobs in Heights neighborhood"
    """
    text_lower = text.lower()

    # Determine learning type
    if "increase" in text_lower or "reduce" in text_lower or "by ~" in text_lower:
        learning_type = "adjustment"
    elif "always" in text_lower or "should" in text_lower:
        learning_type = "rule"
    elif "tend" in text_lower or "generally" in text_lower or "typically" in text_lower:
        learning_type = "tendency"
    else:
        learning_type = "pattern"

    # Extract target (what this applies to)
    # Common targets: labor, materials, demolition, decking, etc.
    target = "general"
    for keyword in ["labor", "material", "demolition", "deck", "fence", "rail", "stair"]:
        if keyword in text_lower:
            target = keyword
            break

    # Extract reason if present (text in parentheses)
    reason = None
    if "(" in text and ")" in text:
        start = text.index("(")
        end = text.rindex(")")
        reason = text[start+1:end].strip()

    return {
        "category": category,
        "learning_type": learning_type,
        "target": target,
        "adjustment": text,
        "reason": reason,
        "confidence": 0.7,  # Default confidence for migrated learnings
        "sample_count": 1,  # Conservative estimate
        "total_impact_dollars": 0.0,  # Unknown for historical data
    }


async def migrate_contractor_learnings(
    session: AsyncSession,
    contractor: Contractor,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Migrate one contractor's learnings from text to structured format.

    Returns:
        Dict with migration stats
    """
    stats = {
        "categories_processed": 0,
        "learnings_created": 0,
        "learnings_skipped": 0,
    }

    # Get pricing model
    result = await session.execute(
        select(PricingModel).where(PricingModel.contractor_id == contractor.id)
    )
    pricing_model = result.scalar_one_or_none()

    if not pricing_model or not pricing_model.pricing_knowledge:
        return stats

    pricing_knowledge = pricing_model.pricing_knowledge
    categories = pricing_knowledge.get("categories", {})

    # Process each category
    for category_name, category_data in categories.items():
        stats["categories_processed"] += 1

        # Get learned adjustments
        learned_adjustments = category_data.get("learned_adjustments", [])
        if not learned_adjustments:
            continue

        # Get category metadata
        correction_count = category_data.get("correction_count", 1)
        confidence = category_data.get("confidence", 0.5)

        # Convert each text learning to structured Learning record
        for adjustment_text in learned_adjustments:
            # Parse the text
            parsed = parse_learning_text(adjustment_text, category_name)

            # Override with actual category metadata
            parsed["confidence"] = confidence
            parsed["sample_count"] = max(1, correction_count // len(learned_adjustments))

            # Calculate priority score (recency=0.5 since historical, + confidence + impact=0)
            priority_score = 0.5 * 0.3 + parsed["confidence"] * 0.5 + 0.0 * 0.2

            if not dry_run:
                # Create Learning record
                learning = Learning(
                    contractor_id=contractor.id,
                    category=parsed["category"],
                    learning_type=parsed["learning_type"],
                    target=parsed["target"],
                    adjustment=parsed["adjustment"],
                    reason=parsed["reason"],
                    confidence=parsed["confidence"],
                    sample_count=parsed["sample_count"],
                    total_impact_dollars=parsed["total_impact_dollars"],
                    priority_score=priority_score,
                    created_at=datetime.utcnow(),
                    last_seen_at=datetime.utcnow(),
                    examples=None,  # Historical data doesn't have examples
                    embedding=None,  # Will be populated by DISC-055
                )
                session.add(learning)
                stats["learnings_created"] += 1
            else:
                stats["learnings_created"] += 1  # Count what would be created

    if not dry_run:
        await session.commit()

    return stats


async def run_migration(dry_run: bool = False):
    """
    Run the full migration across all contractors.
    """
    print("=" * 60)
    print("DISC-053: Structured Learning Storage Migration")
    print("=" * 60)
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()

    # Initialize database
    await init_db()

    # Get all contractors
    async with async_session_factory() as session:
        result = await session.execute(select(Contractor))
        contractors = result.scalars().all()

        total_stats = {
            "contractors_processed": 0,
            "categories_processed": 0,
            "learnings_created": 0,
            "learnings_skipped": 0,
        }

        for contractor in contractors:
            print(f"Processing contractor: {contractor.business_name} ({contractor.id})")

            stats = await migrate_contractor_learnings(session, contractor, dry_run)

            total_stats["contractors_processed"] += 1
            total_stats["categories_processed"] += stats["categories_processed"]
            total_stats["learnings_created"] += stats["learnings_created"]
            total_stats["learnings_skipped"] += stats["learnings_skipped"]

            print(f"  ✓ Categories: {stats['categories_processed']}, Learnings: {stats['learnings_created']}")
            print()

    print("=" * 60)
    print("Migration Complete")
    print("=" * 60)
    print(f"Contractors processed: {total_stats['contractors_processed']}")
    print(f"Categories processed: {total_stats['categories_processed']}")
    print(f"Learnings created: {total_stats['learnings_created']}")
    print(f"Learnings skipped: {total_stats['learnings_skipped']}")
    print()

    if dry_run:
        print("✅ Dry run successful - rerun without --dry-run to apply changes")
    else:
        print("✅ Migration successful - structured learnings created")
        print()
        print("⚠️  IMPORTANT: Enable dual-write mode in learning service")
        print("   Both text and structured formats will be maintained during transition")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate learnings to structured format")
    parser.add_argument("--dry-run", action="store_true", help="Run without making changes")
    args = parser.parse_args()

    asyncio.run(run_migration(dry_run=args.dry_run))
