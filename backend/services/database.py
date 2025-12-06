"""
Database service for Quoted.
Provides async CRUD operations for all models.

This is the single source of truth for data persistence.
All API endpoints should use these functions instead of in-memory storage.
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, attributes

from ..config import settings
from ..models.database import (
    Base, User, Contractor, PricingModel, ContractorTerms,
    Quote, JobType, SetupConversation, UserIssue, QuoteFeedback, Learning
)
from .analytics import analytics_service
from .embeddings import get_embedding_service


# Create async engine and session factory
engine = create_async_engine(settings.async_database_url, echo=False)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Get a new database session."""
    async with async_session_factory() as session:
        yield session


class DatabaseService:
    """
    Unified database service for all Quoted models.
    Provides clean async CRUD operations.
    """

    def __init__(self):
        self.engine = engine

    async def _get_session(self) -> AsyncSession:
        """Create a new session."""
        return async_session_factory()

    # ============== USER OPERATIONS ==============

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

    # ============== CONTRACTOR OPERATIONS ==============

    async def create_contractor(
        self,
        user_id: str,
        business_name: str,
        email: str,
        primary_trade: str,
        owner_name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        services: Optional[List[str]] = None,
    ) -> Contractor:
        """Create a new contractor profile."""
        async with async_session_factory() as session:
            contractor = Contractor(
                user_id=user_id,
                business_name=business_name,
                email=email,
                primary_trade=primary_trade,
                owner_name=owner_name,
                phone=phone,
                address=address,
                services=services or [],
            )
            session.add(contractor)
            await session.commit()
            await session.refresh(contractor)
            return contractor

    async def get_contractor_by_id(self, contractor_id: str) -> Optional[Contractor]:
        """Get a contractor by ID."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Contractor).where(Contractor.id == contractor_id)
            )
            return result.scalar_one_or_none()

    async def get_contractor_by_user_id(self, user_id: str) -> Optional[Contractor]:
        """Get a contractor by user ID."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Contractor).where(Contractor.user_id == user_id)
            )
            return result.scalar_one_or_none()

    async def update_contractor(
        self,
        contractor_id: str,
        **kwargs
    ) -> Optional[Contractor]:
        """Update a contractor."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Contractor).where(Contractor.id == contractor_id)
            )
            contractor = result.scalar_one_or_none()
            if not contractor:
                return None

            for key, value in kwargs.items():
                # Allow setting logo_data to None (for deletion)
                if hasattr(contractor, key):
                    if key == 'logo_data' or value is not None:
                        setattr(contractor, key, value)

            contractor.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(contractor)
            return contractor

    # ============== PRICING MODEL OPERATIONS ==============

    async def create_pricing_model(
        self,
        contractor_id: str,
        labor_rate_hourly: Optional[float] = None,
        helper_rate_hourly: Optional[float] = None,
        material_markup_percent: float = 20.0,
        minimum_job_amount: Optional[float] = None,
        pricing_knowledge: Optional[Dict] = None,
        pricing_notes: Optional[str] = None,
    ) -> PricingModel:
        """Create a new pricing model for a contractor."""
        async with async_session_factory() as session:
            pricing_model = PricingModel(
                contractor_id=contractor_id,
                labor_rate_hourly=labor_rate_hourly,
                helper_rate_hourly=helper_rate_hourly,
                material_markup_percent=material_markup_percent,
                minimum_job_amount=minimum_job_amount,
                pricing_knowledge=pricing_knowledge or {},
                pricing_notes=pricing_notes,
            )
            session.add(pricing_model)
            await session.commit()
            await session.refresh(pricing_model)
            return pricing_model

    async def get_pricing_model(self, contractor_id: str) -> Optional[PricingModel]:
        """Get a contractor's pricing model."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(PricingModel).where(PricingModel.contractor_id == contractor_id)
            )
            return result.scalar_one_or_none()

    async def update_pricing_model(
        self,
        contractor_id: str,
        **kwargs
    ) -> Optional[PricingModel]:
        """Update a pricing model."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(PricingModel).where(PricingModel.contractor_id == contractor_id)
            )
            pricing_model = result.scalar_one_or_none()
            if not pricing_model:
                return None

            for key, value in kwargs.items():
                if hasattr(pricing_model, key) and value is not None:
                    setattr(pricing_model, key, value)

            pricing_model.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(pricing_model)
            return pricing_model

    async def apply_learnings_to_pricing_model(
        self,
        contractor_id: str,
        learnings: Dict[str, Any],
        category: Optional[str] = None,
    ) -> Optional[PricingModel]:
        """
        Apply learnings from quote corrections to the pricing model.
        This is the core of the learning loop.

        Learnings are stored per-category in:
        pricing_knowledge["categories"][category]["learned_adjustments"]

        Args:
            contractor_id: The contractor's ID
            learnings: Dict with pricing_adjustments, new_pricing_rules, overall_tendency
            category: The category (job_type) this correction applies to
        """
        async with async_session_factory() as session:
            result = await session.execute(
                select(PricingModel).where(PricingModel.contractor_id == contractor_id)
            )
            pricing_model = result.scalar_one_or_none()
            if not pricing_model:
                return None

            # Get current pricing knowledge
            pricing_knowledge = pricing_model.pricing_knowledge or {}

            # Ensure categories structure exists
            if "categories" not in pricing_knowledge:
                pricing_knowledge["categories"] = {}

            # Ensure global_rules exists
            if "global_rules" not in pricing_knowledge:
                pricing_knowledge["global_rules"] = []

            # If we have a category, store learnings there
            if category:
                # Initialize category if it doesn't exist
                if category not in pricing_knowledge["categories"]:
                    pricing_knowledge["categories"][category] = {
                        "display_name": category.replace("_", " ").title(),
                        "learned_adjustments": [],
                        "samples": 0,
                        "confidence": 0.5,
                        "correction_count": 0,  # DISC-035
                    }

                cat_data = pricing_knowledge["categories"][category]

                # Ensure learned_adjustments list exists
                if "learned_adjustments" not in cat_data:
                    cat_data["learned_adjustments"] = []

                # Convert pricing adjustments to text statements
                for adjustment in learnings.get("pricing_adjustments", []):
                    item_type = adjustment.get("item_type", "item")
                    original = adjustment.get("original_value", 0)
                    corrected = adjustment.get("corrected_value", 0)
                    reason = adjustment.get("reason", "")

                    # Build a human-readable learning statement
                    if corrected > original:
                        change_pct = ((corrected - original) / original * 100) if original > 0 else 0
                        statement = f"Increase {item_type} by ~{change_pct:.0f}%"
                        if reason:
                            statement += f" ({reason})"
                    elif corrected < original:
                        change_pct = ((original - corrected) / original * 100) if original > 0 else 0
                        statement = f"Reduce {item_type} by ~{change_pct:.0f}%"
                        if reason:
                            statement += f" ({reason})"
                    else:
                        continue  # No change, skip

                    # Add if not duplicate (fuzzy check)
                    if statement and not any(statement.lower() in adj.lower() or adj.lower() in statement.lower()
                                             for adj in cat_data["learned_adjustments"]):
                        cat_data["learned_adjustments"].append(statement)

                # Add new pricing rules as learned adjustments
                for rule in learnings.get("new_pricing_rules", []):
                    applies_to = rule.get("applies_to", "")
                    rule_text = rule.get("rule", "")

                    # If rule applies to this category or is general, add it
                    if applies_to == category or applies_to in ["general", ""]:
                        if rule_text and rule_text not in cat_data["learned_adjustments"]:
                            cat_data["learned_adjustments"].append(rule_text)

                # Add overall tendency as a learned adjustment
                tendency = learnings.get("overall_tendency", "")
                if tendency and tendency not in cat_data["learned_adjustments"]:
                    cat_data["learned_adjustments"].append(tendency)

                # Update samples and correction count
                cat_data["samples"] = cat_data.get("samples", 0) + 1
                cat_data["correction_count"] = cat_data.get("correction_count", 0) + 1

                # DISC-054: Dynamic Learning Rate - adjust confidence increment based on correction count
                # Early learning (< 5 corrections): aggressive learning, larger confidence increments
                # Mid learning (5-15 corrections): balanced learning, moderate increments
                # Late learning (> 15 corrections): conservative refinement, small increments
                correction_count = cat_data["correction_count"]
                if correction_count < 5:
                    confidence_increment = 0.04  # Aggressive: 60% new learning (2x baseline)
                elif correction_count < 15:
                    confidence_increment = 0.02  # Balanced: 30% new learning (1x baseline)
                else:
                    confidence_increment = 0.01  # Conservative: 15% new learning (0.5x baseline)

                cat_data["confidence"] = min(0.95, cat_data.get("confidence", 0.5) + confidence_increment)

                # DISC-054: Track learning velocity metrics
                try:
                    # Get user_id for analytics (contractor_id is user_id)
                    analytics_service.track_event(
                        user_id=contractor_id,
                        event_name="dynamic_learning_rate_applied",
                        properties={
                            "category": category,
                            "correction_count": correction_count,
                            "learning_phase": "aggressive" if correction_count < 5 else ("balanced" if correction_count < 15 else "conservative"),
                            "confidence_increment": confidence_increment,
                            "new_confidence": cat_data["confidence"],
                            "samples": cat_data["samples"],
                        }
                    )
                except Exception as e:
                    # Don't fail learning if analytics fails
                    print(f"Warning: Failed to track learning velocity: {e}")

                # Keep learned_adjustments manageable (max 20 per category)
                if len(cat_data["learned_adjustments"]) > 20:
                    # Keep most recent 20
                    cat_data["learned_adjustments"] = cat_data["learned_adjustments"][-20:]

                pricing_knowledge["categories"][category] = cat_data

            else:
                # No category specified - add rules to global_rules
                for rule in learnings.get("new_pricing_rules", []):
                    rule_text = rule.get("rule", "")
                    if rule_text and rule_text not in pricing_knowledge["global_rules"]:
                        pricing_knowledge["global_rules"].append(rule_text)

                tendency = learnings.get("overall_tendency", "")
                if tendency and tendency not in pricing_knowledge["global_rules"]:
                    pricing_knowledge["global_rules"].append(tendency)

            # Also update pricing_notes for backward compatibility
            tendency = learnings.get("overall_tendency", "")
            if tendency:
                current_notes = pricing_model.pricing_notes or ""
                if tendency not in current_notes:
                    pricing_model.pricing_notes = f"{current_notes}\n\nLearned: {tendency}".strip()

            # Update model - must flag_modified for SQLAlchemy to detect JSON mutation
            pricing_model.pricing_knowledge = pricing_knowledge
            pricing_model.updated_at = datetime.utcnow()
            attributes.flag_modified(pricing_model, 'pricing_knowledge')

            # DISC-053: Dual-write to structured Learning table
            # Create Learning records for new learnings during transition period
            if category:
                await self._create_structured_learnings(
                    session=session,
                    contractor_id=contractor_id,
                    category=category,
                    learnings=learnings,
                    cat_data=pricing_knowledge["categories"][category]
                )

            await session.commit()
            await session.refresh(pricing_model)
            return pricing_model

    async def _create_structured_learnings(
        self,
        session: AsyncSession,
        contractor_id: str,
        category: str,
        learnings: Dict[str, Any],
        cat_data: Dict[str, Any],
    ):
        """
        DISC-053: Create structured Learning records (dual-write mode).
        DISC-055: Generate embeddings and check for semantic duplicates.

        This is called during apply_learnings_to_pricing_model to maintain
        both text-based and structured formats during the transition period.
        """
        # Get category metadata
        confidence = cat_data.get("confidence", 0.5)
        correction_count = cat_data.get("correction_count", 1)

        # Get embedding service for semantic similarity
        embedding_service = get_embedding_service()

        # Process pricing adjustments
        for adjustment in learnings.get("pricing_adjustments", []):
            item_type = adjustment.get("item_type", "item")
            original = adjustment.get("original_value", 0)
            corrected = adjustment.get("corrected_value", 0)
            reason = adjustment.get("reason", "")

            # Build statement (same logic as text-based)
            if corrected > original:
                change_pct = ((corrected - original) / original * 100) if original > 0 else 0
                statement = f"Increase {item_type} by ~{change_pct:.0f}%"
                if reason:
                    statement += f" ({reason})"
            elif corrected < original:
                change_pct = ((original - corrected) / original * 100) if original > 0 else 0
                statement = f"Reduce {item_type} by ~{change_pct:.0f}%"
                if reason:
                    statement += f" ({reason})"
            else:
                continue  # No change

            # Calculate impact
            impact_dollars = abs(corrected - original)

            # Calculate priority score
            priority_score = 0.8 * 0.3 + confidence * 0.5 + min(1.0, impact_dollars / 1000) * 0.2

            # DISC-055: Generate embedding for new learning
            embedding = await embedding_service.generate_embedding(statement)

            # Check if similar learning already exists (semantic similarity)
            existing_result = await session.execute(
                select(Learning).where(
                    Learning.contractor_id == contractor_id,
                    Learning.category == category,
                    Learning.target == item_type,
                ).order_by(Learning.created_at.desc()).limit(20)
            )
            existing_learnings = existing_result.scalars().all()

            # DISC-055: Use semantic similarity to find duplicates (0.90+ threshold)
            found_match = None
            if existing_learnings:
                # Convert to dicts for embedding service
                existing_dicts = []
                for el in existing_learnings:
                    existing_dicts.append({
                        "id": el.id,
                        "adjustment": el.adjustment,
                        "embedding": el.embedding,
                        "object": el  # Keep reference to ORM object
                    })

                # Find semantically similar learnings
                similar = await embedding_service.find_similar_learnings(
                    statement,
                    existing_dicts,
                    similarity_threshold=0.90
                )

                if similar:
                    # Use the most similar one
                    found_match = similar[0][0]["object"]

            if found_match:
                # Update existing learning
                found_match.sample_count += 1
                found_match.total_impact_dollars += impact_dollars
                found_match.last_seen_at = datetime.utcnow()
                found_match.confidence = min(0.95, found_match.confidence + 0.02)
                found_match.priority_score = priority_score
                # Update embedding to latest version
                found_match.embedding = embedding
            else:
                # Create new Learning record with embedding
                learning = Learning(
                    contractor_id=contractor_id,
                    category=category,
                    learning_type="adjustment",
                    target=item_type,
                    adjustment=statement,
                    reason=reason if reason else None,
                    confidence=confidence,
                    sample_count=1,
                    total_impact_dollars=impact_dollars,
                    priority_score=priority_score,
                    embedding=embedding,  # DISC-055: Store embedding
                    created_at=datetime.utcnow(),
                    last_seen_at=datetime.utcnow(),
                    examples=[{
                        "original": original,
                        "corrected": corrected,
                        "timestamp": datetime.utcnow().isoformat()
                    }],
                )
                session.add(learning)

        # Process new pricing rules
        for rule in learnings.get("new_pricing_rules", []):
            rule_text = rule.get("rule", "")
            applies_to = rule.get("applies_to", "general")

            if rule_text and (applies_to == category or applies_to in ["general", ""]):
                # Calculate priority (rules are generally important)
                priority_score = 0.7 * 0.3 + confidence * 0.5 + 0.3 * 0.2

                # DISC-055: Generate embedding
                embedding = await embedding_service.generate_embedding(rule_text)

                learning = Learning(
                    contractor_id=contractor_id,
                    category=category,
                    learning_type="rule",
                    target=applies_to,
                    adjustment=rule_text,
                    reason=None,
                    confidence=confidence,
                    sample_count=1,
                    total_impact_dollars=0.0,
                    priority_score=priority_score,
                    embedding=embedding,  # DISC-055: Store embedding
                    created_at=datetime.utcnow(),
                    last_seen_at=datetime.utcnow(),
                )
                session.add(learning)

        # Process overall tendency
        tendency = learnings.get("overall_tendency", "")
        if tendency:
            priority_score = 0.6 * 0.3 + confidence * 0.5 + 0.2 * 0.2

            # DISC-055: Generate embedding
            embedding = await embedding_service.generate_embedding(tendency)

            learning = Learning(
                contractor_id=contractor_id,
                category=category,
                learning_type="tendency",
                target="general",
                adjustment=tendency,
                reason=None,
                confidence=confidence,
                sample_count=correction_count,
                total_impact_dollars=0.0,
                priority_score=priority_score,
                embedding=embedding,  # DISC-055: Store embedding
                created_at=datetime.utcnow(),
                last_seen_at=datetime.utcnow(),
            )
            session.add(learning)

    async def ensure_category_exists(
        self,
        contractor_id: str,
        category: str,
        display_name: Optional[str] = None,
    ) -> bool:
        """
        Ensure a category exists in the contractor's pricing_knowledge.
        This is called after quote generation to register new categories
        so they can be matched against in future quotes.

        Args:
            contractor_id: The contractor's ID
            category: The category name (snake_case)
            display_name: Optional human-readable name

        Returns:
            True if category was newly created, False if it already existed
        """
        async with async_session_factory() as session:
            result = await session.execute(
                select(PricingModel).where(PricingModel.contractor_id == contractor_id)
            )
            pricing_model = result.scalar_one_or_none()
            if not pricing_model:
                print(f"[SYNC DEBUG] No pricing model found for contractor {contractor_id}")
                return False

            # Get current pricing knowledge - MUST make a copy to ensure mutation is detected
            pricing_knowledge = dict(pricing_model.pricing_knowledge) if pricing_model.pricing_knowledge else {}
            print(f"[SYNC DEBUG] Current pricing_knowledge keys: {list(pricing_knowledge.keys())}")

            # Ensure categories structure exists
            if "categories" not in pricing_knowledge:
                pricing_knowledge["categories"] = {}

            # Check if category already exists
            if category in pricing_knowledge["categories"]:
                print(f"[SYNC DEBUG] Category '{category}' already exists")
                return False

            # Create the new category with minimal structure
            # (no learned_adjustments yet - that comes from quote edits)
            pricing_knowledge["categories"][category] = {
                "display_name": display_name or category.replace("_", " ").title(),
                "learned_adjustments": [],
                "samples": 0,
                "confidence": 0.5,
                "correction_count": 0,  # DISC-035
            }
            print(f"[SYNC DEBUG] Adding category '{category}', total categories: {len(pricing_knowledge['categories'])}")

            # Update model - assign new dict to ensure SQLAlchemy detects the change
            pricing_model.pricing_knowledge = pricing_knowledge
            pricing_model.updated_at = datetime.utcnow()
            attributes.flag_modified(pricing_model, 'pricing_knowledge')

            await session.commit()
            print(f"[SYNC DEBUG] Committed category '{category}'")
            return True

    # ============== TERMS OPERATIONS ==============

    async def create_terms(
        self,
        contractor_id: str,
        deposit_percent: float = 50.0,
        quote_valid_days: int = 30,
        labor_warranty_years: int = 2,
        **kwargs
    ) -> ContractorTerms:
        """Create terms for a contractor."""
        async with async_session_factory() as session:
            terms = ContractorTerms(
                contractor_id=contractor_id,
                deposit_percent=deposit_percent,
                quote_valid_days=quote_valid_days,
                labor_warranty_years=labor_warranty_years,
                **kwargs
            )
            session.add(terms)
            await session.commit()
            await session.refresh(terms)
            return terms

    async def get_terms(self, contractor_id: str) -> Optional[ContractorTerms]:
        """Get a contractor's terms."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(ContractorTerms).where(ContractorTerms.contractor_id == contractor_id)
            )
            return result.scalar_one_or_none()

    async def update_terms(
        self,
        contractor_id: str,
        **kwargs
    ) -> Optional[ContractorTerms]:
        """Update terms."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(ContractorTerms).where(ContractorTerms.contractor_id == contractor_id)
            )
            terms = result.scalar_one_or_none()
            if not terms:
                return None

            for key, value in kwargs.items():
                if hasattr(terms, key) and value is not None:
                    setattr(terms, key, value)

            await session.commit()
            await session.refresh(terms)
            return terms

    # ============== QUOTE OPERATIONS ==============

    async def create_quote(
        self,
        contractor_id: str,
        transcription: str,
        job_type: Optional[str] = None,
        job_description: Optional[str] = None,
        line_items: Optional[List[Dict]] = None,
        subtotal: float = 0,
        customer_name: Optional[str] = None,
        customer_address: Optional[str] = None,
        customer_phone: Optional[str] = None,
        estimated_days: Optional[int] = None,
        notes: Optional[str] = None,
        ai_generated_total: Optional[float] = None,
        **kwargs
    ) -> Quote:
        """Create a new quote."""
        async with async_session_factory() as session:
            quote = Quote(
                contractor_id=contractor_id,
                transcription=transcription,
                job_type=job_type,
                job_description=job_description,
                line_items=line_items or [],
                subtotal=subtotal,
                total=subtotal,  # Can be adjusted later for taxes/discounts
                ai_generated_total=ai_generated_total or subtotal,
                customer_name=customer_name,
                customer_address=customer_address,
                customer_phone=customer_phone,
                estimated_days=estimated_days,
            )
            session.add(quote)
            await session.commit()
            await session.refresh(quote)
            return quote

    async def get_quote(self, quote_id: str) -> Optional[Quote]:
        """Get a quote by ID."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Quote).where(Quote.id == quote_id)
            )
            return result.scalar_one_or_none()

    async def get_quote_by_share_token(self, share_token: str) -> Optional[Quote]:
        """Get a quote by share token (for public access)."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Quote).where(Quote.share_token == share_token)
            )
            return result.scalar_one_or_none()

    async def update_quote(
        self,
        quote_id: str,
        **kwargs
    ) -> Optional[Quote]:
        """Update a quote."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Quote).where(Quote.id == quote_id)
            )
            quote = result.scalar_one_or_none()
            if not quote:
                return None

            for key, value in kwargs.items():
                if hasattr(quote, key) and value is not None:
                    setattr(quote, key, value)

            # Recalculate subtotal if line_items changed
            if "line_items" in kwargs and kwargs["line_items"]:
                quote.subtotal = sum(item.get("amount", 0) for item in kwargs["line_items"])
                quote.total = quote.subtotal

            quote.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(quote)
            return quote

    async def get_quotes_by_contractor(
        self,
        contractor_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Quote]:
        """Get all quotes for a contractor."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Quote)
                .where(Quote.contractor_id == contractor_id)
                .order_by(Quote.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return list(result.scalars().all())

    async def get_quote_history_for_learning(
        self,
        contractor_id: str,
        limit: int = 100,
    ) -> List[Dict]:
        """Get quote history formatted for learning analysis."""
        quotes = await self.get_quotes_by_contractor(contractor_id, limit=limit)
        return [
            {
                "id": q.id,
                "job_type": q.job_type,
                "was_edited": q.was_edited,
                "edit_details": q.edit_details,
                "ai_generated_total": q.ai_generated_total,
                "final_total": q.total,
                "outcome": q.outcome,
            }
            for q in quotes
        ]

    async def get_correction_examples(
        self,
        contractor_id: str,
        limit: int = 5,
        job_type: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get recent edited quotes formatted for few-shot learning injection.

        Returns quotes where was_edited=True with their original vs final state.
        Used to inject into the quote generation prompt so Claude can learn
        from past corrections.

        Args:
            contractor_id: The contractor's ID
            limit: Max examples to return (default 5 to avoid token bloat)
            job_type: Optional filter to get examples of specific job type

        Returns:
            List of correction examples with original/final state for prompt injection
        """
        async with async_session_factory() as session:
            query = (
                select(Quote)
                .where(Quote.contractor_id == contractor_id)
                .where(Quote.was_edited == True)
            )

            # Optionally filter by job type for more relevant examples
            if job_type:
                query = query.where(Quote.job_type == job_type)

            query = query.order_by(Quote.updated_at.desc()).limit(limit)

            result = await session.execute(query)
            quotes = list(result.scalars().all())

        # Format for prompt injection
        examples = []
        for q in quotes:
            edit_details = q.edit_details or {}

            example = {
                "job_type": q.job_type or "Unknown",
                "original_total": q.ai_generated_total or 0,
                "final_total": q.total or 0,
                "original_line_items": edit_details.get("original_line_items", []),
                "final_line_items": q.line_items or [],
                "correction_notes": edit_details.get("learning_note", ""),
            }
            examples.append(example)

        return examples

    # ============== SETUP CONVERSATION OPERATIONS ==============

    async def get_setup_conversation(
        self,
        conversation_id: str,
    ) -> Optional[SetupConversation]:
        """Get a setup conversation by ID."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(SetupConversation).where(SetupConversation.id == conversation_id)
            )
            return result.scalar_one_or_none()

    async def create_setup_conversation(
        self,
        messages: List[Dict],
        session_data: Optional[Dict] = None,
        contractor_id: Optional[str] = None,
    ) -> SetupConversation:
        """Create a setup conversation record."""
        async with async_session_factory() as session:
            conversation = SetupConversation(
                contractor_id=contractor_id,
                messages=messages,
                session_data=session_data or {},
                status="in_progress",
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation

    async def update_setup_conversation(
        self,
        conversation_id: str,
        messages: Optional[List[Dict]] = None,
        session_data: Optional[Dict] = None,
        status: Optional[str] = None,
        extracted_data: Optional[Dict] = None,
    ) -> Optional[SetupConversation]:
        """Update a setup conversation."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(SetupConversation).where(SetupConversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                return None

            if messages is not None:
                conversation.messages = messages
            if session_data is not None:
                conversation.session_data = session_data
            if status is not None:
                conversation.status = status
                if status == "completed":
                    conversation.completed_at = datetime.utcnow()
            if extracted_data is not None:
                conversation.extracted_data = extracted_data

            await session.commit()
            await session.refresh(conversation)
            return conversation

    # ============== ISSUE OPERATIONS ==============

    async def create_issue(
        self,
        title: str,
        description: str,
        category: str = "bug",
        severity: str = "medium",
        user_id: Optional[str] = None,
        **kwargs
    ) -> UserIssue:
        """Create a new user issue."""
        async with async_session_factory() as session:
            issue = UserIssue(
                title=title,
                description=description,
                category=category,
                severity=severity,
                user_id=user_id,
                **kwargs
            )
            session.add(issue)
            await session.commit()
            await session.refresh(issue)
            return issue

    async def get_issue(self, issue_id: str) -> Optional[UserIssue]:
        """Get a single issue by ID."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(UserIssue).where(UserIssue.id == issue_id)
            )
            return result.scalar_one_or_none()

    async def get_new_issues(self) -> List[UserIssue]:
        """Get all issues with status='new'."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(UserIssue)
                .where(UserIssue.status == "new")
                .order_by(UserIssue.created_at)
            )
            return list(result.scalars().all())

    async def get_all_issues(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[UserIssue]:
        """Get all issues, optionally filtered by status and/or category."""
        async with async_session_factory() as session:
            query = select(UserIssue)

            if status:
                query = query.where(UserIssue.status == status)
            if category:
                query = query.where(UserIssue.category == category)

            query = query.order_by(UserIssue.created_at.desc())

            result = await session.execute(query)
            return list(result.scalars().all())

    async def update_issue(
        self,
        issue_id: str,
        **kwargs
    ) -> Optional[UserIssue]:
        """Update an issue."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(UserIssue).where(UserIssue.id == issue_id)
            )
            issue = result.scalar_one_or_none()
            if not issue:
                return None

            for key, value in kwargs.items():
                if hasattr(issue, key) and value is not None:
                    setattr(issue, key, value)

            issue.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(issue)
            return issue

    # ============== QUOTE FEEDBACK OPERATIONS (Enhancement 4) ==============

    async def create_quote_feedback(
        self,
        quote_id: str,
        overall_rating: Optional[int] = None,
        pricing_accuracy: Optional[int] = None,
        description_quality: Optional[int] = None,
        line_item_completeness: Optional[int] = None,
        timeline_accuracy: Optional[int] = None,
        issues: Optional[List[str]] = None,
        pricing_direction: Optional[str] = None,
        pricing_off_by_percent: Optional[float] = None,
        actual_total: Optional[float] = None,
        actual_line_items: Optional[List[Dict]] = None,
        feedback_text: Optional[str] = None,
        improvement_suggestions: Optional[str] = None,
        quote_was_sent: Optional[bool] = None,
        quote_outcome: Optional[str] = None,
    ) -> QuoteFeedback:
        """Create feedback for a quote."""
        async with async_session_factory() as session:
            feedback = QuoteFeedback(
                quote_id=quote_id,
                overall_rating=overall_rating,
                pricing_accuracy=pricing_accuracy,
                description_quality=description_quality,
                line_item_completeness=line_item_completeness,
                timeline_accuracy=timeline_accuracy,
                issues=issues or [],
                pricing_direction=pricing_direction,
                pricing_off_by_percent=pricing_off_by_percent,
                actual_total=actual_total,
                actual_line_items=actual_line_items,
                feedback_text=feedback_text,
                improvement_suggestions=improvement_suggestions,
                quote_was_sent=quote_was_sent,
                quote_outcome=quote_outcome,
            )
            session.add(feedback)
            await session.commit()
            await session.refresh(feedback)
            return feedback

    async def get_quote_feedback(self, quote_id: str) -> Optional[QuoteFeedback]:
        """Get feedback for a specific quote."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(QuoteFeedback).where(QuoteFeedback.quote_id == quote_id)
            )
            return result.scalar_one_or_none()

    async def update_quote_feedback(
        self,
        feedback_id: str,
        **kwargs
    ) -> Optional[QuoteFeedback]:
        """Update quote feedback."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(QuoteFeedback).where(QuoteFeedback.id == feedback_id)
            )
            feedback = result.scalar_one_or_none()
            if not feedback:
                return None

            for key, value in kwargs.items():
                if hasattr(feedback, key) and value is not None:
                    setattr(feedback, key, value)

            feedback.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(feedback)
            return feedback

    async def get_feedback_stats(self, contractor_id: str) -> Dict[str, Any]:
        """Get aggregated feedback statistics for a contractor."""
        async with async_session_factory() as session:
            # Get all quotes for this contractor
            quotes_result = await session.execute(
                select(Quote.id).where(Quote.contractor_id == contractor_id)
            )
            quote_ids = [q for q in quotes_result.scalars().all()]

            if not quote_ids:
                return {
                    "total_quotes": 0,
                    "total_feedback": 0,
                    "feedback_rate": 0,
                    "average_rating": None,
                    "pricing_accuracy_avg": None,
                    "common_issues": [],
                    "pricing_direction_breakdown": {},
                }

            # Get all feedback for these quotes
            feedback_result = await session.execute(
                select(QuoteFeedback).where(QuoteFeedback.quote_id.in_(quote_ids))
            )
            feedbacks = list(feedback_result.scalars().all())

            total_quotes = len(quote_ids)
            total_feedback = len(feedbacks)

            if not feedbacks:
                return {
                    "total_quotes": total_quotes,
                    "total_feedback": 0,
                    "feedback_rate": 0,
                    "average_rating": None,
                    "pricing_accuracy_avg": None,
                    "common_issues": [],
                    "pricing_direction_breakdown": {},
                }

            # Calculate averages
            ratings = [f.overall_rating for f in feedbacks if f.overall_rating]
            pricing_ratings = [f.pricing_accuracy for f in feedbacks if f.pricing_accuracy]

            # Count issues
            issue_counts = {}
            for f in feedbacks:
                for issue in (f.issues or []):
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1

            # Pricing direction breakdown
            direction_counts = {}
            for f in feedbacks:
                if f.pricing_direction:
                    direction_counts[f.pricing_direction] = direction_counts.get(f.pricing_direction, 0) + 1

            return {
                "total_quotes": total_quotes,
                "total_feedback": total_feedback,
                "feedback_rate": round(total_feedback / total_quotes * 100, 1) if total_quotes else 0,
                "average_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                "pricing_accuracy_avg": round(sum(pricing_ratings) / len(pricing_ratings), 2) if pricing_ratings else None,
                "common_issues": sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "pricing_direction_breakdown": direction_counts,
            }


# Singleton pattern
_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get the database service singleton."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
