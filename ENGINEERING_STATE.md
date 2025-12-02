# Engineering State

**Last Updated**: 2025-12-02 09:00 PST
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
| **Production** | https://web-production-0550.up.railway.app | RUNNING | 7d50e73 |
| **Custom Domain** | https://quoted.it.com | LIVE (SSL ACTIVE) | 7d50e73 |

**Railway Project**: Connected to main branch, auto-deploys on push

**Environment Variable**: `ENVIRONMENT=production` is set ✓ (HTTPS redirect and CORS active)

---

## In Progress

| Ticket | Description | Assignee | Status | Blockers |
|--------|-------------|----------|--------|----------|
| PAY-001 | Payment Infrastructure (Stripe) | Backend Engineer | **READY** | None - All keys received ✓ |
| PAY-002 | Trial Logic & Quote Limits | Backend Engineer | QUEUED | Depends on PAY-001 |
| PAY-003 | Billing UI | Frontend Engineer | QUEUED | Depends on PAY-002 |
| PAY-004 | Email System (Resend) | Backend Engineer | **READY** | None - API key received ✓ |
| PAY-005 | Referral System | Backend Engineer | QUEUED | Depends on PAY-002 |
| ~~PAY-006~~ | ~~Terms of Service + Privacy Policy~~ | ~~CTO~~ | **COMPLETE** | Deployed 325fb25 |

---

## PAY-001 Task Breakdown (READY FOR EXECUTION)

**Stripe Account Status**: SANDBOX ACTIVE ✓ ALL KEYS RECEIVED
- Publishable Key: `pk_test_51SZugaKF9pNNNH32Psj...` ✓
- Secret Key: `sk_test_51SZugaKF9pNNNH32Wti...` ✓
- Webhook Secret: Will create after backend routes deployed

**Products Created in Stripe**:
| Product | Product ID | Status |
|---------|------------|--------|
| Starter ($29/mo) | `prod_TWyp6aH4vMY7A8` | ✓ Ready |
| Pro ($49/mo) | `prod_TWyzygs71MWNeQ` | ✓ Ready |
| Team ($79/mo) | `prod_TWz0uN0EAbgPKI` | ✓ Ready |
| Quotes Meter | Created | ✓ Ready |

**Implementation Tasks** (for Backend Engineer):
1. [ ] Add Stripe SDK to requirements.txt
2. [ ] Create `/api/billing/` routes:
   - `POST /api/billing/create-checkout` - Start subscription
   - `POST /api/billing/webhook` - Handle Stripe events
   - `GET /api/billing/portal` - Customer portal link
   - `GET /api/billing/status` - Current subscription status
3. [ ] Add user fields: `stripe_customer_id`, `subscription_id`, `plan_tier`, `quotes_used`, `billing_cycle_start`
4. [ ] Implement quote counting + overage reporting to Stripe meter
5. [ ] Add subscription status checks to quote generation endpoint

**Environment Variables** (add to Railway):
```
STRIPE_SECRET_KEY=sk_test_51SZugaKF9pNNNH32WtiBokn1imZ0IFRdRr38mht4mpebsaZWaH5YM2RhfF2pbxpju2Yo9Z2f67pVTYPdVnLqwBMM000CI0hXIl
STRIPE_PUBLISHABLE_KEY=pk_test_51SZugaKF9pNNNH32PsjrEPHK1ynwZ1vTnHRHlQKqdS5u6r2ivaMcLTpvpK5H1VehWBLyx4hTn5rsZXTza8oVM9qM00K5n28vOe
STRIPE_STARTER_PRODUCT_ID=prod_TWyp6aH4vMY7A8
STRIPE_PRO_PRODUCT_ID=prod_TWyzygs71MWNeQ
STRIPE_TEAM_PRODUCT_ID=prod_TWz0uN0EAbgPKI
STRIPE_WEBHOOK_SECRET=whsec_...      # After webhook creation
```

