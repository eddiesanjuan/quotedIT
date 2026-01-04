# GROWTH-001: Premium Setup Tier Implementation

**Status**: READY for Implementation
**Priority**: P0 - Revenue Generation
**Effort**: S-M (4-6 hours)
**Owner**: Quoted AI Team

---

## Executive Summary

Add a "Premium Setup" one-time purchase option ($149-199) that provides personalized onboarding for new users. This creates immediate revenue without requiring subscription volume, funds growth, and converts users into power users who retain longer.

**Target**: 10 sales/month = $1,500-2,000/month additional revenue

---

## Business Context

### The Problem
- Current pricing: $9/month or $59/year
- To hit $2,000/month revenue: need 222 monthly subscribers
- Starting from near-zero users, this takes 6-12 months
- Need faster monetization path

### The Solution
- Add high-ticket one-time purchase
- $149-199 "Premium Setup" tier
- Includes personalized onboarding call with founder
- Converts casual trials into committed power users
- 10 sales = $1,500-2,000 (vs 222 subscribers needed)

### Why This Works
1. **Service professionals value time over money** - $199 to skip setup is obvious ROI
2. **Personal touch builds loyalty** - Call with founder = referral machine
3. **Power users retain** - Properly configured users stay 3x longer
4. **Immediate revenue** - One sale = 22 months of $9 subscription value

---

## User Experience Flow

### Landing Page / Pricing
```
┌─────────────────────────────────────────────────────────────┐
│                    Choose Your Plan                          │
├─────────────────────┬───────────────────────────────────────┤
│      MONTHLY        │            PREMIUM SETUP              │
│      $9/mo          │            $199 one-time              │
│                     │          + $9/mo subscription          │
│  • Unlimited quotes │                                       │
│  • AI learning      │  Everything in Monthly, PLUS:         │
│  • PDF generation   │                                       │
│  • Customer CRM     │  ✓ 30-min personal onboarding call    │
│                     │  ✓ Custom pricing model setup         │
│                     │  ✓ Logo & template configuration      │
│                     │  ✓ First 5 quotes reviewed by founder │
│                     │  ✓ 30 days priority email support     │
│                     │  ✓ Setup guarantee - works or free    │
│                     │                                       │
│  [Start Free Trial] │     [Get Premium Setup →]             │
└─────────────────────┴───────────────────────────────────────┘
```

### Purchase Flow
1. User clicks "Get Premium Setup"
2. Stripe checkout for $199 (one-time) + $9/month subscription
3. Success page: "Book Your Onboarding Call" with Calendly embed
4. Email confirmation with Calendly link + what to prepare
5. After call: Follow-up email with recording + setup summary

### Post-Purchase Dashboard
- Badge: "Premium Member"
- Priority support indicator
- "Your setup call" section with date/reschedule
- Setup progress checklist (visible until complete)

---

## Technical Implementation

### Database Changes

```sql
-- Add premium_setup fields to contractors table
ALTER TABLE contractors ADD COLUMN premium_setup_purchased BOOLEAN DEFAULT FALSE;
ALTER TABLE contractors ADD COLUMN premium_setup_purchased_at TIMESTAMP;
ALTER TABLE contractors ADD COLUMN premium_setup_call_scheduled BOOLEAN DEFAULT FALSE;
ALTER TABLE contractors ADD COLUMN premium_setup_call_completed BOOLEAN DEFAULT FALSE;
ALTER TABLE contractors ADD COLUMN premium_setup_notes TEXT;
```

### Stripe Configuration

**Product**: "Quoted Premium Setup"
- Product ID: Create in Stripe Dashboard
- Price: $199 one-time
- Checkout mode: `payment` (not subscription)
- Bundle with: Standard subscription ($9/mo) as separate line item

