# Product State

**Last Updated**: 2025-12-24
**Updated By**: CPO (AI)

---

## Product Vision

**Mission**: Make quoting so fast and accurate that contractors never lose a job to slow estimates again.

**North Star Metric**: Quotes generated per active user per week

---

## Current Roadmap

### Phase 1: Core Product (COMPLETE)
**Status**: SHIPPED
**Outcome**: Full voice-to-quote pipeline operational

| Feature | Status | Notes |
|---------|--------|-------|
| Voice-to-quote pipeline | SHIPPED | Works end-to-end |
| Onboarding interview | SHIPPED | Adaptive pricing extraction |
| Learning system | SHIPPED | Per-category corrections |
| PDF export | SHIPPED | Professional formatting, 8 templates |
| Landing page | SHIPPED | Premium dark design |
| Confidence sampling | SHIPPED | 3-sample variance |
| Active learning questions | SHIPPED | Clarifying questions API |
| Feedback system | SHIPPED | Non-destructive feedback |

### Phase 2: Competitive Parity - Proposify Domination (COMPLETE)
**Status**: SHIPPED (Dec 24, 2025)
**Outcome**: Full feature parity with enterprise competitors

| Feature | Status | Notes |
|---------|--------|-------|
| Quote sharing | **E2E VERIFIED** | Share link + email with PDF |
| Quote accept/reject | **E2E VERIFIED** | Customer decision flow with e-signatures |
| Quote-to-invoice | **E2E VERIFIED** | One-click conversion from won quotes |
| Invoice public view | **E2E VERIFIED** | `/invoice/{token}` with status banners |
| Mark invoice paid | **E2E VERIFIED** | Payment method + reference tracking |
| Invoice PDF download | **E2E VERIFIED** | Professional invoice PDFs |
| View count tracking | SHIPPED | Badge on quote cards, persisted in DB |
| Expiration banners | SHIPPED | Soft warnings on shared quotes |
| Task system | **E2E VERIFIED** | Full CRUD, due dates, priority, customer linking |
| CRM system | **E2E VERIFIED** | Customer management with tags, notes, history |
| Background scheduler | SHIPPED | APScheduler (reminders, follow-ups) |
| First-view notifications | SHIPPED | Email contractor when customer views |

### Phase 3: Production Infrastructure (COMPLETE)
**Status**: SHIPPED (Dec 23-24, 2025)

| Feature | Status | PR |
|---------|--------|-----|
| Database connection pooling | SHIPPED | PR #9 |
| Multi-worker Uvicorn | SHIPPED | PR #9 |
| Security fixes (XSS, CORS, auth) | SHIPPED | PR #9 |
| JWT refresh token security | SHIPPED | PR #10 |
| S3 file storage | SHIPPED | PR #11 |
| Redis caching | SHIPPED | PR #12 |
| Rate limiting | SHIPPED | PR #12 |
| Health checks | SHIPPED | PR #12 |
| Audit logging | SHIPPED | PR #13 |

### Phase 4: Growth (NEXT)
**Status**: READY TO START

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Reddit launch | **P0** | READY | DISC-033 - 410K+ contractors |
| Mobile app (PWA → React Native) | HIGH | QUEUED | MOBILE-001 |
| Vector embeddings (RAG) | MEDIUM | BACKLOG | 15-25% accuracy improvement |
| QuickBooks integration | MEDIUM | BACKLOG | DISC-081 |
| Voice-driven PDF customization | MEDIUM | READY | DISC-070 |

---

## Current Priorities

| Priority | Feature | Status | Owner |
|----------|---------|--------|-------|
| ~~P0~~ | ~~Proposify Domination Wave 1-3~~ | ~~DEPLOYED~~ | ~~Engineering~~ |
| ~~P0~~ | ~~Production Infrastructure PRs 9-13~~ | ~~DEPLOYED~~ | ~~Engineering~~ |
| P0 | Resend Domain Verification | **🔴 FOUNDER ACTION** | Eddie |
| P0 | Reddit Contractor Launch | READY | Eddie |
| P1 | Monitor Production | ONGOING | All |

---

## Pricing Strategy (UPDATED 2025-12-19)

**Decision**: Single-tier pricing with lowest possible entry point for contractor market (DISC-098).

| Plan | Price | Quotes |
|------|-------|--------|
| **Monthly** | $9/mo | Unlimited |
| **Annual** | $59/year | Unlimited (save 45%) |

**Trial**: 7 days free
- **Referral bonus**: +7 days when referred friend signs up AND generates first quote
- **No cap on referral days**: Viral growth > trial extension cost
- Trial IS the beta—forces real purchase decisions

### Unit Economics (DISC-098 Unlimited Model)

**Variable cost per quote**: $0.02-0.03 (current)
**Monthly pricing**: $9/mo = 99%+ gross margin at typical usage (10-50 quotes/mo)
**Annual pricing**: $59/year = ~$4.92/mo effective, still 95%+ gross margin

**Risk tolerance**: At $0.03/quote, break-even is ~300 quotes/mo. 99% of contractors won't hit this.

**Target CAC**: $22-50
**LTV (12-month)**: $108 (monthly) or $59 (annual)
**LTV:CAC ratio**: 2-5x (acceptable for high-margin SaaS)

---

## Feature Backlog

