# DISC-050: Stripe Pricing Configuration Fix

## Problem
Only the Pro plan button works on the pricing page. Starter and Team plan buttons fail because those products don't have active prices configured in Stripe.

## Root Cause
The backend code at `backend/services/billing.py` line 240 calls:
```python
prices = stripe.Price.list(product=plan_config["product_id"], active=True)
```

This returns an empty list for Starter and Team products, causing the checkout to fail.

## Solution
Configure active prices for all three products in the Stripe Dashboard.

## Steps to Fix in Stripe Dashboard

### 1. Navigate to Products
Go to: https://dashboard.stripe.com/products

### 2. Configure Starter Plan (prod_TXB6SKP96LAlcM)
- Click on the Starter product
- Add a new price:
  - **Amount**: $19.00 USD
  - **Billing period**: Monthly
  - **Status**: Active
- Optional: Add annual price:
  - **Amount**: $190.00 USD (or $158.33 for 2 months free)
  - **Billing period**: Yearly
  - **Status**: Active

### 3. Configure Pro Plan (prod_TXB6du0ylntvVV)
- Verify this already has active prices configured
- Should have:
  - Monthly: $39.00 USD (active)
  - Annual: $390.00 USD or similar (active)

### 4. Configure Team Plan (prod_TXB6aO5kvAD4uV)
- Click on the Team product
- Add a new price:
  - **Amount**: $79.00 USD
  - **Billing period**: Monthly
  - **Status**: Active
- Optional: Add annual price:
  - **Amount**: $790.00 USD (or $658.33 for 2 months free)
  - **Billing period**: Yearly
  - **Status**: Active

## Verification
After configuring prices in Stripe:

1. **Test locally**:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Open browser**: http://localhost:8000/app

3. **Navigate to**: Account & Billing section

4. **Click each plan button**: Starter, Pro, Team
   - Each should redirect to Stripe Checkout
   - Checkout page should show correct price

## Current Pricing (as of config.py)
- **Starter**: $19/month (75 quotes, $0.50 overage)
- **Pro**: $39/month (200 quotes, $0.35 overage)
- **Team**: $79/month (unlimited quotes)

## Code Changes Made
Added better error handling in `backend/services/billing.py`:
- Clear error messages when prices are missing
- Logging to help diagnose configuration issues
- Graceful degradation with fallback to first available price

## Related Files
- `backend/config.py` - Product IDs
- `backend/services/billing.py` - Checkout logic
- `backend/api/billing.py` - API endpoint
- `frontend/index.html` - Pricing cards and checkout flow