```python
# backend/api/billing.py - Add to checkout session creation

async def create_premium_setup_checkout(contractor_id: str):
    session = stripe.checkout.Session.create(
        mode="payment",  # One-time payment
        line_items=[
            {
                "price": settings.stripe_premium_setup_price_id,  # $199 one-time
                "quantity": 1,
            },
            {
                "price": settings.stripe_monthly_price_id,  # $9/mo subscription
                "quantity": 1,
            }
        ],
        success_url=f"{settings.frontend_url}/premium-setup-success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.frontend_url}/pricing",
        metadata={
            "contractor_id": contractor_id,
            "purchase_type": "premium_setup"
        },
        subscription_data={
            "metadata": {
                "contractor_id": contractor_id,
                "premium_setup": "true"
            }
        }
    )
    return session
```

### Webhook Handler

```python
# backend/api/billing.py - Add webhook event handler

@router.post("/webhooks/stripe")
async def handle_stripe_webhook(request: Request):
    # ... existing signature verification ...

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        if session.get("metadata", {}).get("purchase_type") == "premium_setup":
            contractor_id = session["metadata"]["contractor_id"]

            # Update contractor record
            await update_contractor(
                contractor_id,
                premium_setup_purchased=True,
                premium_setup_purchased_at=datetime.utcnow()
            )

            # Send onboarding email with Calendly link
            await send_premium_setup_email(contractor_id)

            # Track in PostHog
            posthog.capture(
                contractor_id,
                "premium_setup_purchased",
                {"amount": 199}
            )
```

### API Endpoints

```python
# backend/api/premium_setup.py - New file

from fastapi import APIRouter, Depends
from backend.services.auth import get_current_contractor

router = APIRouter(prefix="/api/premium-setup", tags=["premium-setup"])

@router.get("/status")
async def get_premium_setup_status(
    contractor: Contractor = Depends(get_current_contractor)
):
    """Get premium setup status for current user"""
    return {
        "purchased": contractor.premium_setup_purchased,
        "purchased_at": contractor.premium_setup_purchased_at,
        "call_scheduled": contractor.premium_setup_call_scheduled,
        "call_completed": contractor.premium_setup_call_completed,
        "calendly_url": settings.calendly_premium_setup_url if contractor.premium_setup_purchased else None
    }

@router.post("/mark-call-scheduled")
async def mark_call_scheduled(
    contractor: Contractor = Depends(get_current_contractor)
):
    """Mark that user has scheduled their onboarding call"""
    await update_contractor(
        contractor.id,
        premium_setup_call_scheduled=True
    )
    return {"success": True}

@router.post("/mark-call-completed")
async def mark_call_completed(
    contractor: Contractor = Depends(get_current_contractor),
    notes: str = None
):
    """Mark onboarding call as completed (admin only)"""
    # TODO: Add admin auth check
    await update_contractor(
        contractor.id,
        premium_setup_call_completed=True,
        premium_setup_notes=notes
    )
    return {"success": True}
```

### Frontend Changes

**File: `frontend/landing.html`**
- Add Premium Setup tier to pricing section
- Add feature comparison table
- Add "Most Popular" badge

**File: `frontend/index.html`**
- Add premium setup status indicator
- Show "Book Call" prompt if purchased but not scheduled
- Show setup progress checklist

**New File: `frontend/premium-setup-success.html`**
- Celebration animation
- Calendly embed for booking
- What to prepare for call
- "What happens next" section

### Email Templates

**Email 1: Purchase Confirmation**
```
Subject: Welcome to Premium Setup! Book your onboarding call

Hi [Name],

You're in! Here's what happens next:

1. Book your 30-minute onboarding call: [Calendly Link]
2. Before the call, have ready:
   - Your logo file (PNG or JPG)
   - 2-3 example quotes you've done before
   - Any specific pricing rules (markup %, labor rates)

3. After the call, you'll have:
   - Your pricing model configured
   - Templates ready to go
   - First quote created together

Questions before then? Just reply to this email.

– Eddie, Founder of Quoted
```

**Email 2: Call Reminder (24 hours before)**
```
Subject: Your Quoted setup call is tomorrow

Quick reminder: we're meeting tomorrow at [TIME].

Here's what to have ready:
- Your logo file
- Example quotes (if you have them)
- 10 minutes to describe your typical jobs

Talk soon!
– Eddie
```

