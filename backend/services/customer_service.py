"""
Customer Service for Quoted CRM (DISC-087).
Handles customer aggregation, deduplication, and management.

Customers are auto-created from quote data and can be managed via voice/UI.
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from ..models.database import Customer, Quote, Contractor


class CustomerService:
    """Service for managing customer operations in the CRM."""

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize customer name for deduplication.
        - Lowercase
        - Remove punctuation
        - Collapse whitespace
        - Strip leading/trailing whitespace

        Args:
            name: Raw customer name

        Returns:
            str: Normalized name for matching
        """
        if not name:
            return ""
        # Lowercase
        normalized = name.lower()
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Collapse whitespace
        normalized = ' '.join(normalized.split())
        return normalized.strip()

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Normalize phone number for deduplication.
        - Extract digits only
        - Remove country code if 11+ digits starting with 1

        Args:
            phone: Raw phone number

        Returns:
            str: Digits-only phone number
        """
        if not phone:
            return ""
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        # Remove US country code if present (11 digits starting with 1)
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        return digits

    @staticmethod
    async def find_or_create_customer(
        db: AsyncSession,
        contractor_id: str,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None
    ) -> Optional[Customer]:
        """
        Find existing customer or create new one based on normalized name/phone.

        Deduplication strategy:
        1. If phone provided: match on (contractor_id, normalized_phone)
        2. If no phone match: match on (contractor_id, normalized_name)
        3. If no match: create new customer

        Args:
            db: Database session
            contractor_id: Contractor ID (customers are scoped to contractors)
            name: Customer name
            phone: Customer phone (optional)
            email: Customer email (optional)
            address: Customer address (optional)

        Returns:
            Customer: Found or created customer, None if insufficient data
        """
        # Require at least a name
        if not name or not name.strip():
            return None

        normalized_name = CustomerService.normalize_name(name)
        normalized_phone = CustomerService.normalize_phone(phone) if phone else None

        customer = None

        # Try to find by phone first (most reliable)
        if normalized_phone:
            result = await db.execute(
                select(Customer).where(
                    and_(
                        Customer.contractor_id == contractor_id,
                        Customer.normalized_phone == normalized_phone
                    )
                )
            )
            customer = result.scalar_one_or_none()

        # If no phone match, try by name
        if not customer and normalized_name:
            result = await db.execute(
                select(Customer).where(
                    and_(
                        Customer.contractor_id == contractor_id,
                        Customer.normalized_name == normalized_name
                    )
                )
            )
            customer = result.scalar_one_or_none()

        # If still no match, create new customer
        if not customer:
            customer = Customer(
                contractor_id=contractor_id,
                name=name.strip(),
                phone=phone,
                email=email,
                address=address,
                normalized_name=normalized_name,
                normalized_phone=normalized_phone or "",
                status="active"
            )
            db.add(customer)
            await db.flush()  # Get the ID without committing
        else:
            # Update customer with newer data if provided
            if email and not customer.email:
                customer.email = email
            if address and not customer.address:
                customer.address = address
            if phone and not customer.phone:
                customer.phone = phone
                customer.normalized_phone = normalized_phone
            customer.updated_at = datetime.utcnow()

        return customer

    @staticmethod
    async def link_quote_to_customer(
        db: AsyncSession,
        quote: Quote
    ) -> Optional[Customer]:
        """
        Link a quote to a customer record, creating the customer if needed.
        Also updates customer stats.

        Args:
            db: Database session
            quote: Quote to link

        Returns:
            Customer: The linked customer, or None if insufficient data
        """
        if not quote.customer_name:
            return None

        customer = await CustomerService.find_or_create_customer(
            db=db,
            contractor_id=quote.contractor_id,
            name=quote.customer_name,
            phone=getattr(quote, 'customer_phone', None),
            email=getattr(quote, 'customer_email', None),
            address=getattr(quote, 'customer_address', None)
        )

        if customer:
            # Link quote to customer via UPDATE statement
            # (quote object may be detached from this session)
            from sqlalchemy import update
            await db.execute(
                update(Quote)
                .where(Quote.id == quote.id)
                .values(customer_id=customer.id)
            )
            await db.flush()

            # Update customer stats
            await CustomerService.update_customer_stats(db, customer)

        return customer

    @staticmethod
    async def update_customer_stats(
        db: AsyncSession,
        customer: Customer
    ) -> None:
        """
        Recalculate and update customer computed fields.

        Args:
            db: Database session
            customer: Customer to update
        """
        # Get all quotes for this customer
        result = await db.execute(
            select(Quote).where(Quote.customer_id == customer.id)
        )
        quotes = result.scalars().all()

        # Calculate stats
        customer.quote_count = len(quotes)

        total_quoted = 0
        total_won = 0
        first_quote_at = None
        last_quote_at = None

        for quote in quotes:
            if quote.total:
                total_quoted += quote.total
                if quote.status == "won" or quote.outcome == "won":
                    total_won += quote.total

            if quote.created_at:
                if first_quote_at is None or quote.created_at < first_quote_at:
                    first_quote_at = quote.created_at
                if last_quote_at is None or quote.created_at > last_quote_at:
                    last_quote_at = quote.created_at

        customer.total_quoted = total_quoted
        customer.total_won = total_won
        customer.first_quote_at = first_quote_at
        customer.last_quote_at = last_quote_at
        customer.updated_at = datetime.utcnow()

    @staticmethod
    async def get_customers(
        db: AsyncSession,
        contractor_id: str,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        sort_by: str = "last_quote_at",
        sort_desc: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Customer], int]:
        """
        Get paginated list of customers for a contractor.

        Args:
            db: Database session
            contractor_id: Contractor ID
            search: Optional search term (name, phone, email)
            status_filter: Optional status filter (active, inactive, lead, vip)
            sort_by: Field to sort by (last_quote_at, name, total_quoted, quote_count)
            sort_desc: Sort descending
            limit: Max results per page
            offset: Pagination offset

        Returns:
            Tuple of (list of customers, total count)
        """
        # Base query
        base_query = select(Customer).where(Customer.contractor_id == contractor_id)

        # Apply search filter
        if search:
            search_term = f"%{search.lower()}%"
            base_query = base_query.where(
                or_(
                    func.lower(Customer.name).like(search_term),
                    func.lower(Customer.phone).like(search_term),
                    func.lower(Customer.email).like(search_term),
                    func.lower(Customer.address).like(search_term)
                )
            )

        # Apply status filter
        if status_filter:
            base_query = base_query.where(Customer.status == status_filter)

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(Customer, sort_by, Customer.last_quote_at)
        if sort_desc:
            base_query = base_query.order_by(sort_column.desc().nullslast())
        else:
            base_query = base_query.order_by(sort_column.asc().nullsfirst())

        # Apply pagination
        base_query = base_query.limit(limit).offset(offset)

        # Execute query
        result = await db.execute(base_query)
        customers = result.scalars().all()

        return list(customers), total_count

    @staticmethod
    async def get_customer_by_id(
        db: AsyncSession,
        contractor_id: str,
        customer_id: str,
        include_quotes: bool = False
    ) -> Optional[Customer]:
        """
        Get a single customer by ID.

        Args:
            db: Database session
            contractor_id: Contractor ID (for authorization)
            customer_id: Customer ID
            include_quotes: Whether to eagerly load quotes

        Returns:
            Customer or None
        """
        query = select(Customer).where(
            and_(
                Customer.id == customer_id,
                Customer.contractor_id == contractor_id
            )
        )

        if include_quotes:
            query = query.options(selectinload(Customer.quotes))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_customer(
        db: AsyncSession,
        contractor_id: str,
        customer_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Customer]:
        """
        Update a customer record.

        Allowed update fields: name, phone, email, address, status, notes, tags, source

        Args:
            db: Database session
            contractor_id: Contractor ID (for authorization)
            customer_id: Customer ID
            updates: Dict of field updates

        Returns:
            Updated customer or None if not found
        """
        customer = await CustomerService.get_customer_by_id(db, contractor_id, customer_id)
        if not customer:
            return None

        allowed_fields = {'name', 'phone', 'email', 'address', 'status', 'notes', 'tags', 'source'}

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(customer, field, value)

                # Update normalized fields if name/phone changed
                if field == 'name':
                    customer.normalized_name = CustomerService.normalize_name(value)
                elif field == 'phone':
                    customer.normalized_phone = CustomerService.normalize_phone(value)

        customer.updated_at = datetime.utcnow()
        return customer

    @staticmethod
    async def add_note(
        db: AsyncSession,
        contractor_id: str,
        customer_id: str,
        note: str
    ) -> Optional[Customer]:
        """
        Add a note to a customer (appends to existing notes).

        Args:
            db: Database session
            contractor_id: Contractor ID
            customer_id: Customer ID
            note: Note text to add

        Returns:
            Updated customer or None
        """
        customer = await CustomerService.get_customer_by_id(db, contractor_id, customer_id)
        if not customer:
            return None

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        formatted_note = f"[{timestamp}] {note}"

        if customer.notes:
            customer.notes = f"{customer.notes}\n{formatted_note}"
        else:
            customer.notes = formatted_note

        customer.updated_at = datetime.utcnow()
        return customer

    @staticmethod
    async def add_tag(
        db: AsyncSession,
        contractor_id: str,
        customer_id: str,
        tag: str
    ) -> Optional[Customer]:
        """
        Add a tag to a customer.

        Args:
            db: Database session
            contractor_id: Contractor ID
            customer_id: Customer ID
            tag: Tag to add

        Returns:
            Updated customer or None
        """
        customer = await CustomerService.get_customer_by_id(db, contractor_id, customer_id)
        if not customer:
            return None

        tags = customer.tags or []
        tag_lower = tag.lower().strip()
        if tag_lower not in [t.lower() for t in tags]:
            tags.append(tag.strip())
            customer.tags = tags
            customer.updated_at = datetime.utcnow()

        return customer

    @staticmethod
    async def remove_tag(
        db: AsyncSession,
        contractor_id: str,
        customer_id: str,
        tag: str
    ) -> Optional[Customer]:
        """
        Remove a tag from a customer.

        Args:
            db: Database session
            contractor_id: Contractor ID
            customer_id: Customer ID
            tag: Tag to remove

        Returns:
            Updated customer or None
        """
        customer = await CustomerService.get_customer_by_id(db, contractor_id, customer_id)
        if not customer:
            return None

        tags = customer.tags or []
        tag_lower = tag.lower().strip()
        customer.tags = [t for t in tags if t.lower() != tag_lower]
        customer.updated_at = datetime.utcnow()

        return customer

    @staticmethod
    async def search_customers(
        db: AsyncSession,
        contractor_id: str,
        query: str,
        limit: int = 10
    ) -> List[Customer]:
        """
        Quick search for customers by name/phone/email.
        Used for voice command lookups and autocomplete.

        Args:
            db: Database session
            contractor_id: Contractor ID
            query: Search query
            limit: Max results

        Returns:
            List of matching customers
        """
        search_term = f"%{query.lower()}%"

        result = await db.execute(
            select(Customer)
            .where(
                and_(
                    Customer.contractor_id == contractor_id,
                    or_(
                        func.lower(Customer.name).like(search_term),
                        func.lower(Customer.phone).like(search_term),
                        func.lower(Customer.email).like(search_term)
                    )
                )
            )
            .order_by(Customer.last_quote_at.desc().nullslast())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_dormant_customers(
        db: AsyncSession,
        contractor_id: str,
        days: int = 90,
        limit: int = 50
    ) -> List[Customer]:
        """
        Get customers who haven't had a quote in X days.
        Used for re-engagement reminders.

        Args:
            db: Database session
            contractor_id: Contractor ID
            days: Days since last quote
            limit: Max results

        Returns:
            List of dormant customers
        """
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days) if hasattr(datetime, 'timedelta') else None

        # Import timedelta properly
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(Customer)
            .where(
                and_(
                    Customer.contractor_id == contractor_id,
                    Customer.last_quote_at < cutoff_date,
                    Customer.status == "active"
                )
            )
            .order_by(Customer.last_quote_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_top_customers(
        db: AsyncSession,
        contractor_id: str,
        by: str = "total_quoted",
        limit: int = 10
    ) -> List[Customer]:
        """
        Get top customers by revenue or quote count.

        Args:
            db: Database session
            contractor_id: Contractor ID
            by: Metric to sort by (total_quoted, total_won, quote_count)
            limit: Max results

        Returns:
            List of top customers
        """
        sort_column = getattr(Customer, by, Customer.total_quoted)

        result = await db.execute(
            select(Customer)
            .where(Customer.contractor_id == contractor_id)
            .order_by(sort_column.desc().nullslast())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_customer_summary(
        db: AsyncSession,
        contractor_id: str
    ) -> Dict[str, Any]:
        """
        Get summary statistics for all customers.

        Args:
            db: Database session
            contractor_id: Contractor ID

        Returns:
            Dict with summary stats
        """
        # Total customers
        total_result = await db.execute(
            select(func.count(Customer.id))
            .where(Customer.contractor_id == contractor_id)
        )
        total_customers = total_result.scalar() or 0

        # By status
        status_result = await db.execute(
            select(Customer.status, func.count(Customer.id))
            .where(Customer.contractor_id == contractor_id)
            .group_by(Customer.status)
        )
        by_status = {row[0]: row[1] for row in status_result.fetchall()}

        # Total revenue
        revenue_result = await db.execute(
            select(
                func.sum(Customer.total_quoted),
                func.sum(Customer.total_won)
            )
            .where(Customer.contractor_id == contractor_id)
        )
        revenue_row = revenue_result.fetchone()

        return {
            "total_customers": total_customers,
            "by_status": by_status,
            "total_quoted": revenue_row[0] or 0 if revenue_row else 0,
            "total_won": revenue_row[1] or 0 if revenue_row else 0,
        }


# Singleton instance for convenience
customer_service = CustomerService()
