# Backend Learning

**Last Updated**: 2025-12-02
**Purpose**: Accumulated knowledge about the Quoted backend codebase

---

## Architecture Patterns

### Database
- SQLite with aiosqlite for async operations
- Database file: `./data/quoted.db`
- Connection pooling via SQLAlchemy

### API Structure
- All routes in `backend/api/` directory
- Auth: Session-based with cookies
- Rate limiting: slowapi (5/min on expensive endpoints)
- CORS: Restricted to quoted.it.com in production

### AI Integration
- Claude Sonnet 4 for quote generation (tool calling mode)
- Claude Haiku for category detection (fast, cheap)
- OpenAI Whisper for transcription
- Structured outputs via Pydantic models

---

## Key Learnings

| Date | Learning | Context |
|------|----------|---------|
| 2025-12-01 | Tool calling eliminates JSON parsing failures | Switched from text extraction to structured outputs |
| 2025-12-01 | 3-sample confidence scoring catches hallucinations | Variance > 30% triggers clarifying questions |
| 2025-12-02 | SQLite is sufficient for single-server MVP | No need for PostgreSQL until horizontal scale |
| 2025-12-02 | Rate limiting prevents API cost abuse | 5/min on /api/quotes/generate |
| 2025-12-02 | Resend email service added for transactional emails | Welcome, trial, subscription, payment failed notifications |
| 2025-12-02 | Stripe payment infrastructure implemented | PAY-001: Subscriptions, usage metering, webhook handling, trial management |
| 2025-12-02 | Pricing Brain API for learned knowledge visibility | FEAT-001: View/edit AI-learned pricing rules per category, Haiku analysis |
| 2025-12-02 | Separate endpoint for customer edits avoids learning trigger | FEAT-002: PUT /customer endpoint for non-pricing updates, no learning overhead |
| 2025-12-02 | Analytics service with graceful degradation pattern | CONVERT-001: PostHog tracking wraps all events in try/except, logs even without API key |
| 2025-12-02 | Sentry initialization must happen before app creation | INFRA-001: Initialize Sentry SDK in main.py before FastAPI app instantiation |
| 2025-12-02 | Referral system with automatic code generation | GROWTH-002: Unique codes from email (JOHN-A3X9), 14-day extended trial for referee, 1-month credit for referrer on subscription |

---

## Common Gotchas

1. **Environment variable**: Check `ENVIRONMENT=production` for HTTPS/CORS behavior
2. **Database path**: Relative to working directory (`./data/quoted.db`)
3. **Session secrets**: Must be set in Railway environment
4. **Transcription timeout**: Whisper can be slow on long recordings

---

## Code Patterns to Follow

### Route Structure
```python
@router.post("/endpoint")
async def endpoint_name(
    request: RequestModel,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> ResponseModel:
    """Docstring explaining purpose."""
    # Implementation
    return ResponseModel(...)
```

### Error Handling
```python
from fastapi import HTTPException

if not resource:
    raise HTTPException(status_code=404, detail="Resource not found")
```

---

## Files to Know

| File | Purpose | Complexity |
|------|---------|------------|
| `backend/main.py` | App entry, middleware setup | Medium |
| `backend/services/quote_generator.py` | Core AI logic | High |
| `backend/services/learning.py` | Correction processing | Medium |
| `backend/services/pricing_brain.py` | Pricing knowledge management, Haiku analysis | Low |
| `backend/services/email.py` | Transactional emails via Resend | Low |
| `backend/services/billing.py` | Stripe subscription management | Medium |
| `backend/services/analytics.py` | PostHog event tracking | Low |
| `backend/prompts/quote_generation.py` | Prompt construction | Medium |
| `backend/api/quotes.py` | Quote CRUD endpoints | Medium |
| `backend/api/pricing_brain.py` | Pricing Brain CRUD endpoints | Low |
| `backend/api/auth.py` | Authentication, registration | Medium |
| `backend/api/billing.py` | Stripe webhooks, checkout, portal | Medium |

---

## Billing & Payments (PAY-001)

### Implementation Details
- **Provider**: Stripe (Test Mode)
- **Product IDs**: Configured in settings (starter, pro, team)
- **Trial**: 7 days, 75 quotes, automatic initialization on registration
- **Usage Tracking**: Increments on every successful quote generation
- **Overage**: Allowed for paid plans, reported to Stripe meter

