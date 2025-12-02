# Engineering State

**Last Updated**: 2025-12-02 11:15 PST
**Updated By**: CEO (AI)

---

## Current Sprint

**Sprint**: 1 (Beta Launch)
**Goal**: Stable production, DNS configured, first beta users onboarded
**Dates**: 2025-12-01 to 2025-12-08

---

## Deployment Status

| Environment | URL | Status | Version |
|-------------|-----|--------|---------|
| **Production** | https://web-production-0550.up.railway.app | RUNNING | 5a84de5 |
| **Custom Domain** | https://quoted.it.com | LIVE (SSL ACTIVE) | 5a84de5 |

**Railway Project**: Connected to main branch, auto-deploys on push

**Environment Variable**: `ENVIRONMENT=production` is set ✓ (HTTPS redirect and CORS active)

---

## In Progress

| Ticket | Description | Assignee | Status | Blockers |
|--------|-------------|----------|--------|----------|
| ~~PAY-001~~ | ~~Payment Infrastructure (Stripe)~~ | ~~Backend Engineer~~ | **COMPLETE** | Committed cb1e311 |
| ~~PAY-002~~ | ~~Trial Logic & Quote Limits~~ | ~~Backend Engineer~~ | **COMPLETE** | Included in PAY-001 |
| ~~PAY-003~~ | ~~Billing UI~~ | ~~Frontend Engineer~~ | **COMPLETE** | Committed b4e9fdc |
| ~~PAY-004~~ | ~~Email System (Resend)~~ | ~~Backend Engineer~~ | **COMPLETE** | Committed 33fa641 |
| PAY-005 | Referral System | Backend Engineer | **READY** | Can start now |
| ~~PAY-006~~ | ~~Terms of Service + Privacy Policy~~ | ~~CTO~~ | **COMPLETE** | Deployed 325fb25 |

---

## PAY-001 Implementation (COMPLETE ✓)

**Commit**: `cb1e311` - "Add: Stripe payment infrastructure for subscription billing"

**Implementation Summary**:
- ✅ Stripe SDK added (`stripe==11.1.1`)
- ✅ Billing routes created (`/api/billing/*`)
- ✅ User model extended with billing fields
- ✅ Trial auto-initialization (7 days, 75 quotes)
- ✅ Quote limits enforced (402 responses when exceeded)
- ✅ Usage tracking integrated into quote generation

**New API Endpoints**:
```
POST /api/billing/create-checkout - Start subscription
POST /api/billing/webhook - Stripe webhook handler
POST /api/billing/portal - Customer portal access
GET /api/billing/status - Current subscription status
GET /api/billing/plans - Available pricing (public)
```

**New Files**:
- `backend/services/billing.py` - BillingService class
- `backend/api/billing.py` - API routes

---

## PAY-004 Implementation (COMPLETE ✓)

**Commit**: `33fa641` - "Add: Resend email service for transactional emails"

**Implementation Summary**:
- ✅ Resend SDK added (`resend==2.4.0`)
- ✅ Email service created with 5 email types
- ✅ Welcome email integrated with registration
- ✅ Dark premium HTML templates

**Emails Ready**:
- ✅ Welcome email (sends on registration)
- 🔜 Trial starting email (hook into first quote)
- 🔜 Trial ending reminder (hook into day 5 cron)
- 🔜 Subscription confirmation (hook into Stripe webhook)
- 🔜 Payment failed notification (hook into Stripe webhook)

**New Files**:
- `backend/services/email.py` - EmailService class (455 lines)

---

## Code Review Queue

| PR | Author | Reviewer | Status |
|----|--------|----------|--------|
| - | No open PRs | - | - |

---

## Technical Debt

| Item | Priority | Effort | Notes |
|------|----------|--------|-------|
| ~~Issues API uses in-memory storage~~ | ~~LOW~~ | ~~2h~~ | RESOLVED - Migrated to SQLite (7d50e73) |
| ~~CORS allows all origins~~ | ~~LOW~~ | ~~1h~~ | RESOLVED - Restricted to quoted.it.com (7d50e73) |
| ~~No rate limiting~~ | ~~MEDIUM~~ | ~~3h~~ | RESOLVED - Added slowapi limits (7d50e73) |
| No error tracking (Sentry) | MEDIUM | 2h | Add before scaling |
| No automated tests | MEDIUM | 4h | Add unit tests for core flows |

---

## Recent Deployments

