# Engineering State

**Last Updated**: 2025-12-02 08:30 PST
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
| PAY-001 | Payment Infrastructure (Stripe) | CTO | BLOCKED | Waiting for Stripe account + API keys |
| PAY-002 | Trial Logic & Quote Limits | CTO | BLOCKED | Depends on PAY-001 |
| PAY-003 | Billing UI | CTO | BLOCKED | Depends on PAY-002 |
| PAY-004 | Email System (Resend) | CTO | BLOCKED | Waiting for Resend account + API key |
| PAY-005 | Referral System | CTO | BLOCKED | Depends on PAY-002 |
| ~~PAY-006~~ | ~~Terms of Service + Privacy Policy~~ | ~~CTO~~ | **COMPLETE** | Deployed 325fb25 |

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
ANTHROPIC_API_KEY     - Claude API key
OPENAI_API_KEY        - Whisper transcription
SESSION_SECRET        - Auth session signing
```

---

## Testing

| Type | Coverage | Status |
|------|----------|--------|
| Unit Tests | 0% | NOT IMPLEMENTED |
| Integration Tests | 0% | NOT IMPLEMENTED |
| Manual Testing | 100% | Ongoing |

**Note**: MVP shipped without automated tests. Add before scaling.