### Webhook Events Handled
- `checkout.session.completed` - Subscription created
- `customer.subscription.updated` - Renewal or plan change (resets usage)
- `customer.subscription.deleted` - Cancellation (downgrades to expired trial)
- `invoice.payment_succeeded` - Successful payment
- `invoice.payment_failed` - Payment failure (TODO: email notification)

### API Endpoints
- `POST /api/billing/create-checkout` - Start subscription flow
- `POST /api/billing/webhook` - Stripe event handler (public, signature verified)
- `POST /api/billing/portal` - Customer portal URL
- `GET /api/billing/status` - Current usage and limits
- `GET /api/billing/plans` - Available pricing plans

### Quote Generation Guards
- Both `/api/quotes/generate` and `/api/quotes/generate-from-audio` check limits before processing
- Returns 402 Payment Required with structured error:
  - `trial_expired` - Trial period ended
  - `trial_limit_reached` - Used all trial quotes
  - `quota_exceeded` - Generic limit error
- Usage incremented after successful quote creation

### Environment Variables Required
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Analytics & Monitoring (CONVERT-001 + INFRA-001)

### PostHog Analytics
- **Service**: `backend/services/analytics.py`
- **Pattern**: Graceful degradation - logs events even without API key
- **Events Tracked**:
  - `signup_completed` - User registration (with identification)
  - `onboarding_completed` - Setup interview finished
  - `quote_generated` - Quote created (with category, confidence, subtotal)
  - `quote_edited` - Quote modified (with change type and magnitude)
  - `subscription_activated` - Payment successful (with plan tier)

### Sentry Error Tracking
- **Initialization**: `backend/main.py` (before app creation)
- **Integrations**: FastAPI + Starlette
- **Sampling**: 100% transactions (for MVP - reduce when scaling)
- **Environment**: Auto-detected from `ENVIRONMENT` setting

### Environment Variables Required
```
POSTHOG_API_KEY=phc_...     # Optional - degrades gracefully
SENTRY_DSN=https://...      # Optional - degrades gracefully
```

### Design Pattern
Both services follow "fail-safe" pattern:
- Missing API keys log warnings, don't crash
- All tracking wrapped in try/except
- Events logged to console for debugging
- Never block core business logic

---

## Referral System (GROWTH-002)

### Implementation Details
- **Code Generation**: Format is FIRSTNAME-XXXX (e.g., JOHN-A3X9) extracted from email username
- **Uniqueness**: Collision detection with retry logic, timestamp fallback if needed
- **Referee Benefit**: Extended trial from 7 to 14 days when using referral code
- **Referrer Reward**: 1 month credit when referee subscribes to paid plan

### Database Columns Added
- `users.referral_code` - User's unique referral code (indexed, unique)
- `users.referred_by_code` - Referral code used during signup (indexed)
- `users.referral_count` - Count of successful referrals (incremented on subscription)
- `users.referral_credits` - Months of credit earned (1 per successful referral)

### API Endpoints
- `GET /api/referral/code` - Get user's referral code
- `GET /api/referral/stats` - Get referral count and credits
- `GET /api/referral/link` - Get full shareable link (https://quoted.it.com/?ref=CODE)

### Integration Points
1. **Registration** (`backend/services/auth.py`):
   - Auto-generates referral code on signup
   - Accepts optional `referral_code` in UserCreate payload
   - Applies referral code after trial initialization (extends to 14 days)

2. **Billing** (`backend/services/billing.py`):
   - Credits referrer when referee subscribes (checkout.session.completed webhook)
   - Increments referrer's referral_count and referral_credits

3. **Analytics** (PostHog events):
   - `referral_code_generated` - When user gets their code
   - `referral_code_applied` - When new user uses a code
   - `referral_credit_earned` - When referrer earns a credit
   - `signup_completed` - Now includes referral data
   - `subscription_activated` - Now includes was_referred flag

### Edge Cases Handled
- Invalid referral code → HTTP 400, doesn't block registration (logged warning)
- Self-referral → HTTP 400 "Cannot use your own referral code"
- Code collision → Retry with new random suffix, fallback to timestamp
- Missing referrer → Logged warning, doesn't block credit flow

### Configuration
- `frontend_url` setting in config.py for generating shareable links
- Default: "https://quoted.it.com"

---

## Pending Improvements

- [ ] Add unit tests for core flows
- [ ] Add pagination to list endpoints
- [ ] Add email notifications for payment events
- [ ] Implement actual overage reporting to Stripe meter API
