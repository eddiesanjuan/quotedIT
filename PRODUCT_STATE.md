# Product State

**Last Updated**: 2025-12-02 04:20 PST
**Updated By**: CPO (AI)

---

## Product Vision

**Mission**: Make quoting so fast and accurate that contractors never lose a job to slow estimates again.

**North Star Metric**: Quotes generated per active user per week

---

## Current Roadmap

### Phase 1: Beta Launch (Current)
**Status**: READY
**Target**: 10-20 beta users, validate core value prop

| Feature | Status | Notes |
|---------|--------|-------|
| Voice-to-quote pipeline | SHIPPED | Works end-to-end |
| Onboarding interview | SHIPPED | Adaptive pricing extraction |
| Learning system | SHIPPED | Per-category corrections |
| PDF export | SHIPPED | Professional formatting |
| Landing page | SHIPPED | Premium dark design |
| Confidence sampling | SHIPPED | 3-sample variance |
| Active learning questions | SHIPPED | Clarifying questions API |
| Feedback system | SHIPPED | Non-destructive feedback |

### Phase 2: Product-Market Fit (Post-Beta)
**Status**: PLANNED
**Target**: Validate pricing, reduce edit rate to <20%

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Vector embeddings (RAG) | HIGH | BACKLOG | 15-25% accuracy improvement |
| Quote history dashboard | MEDIUM | BACKLOG | View/search past quotes |
| Customer management | MEDIUM | BACKLOG | Save customer info |
| Multi-agent quotes | LOW | BACKLOG | Complex quote accuracy |

### Phase 3: Growth (Future)
**Status**: NOT STARTED

| Feature | Priority | Notes |
|---------|----------|-------|
| Mobile app (React Native) | HIGH | Contractors are in the field |
| CRM integrations | MEDIUM | QuickBooks, Jobber |
| Team accounts | LOW | Multiple estimators |
| Real-time material pricing | LOW | Home Depot API etc. |

---

## Current Priorities

| Priority | Feature | Status | Owner |
|----------|---------|--------|-------|
| ~~P0~~ | ~~DNS Configuration~~ | ~~COMPLETE~~ | ~~Founder~~ |
| P0 | Beta User Recruitment | READY TO START | CGO |
| P1 | Monitor First Usage | READY | All |
| ~~P2~~ | ~~Pricing Strategy~~ | ~~COMPLETE~~ | ~~CFO~~ |

---

## Pricing Strategy (APPROVED 2025-12-02)

**Decision**: Usage-capped tiers with overage pricing for margin protection.

| Tier | Monthly | Annual | Quotes | Overage | Target |
|------|---------|--------|--------|---------|--------|
| **Starter** | $29 | $290/yr | 75/mo | $0.50/quote | Solo contractors |
| **Pro** | $49 | $490/yr | 200/mo | $0.35/quote | Growing businesses |
| **Team** | $79 | $790/yr | 500/mo | $0.25/quote | Small firms (3-10) |

**Trial**: 7 days, 75 quotes (mirrors Starter—no free tier exists)
- **Referral bonus**: +7 days when referred friend signs up AND generates first quote
- **No cap on referral days**: Viral growth > trial extension cost
- Trial IS the beta—forces real purchase decisions

**Annual Discount**: 2 months free (17% off)

### Why Usage Caps (Executive Decision)

**Risk mitigated**: Unlimited pricing at $29 exposed us to:
- Extreme users (500+ quotes/month) destroying margins
- API price increases (2-3x) making accounts unprofitable
- No protection against both happening together

**Stress-tested margins** (even at 3x API pricing):
| Tier | Max API Cost @ 3x | Margin @ 3x |
|------|-------------------|-------------|
| Starter (75) | $6.75 | 77% |
| Pro (200) | $18.00 | 63% |
| Team (500) | $45.00 | 43% |

**Overage economics**: Heavy users become profit centers, not liabilities.

### Unit Economics
- Variable cost per quote: $0.02-0.03 (current), $0.06-0.09 (3x stress)
- Base gross margin: 81-92% (current), 43-77% (3x stress)
- Overage margin: 91% (current), 74% (3x stress)
- Target CAC: $22-50
- LTV (12-month Starter): $290+
- LTV:CAC ratio: 5.8-13x

---

## Feature Backlog

| Feature | Impact | Confidence | Effort | Score | Notes |
|---------|--------|------------|--------|-------|-------|
| Vector embeddings | 5 | 4 | 3 | 6.7 | Accuracy boost |
| Mobile app | 5 | 3 | 5 | 3.0 | Field access |
| Customer management | 3 | 4 | 2 | 6.0 | Convenience |
| Quote templates | 3 | 3 | 2 | 4.5 | Repeat jobs |
| Team accounts | 2 | 3 | 4 | 1.5 | Enterprise |
| QuickBooks integration | 3 | 3 | 4 | 2.3 | Accounting |

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
| Buildxact | Fast estimates | Text-only, no learning | Voice + learning |
| CountBricks | Voice interface | Low awareness | Better UX |
| Jobber | Full CRM | No voice quoting | Speed, simplicity |
| Spreadsheets | Familiar | Slow, error-prone | 10x faster |

**Our Category**: "Instant voice quote from job site"
**Status**: Unclaimed

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
| 2025-12-01 | Position as "ballpark quotes" not final proposals | Set correct expectations, faster adoption | Landing page updated |
| 2025-12-01 | Defer vector embeddings to post-beta | Not MVP-critical, focus on users first | Prioritized correctly |
