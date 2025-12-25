# Quoted Company State

**Last Updated**: 2025-12-24 (auto)
**Updated By**: CEO (AI)

---

## 🟡 Founder Action Required

**Status: 1 CONFIG ACTION** - AI operating autonomously otherwise

| Category | Count | Details |
|----------|-------|---------|
| Type 3/4 Decisions Pending | 0 | None - see [DECISION_QUEUE.md](DECISION_QUEUE.md) |
| Blockers Requiring Founder | 1 | CONFIG-001: Resend domain verification for `quoted.it.com` |
| Founder-Only Actions | 1 | DISC-033: Reddit Contractor Launch Post |

**Your Focus Today:** Add Resend DNS records to Namecheap (DKIM, SPF, DMARC). Then launch on Reddit!

---

## Current Stage

**BETA ACTIVE - SPRINT 3 (Product Polish & Infrastructure)**

**MAJOR MILESTONE**: Proposify Domination Wave 1-3 DEPLOYED (Dec 24, 2025)! Full competitive feature parity achieved: quote sharing with accept/reject + e-signatures, invoicing with public view, CRM system, background jobs with auto-reminders.

**Live URL**: https://quoted.it.com (SSL active)
**Railway Direct**: https://web-production-0550.up.railway.app
**Current Sprint**: Sprint 3 - Production-ready with complete feature set (Dec 17-31)

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
| Pricing Brain Management | **LIVE** | View/edit AI learned pricing + Haiku analysis |
| Customer Info Editing | **LIVE** | Edit customer name/address/phone on quotes |
| PDF Generation | **LIVE** | Professional quote PDFs with 8 templates |
| Onboarding Interview | **LIVE** | Adaptive pricing model setup |
| Landing Page | **LIVE** | Premium dark design, randomized industry spinner |
| Issue Tracking API | **LIVE** | /api/issues for autonomous processing |

### Wave 1-3 Features (Proposify Domination - Dec 2024)

| Feature | Status | Notes |
|---------|--------|-------|
| Quote Sharing | **E2E VERIFIED** | Share link generation, public view, email sharing |
| Quote Accept/Reject | **E2E VERIFIED** | Customer acceptance with typed e-signature (name, IP, timestamp) |
| Quote-to-Invoice | **E2E VERIFIED** | One-click conversion from won quotes |
| Invoice Public View | **E2E VERIFIED** | `/invoice/{token}` page with status banners |
| Mark Invoice Paid | **E2E VERIFIED** | Payment method + reference number tracked |
| Invoice PDF Download | **E2E VERIFIED** | Professional invoice PDF generation |
| View Count Tracking | **LIVE** | View count badge on quote cards, persisted in DB |
| Expiration Banners | **LIVE** | Soft expiration warnings on shared quotes |
| Background Scheduler | **LIVE** | APScheduler (task reminders every 5min, quote follow-ups daily) |
| Task System | **E2E VERIFIED** | Full CRUD with due dates, priority, customer linking |
| CRM System | **E2E VERIFIED** | Customer create/view/edit, tags, notes, quote history |
| First-View Notifications | **LIVE** | Email contractor when customer opens quote |

### Production Infrastructure (Dec 2024)

| Feature | Status | PR |
|---------|--------|-----|
| Database Connection Pooling | **DEPLOYED** | PR #9 |
| Multi-worker Uvicorn | **DEPLOYED** | PR #9 |
| XSS Fix (customer autocomplete) | **DEPLOYED** | PR #9 |
| Auth Fix (contractor endpoints) | **DEPLOYED** | PR #9 |
| CORS Regex Tightening | **DEPLOYED** | PR #9 |
| Stripe Webhook Error Handling | **DEPLOYED** | PR #9 |
| JWT Refresh Token Security | **DEPLOYED** | PR #10 |
| S3 File Storage | **DEPLOYED** | PR #11 |
| Redis Caching | **DEPLOYED** | PR #12 |
| Rate Limiting | **DEPLOYED** | PR #12 |
| Health Checks | **DEPLOYED** | PR #12 |
| Audit Logging | **DEPLOYED** | PR #13 |

### Technical Architecture

- **Backend**: FastAPI + PostgreSQL (Railway)
- **AI**: Claude Sonnet 4 (quote generation) + Claude Haiku (category detection)
- **Transcription**: OpenAI Whisper
- **Payments**: Stripe (subscriptions + checkout)
- **Email**: Resend (transactional) - domain verification pending
- **Deployment**: Railway (web + Postgres + Redis)
- **Auth**: JWT-based (Bearer token) with secure refresh tokens
- **File Storage**: AWS S3
- **Background Jobs**: APScheduler

---

## Active Initiatives

| Initiative | Status | Owner | Next Action |
|------------|--------|-------|-------------|
| ~~Proposify Domination Wave 1~~ | **DEPLOYED** | ~~Engineering~~ | ~~Invoice public view, quote accept/reject~~ |
| ~~Proposify Domination Wave 2~~ | **DEPLOYED** | ~~Engineering~~ | ~~Analytics, view tracking, expiration banners~~ |
| ~~Proposify Domination Wave 3~~ | **DEPLOYED** | ~~Engineering~~ | ~~Background jobs, task reminders~~ |
| ~~Production Infrastructure PRs 9-13~~ | **DEPLOYED** | ~~Engineering~~ | ~~Security, caching, S3, audit logging~~ |
| Resend Domain Verification | **🔴 FOUNDER ACTION** | Eddie | Add DNS records in Namecheap |
| Reddit Contractor Launch | **READY** | Eddie | DISC-033 - Post to r/contractors |
| Mobile App Strategy | **QUEUED** | Strategic | MOBILE-001 - PWA first, then React Native |
| Vector Embeddings (RAG) | **BACKLOG** | Engineering | Not MVP-critical, defer to post-beta |

