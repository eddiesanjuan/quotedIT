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


    # =========================================================================
    # INNOV-8: Repeat Customer Auto-Quote Support
    # =========================================================================

    @staticmethod
    async def get_customer_quote_history(
        db: AsyncSession,
        contractor_id: str,
        customer_id: str,
        limit: int = 20
    ) -> List[Quote]:
        """
        Get quote history for a customer, ordered by most recent.

        INNOV-8: Used to pre-fill data and suggest pricing for repeat customers.

        Args:
            db: Database session
            contractor_id: Contractor ID (for authorization)
            customer_id: Customer ID
            limit: Max quotes to return

        Returns:
            List of quotes for this customer
        """
        result = await db.execute(
            select(Quote)
            .where(
                and_(
                    Quote.customer_id == customer_id,
                    Quote.contractor_id == contractor_id
                )
            )
            .order_by(Quote.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_similar_quotes_for_customer(
        db: AsyncSession,
        contractor_id: str,
        customer_id: str,
        job_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Quote]:
        """
        Get similar past quotes for a customer, optionally filtered by job type.

        INNOV-8: Helps suggest pricing based on customer's history.

        Args:
            db: Database session
            contractor_id: Contractor ID
            customer_id: Customer ID
            job_type: Optional job type to filter by
            limit: Max results

        Returns:
            List of similar quotes
        """
        query = select(Quote).where(
            and_(
                Quote.customer_id == customer_id,
                Quote.contractor_id == contractor_id
            )
        )

        if job_type:
            query = query.where(Quote.job_type == job_type)

        query = query.order_by(Quote.created_at.desc()).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_auto_quote_suggestions(
        db: AsyncSession,
        contractor_id: str,
        customer_identifier: str,  # Can be name, phone, or email
        job_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        INNOV-8: Get auto-quote suggestions for a repeat customer.

        Returns:
        - Customer info (if recognized)
        - Pre-fill data from last quote
        - Pricing suggestions based on history
        - VIP/loyalty indicators

        Args:
            db: Database session
            contractor_id: Contractor ID
            customer_identifier: Name, phone, or email to search
            job_type: Optional job type for filtering

        Returns:
            Dict with suggestions for auto-quote
        """
        # Search for customer
        customers = await CustomerService.search_customers(
            db, contractor_id, customer_identifier, limit=5
        )

        if not customers:
            return {
                "recognized": False,
                "customer": None,
                "prefill": {},
                "pricing_suggestions": {},
                "loyalty_info": {}
            }

        # Use the best match (first result)
        customer = customers[0]

        # Get quote history
        quotes = await CustomerService.get_customer_quote_history(
            db, contractor_id, customer.id, limit=20
        )

        if not quotes:
            return {
                "recognized": True,
                "customer": {
                    "id": customer.id,
                    "name": customer.name,
                    "phone": customer.phone,
                    "email": customer.email,
                    "address": customer.address,
                    "status": customer.status,
                    "quote_count": customer.quote_count or 0,
                    "total_won": customer.total_won or 0,
                },
                "prefill": {
                    "customer_name": customer.name,
                    "customer_phone": customer.phone,
                    "customer_email": customer.email,
                    "customer_address": customer.address,
                },
                "pricing_suggestions": {},
                "loyalty_info": {
                    "is_repeat": False,
                    "total_quotes": 0,
                    "total_spent": 0,
                }
            }

        # Get last quote for pre-fill
        last_quote = quotes[0]

        # Build prefill data
        prefill = {
            "customer_name": customer.name,
            "customer_phone": customer.phone or last_quote.customer_phone,
            "customer_email": customer.email or last_quote.customer_email,
            "customer_address": customer.address or last_quote.customer_address,
        }

        # Calculate pricing suggestions
        pricing_suggestions = {}
        if job_type:
            # Filter quotes by job type
            same_type_quotes = [q for q in quotes if q.job_type == job_type]
            if same_type_quotes:
                totals = [q.total for q in same_type_quotes if q.total]
                if totals:
                    pricing_suggestions = {
                        "job_type": job_type,
                        "previous_quotes_count": len(same_type_quotes),
                        "avg_quote_amount": sum(totals) / len(totals),
                        "min_quote_amount": min(totals),
                        "max_quote_amount": max(totals),
                        "last_quote_amount": same_type_quotes[0].total,
                        "last_quote_date": same_type_quotes[0].created_at.isoformat() if same_type_quotes[0].created_at else None,
                        "suggestion": f"Based on {len(same_type_quotes)} previous {job_type} jobs for {customer.name}, suggest starting around ${sum(totals)/len(totals):.0f}",
                    }
        else:
            # General pricing based on all quotes
            totals = [q.total for q in quotes if q.total]
            if totals:
                pricing_suggestions = {
                    "previous_quotes_count": len(quotes),
                    "avg_quote_amount": sum(totals) / len(totals),
                    "min_quote_amount": min(totals),
                    "max_quote_amount": max(totals),
                    "last_quote_amount": quotes[0].total,
                    "last_quote_date": quotes[0].created_at.isoformat() if quotes[0].created_at else None,
                    "most_common_job_types": CustomerService._get_common_job_types(quotes),
                }

        # Calculate loyalty info
        won_quotes = [q for q in quotes if q.status == "won" or q.outcome == "won"]
        total_spent = sum(q.total for q in won_quotes if q.total)

        loyalty_info = {
            "is_repeat": len(quotes) > 1,
            "is_vip": customer.status == "vip" or total_spent > 5000,
            "total_quotes": len(quotes),
            "total_won": len(won_quotes),
            "total_spent": total_spent,
            "win_rate": len(won_quotes) / len(quotes) if quotes else 0,
            "first_quote_date": customer.first_quote_at.isoformat() if customer.first_quote_at else None,
            "last_quote_date": customer.last_quote_at.isoformat() if customer.last_quote_at else None,
            "customer_since_months": CustomerService._months_since(customer.first_quote_at) if customer.first_quote_at else 0,
        }

        # Add loyalty tier
        if total_spent >= 10000:
            loyalty_info["tier"] = "platinum"
            loyalty_info["tier_label"] = "Platinum Customer"
        elif total_spent >= 5000:
            loyalty_info["tier"] = "gold"
            loyalty_info["tier_label"] = "Gold Customer"
        elif total_spent >= 2000:
            loyalty_info["tier"] = "silver"
            loyalty_info["tier_label"] = "Silver Customer"
        elif len(won_quotes) >= 2:
            loyalty_info["tier"] = "bronze"
            loyalty_info["tier_label"] = "Repeat Customer"
        else:
            loyalty_info["tier"] = "new"
            loyalty_info["tier_label"] = "New Customer"

        return {
            "recognized": True,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "status": customer.status,
                "quote_count": customer.quote_count or 0,
                "total_won": customer.total_won or 0,
            },
            "prefill": prefill,
            "pricing_suggestions": pricing_suggestions,
            "loyalty_info": loyalty_info,
            "recent_quotes": [
                {
                    "id": q.id,
                    "job_type": q.job_type,
                    "job_description": q.job_description[:100] if q.job_description else None,
                    "total": q.total,
                    "status": q.status,
                    "created_at": q.created_at.isoformat() if q.created_at else None,
                }
                for q in quotes[:5]  # Include last 5 quotes
            ]
        }

    @staticmethod
    def _get_common_job_types(quotes: List[Quote], limit: int = 3) -> List[Dict[str, Any]]:
        """Get the most common job types from a list of quotes."""
        job_type_counts = {}
        for q in quotes:
            if q.job_type:
                job_type_counts[q.job_type] = job_type_counts.get(q.job_type, 0) + 1

        sorted_types = sorted(job_type_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"job_type": jt, "count": count}
            for jt, count in sorted_types[:limit]
        ]

    @staticmethod
    def _months_since(date: Optional[datetime]) -> int:
        """Calculate months since a given date."""
        if not date:
            return 0
        now = datetime.utcnow()
        months = (now.year - date.year) * 12 + (now.month - date.month)
        return max(0, months)

    # =========================================================================
    # DISC-126: Bulletproof Customer Identification
    # =========================================================================

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return CustomerService._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    @staticmethod
    def _name_similarity(name1: str, name2: str) -> float:
        """
        Calculate similarity between two names (0.0 to 1.0).
        Uses normalized Levenshtein distance.
        """
        if not name1 or not name2:
            return 0.0
        n1 = CustomerService.normalize_name(name1)
        n2 = CustomerService.normalize_name(name2)
        if n1 == n2:
            return 1.0
        if not n1 or not n2:
            return 0.0

        distance = CustomerService._levenshtein_distance(n1, n2)
        max_len = max(len(n1), len(n2))
        return 1.0 - (distance / max_len)

    @staticmethod
    def _normalize_address(address: str) -> str:
        """
        Normalize address for comparison.
        - Lowercase
        - Expand common abbreviations
        - Remove punctuation
        - Collapse whitespace
        """
        if not address:
            return ""
        normalized = address.lower()
        # Expand common abbreviations
        replacements = {
            r'\bst\b': 'street',
            r'\bave\b': 'avenue',
            r'\bblvd\b': 'boulevard',
            r'\bdr\b': 'drive',
            r'\bln\b': 'lane',
            r'\brd\b': 'road',
            r'\bct\b': 'court',
            r'\bpl\b': 'place',
            r'\bapt\b': 'apartment',
            r'\bste\b': 'suite',
            r'\bn\b': 'north',
            r'\bs\b': 'south',
            r'\be\b': 'east',
            r'\bw\b': 'west',
        }
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Collapse whitespace
        normalized = ' '.join(normalized.split())
        return normalized.strip()

    @staticmethod
    def _address_similarity(addr1: str, addr2: str) -> float:
        """
        Calculate similarity between two addresses (0.0 to 1.0).
        """
        if not addr1 or not addr2:
            return 0.0
        n1 = CustomerService._normalize_address(addr1)
        n2 = CustomerService._normalize_address(addr2)
        if n1 == n2:
            return 1.0
        if not n1 or not n2:
            return 0.0

        # Use Levenshtein similarity
        distance = CustomerService._levenshtein_distance(n1, n2)
        max_len = max(len(n1), len(n2))
        return 1.0 - (distance / max_len)

    @staticmethod
    async def find_customer_matches(
        db: AsyncSession,
        contractor_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Find potential customer matches with confidence scores.

        DISC-126: Bulletproof customer identification with confidence-based matching.

        Confidence Levels:
        - EXACT (>= 0.95): Phone match or exact normalized name
        - HIGH (>= 0.80): Very similar name + address match
        - MEDIUM (>= 0.60): Similar name or partial matches
        - LOW (< 0.60): Weak matches, likely different customers

        Args:
            db: Database session
            contractor_id: Contractor ID to scope search
            name: Customer name to match
            phone: Customer phone to match (most reliable)
            address: Customer address (secondary signal)
            limit: Maximum matches to return

        Returns:
            Dict with:
            - matches: List of potential matches with confidence
            - exact_match: Customer if confidence >= 0.95
            - recommendation: "auto_link", "confirm_needed", "create_new"
            - message: Human-readable explanation
        """
        matches = []
        exact_match = None

        # Normalize inputs
        normalized_name = CustomerService.normalize_name(name) if name else None
        normalized_phone = CustomerService.normalize_phone(phone) if phone else None
        normalized_addr = CustomerService._normalize_address(address) if address else None

        # Get all customers for this contractor
        result = await db.execute(
            select(Customer).where(Customer.contractor_id == contractor_id)
        )
        all_customers = result.scalars().all()

        for customer in all_customers:
            confidence = 0.0
            match_reasons = []

            # Phone match (highest priority - nearly unique identifier)
            if normalized_phone and customer.normalized_phone:
                if normalized_phone == customer.normalized_phone:
                    confidence = 0.98  # Near-certain match
                    match_reasons.append("phone_exact")
                elif normalized_phone[-7:] == customer.normalized_phone[-7:]:
                    # Last 7 digits match (handles area code differences)
                    confidence = max(confidence, 0.85)
                    match_reasons.append("phone_partial")

            # Name match
            if normalized_name and customer.normalized_name:
                if normalized_name == customer.normalized_name:
                    # Exact normalized name
                    name_conf = 0.90
                    match_reasons.append("name_exact")
                else:
                    # Fuzzy name match
                    similarity = CustomerService._name_similarity(name, customer.name)
                    if similarity >= 0.85:
                        name_conf = similarity * 0.85  # Scale to 0.72 max
                        match_reasons.append(f"name_similar_{similarity:.0%}")
                    elif similarity >= 0.70:
                        name_conf = similarity * 0.70  # Scale to 0.49 max
                        match_reasons.append(f"name_fuzzy_{similarity:.0%}")
                    else:
                        name_conf = 0.0

                # Combine with phone confidence
                if confidence > 0:
                    confidence = min(0.99, confidence + name_conf * 0.1)  # Boost if both match
                else:
                    confidence = name_conf

            # Address boost (secondary signal - doesn't create match alone)
            if normalized_addr and customer.address:
                addr_similarity = CustomerService._address_similarity(address, customer.address)
                if addr_similarity >= 0.80:
                    # Boost confidence by up to 10% for address match
                    confidence = min(0.99, confidence + addr_similarity * 0.10)
                    match_reasons.append(f"address_match_{addr_similarity:.0%}")

            # Only include if there's meaningful confidence
            if confidence >= 0.40:
                matches.append({
                    "customer_id": customer.id,
                    "name": customer.name,
                    "phone": customer.phone,
                    "email": customer.email,
                    "address": customer.address,
                    "confidence": round(confidence, 3),
                    "match_reasons": match_reasons,
                    "quote_count": customer.quote_count or 0,
                    "total_quoted": float(customer.total_quoted or 0),
                    "last_quote_at": customer.last_quote_at.isoformat() if customer.last_quote_at else None
                })

        # Sort by confidence descending
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        matches = matches[:limit]

        # Determine recommendation
        if matches and matches[0]["confidence"] >= 0.95:
            exact_match = matches[0]
            recommendation = "auto_link"
            message = f"High confidence match: {exact_match['name']} ({exact_match['confidence']:.0%})"
        elif matches and matches[0]["confidence"] >= 0.70:
            recommendation = "confirm_needed"
            message = f"Possible match found: {matches[0]['name']} ({matches[0]['confidence']:.0%}). Please confirm."
        elif matches and matches[0]["confidence"] >= 0.50:
            recommendation = "confirm_needed"
            message = f"Weak match found: {matches[0]['name']} ({matches[0]['confidence']:.0%}). Is this the same customer?"
        else:
            recommendation = "create_new"
            message = "No matching customer found. A new customer record will be created."

        return {
            "matches": matches,
            "exact_match": exact_match,
            "recommendation": recommendation,
            "message": message,
            "input": {
                "name": name,
                "phone": phone,
                "address": address
            }
        }

    @staticmethod
    async def link_quote_to_customer_explicit(
        db: AsyncSession,
        quote: Quote,
        customer_id: Optional[str] = None,
        create_new: bool = False
    ) -> Dict[str, Any]:
        """
        Explicitly link a quote to a customer with full control.

        DISC-126: Bulletproof linking with explicit user choice.

        Args:
            db: Database session
            quote: Quote to link
            customer_id: Explicit customer ID to link (if user confirmed)
            create_new: Force create new customer even if matches exist

        Returns:
            Dict with:
            - success: bool
            - customer: Customer data if linked
            - action: "linked_existing", "created_new", "no_data"
            - message: Human-readable result
        """
        from sqlalchemy import update

        # No customer data to work with
        if not quote.customer_name and not customer_id:
            return {
                "success": False,
                "customer": None,
                "action": "no_data",
                "message": "No customer information available to link"
            }

        customer = None
        action = None

        if customer_id:
            # Explicit link to existing customer
            result = await db.execute(
                select(Customer).where(
                    and_(
                        Customer.id == customer_id,
                        Customer.contractor_id == quote.contractor_id
                    )
                )
            )
            customer = result.scalar_one_or_none()
            if customer:
                action = "linked_existing"
                # Update customer with any new info from quote
                if quote.customer_phone and not customer.phone:
                    customer.phone = quote.customer_phone
                    customer.normalized_phone = CustomerService.normalize_phone(quote.customer_phone)
                if getattr(quote, 'customer_email', None) and not customer.email:
                    customer.email = quote.customer_email
                if quote.customer_address and not customer.address:
                    customer.address = quote.customer_address
                customer.updated_at = datetime.utcnow()
            else:
                return {
                    "success": False,
                    "customer": None,
                    "action": "error",
                    "message": f"Customer {customer_id} not found"
                }
        elif create_new or not quote.customer_name:
            # Force create new customer
            customer = Customer(
                contractor_id=quote.contractor_id,
                name=quote.customer_name.strip() if quote.customer_name else "Unknown",
                phone=quote.customer_phone,
                email=getattr(quote, 'customer_email', None),
                address=quote.customer_address,
                normalized_name=CustomerService.normalize_name(quote.customer_name) if quote.customer_name else "",
                normalized_phone=CustomerService.normalize_phone(quote.customer_phone) if quote.customer_phone else "",
                status="active"
            )
            db.add(customer)
            await db.flush()
            action = "created_new"
        else:
            # Auto-match using find_or_create (legacy behavior for backward compatibility)
            customer = await CustomerService.find_or_create_customer(
                db=db,
                contractor_id=quote.contractor_id,
                name=quote.customer_name,
                phone=quote.customer_phone,
                email=getattr(quote, 'customer_email', None),
                address=quote.customer_address
            )
            action = "auto_matched"

        if customer:
            # Link quote to customer
            await db.execute(
                update(Quote)
                .where(Quote.id == quote.id)
                .values(customer_id=customer.id)
            )
            await db.flush()

            # Update customer stats
            await CustomerService.update_customer_stats(db, customer)

            return {
                "success": True,
                "customer": {
                    "id": customer.id,
                    "name": customer.name,
                    "phone": customer.phone,
                    "email": customer.email,
                    "address": customer.address,
                    "quote_count": customer.quote_count,
                    "total_quoted": float(customer.total_quoted or 0)
                },
                "action": action,
                "message": f"Quote linked to customer: {customer.name}"
            }

        return {
            "success": False,
            "customer": None,
            "action": "error",
            "message": "Failed to link customer"
        }

    @staticmethod
    async def get_recent_customers(
        db: AsyncSession,
        contractor_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most recently quoted customers for quick picker.

        DISC-126: For "repeat customer" voice signal - show recent customers.

        Args:
            db: Database session
            contractor_id: Contractor ID
            limit: Maximum customers to return

        Returns:
            List of recent customers with quote counts
        """
        result = await db.execute(
            select(Customer)
            .where(
                and_(
                    Customer.contractor_id == contractor_id,
                    Customer.status == "active"
                )
            )
            .order_by(Customer.last_quote_at.desc().nullslast())
            .limit(limit)
        )
        customers = result.scalars().all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "address": c.address,
                "quote_count": c.quote_count or 0,
                "last_quote_at": c.last_quote_at.isoformat() if c.last_quote_at else None,
                "total_quoted": float(c.total_quoted or 0)
            }
            for c in customers
        ]


# Singleton instance for convenience
customer_service = CustomerService()