| Date | Commit | Description | Status |
|------|--------|-------------|--------|
| 2025-12-02 | 5a84de5 | Add billing column migrations for existing Postgres databases | **DEPLOYED** |
| 2025-12-02 | 6aedad1 | Add annual billing interval support | **DEPLOYED** |
| 2025-12-02 | f871c12 | Fix pricing card field mapping (API response → frontend) | **DEPLOYED** |
| 2025-12-02 | b4e9fdc | Add Billing UI with pricing, usage tracking, upgrade modal | **DEPLOYED** |
| 2025-12-02 | 33fa641 | Add Resend email service for transactional emails | **DEPLOYED** |
| 2025-12-02 | cb1e311 | Add Stripe payment infrastructure for subscription billing | **DEPLOYED** |
| 2025-12-02 | 325fb25 | Add Terms of Service and Privacy Policy pages | **DEPLOYED** |
| 2025-12-02 | 7d50e73 | Security hardening: SQLite issues, rate limiting, CORS, HTTPS | SUCCESS |
| 2025-12-02 | eb290f0 | Add autonomous operations infrastructure | SUCCESS |
| 2025-12-01 | 43af5c6 | Add quote history UI with editable line items | SUCCESS |

---

## Architecture Notes

### Stack
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL (Railway) - Production; SQLite (dev fallback)
- **AI**: Claude Sonnet 4 (quotes) + Claude Haiku (category detection)
- **Transcription**: OpenAI Whisper
- **PDF**: ReportLab
- **Hosting**: Railway (web service + Postgres)

### Key Files
- `backend/main.py` - FastAPI app entry
- `backend/services/quote_generator.py` - Core quote generation
- `backend/services/learning.py` - Correction processing
- `backend/services/billing.py` - Stripe subscription handling
- `backend/services/email.py` - Resend transactional emails
- `backend/prompts/quote_generation.py` - Prompt construction (learning injection)
- `frontend/index.html` - Main app (31K tokens, vanilla JS)
- `frontend/landing.html` - Landing page
- `frontend/terms.html` - Terms of Service
- `frontend/privacy.html` - Privacy Policy

### API Endpoints
```
/api/auth/*           - Authentication
/api/quotes/*         - Quote CRUD, generation, PDF
/api/billing/*        - Stripe subscriptions, checkout, portal
/api/contractors/*    - Contractor profile
/api/onboarding/*     - Setup interview
/api/issues/*         - Issue reporting (autonomous processing)
/terms                - Terms of Service page
/privacy              - Privacy Policy page
```

---

## On-Call

**Primary**: Autonomous AI Engineering
**Escalation**: Eddie (Founder) for Type 3-4 decisions

---

## Incidents

| Date | Severity | Issue | Resolution | Post-mortem |
|------|----------|-------|------------|-------------|
| 2025-12-02 | MEDIUM | Missing billing columns in Postgres (500 errors on /api/quotes) | Added auto-migrations for billing columns (5a84de5) | SQLAlchemy create_all doesn't add columns to existing tables; need explicit ALTER migrations |

---

## Known Issues

| Issue | Severity | Workaround | Fix ETA |
|-------|----------|------------|---------|
| ~~Issues reset on Railway restart~~ | ~~LOW~~ | ~~None~~ | RESOLVED (SQLite) |
| No issues currently | - | - | - |

---

## Environment Variables

Required in Railway:
```
# Existing (already set)
ANTHROPIC_API_KEY     - Claude API key
OPENAI_API_KEY        - Whisper transcription
SESSION_SECRET        - Auth session signing
ENVIRONMENT           - "production"

# PAYMENT - Add before deployment
STRIPE_SECRET_KEY=sk_test_51SZugaKF9pNNNH32WtiBokn1imZ0IFRdRr38mht4mpebsaZWaH5YM2RhfF2pbxpju2Yo9Z2f67pVTYPdVnLqwBMM000CI0hXIl
STRIPE_PUBLISHABLE_KEY=pk_test_51SZugaKF9pNNNH32PsjrEPHK1ynwZ1vTnHRHlQKqdS5u6r2ivaMcLTpvpK5H1VehWBLyx4hTn5rsZXTza8oVM9qM00K5n28vOe
STRIPE_STARTER_PRODUCT_ID=prod_TWyp6aH4vMY7A8
STRIPE_PRO_PRODUCT_ID=prod_TWyzygs71MWNeQ
STRIPE_TEAM_PRODUCT_ID=prod_TWz0uN0EAbgPKI
STRIPE_WEBHOOK_SECRET=whsec_...  # Generate in Stripe dashboard after deployment

# EMAIL - Add before deployment
RESEND_API_KEY=re_igyXR4D5_6VcjoKhx6SUjPAWZ9UsLwWx6
```

**Post-Deployment Steps**:
1. Add all env vars above to Railway
2. Deploy (auto on push to main)
3. Configure Stripe webhook: `https://quoted.it.com/api/billing/webhook`
4. Get webhook secret from Stripe, add `STRIPE_WEBHOOK_SECRET` to Railway
5. Test checkout flow end-to-end

---

## Testing

| Type | Coverage | Status |
|------|----------|--------|
| Unit Tests | 0% | NOT IMPLEMENTED |
| Integration Tests | 0% | NOT IMPLEMENTED |
| Manual Testing | 100% | Ongoing |

**Note**: MVP shipped without automated tests. Add before scaling.