---

## PAY-004 Task Breakdown (READY FOR EXECUTION)

**Resend Account Status**: ACTIVE ✓
- API Key: `re_igyXR4D5_6VcjoKhx6SUjPAWZ9UsLwWx6` ✓

**Implementation Tasks** (for Backend Engineer):
1. [ ] Add Resend SDK to requirements.txt
2. [ ] Create email service (`backend/services/email.py`)
3. [ ] Implement transactional emails:
   - Welcome email (after signup)
   - Trial starting email
   - Trial ending reminder (day 5)
   - Subscription confirmation
   - Payment failed notification
4. [ ] Create email templates (HTML)

**Environment Variables** (add to Railway):
```
RESEND_API_KEY=re_igyXR4D5_6VcjoKhx6SUjPAWZ9UsLwWx6
```

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
| 2025-12-02 | 325fb25 | Add Terms of Service and Privacy Policy pages | PENDING DEPLOY |
| 2025-12-02 | 7d50e73 | Security hardening: SQLite issues, rate limiting, CORS, HTTPS | SUCCESS |
| 2025-12-02 | eb290f0 | Add autonomous operations infrastructure | SUCCESS |
| 2025-12-01 | 43af5c6 | Add quote history UI with editable line items | SUCCESS |
| 2025-12-01 | d050eec | Update anthropic SDK for tool calling | SUCCESS |
| 2025-12-01 | 8b91f15 | Add structured outputs, feedback, confidence | SUCCESS |

---

## Architecture Notes

### Stack
- **Backend**: FastAPI + Python 3.11
- **Database**: SQLite (aiosqlite) - single file at `./data/quoted.db`
- **AI**: Claude Sonnet 4 (quotes) + Claude Haiku (category detection)
- **Transcription**: OpenAI Whisper
- **PDF**: ReportLab
- **Hosting**: Railway (web service)

### Key Files
- `backend/main.py` - FastAPI app entry
- `backend/services/quote_generator.py` - Core quote generation
- `backend/services/learning.py` - Correction processing
- `backend/prompts/quote_generation.py` - Prompt construction (learning injection)
- `frontend/index.html` - Main app (31K tokens, vanilla JS)
- `frontend/landing.html` - Landing page
- `frontend/terms.html` - Terms of Service
- `frontend/privacy.html` - Privacy Policy

### API Endpoints
```
/api/auth/*           - Authentication
/api/quotes/*         - Quote CRUD, generation, PDF
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
| - | - | No incidents recorded | - | - |

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

# NEW - Add before next /quoted-run
STRIPE_SECRET_KEY=sk_test_51SZugaKF9pNNNH32WtiBokn1imZ0IFRdRr38mht4mpebsaZWaH5YM2RhfF2pbxpju2Yo9Z2f67pVTYPdVnLqwBMM000CI0hXIl
STRIPE_PUBLISHABLE_KEY=pk_test_51SZugaKF9pNNNH32PsjrEPHK1ynwZ1vTnHRHlQKqdS5u6r2ivaMcLTpvpK5H1VehWBLyx4hTn5rsZXTza8oVM9qM00K5n28vOe
STRIPE_STARTER_PRODUCT_ID=prod_TWyp6aH4vMY7A8
STRIPE_PRO_PRODUCT_ID=prod_TWyzygs71MWNeQ
STRIPE_TEAM_PRODUCT_ID=prod_TWz0uN0EAbgPKI
RESEND_API_KEY=re_igyXR4D5_6VcjoKhx6SUjPAWZ9UsLwWx6
```

---

## Testing

| Type | Coverage | Status |
|------|----------|--------|
| Unit Tests | 0% | NOT IMPLEMENTED |
| Integration Tests | 0% | NOT IMPLEMENTED |
| Manual Testing | 100% | Ongoing |

**Note**: MVP shipped without automated tests. Add before scaling.