| Feature | Impact | Confidence | Effort | Score | Notes |
|---------|--------|------------|--------|-------|-------|
| Vector embeddings | 5 | 4 | 3 | 6.7 | Accuracy boost |
| Voice PDF customization | 4 | 4 | 4 | 4.0 | DISC-070 - PRO/TEAM |
| Mobile app (PWA) | 5 | 4 | 2 | 10.0 | MOBILE-001 Phase 0 |
| Mobile app (React Native) | 5 | 3 | 5 | 3.0 | MOBILE-001 Phase 1 |
| Quote templates | 3 | 3 | 2 | 4.5 | Repeat jobs |
| QuickBooks integration | 3 | 3 | 4 | 2.3 | DISC-081 |
| Team accounts | 2 | 3 | 4 | 1.5 | Enterprise |
| ~~Customer management~~ | ~~3~~ | ~~4~~ | ~~2~~ | ~~6.0~~ | ~~SHIPPED - CRM system~~ |

*Score = (Impact × Confidence) / Effort*

---

## User Research

### Insights to Validate

| Hypothesis | Confidence | How to Validate |
|------------|------------|-----------------|
| Contractors will use voice input | MEDIUM | Track voice vs text usage |
| Learning improves accuracy | HIGH | Measure edit rate over time |
| Onboarding captures pricing | MEDIUM | Survey beta users |
| 30-second quotes save time | HIGH | User interviews |

### User Personas

**Primary: Solo Contractor**
- 1-3 person operation
- Prices "by feel" (Type B)
- Gives quotes on job site
- Uses phone primarily
- Values speed over precision

**Secondary: Small Contractor**
- 4-10 employees
- Has pricing system (Type A)
- Office-based estimating
- Uses laptop
- Values accuracy

---

## Competitive Position

| Competitor | Strength | Weakness | Our Advantage |
|------------|----------|----------|---------------|
| Proposify | E-signatures, tracking | $19/mo basic, enterprise focus | Voice-first, built-in CRM, contractor pricing |
| Buildxact | Fast estimates | Text-only, no learning | Voice + learning |
| CountBricks | Voice interface | Low awareness | Better UX |
| Jobber | Full CRM | No voice quoting | Speed, simplicity |
| Spreadsheets | Familiar | Slow, error-prone | 10x faster |

**Our Category**: "Instant voice quote from job site"
**Status**: Unclaimed

**Proposify Gap Analysis (Post-Wave 1-3)**:
| Feature | Proposify | Quoted | Status |
|---------|-----------|--------|--------|
| E-Signatures | ✅ DocuSign-level | ✅ Typed-name (free) | PARITY |
| Quote Accept/Reject | ✅ Yes | ✅ Yes | PARITY |
| Document Tracking | ✅ Views, time | ✅ View count, first-view email | PARITY |
| Auto-Reminders | ✅ Sequences | ✅ APScheduler jobs | PARITY |
| Invoice Portal | ✅ Yes | ✅ Yes | PARITY |
| CRM | ❌ External required | ✅ Built-in | ADVANTAGE |
| Voice-First | ❌ No | ✅ Core differentiator | ADVANTAGE |
| Mobile Optimized | ❌ Desktop focus | ✅ Mobile-first | ADVANTAGE |
| Pricing | $19-3,900/yr | $19-79/mo | ADVANTAGE |

---

## Metrics Targets

| Metric | Beta Target | Launch Target | PMF Target |
|--------|-------------|---------------|------------|
| Activation Rate | 60% | 70% | 80% |
| Weekly Retention | 40% | 50% | 60% |
| Quote Edit Rate | <35% | <25% | <15% |
| NPS | 30 | 45 | 60 |
| Time to Quote | <60s | <45s | <30s |

---

## User Feedback Log

| Date | User | Feedback | Action Taken |
|------|------|----------|--------------|
| - | - | No feedback yet | Awaiting beta users |

---

## A/B Tests

| Test | Hypothesis | Status | Results |
|------|------------|--------|---------|
| - | - | No tests running | - |

---

## Product Decisions Log

| Date | Decision | Rationale | Outcome |
|------|----------|-----------|---------|
| 2025-12-24 | Typed-name e-signatures only | API signatures cost $0.50-3/each, unacceptable at $19/mo | Implemented |
| 2025-12-24 | Soft quote expiration (warning only) | Contractor flexibility > strict enforcement | Implemented |
| 2025-12-24 | APScheduler for background jobs | In-process sufficient, no Celery/Redis needed at scale | Deployed |
| 2025-12-24 | Built-in CRM over integration | Competitive advantage - Proposify requires external | Key differentiator |
| 2025-12-24 | Financing integration first (Wisetack/Affirm) | Highest $/transaction for network monetization | Queued |
| 2025-12-19 | Lower pricing to $19/$39/$79 | Better market fit for contractors | Pricing updated |
| 2025-12-02 | Lead with qualification value prop for beta | CGO: faster activation, lower CAC, better virality | Landing page updated |
| 2025-12-02 | Soften "30-second" to "under 2 minutes" | CPO: Real UX is 1-3 minutes end-to-end | All copy updated |
| 2025-12-02 | Defer ballpark-only segment messaging | CMO+CGO: Validate through beta behavior first | Removed from landing |
| 2025-12-02 | Reject "only tool you need" tagline | CMO: Sounds limited, not focused | Not implemented |
| 2025-12-02 | Add "Qualify faster. Close more." tagline | CMO: Ranked #2, outcome-focused | Landing + emails |
| 2025-12-01 | Position as "ballpark quotes" not final proposals | Set correct expectations, faster adoption | Landing page updated |
| 2025-12-01 | Defer vector embeddings to post-beta | Not MVP-critical, focus on users first | Prioritized correctly |
