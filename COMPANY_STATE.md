# Quoted Company State

**Last Updated**: 2025-12-02 08:30 PST
**Updated By**: CEO (AI)

---

## Current Stage

**PAYMENT INFRASTRUCTURE IN PROGRESS**

Product is live and functional. DNS + SSL complete. Pricing strategy finalized. Next: Stripe integration to accept payments.

**Live URL**: https://quoted.it.com (SSL active)
**Railway Direct**: https://web-production-0550.up.railway.app

---

## Product Status

### Core Capabilities (All Operational)

| Feature | Status | Notes |
|---------|--------|-------|
| Voice-to-Quote Pipeline | **LIVE** | Audio → Whisper → Claude → Quote |
| Structured Outputs | **LIVE** | Tool calling + Pydantic validation |
| Confidence Sampling | **LIVE** | 3-sample variance estimation |
| Active Learning Questions | **LIVE** | Clarifying questions for low-confidence |
| Feedback System | **LIVE** | Non-destructive quote feedback API |
| Learning System | **LIVE** | Per-category weighted corrections |
| PDF Generation | **LIVE** | Professional quote PDFs |
| Onboarding Interview | **LIVE** | Adaptive pricing model setup |
| Landing Page | **LIVE** | Premium dark design, industry spinner |
| Issue Tracking API | **LIVE** | /api/issues for autonomous processing |

### Technical Architecture

- **Backend**: FastAPI + SQLite (aiosqlite)
- **AI**: Claude Sonnet 4 (quote generation) + Claude Haiku (category detection)
- **Transcription**: OpenAI Whisper
- **Deployment**: Railway (web + worker)
- **Auth**: Session-based (cookie)

---

## Active Initiatives

| Initiative | Status | Owner | Next Action |
|------------|--------|-------|-------------|
| ~~DNS Configuration~~ | **COMPLETE** | ~~CTO~~ | ~~SSL active at quoted.it.com~~ |
| ~~Pricing Strategy~~ | **COMPLETE** | ~~CFO~~ | ~~$29/49/79 tiers approved~~ |
| Payment Infrastructure | **IN PROGRESS** | CTO | Stripe + trial logic + billing UI |
| Beta User Recruitment | **READY** | CGO | Start outreach after payments work |
| Vector Embeddings (RAG) | **BACKLOG** | Engineering | Not MVP-critical, defer to post-beta |

---

## Key Metrics

| Metric | Current | Target (Beta) | Target (Launch) |
|--------|---------|---------------|-----------------|
| Users | 0 | 10-20 beta | 100 |
| Quotes Generated | 0 | 50 | 500 |
| Activation Rate | - | 60% | 70% |
| Quote Edit Rate | - | <30% | <20% |
| NPS | - | 40+ | 50+ |

---

## This Week's Priorities

1. ~~**Configure DNS**~~ - COMPLETE (SSL active)
2. ~~**Define Pricing**~~ - COMPLETE ($29/49/79 tiers with usage caps)
3. **Implement Payments** - Stripe integration, trial logic, billing UI
4. **Launch Beta** - Start recruiting after payments are live

---

## Blockers & Decisions Needed

| Blocker | What's Needed | Owner | Status |
|---------|---------------|-------|--------|
| Stripe Account | Eddie to create Stripe account + verify identity | Founder | WAITING |
| Resend Account | Eddie to create Resend account for transactional email | Founder | WAITING |
| API Keys | Share Stripe + Resend keys to proceed with implementation | Founder | WAITING |

---

## Resources & Assets

**Domain**: quoted.it.com (registered, not configured)
**Codebase**: Complete MVP with Phase 1 enhancements
**Deployment**: Railway (running)
**Brand**: Dark premium aesthetic, "quoted.it" with industry spinner

---

## Learnings & Insights

| Date | Learning | Source |
|------|----------|--------|
| 2025-12-01 | Structured outputs eliminate JSON parsing failures | Engineering |
| 2025-12-01 | Confidence sampling provides reliable uncertainty estimates | Engineering |
| 2025-12-01 | Landing page positions as "ballpark quotes, not blueprints" | Marketing |
| 2025-12-01 | Voice-first + learning = unique market position | Product |
| 2025-12-02 | API costs are negligible ($0.02-0.03/quote) - 95%+ gross margin | CFO |
| 2025-12-02 | Usage caps protect against API price increases and abuse | CFO |
| 2025-12-02 | 7-day trial with referral bonus creates viral loop | CGO |
| 2025-12-02 | Short trial forces decision - matches founder behavior pattern | Product |
| 2025-12-02 | Qualification value prop > speed for messaging | Executive Team (CMO/CGO) |
| 2025-12-02 | "Under 2 minutes" is honest; "30 seconds" overpromises | CPO |
| 2025-12-02 | Segment B (ballpark-only) has 2x better LTV:CAC but defer messaging | CFO/CMO |
| 2025-12-02 | Learning system is key differentiator - "gets smarter with every correction" | CPO |

---

## Strategic Context

**Why We Win**:
1. Voice-first matches how contractors actually work (in the field)
2. Learning system creates accuracy moat over time
3. Speed: 30-second quotes vs 30-minute spreadsheets
4. "Instant voice quote from job site" - unclaimed category

**Risks**:
1. Buildxact could add voice interface
2. Quote accuracy must be high (>85%) or trust breaks
3. Contractors may resist new tools
4. Need enough corrections to make learning meaningful

**Assumptions to Validate in Beta**:
1. Contractors will use voice input (vs typing)
2. Learning system creates measurable accuracy improvement
3. Onboarding captures enough pricing knowledge
4. Word-of-mouth drives growth in contractor communities

---

## Founder Notes

*Space for Eddie's input, direction, or context*

---

## Session Log

| Date | Duration | Focus | Outcomes |
|------|----------|-------|----------|
| 2025-12-01 | Initial | Bootstrap | Created initial state, identified Phase 1 priorities |
| 2025-12-01 | 2 hours | Audit | Full product audit, state file update, ops infrastructure |
| 2025-12-02 | 3 hours | Security + Pricing + GTM | SQLite migration, rate limiting, CORS, HTTPS redirect, full pricing strategy ($29/49/79), GTM plan, beta acquisition strategy |
| 2025-12-02 | 1 hour | Payment Readiness | Full executive analysis, 24-hour implementation plan for Stripe/trial/referrals/email |
| 2025-12-02 | 30 min | Legal + Content | Terms of Service, Privacy Policy pages, beta email sequence, knowledge infrastructure |
| 2025-12-02 | 45 min | Executive Audit + Implementation | Multi-agent executive audit (CMO/CPO/CFO/CGO), landing page messaging updates, email sequence revision |

---

## Operational Infrastructure

### State Files
- `COMPANY_STATE.md` - This file (strategic state)
- `ENGINEERING_STATE.md` - Sprints, tech debt, deployments
- `SUPPORT_QUEUE.md` - User issues and tickets
- `PRODUCT_STATE.md` - Roadmap and backlog
- `METRICS_DASHBOARD.md` - KPI tracking

### Autonomous Operations
The company can process issues via `/api/issues` endpoint:
1. Users report issues in-app
2. Issues appear in SUPPORT_QUEUE.md
3. Engineering claims and resolves
4. Updates pushed to production

**Type 1 Decisions** (Just Do): Bug fixes, docs, minor improvements
**Type 2 Decisions** (Do Then Report): Feature work within roadmap
**Type 3 Decisions** (Propose Then Do): Architecture changes, new integrations
**Type 4 Decisions** (Founder Required): Pricing, external commitments, major pivots
