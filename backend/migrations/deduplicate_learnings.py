"""
Deduplication script: Remove semantic duplicates from Learning table

DISC-055: Semantic Learning Deduplication

This script:
1. Reads all learnings for each contractor
2. Generates embeddings for learnings without them
3. Clusters semantically similar learnings (0.90+ similarity)
4. Keeps the best learning from each cluster
5. Deletes duplicates

Usage:
    python -m backend.migrations.deduplicate_learnings [--dry-run] [--threshold 0.90]
"""

import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import (
    Contractor,
    Learning,
    async_session_factory,
    init_db,
)
from backend.services.embeddings import get_embedding_service


async def deduplicate_contractor_learnings(
    session: AsyncSession,
    contractor: Contractor,
    similarity_threshold: float = 0.90,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Deduplicate learnings for one contractor.

    Returns:
        Dict with deduplication stats
    """
    embedding_service = get_embedding_service()

    # Get all learnings for this contractor
    result = await session.execute(
        select(Learning).where(Learning.contractor_id == contractor.id)
    )
    learnings = result.scalars().all()

    if not learnings:
        return {
            "original_count": 0,
            "final_count": 0,
            "deleted_count": 0,
            "categories_processed": 0,
        }

    original_count = len(learnings)

    # Process by category for better accuracy
    categories = {}
    for learning in learnings:
        category = learning.category
        if category not in categories:
            categories[category] = []
        categories[category].append(learning)

    total_deleted = 0
    total_kept = 0

    for category, category_learnings in categories.items():
        print(f"  Processing category: {category} ({len(category_learnings)} learnings)")

        # Convert to dicts
        learning_dicts = []
        for learning in category_learnings:
            # Generate embedding if missing
            if not learning.embedding:
                learning.embedding = await embedding_service.generate_embedding(
                    learning.adjustment
                )

            learning_dicts.append({
                "id": learning.id,
                "category": learning.category,
                "learning_type": learning.learning_type,
                "target": learning.target,
                "adjustment": learning.adjustment,
                "reason": learning.reason,
                "confidence": learning.confidence,
                "sample_count": learning.sample_count,
                "total_impact_dollars": learning.total_impact_dollars,
                "priority_score": learning.priority_score,
                "embedding": learning.embedding,
                "last_seen_at": learning.last_seen_at,
                "created_at": learning.created_at,
                "orm_object": learning,
            })

        # Deduplicate this category
        deduplicated, stats = await embedding_service.deduplicate_learnings(
            learning_dicts,
            similarity_threshold=similarity_threshold
        )

        # Find learnings to delete (those not in deduplicated list)
        kept_ids = {l["id"] for l in deduplicated}
        to_delete = [l for l in category_learnings if l.id not in kept_ids]

        print(f"    Original: {stats['original_count']}, Clusters: {stats['clusters_found']}, Final: {stats['final_count']}, Reduction: {stats['reduction_percent']}%")

        if not dry_run:
            # Delete duplicates
            for learning in to_delete:
                await session.delete(learning)

            # Update kept learnings with merged metadata
            for dedup_dict in deduplicated:
                if dedup_dict.get("was_deduplicated"):
                    learning = dedup_dict["orm_object"]
                    learning.sample_count = dedup_dict["sample_count"]
                    learning.total_impact_dollars = dedup_dict["total_impact_dollars"]
                    learning.confidence = dedup_dict["confidence"]
                    # Add note about deduplication
                    if learning.reason:
                        learning.reason += f" [Merged {dedup_dict['merged_count']} similar learnings]"
                    else:
                        learning.reason = f"Merged {dedup_dict['merged_count']} similar learnings"

        total_deleted += len(to_delete)
        total_kept += len(deduplicated)

    if not dry_run:
        await session.commit()

    return {
        "original_count": original_count,
        "final_count": total_kept,
        "deleted_count": total_deleted,
        "categories_processed": len(categories),
    }


async def run_deduplication(
    similarity_threshold: float = 0.90,
    dry_run: bool = False
):
    """
    Run deduplication across all contractors.
    """
    print("=" * 60)
    print("DISC-055: Semantic Learning Deduplication")
    print("=" * 60)
    print(f"Similarity threshold: {similarity_threshold}")
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
            "original_count": 0,
            "final_count": 0,
            "deleted_count": 0,
            "categories_processed": 0,
        }

        for contractor in contractors:
            print(f"Processing contractor: {contractor.business_name} ({contractor.id})")

            stats = await deduplicate_contractor_learnings(
                session, contractor, similarity_threshold, dry_run
            )

            total_stats["contractors_processed"] += 1
            total_stats["original_count"] += stats["original_count"]
            total_stats["final_count"] += stats["final_count"]
            total_stats["deleted_count"] += stats["deleted_count"]
            total_stats["categories_processed"] += stats["categories_processed"]

            if stats["original_count"] > 0:
                reduction = (stats["deleted_count"] / stats["original_count"] * 100)
                print(f"  ✓ Deleted: {stats['deleted_count']}, Kept: {stats['final_count']}, Reduction: {reduction:.1f}%")
            print()

    print("=" * 60)
    print("Deduplication Complete")
    print("=" * 60)
    print(f"Contractors processed: {total_stats['contractors_processed']}")
    print(f"Categories processed: {total_stats['categories_processed']}")
    print(f"Original learnings: {total_stats['original_count']}")
    print(f"Final learnings: {total_stats['final_count']}")
    print(f"Deleted duplicates: {total_stats['deleted_count']}")

    if total_stats["original_count"] > 0:
        reduction = (total_stats["deleted_count"] / total_stats["original_count"] * 100)
        print(f"Overall reduction: {reduction:.1f}%")

    print()

    if dry_run:
        print("✅ Dry run successful - rerun without --dry-run to apply changes")
    else:
        print("✅ Deduplication successful - duplicates removed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate learnings using semantic similarity")
    parser.add_argument("--dry-run", action="store_true", help="Run without making changes")
    parser.add_argument("--threshold", type=float, default=0.90, help="Similarity threshold (0.0-1.0)")
    args = parser.parse_args()

    asyncio.run(run_deduplication(
        similarity_threshold=args.threshold,
        dry_run=args.dry_run
    ))
