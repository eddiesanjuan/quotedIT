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
from sqlalchemy.orm import sessionmaker

from ..config import settings
from ..models.database import (
    Base, User, Contractor, PricingModel, ContractorTerms,
    Quote, JobType, SetupConversation, UserIssue
)


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
                if hasattr(contractor, key) and value is not None:
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
    ) -> Optional[PricingModel]:
        """
        Apply learnings from quote corrections to the pricing model.
        This is the core of the learning loop.
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

            # Apply pricing adjustments
            for adjustment in learnings.get("pricing_adjustments", []):
                item_type = adjustment.get("item_type")
                if item_type:
                    if item_type not in pricing_knowledge:
                        pricing_knowledge[item_type] = {}

                    existing = pricing_knowledge[item_type]
                    if isinstance(existing, dict):
                        # Weighted average: 70% existing, 30% new
                        if "base_rate" in existing or "base_per_sqft" in existing:
                            rate_key = "base_rate" if "base_rate" in existing else "base_per_sqft"
                            old_rate = existing.get(rate_key, 0)
                            new_rate = adjustment.get("corrected_value", old_rate)
                            existing[rate_key] = old_rate * 0.7 + new_rate * 0.3

                        existing["samples"] = existing.get("samples", 1) + 1
                        existing["confidence"] = min(0.95, existing.get("confidence", 0.5) + 0.02)

                    pricing_knowledge[item_type] = existing

            # Add new pricing rules
            for rule in learnings.get("new_pricing_rules", []):
                rule_key = rule.get("applies_to", "general")
                if rule_key not in pricing_knowledge:
                    pricing_knowledge[rule_key] = {}

                if isinstance(pricing_knowledge[rule_key], dict):
                    existing_notes = pricing_knowledge[rule_key].get("notes", "")
                    new_note = rule.get("rule", "")
                    if new_note and new_note not in existing_notes:
                        pricing_knowledge[rule_key]["notes"] = f"{existing_notes}\n{new_note}".strip()

            # Update pricing notes
            tendency = learnings.get("overall_tendency", "")
            if tendency:
                current_notes = pricing_model.pricing_notes or ""
                if tendency not in current_notes:
                    pricing_model.pricing_notes = f"{current_notes}\n\nLearned: {tendency}".strip()

            # Update model
            pricing_model.pricing_knowledge = pricing_knowledge
            pricing_model.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(pricing_model)
            return pricing_model

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

    async def create_setup_conversation(
        self,
        contractor_id: str,
        messages: List[Dict],
    ) -> SetupConversation:
        """Create a setup conversation record."""
        async with async_session_factory() as session:
            conversation = SetupConversation(
                contractor_id=contractor_id,
                messages=messages,
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

    async def get_new_issues(self) -> List[UserIssue]:
        """Get all issues with status='new'."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(UserIssue)
                .where(UserIssue.status == "new")
                .order_by(UserIssue.created_at)
            )
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


# Singleton pattern
_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get the database service singleton."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