---

## Key Metrics

| Metric | Current | Target (Beta) | Target (Launch) |
|--------|---------|---------------|-----------------|
| Users | ~10 beta | 10-20 beta | 100 |
| Quotes Generated | 200+ | 50 | 500 |
| Quote Value | $50K+ total | - | $500K+ |
| Activation Rate | - | 60% | 70% |
| Quote Edit Rate | - | <30% | <20% |
| NPS | - | 40+ | 50+ |

---

## Pricing

| Plan | Price | Quotes |
|------|-------|--------|
| Monthly | $9/mo | Unlimited |
| Annual | $59/year | Unlimited |

**Trial**: 7 days free

---

## This Week's Priorities (Sprint 3)

1. ~~**Proposify Domination Wave 1-3**~~ - DEPLOYED (Dec 24)
2. ~~**Production Infrastructure PRs 9-13**~~ - DEPLOYED (Dec 23)
3. **Resend Domain Verification** - FOUNDER ACTION
4. **Reddit Contractor Launch** - DISC-033 (FOUNDER ACTION)
5. **Monitor production** - Watch for background job execution

---

## Blockers & Decisions Needed

| Blocker | What's Needed | Owner | Status |
|---------|---------------|-------|--------|
| CONFIG-001: Resend Domain | Add DNS records to Namecheap for `quoted.it.com` | Eddie | **🔴 PENDING** |
| ~~Stripe Account~~ | ~~Eddie to create Stripe account + verify identity~~ | ~~Founder~~ | COMPLETE ✓ |
| ~~Resend Account~~ | ~~Eddie to create Resend account~~ | ~~Founder~~ | COMPLETE ✓ |
| ~~API Keys~~ | ~~Share Stripe + Resend keys~~ | ~~Founder~~ | COMPLETE ✓ |
| ~~Railway Env Vars~~ | ~~Add Stripe + Resend keys to Railway~~ | ~~Founder~~ | COMPLETE ✓ |
| ~~Stripe Webhook~~ | ~~Configure webhook~~ | ~~Founder~~ | COMPLETE ✓ |

**DNS Records Needed (Namecheap)**:
- DKIM TXT: `resend._domainkey` → (value from Resend dashboard)
- SPF MX: `send` → `feedback-smtp.us-east-1.amazonses.com` (Priority 10)
- SPF TXT: `send` → `v=spf1 include:amazonses.com ~all`
- DMARC TXT: `_dmarc` → `v=DMARC1; p=none;`

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
| 2025-12-02 | SQLAlchemy create_all doesn't add columns to existing tables - need explicit migrations | Engineering |
| 2025-12-02 | Railway Postgres + auto-migrations = robust production database | Engineering |
| 2025-12-02 | Categories must be registered on quote generation, not just edits - enables matching | Engineering |
| 2025-12-11 | Onboarding check: use explicit timestamp (onboarding_completed_at) not derived state (pricing defaults) | Engineering |
| 2025-12-11 | Data migrations can backfill existing users when adding new required fields | Engineering |
| 2025-12-11 | Feature flags (PostHog) enable safe rollout and instant rollback for new features | Engineering |
| 2025-12-23 | Production infrastructure (PRs 9-13) must precede feature work for stability | Engineering |
| 2025-12-24 | E2E browser testing catches issues that unit tests miss (real user flows) | QA |
| 2025-12-24 | Typed-name e-signatures are sufficient for contractor use case ($0 vs $0.50-3/signature) | Product |
| 2025-12-24 | Soft expiration (warning banner) > strict expiration for contractor flexibility | Product |
| 2025-12-24 | APScheduler (in-process) sufficient for background jobs at our scale; no need for Celery/Redis queue | Engineering |
| 2025-12-24 | Email FROM domain must match Resend verified domain exactly (quoted.it.com not quoted.it) | Engineering |
| 2025-12-24 | Wave-based feature deployment (1→2→3) allows incremental verification | Engineering |
| 2025-12-24 | CRM system is competitive advantage - Proposify requires external integration | Product |

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
| 2025-12-02 | 45 min | Payment Implementation | Full payment stack (Stripe + Resend + Billing UI) - 3 commits, feature-complete |
| 2025-12-02 | 30 min | Post-Deploy Fixes | Fixed pricing cards, annual billing, database migrations - 3 commits, all systems operational |
| 2025-12-02 | 30 min | Feature Sprint | FEAT-001 Pricing Brain (full stack), FEAT-002 Customer Edit (full stack), FIX-001 Slot Animation - 5 commits, 7 total pending push |
| 2025-12-23 | 2 hours | Production Infrastructure | PRs 9-13: Connection pooling, XSS fix, JWT security, S3, Redis, audit logging |
| 2025-12-24 | 4 hours | Proposify Domination Wave 1-3 | Invoice public view, quote accept/reject, e-signatures, background jobs, E2E testing |
| 2025-12-24 | 30 min | Hotfixes | Email FROM domain fix, invoice email sending fix, feature flag default fix |
| 2025-12-24 | 1 hour | Documentation Sync | Full state file update - ENGINEERING_STATE, DISCOVERY_BACKLOG, COMPANY_STATE, etc. |

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
