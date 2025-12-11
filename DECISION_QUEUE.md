# Decision Queue

**Last Checked by Founder**: Never
**Last Updated by AI**: 2025-12-11 (no new decisions pending)

---

## How This Works

1. AI encounters Type 3 or Type 4 decision
2. AI adds decision to this queue with context
3. AI continues working on other tasks
4. Eddie checks this file (daily or as needed)
5. Eddie marks `[x]` to approve or adds rejection note
6. Next AI session picks up approvals and executes

**Quick Actions:**
- `[x]` = Approved, execute it
- `[ ]` = Still pending
- `[~]` = Rejected (add reason below)
- `[?]` = Need more info (add question below)

---

## Awaiting Decision

<!-- Type 4: Founder-only decisions -->
<!-- Type 3: Propose-then-do decisions -->

### ~~DECISION-007: External Consultant Architecture & Autonomy Review~~ ✅ RESOLVED BY EXECUTIVE COUNCIL
**Type**: 2 (Autonomous - Delegated by Founder)
**Added**: 2025-12-03 05:00 PST
**Resolved**: 2025-12-03 18:00 PST
**Requested By**: Founder (Eddie)
**Source Document**: `docs/2025-12-03-autonomous-operations-consultant-brief.md`

---

#### Executive Council Vote (2025-12-03)

| Question | CGO | CPO | CFO | CMO | Result |
|----------|-----|-----|-----|-----|--------|
| **Q1: Autonomy** | B (HIGH) | B (HIGH) | B (HIGH) | B (HIGH) | **UNANIMOUS B** |
| **Q2: Security** | A (HIGH) | A (HIGH) | A (HIGH) | A (HIGH) | **UNANIMOUS A** |
| **Q3: Learning** | A (HIGH) | A (MED-HIGH) | A (MED) | A (HIGH) | **UNANIMOUS A** |
| **Q4: QA** | A (HIGH) | A (HIGH) | A (HIGH) | A (MED-HIGH) | **UNANIMOUS A** |
| **Q5: CSO** | B (MED) | A (MED) | B (MED) | A (MED) | **SPLIT 2-2** |

---

#### Final Decisions (CEO Synthesis)

**Q1: Autonomy Boundaries** → **B) No, staging only**
- [x] Autonomous agents limited to patch proposals and PRs
- Rationale: Production autonomy = existential risk in pre-revenue beta

**Q2: Security vs. Velocity** → **A) Safety First**
- [x] Remove bypass mode immediately, accept slower velocity
- Rationale: Lethal Trifecta must be eliminated - unanimous HIGH confidence

**Q3: Learning System Priority** → **A) Yes, RAG is the moat**
- [x] Defer new features, invest in learning depth
- Rationale: Learning depth is only defensible advantage against competitors

**Q4: Operational Standards** → **A) Mandatory**
- [x] Enforce QA in `/quoted-run` pipeline, no exceptions
- Rationale: Mandatory QA = referral insurance, pays for itself in 2-4 weeks

**Q5: Security Governance** → **B) Existing roles + upgrade path**
- [x] Add security to CTO responsibilities with explicit mandate
- CEO tiebreaker: CTO owns security now; upgrade to CSO role in Phase 3
- Rationale: Both sides agree security governance needed NOW; organizational structure can evolve

---

#### Implementation Status

**Phase 0 (Immediate)** - IMPLEMENTING NOW:
- [x] Disable bypass mode for user issues
- [x] Add staging-only guardrail
- [x] Introduce QA as required phase in `/quoted-run`

**Phase 1 (2-4 weeks)**:
- [ ] QA agent in pipeline
- [ ] State archival automation
- [ ] Atlas sessions for all major cycles

**Phase 2 (1-3 months)**:
- [ ] RAG over quotes
- [ ] Pricing sanity checks
- [ ] Outcome linking

**Phase 3 (3-6 months)**:
- [ ] Dual-LLM for all Tier 3/4 content
- [ ] Upgrade CTO security → dedicated CSO role
- [ ] Night shift patterns

---

#### Key Rationale Summary

**CGO**: "Production autonomy creates catastrophic downside risk that destroys growth. RAG is THE moat that prevents commodity competition."

