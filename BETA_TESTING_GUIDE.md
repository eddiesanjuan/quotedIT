# Beta Testing Guide for Quoted

**Purpose**: Ensure beta users have a smooth experience before launch.

---

## 1. New User Signup Flow

**Test as a fresh user (use incognito or new email):**

- [ ] Go to https://quoted.it.com
- [ ] Landing page loads, looks professional
- [ ] Click "Start Free Trial" or "Get Started"
- [ ] Complete registration form
- [ ] **Check**: Welcome email arrives (from Resend)
- [ ] **Check**: Redirected to onboarding interview

---

## 2. Onboarding Interview

- [ ] Interview starts with first question
- [ ] Answer questions about your trade/pricing
- [ ] **Check**: Progress feels natural, not too long
- [ ] **Check**: Can skip questions if needed
- [ ] Interview completes, redirected to main app

---

## 3. Quote Generation (Core Value Prop)

### Voice Input
- [ ] Click microphone/record button
- [ ] Speak a job description: *"I need a quote for a 12x14 deck with composite decking and aluminum railings"*
- [ ] **Check**: Transcription appears correctly
- [ ] **Check**: Quote generates in <60 seconds
- [ ] **Check**: Line items are reasonable
- [ ] **Check**: Pricing reflects your onboarding answers

### Text Input
- [ ] Type a job description manually
- [ ] **Check**: Quote generates correctly

### Quote Editing
- [ ] Edit a line item price
- [ ] Add a new line item
- [ ] Remove a line item
- [ ] **Check**: Total updates correctly

### PDF Export
- [ ] Click "Download PDF"
- [ ] **Check**: PDF opens, looks professional
- [ ] **Check**: Your business info appears (if entered)

---

## 4. Learning System

- [ ] Generate a quote
- [ ] Edit the pricing (correct something)
- [ ] Save the correction
- [ ] Generate a similar quote
- [ ] **Check**: New quote reflects your correction (may take 2-3 quotes)

---

## 5. Account & Billing

### Trial Status
- [ ] Click "Account" tab
- [ ] **Check**: Shows "STARTER PLAN" or "TRIAL"
- [ ] **Check**: Shows "X / 75" quotes used
- [ ] **Check**: Shows trial days remaining (if trial)

### Pricing Display
- [ ] **Check**: 3 pricing cards appear (Starter, Pro, Team)
- [ ] Toggle Monthly ↔ Annual
- [ ] **Check**: Prices update (Annual shows "Save 17%")

### Checkout Flow (use Stripe test card)
- [ ] Click "Choose Starter" (or any plan)
- [ ] **Check**: Redirects to Stripe Checkout
- [ ] Use test card: `4242 4242 4242 4242`, any future date, any CVC
- [ ] Complete payment
- [ ] **Check**: Redirected back to app
- [ ] **Check**: Plan shows as active

### Customer Portal
- [ ] Click "Manage Subscription" or portal link
- [ ] **Check**: Opens Stripe portal
- [ ] **Check**: Can see/cancel subscription

---

## 6. Quote Limits & Upgrade Prompts

**Test limit behavior:**
- [ ] Generate quotes until near limit (or temporarily lower limit for testing)
- [ ] **Check**: At 80% usage, see warning/nudge
- [ ] **Check**: At 100%, see upgrade modal
- [ ] **Check**: Can't generate more until upgraded (for trial)

---

## 7. Error Handling

- [ ] Try generating quote with empty input → **Check**: Helpful error message
- [ ] Try very long/complex job description → **Check**: Handles gracefully
- [ ] Disconnect internet, try action → **Check**: Error message, doesn't crash

---

## 8. Mobile Experience

**On your phone:**
- [ ] Load https://quoted.it.com
- [ ] **Check**: Landing page readable, buttons tappable
- [ ] Sign up or log in
- [ ] **Check**: Onboarding works on mobile
- [ ] Generate a voice quote
- [ ] **Check**: Recording works, quote displays well
- [ ] Check Account/Billing section
- [ ] **Check**: Pricing cards stack vertically, readable

---

## 9. Email Delivery

- [ ] **Welcome email**: Received after signup?
- [ ] **Check spam folder** if not in inbox
- [ ] Email looks professional, links work?

---

## Quick Smoke Test (5 min)

If you only have 5 minutes, do this:

1. Incognito → quoted.it.com → Sign up
2. Complete onboarding (or skip)
3. Record voice quote: "10x12 wooden deck"
4. Check quote looks reasonable
5. Download PDF
6. Check Account tab shows trial status

---

## Known Issues to Watch For

| Issue | What to Check |
|-------|---------------|
| Slow transcription | >10 seconds = problem |
| Wrong prices | Learning system needs more data |
| Email not arriving | Check spam, verify Resend domain |
| Checkout fails | Check Stripe webhook is configured |

---

## Stripe Test Cards

| Card | Result |
|------|--------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 3220` | 3D Secure authentication |
| `4000 0000 0000 9995` | Declined (insufficient funds) |

---

## Reporting Issues

If you find bugs during testing:
1. Note the exact steps to reproduce
2. Screenshot any error messages
3. Check browser console for errors (F12 → Console tab)
4. Report via the in-app feedback or directly to Eddie
