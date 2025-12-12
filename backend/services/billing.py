"""
Billing service for Quoted.
Handles Stripe subscriptions, payment processing, and usage metering.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from ..config import settings
from ..models.database import User
from .analytics import analytics_service

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


class BillingService:
    """Service for managing billing operations with Stripe."""

    @staticmethod
    def get_plan_config(plan_tier: str) -> Dict[str, Any]:
        """Get configuration for a specific plan tier.

        DISC-098: Added unlimited tier as the new single-tier pricing model.
        Legacy tiers (starter, pro, team) kept for existing subscribers.
        """
        plans = {
            "trial": {
                "monthly_quotes": settings.trial_quote_limit,
                "overage_price": 0,  # No overage during trial
                "price_monthly": 0,
                "price_annual": 0,
                "product_id": None,
            },
            # New single-tier pricing (DISC-098)
            "unlimited": {
                "monthly_quotes": settings.unlimited_monthly_quotes,
                "overage_price": settings.unlimited_overage_price,
                "price_monthly": settings.unlimited_price_monthly,
                "price_annual": settings.unlimited_price_annual,
                "product_id": settings.stripe_unlimited_product_id,
            },
            # Legacy tiers (deprecated, kept for existing subscribers)
            "starter": {
                "monthly_quotes": settings.starter_monthly_quotes,
                "overage_price": settings.starter_overage_price,
                "price_monthly": settings.starter_price_monthly,
                "price_annual": settings.starter_price_monthly * 10,  # ~17% discount
                "product_id": settings.stripe_starter_product_id,
            },
            "pro": {
                "monthly_quotes": settings.pro_monthly_quotes,
                "overage_price": settings.pro_overage_price,
                "price_monthly": settings.pro_price_monthly,
                "price_annual": settings.pro_price_monthly * 10,  # ~17% discount
                "product_id": settings.stripe_pro_product_id,
            },
            "team": {
                "monthly_quotes": settings.team_monthly_quotes,
                "overage_price": settings.team_overage_price,
                "price_monthly": settings.team_price_monthly,
                "price_annual": settings.team_price_monthly * 10,  # ~17% discount
                "product_id": settings.stripe_team_product_id,
            },
        }
        return plans.get(plan_tier, plans["trial"])

    @staticmethod
    async def check_quote_limit(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """
        Check if user can generate another quote.
        Returns dict with: can_generate, reason, quotes_remaining, plan_tier

        DISC-018: Progressive warnings + grace period:
        - 90% (67/75): soft_warning
        - 95% (71/75): urgent_warning
        - 100% (75/75): grace period (3 quotes with watermark)
        - 103+ (78/75): hard_block
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        plan_config = BillingService.get_plan_config(user.plan_tier)

        # Check trial expiration
        if user.plan_tier == "trial":
            if user.trial_ends_at and datetime.utcnow() > user.trial_ends_at:
                return {
                    "can_generate": False,
                    "reason": "trial_expired",
                    "quotes_remaining": 0,
                    "plan_tier": user.plan_tier,
                    "trial_ends_at": user.trial_ends_at.isoformat(),
                }

        # Check quote limit
        quotes_remaining = plan_config["monthly_quotes"] - user.quotes_used
        quota_percent = (user.quotes_used / plan_config["monthly_quotes"]) * 100 if plan_config["monthly_quotes"] > 0 else 0

        # DISC-018: Trial grace period logic
        if user.plan_tier == "trial" and quotes_remaining <= 0:
            grace_remaining = 3 - (user.grace_quotes_used or 0)

            if grace_remaining > 0:
                # Allow grace quote with watermark
                return {
                    "can_generate": True,
                    "reason": "grace_period",
                    "quotes_remaining": 0,
                    "grace_remaining": grace_remaining,
                    "is_grace_quote": True,
                    "plan_tier": user.plan_tier,
                    "warning_level": "grace",
                }
            else:
                # Hard block after 3 grace quotes
                return {
                    "can_generate": False,
                    "reason": "trial_limit_reached",
                    "quotes_remaining": 0,
                    "grace_remaining": 0,
                    "plan_tier": user.plan_tier,
                }

        # Paid plans: overage allowed
        if quotes_remaining <= 0:
            if user.plan_tier != "trial":
                return {
                    "can_generate": True,
                    "reason": "overage",
                    "quotes_remaining": 0,
                    "quotes_used": user.quotes_used,
                    "overage_count": user.quotes_used - plan_config["monthly_quotes"],
                    "overage_price": plan_config["overage_price"],
                    "plan_tier": user.plan_tier,
                }

        # DISC-018: Warning levels for trial users
        warning_level = None
        if user.plan_tier == "trial":
            if quota_percent >= 95:  # 71+ quotes used
                warning_level = "urgent"
            elif quota_percent >= 90:  # 67+ quotes used
                warning_level = "soft"

        return {
            "can_generate": True,
            "reason": "within_limit",
            "quotes_remaining": quotes_remaining,
            "quotes_used": user.quotes_used,
            "plan_tier": user.plan_tier,
            "quota_percent": round(quota_percent, 1),
            "warning_level": warning_level,
            "is_grace_quote": False,
        }

    @staticmethod
    async def increment_quote_usage(db: AsyncSession, user_id: str, is_grace_quote: bool = False) -> None:
        """
        Increment the quote usage counter for a user.

        DISC-018: If is_grace_quote=True, increment grace_quotes_used instead of quotes_used.
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # DISC-018: Track grace quotes separately
        if is_grace_quote:
            user.grace_quotes_used = (user.grace_quotes_used or 0) + 1
        else:
            user.quotes_used += 1

        await db.commit()

        # Report overage to Stripe if applicable
        if user.plan_tier != "trial" and user.subscription_id:
            plan_config = BillingService.get_plan_config(user.plan_tier)
            if user.quotes_used > plan_config["monthly_quotes"]:
                await BillingService._report_overage_to_stripe(
                    user.subscription_id,
                    user.quotes_used - plan_config["monthly_quotes"]
                )

    @staticmethod
    async def _report_overage_to_stripe(subscription_id: str, overage_count: int) -> None:
        """Report usage overage to Stripe meter (for billing)."""
        # Note: This assumes you have a Stripe meter set up
        # If using metered billing, report usage here
        # For MVP, we'll track overages and bill them at cycle end via invoice items
        pass

    @staticmethod
    async def create_checkout_session(
        db: AsyncSession,
        user_id: str,
        plan_tier: str,
        billing_interval: str,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, str]:
        """
        Create a Stripe checkout session for subscription.
        Returns checkout URL and session ID.

        Args:
            billing_interval: "monthly" or "annual"
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        plan_config = BillingService.get_plan_config(plan_tier)

        if not plan_config["product_id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan tier: {plan_tier}"
            )

        # Create or get Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": user.id}
            )
            user.stripe_customer_id = customer.id
            await db.commit()
        else:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)

        # Get price for this product with correct interval
        # Map billing_interval to Stripe interval
        stripe_interval = "year" if billing_interval == "annual" else "month"

        try:
            prices = stripe.Price.list(product=plan_config["product_id"], active=True)
        except Exception as e:
            print(f"Error listing prices for product {plan_config['product_id']}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve pricing information for {plan_tier} plan. Please contact support."
            )

        if not prices.data:
            print(f"No active prices found for product {plan_config['product_id']} (plan: {plan_tier})")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Pricing not configured for {plan_tier} plan. Please contact support or try a different plan."
            )

        # Find price with matching interval
        # Prefer licensed (fixed) prices over metered prices for checkout
        # Metered prices are for overage tracking, not initial subscription
        licensed_prices = []
        metered_prices = []

        for price in prices.data:
            if price.recurring and price.recurring.interval == stripe_interval:
                if price.recurring.usage_type == "metered":
                    metered_prices.append(price)
                else:
                    licensed_prices.append(price)

        # Use licensed price if available, fall back to metered
        if licensed_prices:
            matching_price = licensed_prices[0]
        elif metered_prices:
            matching_price = metered_prices[0]
        else:
            # Fallback to first price if no interval match
            print(f"No {stripe_interval} price found for {plan_tier}, using first available price")
            matching_price = prices.data[0]

        # Create checkout session
        # Note: For metered prices, don't include quantity
        line_item = {"price": matching_price.id}
        if matching_price.recurring and matching_price.recurring.usage_type != "metered":
            line_item["quantity"] = 1

        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[line_item],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "plan_tier": plan_tier,
            },
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id,
        }

    @staticmethod
    async def create_portal_session(
        db: AsyncSession,
        user_id: str,
        return_url: str,
    ) -> str:
        """
        Create a Stripe customer portal session.
        Returns portal URL for customer to manage their subscription.
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Stripe customer found"
            )

        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=return_url,
        )

        return session.url

    @staticmethod
    async def handle_checkout_completed(db: AsyncSession, session: dict) -> None:
        """Handle successful checkout completion."""
        user_id = session["metadata"]["user_id"]
        plan_tier = session["metadata"]["plan_tier"]

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return

        # Get subscription from session
        subscription = stripe.Subscription.retrieve(session["subscription"])

        # Update user with subscription info
        user.subscription_id = subscription.id
        user.plan_tier = plan_tier
        user.quotes_used = 0  # Reset usage for new billing cycle
        user.billing_cycle_start = datetime.utcnow()
        user.trial_ends_at = None  # Clear trial if set

        await db.commit()

        # Credit referrer if this user was referred (GROWTH-002)
        from .referral import ReferralService
        try:
            await ReferralService.credit_referrer(db, user)
        except Exception as e:
            print(f"Warning: Failed to credit referrer: {e}")

        # Track subscription activation
        try:
            analytics_service.track_event(
                user_id=str(user_id),
                event_name="subscription_activated",
                properties={
                    "plan_tier": plan_tier,
                    "subscription_id": subscription.id,
                    "billing_interval": session["metadata"].get("billing_interval", "monthly"),
                    "was_referred": bool(user.referred_by_code),
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track subscription activation: {e}")

    @staticmethod
    async def handle_subscription_updated(db: AsyncSession, subscription: dict) -> None:
        """Handle subscription update (renewal, plan change, etc.)."""
        # Find user by subscription ID
        result = await db.execute(
            select(User).where(User.subscription_id == subscription["id"])
        )
        user = result.scalar_one_or_none()

        if not user:
            return

        # Reset usage counter at cycle start
        if subscription["status"] == "active":
            user.billing_cycle_start = datetime.utcnow()
            user.quotes_used = 0
            await db.commit()

    @staticmethod
    async def handle_subscription_deleted(db: AsyncSession, subscription: dict) -> None:
        """Handle subscription cancellation."""
        result = await db.execute(
            select(User).where(User.subscription_id == subscription["id"])
        )
        user = result.scalar_one_or_none()

        if not user:
            return

        # Downgrade to trial with no quotes remaining
        user.subscription_id = None
        user.plan_tier = "trial"
        user.quotes_used = settings.trial_quote_limit  # Maxed out
        user.trial_ends_at = datetime.utcnow()  # Expired

        await db.commit()

    @staticmethod
    async def initialize_trial(db: AsyncSession, user_id: str) -> None:
        """Initialize trial period for a new user."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return

        user.plan_tier = "trial"
        user.trial_ends_at = datetime.utcnow() + timedelta(days=settings.trial_days)
        user.billing_cycle_start = datetime.utcnow()
        user.quotes_used = 0

        await db.commit()