**CPO**: "Quoted's core value prop is pricing accuracy. Any autonomous bugs reaching users destroy beta trust. Learning depth delivers on 'learns YOUR pricing' promise."

**CFO**: "A single security breach = $50K-200K impact vs $3-5K cost to fix. Accept 10-20% slower velocity for 90%+ reduction in tail risk."

**CMO**: "Contractors trust Quoted because Quoted is reliable, accurate, and secure. Everything else is secondary."

---

### ~~DECISION-006: Pricing Strategy Review~~ ✅ RESOLVED BY EXECUTIVE COUNCIL
**Type**: 4 (Strategic - Pricing) → **Delegated to Executive Council by Founder**
**Added**: 2025-12-02 20:45 PST
**Resolved**: 2025-12-02 21:30 PST
**Requested By**: Founder

**Founder Delegation**:
> "I would like to push this decision down to the level where I allow the executive team to make the decision entirely."

---

#### Executive Council Vote (UNANIMOUS - 4/4 HIGH Confidence)

| Executive | Vote | Confidence | Key Rationale |
|-----------|------|------------|---------------|
| **CFO** | Option B ($19/$39) | HIGH | Unit economics bulletproof at $0.02-0.03/quote; 90%+ gross margin maintained |
| **CMO** | Option C ($19/$39) | HIGH | $19 = "impulse buy" zone; eliminates comparison shopping friction |
| **CGO** | Option C ($19/$39) | HIGH | Growth velocity in pre-competitive phase > revenue optimization |
| **CPO** | Option B ($19/$39) | HIGH | "No-brainer" threshold achieved; removes pricing objections entirely |

**Decision**: **Option C - Lower Both Plans to $19/$39**

---

#### New Pricing (IMPLEMENTED)

| Plan | Old Price | New Price | Quotes/mo | Per Extra Quote |
|------|-----------|-----------|-----------|-----------------|
| Starter | ~~$29/mo~~ | **$19/mo** | 75 | $0.50 |
| Pro | ~~$49/mo~~ | **$39/mo** | 200 | $0.35 |
| Team | $79/mo | $79/mo | 500 | $0.25 |

**Unit Economics Preserved**:
- Cost per quote: $0.02-0.03 (Whisper + Claude)
- $19/mo Starter: 75 quotes × $0.025 = $1.88 cost → **90% gross margin**
- $39/mo Pro: 200 quotes × $0.025 = $5.00 cost → **87% gross margin**

---

#### Implementation Notes

**Code Changes**:
- `backend/config.py`: Updated `starter_price_monthly` from 2900 to 1900, `pro_price_monthly` from 4900 to 3900
- `frontend/help.html`: Updated FAQ pricing section

**Stripe Action Required** (Founder):
- Update Starter product price from $29 → $19 in Stripe Dashboard
- Update Pro product price from $49 → $39 in Stripe Dashboard
- Or create new price objects and update product IDs in config

---

**Original Analysis Preserved Below for Reference**:

---

### DECISION-004: Bespoke Onboarding Offer Structure
**Type**: 4 (Strategic - Pricing/Positioning)
**Added**: 2025-12-02 19:30 PST
**Requested By**: Founder (via CEO)

**Context**: Proposal to offer personalized 1:1 onboarding where Eddie walks users through their pricing interview. Goal: build trust, learn from users, create referral loop.

**Original Proposal**:
- FREE personalized setup for first 50 users
- Condition: Must refer someone who completes onboarding
- After 50: Charge $50 for setup

**Prior Executive Analysis** (all returned MODIFY):

| Executive | Concern | Recommendation |
|-----------|---------|----------------|
| **CGO** | Referral trigger too slow - "generates quote" takes too long | Change trigger to "completes onboarding" |
| **CPO** | 50 users is too many - learning diminishes after ~25 | Cap at 20-30 users |
| **CFO** | $50 is mispriced - too low for revenue, too high to convert | Either free forever (growth) or $100+ (value signal) |
| **CMO** | Referral requirement creates friction | Make referral optional bonus, not requirement |

**Options**:
- [ ] **A) Original Proposal** - Keep as-is (50 users, referral required, $50 after)
- [X] **B) Modified Per Executives** - 25 users, optional referral bonus, rethink $50
- [ ] **C) Free Forever** - No cap, no charge, pure growth play
- [ ] **D) Other** - (specify below)