**Email 3: Post-Call Follow-up**
```
Subject: Your Quoted setup is complete!

Great call! Here's what we set up:

[Summary of configuration]

Your next steps:
1. Create your first real quote
2. Send it to a customer
3. Watch the AI learn from your edits

Remember: I'm reviewing your first 5 quotes personally.
Just create them normally and I'll check in after.

Priority support for the next 30 days: just reply to any email.

– Eddie
```

---

## Configuration Required

### Environment Variables
```
STRIPE_PREMIUM_SETUP_PRICE_ID=price_xxx  # Create in Stripe
CALENDLY_PREMIUM_SETUP_URL=https://calendly.com/eddie-quoted/premium-setup
```

### Stripe Products to Create
1. **Product**: "Quoted Premium Setup"
   - One-time price: $199.00
   - Description: "Personalized onboarding with founder"

2. **Update Checkout**: Bundle with monthly subscription

### Calendly Setup
1. Create 30-minute event type: "Quoted Premium Setup Call"
2. Set availability (suggest: 2 slots/day, 3 days/week)
3. Add intake questions:
   - What type of work do you quote? (e.g., consulting, design, trades, services)
   - How many quotes do you send per week?
   - What's your biggest quoting pain point?

---

## Success Metrics

| Metric | Target | Tracking |
|--------|--------|----------|
| Premium Setup purchases | 10/month | Stripe + PostHog |
| Call booking rate | >90% within 48hrs | PostHog |
| Call completion rate | >95% | Manual + PostHog |
| 30-day retention | >80% | PostHog cohort |
| Referrals from premium users | 2+ per user | Referral tracking |

### PostHog Events to Track
- `premium_setup_checkout_started`
- `premium_setup_purchased`
- `premium_setup_call_scheduled`
- `premium_setup_call_completed`
- `premium_user_first_quote`
- `premium_user_fifth_quote`

---

## Implementation Checklist

### Phase 1: Backend (2-3 hours)
- [ ] Add database fields (migration)
- [ ] Create Stripe product and price
- [ ] Add checkout endpoint for premium setup
- [ ] Add webhook handler for premium setup purchases
- [ ] Create `/api/premium-setup/*` endpoints
- [ ] Add email templates to Resend

### Phase 2: Frontend (2-3 hours)
- [ ] Update pricing section on landing page
- [ ] Create premium-setup-success.html page
- [ ] Add premium status indicator to dashboard
- [ ] Add Calendly embed integration
- [ ] Add setup progress checklist component

### Phase 3: Operations (1 hour)
- [ ] Set up Calendly event type
- [ ] Create intake form questions
- [ ] Document call script/checklist for Eddie
- [ ] Test full purchase → call → completion flow

---

## Call Script for Eddie

### Before Call
- Review intake form answers
- Check their existing quotes (if any)
- Have their account open and ready

### Call Structure (30 min)
1. **Intro (2 min)**: Quick hello, confirm their business type
2. **Discovery (5 min)**: How do they quote now? What's painful?
3. **Demo (5 min)**: Show them creating a quote for their work
4. **Setup (10 min)**: Configure their pricing model together
5. **First Quote (5 min)**: Create their first real quote together
6. **Q&A (3 min)**: Any questions, how to reach you

### After Call
- Send follow-up email with summary
- Add to "premium users" list for check-ins
- Schedule 1-week follow-up reminder

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Too many calls to handle | Limit to 3/day max, raise price if oversubscribed |
| Users don't book call | Automated reminders at 24h, 72h, 7d |
| Call quality inconsistent | Use structured script, improve each call |
| Users feel setup wasn't worth it | Guarantee: "Works or money back" |

---

## Future Enhancements

1. **Team Setup** ($499): For companies with 2-5 users
2. **Enterprise Setup** (Custom): On-site or multi-hour
3. **Setup Alumni** community/Slack for premium users
4. **Recorded Setup Library**: Common setups as videos

---

*Document created: 2025-12-23*
*For Quoted AI Team implementation*
