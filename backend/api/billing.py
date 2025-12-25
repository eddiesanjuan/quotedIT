"""
Billing API endpoints for Quoted.
Handles Stripe subscription management, webhooks, and usage status.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import stripe

from ..services.auth import get_db, get_current_user
from ..services.billing import BillingService
from ..config import settings

router = APIRouter()


class CheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    plan_tier: str  # "unlimited" (new) or legacy: "starter", "pro", "team"
    billing_interval: str = "monthly"  # "monthly" or "annual"
    success_url: str
    cancel_url: str


class EmbeddedCheckoutRequest(BaseModel):
    """Request to create an embedded checkout session."""
    plan_tier: str = "unlimited"  # Default to unlimited (DISC-098)
    billing_interval: str = "monthly"  # "monthly" or "annual"
    return_url: str  # URL to return to after checkout


class PortalRequest(BaseModel):
    """Request to create a customer portal session."""
    return_url: str


class BillingStatusResponse(BaseModel):
    """Current billing status for a user."""
    plan_tier: str
    quotes_used: int
    quotes_remaining: int
    can_generate: bool
    billing_cycle_start: Optional[str]
    trial_ends_at: Optional[str]
    subscription_id: Optional[str]


@router.post("/create-checkout")
async def create_checkout_session(
    request: CheckoutRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Stripe checkout session for subscription.
    Returns checkout URL to redirect user to Stripe payment page.
    """
    # DISC-098: unlimited is the new single tier; legacy tiers still accepted for existing subscribers
    valid_tiers = ["unlimited", "starter", "pro", "team"]
    if request.plan_tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan tier: {request.plan_tier}. Must be one of: {', '.join(valid_tiers)}"
        )

    try:
        result = await BillingService.create_checkout_session(
            db=db,
            user_id=user["id"],
            plan_tier=request.plan_tier,
            billing_interval=request.billing_interval,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )

        return {
            "checkout_url": result["checkout_url"],
            "session_id": result["session_id"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/create-embedded-checkout")
async def create_embedded_checkout_session(
    request: EmbeddedCheckoutRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Stripe embedded checkout session.
    Returns client_secret for initializing Stripe Embedded Checkout on the frontend.
    """
    valid_tiers = ["unlimited", "starter", "pro", "team"]
    if request.plan_tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan tier: {request.plan_tier}. Must be one of: {', '.join(valid_tiers)}"
        )

    try:
        result = await BillingService.create_embedded_checkout_session(
            db=db,
            user_id=user["id"],
            plan_tier=request.plan_tier,
            billing_interval=request.billing_interval,
            return_url=request.return_url,
        )

        return {
            "client_secret": result["client_secret"],
            "session_id": result["session_id"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedded checkout session: {str(e)}"
        )


@router.post("/portal")
async def create_portal_session(
    request: PortalRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Stripe customer portal session.
    Returns portal URL where customer can manage their subscription.
    """
    try:
        portal_url = await BillingService.create_portal_session(
            db=db,
            user_id=user["id"],
            return_url=request.return_url,
        )

        return {
            "portal_url": portal_url,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create portal session: {str(e)}"
        )


@router.get("/status", response_model=BillingStatusResponse)
async def get_billing_status(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current billing status for the authenticated user.
    Shows plan, usage, and limits.
    """
    try:
        limit_check = await BillingService.check_quote_limit(db, user["id"])

        # Build response
        response = BillingStatusResponse(
            plan_tier=limit_check["plan_tier"],
            quotes_used=limit_check.get("quotes_used", 0),
            quotes_remaining=limit_check["quotes_remaining"],
            can_generate=limit_check["can_generate"],
            billing_cycle_start=None,
            trial_ends_at=limit_check.get("trial_ends_at"),
            subscription_id=None,
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing status: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhook events.
    This endpoint is called by Stripe to notify us of subscription events.

    IMPORTANT: This endpoint must be publicly accessible (no auth required).
    Security is handled via webhook signature verification.
    """
    # Get the webhook payload
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header"
        )

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        # Invalid payload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )

    # Handle the event
    event_type = event["type"]
    event_data = event["data"]["object"]

    # Log webhook receipt for monitoring
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Received Stripe webhook: {event_type}")

    try:
        if event_type == "checkout.session.completed":
            # Check if this is a deposit payment or subscription checkout
            metadata = event_data.get("metadata", {})
            if metadata.get("payment_type") == "quote_deposit":
                # INNOV-2: Handle deposit payment for quote acceptance
                await BillingService.handle_deposit_payment_completed(db, event_data)
            else:
                # Payment successful, subscription created
                await BillingService.handle_checkout_completed(db, event_data)

        elif event_type == "customer.subscription.updated":
            # Subscription renewed or plan changed
            await BillingService.handle_subscription_updated(db, event_data)

        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled or expired
            await BillingService.handle_subscription_deleted(db, event_data)

        elif event_type == "invoice.payment_succeeded":
            # Successful payment (recurring or one-time)
            # Reset usage counter if it's a subscription renewal
            if "subscription" in event_data:
                await BillingService.handle_subscription_updated(
                    db,
                    stripe.Subscription.retrieve(event_data["subscription"])
                )

        elif event_type == "invoice.payment_failed":
            # Payment failed
            # TODO: Send email notification to user
            pass

    except Exception as e:
        # Log the error and return 500 so Stripe will retry
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Webhook processing failed for {event_type}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )

    # Only return success if we actually processed successfully
    return {"status": "success", "event_type": event_type}


@router.get("/plans")
async def get_plans():
    """
    Get available subscription plans and pricing.
    Public endpoint - no authentication required.

    DISC-098: Returns single-tier "unlimited" pricing.
    Legacy tiers no longer shown to new users.
    """
    return {
        "plans": [
            {
                "id": "unlimited",
                "name": "Unlimited",
                "price_monthly": settings.unlimited_price_monthly / 100,  # $9.00
                "price_annual": settings.unlimited_price_annual / 100,  # $59.00
                "quotes_per_month": settings.unlimited_monthly_quotes,
                "overage_price": 0,
                "features": [
                    "Unlimited quotes",
                    "AI-powered quote generation",
                    "PDF export with your branding",
                    "Quote history & customer tracking",
                    "Learning system that improves over time",
                    "Email support",
                ],
                # ROI messaging (DISC-098)
                "value_props": {
                    "time_saved": "20 min per quote",
                    "monthly_savings": "$160+",  # 10 quotes × 20 min × $50/hr
                    "tagline": "Less than a cup of coffee. Unlimited professional quotes.",
                },
            },
        ],
        "trial": {
            "days": settings.trial_days,
            "quote_limit": settings.trial_quote_limit,
        },
        # Legacy plans (not shown in UI, but available for existing subscriber webhook handling)
        "legacy_plans": [
            {"id": "starter", "name": "Starter", "price_monthly": settings.starter_price_monthly / 100},
            {"id": "pro", "name": "Pro", "price_monthly": settings.pro_price_monthly / 100},
            {"id": "team", "name": "Team", "price_monthly": settings.team_price_monthly / 100},
        ],
    }