**Recommendation**: Option B - executives identified real friction points

**Questions to Resolve**:
1. What's the right cap? (20, 25, 30?)
2. Referral: required or optional bonus?
3. After cap: free, $50, $100, or remove entirely?

**Founder Response**:
> Option B and use your judgement on the quetions asked.

---

### DECISION-002: PostHog Analytics Integration
**Type**: 3 (External Service Signup)
**Added**: 2025-12-02 15:30 PST
**Requested By**: CEO

**Context**: Sprint 2 goal is 100 users by Dec 16. We need analytics to measure funnel performance, identify drop-off points, and optimize conversion. Can't improve what we can't measure.

**Service**: PostHog (product analytics)
- Free tier: 1M events/month (more than sufficient for beta)
- Self-hostable if we ever need
- Key events: landing→demo→signup→onboarding→first_quote→subscription

**Options**:
- [x] **A) Approve PostHog** - Free tier, industry standard, no lock-in
- [ ] **B) Defer** - Launch without analytics (flying blind)

**Recommendation**: Option A - analytics is critical for growth optimization

**Impact of Delay**: Every day without analytics is a day we can't measure what's working

**Founder Response**:
>

---

### DECISION-003: Sentry Error Tracking Integration
**Type**: 3 (External Service Signup)
**Added**: 2025-12-02 15:30 PST
**Requested By**: CEO

**Context**: As we scale to 100 users, we need to catch errors before users report them. Currently have zero visibility into production errors.

**Service**: Sentry (error tracking)
- Free tier: 5K errors/month
- FastAPI + JavaScript SDKs
- Alerts when new errors occur

**Options**:
- [x] **A) Approve Sentry** - Free tier, industry standard, critical for production
- [ ] **B) Defer** - Wait for users to report errors

**Recommendation**: Option A - error visibility is production-critical

**Impact of Delay**: Production errors go unnoticed until users complain

**Founder Response**:
>

<!--
Example format:

### DECISION-001: Short title
**Type**: 3 (Architecture) | 4 (Strategic)
**Added**: 2025-12-02 08:00 PST
**Requested By**: CTO

**Context**: Why this decision is needed

**Options**:
- [ ] **A) Option name** - Description. Pros: x. Cons: y.
- [ ] **B) Option name** - Description. Pros: x. Cons: y.

**Recommendation**: Option A because...

**Impact of Delay**: What happens if we wait

**Founder Response**:
> (Eddie writes here)

---
-->

---

## Recently Approved

| ID | Decision | Approved | Executed |
|----|----------|----------|----------|
| DECISION-006 | Pricing Strategy ($19/$39) - Delegated to Exec Council | 2025-12-02 | 2025-12-02 |
| DECISION-005 | Video/Animation Demo (Option B) | 2025-12-02 | 2025-12-02 |
| DNS-001 | Configure quoted.it.com DNS | 2025-12-01 | 2025-12-02 (LIVE) |

---

## Recently Rejected

| ID | Decision | Rejected | Reason |
|----|----------|----------|--------|
| - | - | - | - |

---

## Decision Log

Track patterns in decisions for learning:

| Date | ID | Type | Domain | Outcome | Time to Decision |
|------|-----|------|--------|---------|-----------------|
| 2025-12-02 | DECISION-006 | 4→Delegated | Pricing | Exec Council: Option C ($19/$39) | <1h |
| 2025-12-02 | DECISION-005 | 3 | Product Strategy | Approved (Option B) | <24h |
| 2025-12-01 | DNS-001 | 3 | Infrastructure | Approved | <24h |

---

## Founder Notes

*Space for Eddie to add context, priorities, or standing decisions*

**Standing Approvals** (don't need to ask):
- Bug fixes with passing tests (Type 1)
- Documentation improvements (Type 1)
- Feature work within current sprint (Type 2)

**Always Ask Before**:
- Any external service signup (even free tier)
- Any public announcement
- Pricing decisions
- Anything touching user data handling

---

## Quick Reference

**Type 3 (Propose Then Do)**:
- Architecture changes
- New integrations
- Major refactors
- Process changes

**Type 4 (Founder Only)**:
- Pricing
- External commitments
- Brand/positioning
- Major pivots
- Spend decisions
