# Decision Queue

**Last Checked by Founder**: Never
**Last Updated by AI**: 2025-12-02

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

### DECISION-007: External Consultant Architecture & Autonomy Review 🔴 PRIORITY
**Type**: 4 (Strategic - Safety, Investment, Operations)
**Added**: 2025-12-03 05:00 PST
**Requested By**: Founder (Eddie)
**Source Document**: `docs/2025-12-03-autonomous-operations-consultant-brief.md`

**Context**: Third-party consultant audited Quoted's product architecture and autonomous company infrastructure. The brief identifies critical security concerns with our current autonomous issue resolution and proposes a phased roadmap for safety, learning system depth, and operational maturity.

---

#### Executive Summary from Consultant

**Strengths Identified**:
- Well-architected voice-first quoting product
- Innovative per-contractor learning system (pricing_knowledge, Pricing Brain API)
- Best-in-class AI company scaffolding (role definition, decision governance, state files)
- End-to-end workflow: Voice → Whisper → Haiku → Sonnet → PDF

**Critical Risks Identified**:
1. **Prompt Injection via User Issues**: `autonomous_issue_resolver.py` uses `--dangerously-skip-permissions` with user-sourced (Tier 3) content - violates our own security doctrine
2. **No Dual-LLM Segmentation**: Single privileged agent reads untrusted content AND has tool access
3. **State Drift**: State files grow without automatic archival, increasing noise and cost
4. **No Enforced QA**: Testing described but not mandatory in `/quoted-run` pipeline

---

#### 5 Decision Questions for Executive Council

**Q1: Autonomy Boundaries**
> Do we want autonomous code changes to ever touch production directly?

- [ ] **A) Yes, with guardrails** - Define specific conditions (e.g., passing tests, no auth/billing code)
- [ ] **B) No, staging only** - Autonomous agents limited to patch proposals and PRs
- [ ] **C) Hybrid** - Staging for user-sourced issues, production for internal-generated tasks

**Q2: Security vs. Velocity**
> Are we willing to accept slower throughput (no bypass mode, dual LLMs, staging-only) for stronger safety guarantees?

- [ ] **A) Safety First** - Remove bypass mode immediately, accept slower velocity
- [ ] **B) Balanced** - Implement Dual-LLM for user issues, keep bypass for internal tasks
- [ ] **C) Velocity First** - Accept current risk until post-beta (NOT RECOMMENDED by consultant)

**Q3: Learning System Investment Priority**
> Should we prioritize RAG + outcome-linked learning over new surface features in the next 1-2 sprints?

- [ ] **A) Yes, RAG is the moat** - Defer new features, invest in learning depth
- [ ] **B) Parallel track** - Split engineering between features and learning
- [ ] **C) Features first** - Complete beta features, then RAG in Q1

**Q4: Operational Standards**
> Should QA and Atlas session management be mandatory parts of every autonomous cycle?

- [ ] **A) Mandatory** - Enforce in `/quoted-run` pipeline, no exceptions
- [ ] **B) Best Practice** - Document but don't enforce programmatically
- [ ] **C) Selective** - Mandatory for production, optional for staging

**Q5: Security Governance**
> Should we establish a dedicated "Security & Safety Officer" AI role?

- [ ] **A) Yes, new role** - Create CSO agent with audit responsibilities
- [ ] **B) Existing roles** - Add security to CTO/COO responsibilities
- [ ] **C) Defer** - Address after beta launch

---

#### Consultant's Recommended Roadmap

| Phase | Timeline | Focus |
|-------|----------|-------|
| **Phase 0** | Immediate | Remove bypass mode for user issues, add environment gating |
| **Phase 1** | 2-4 weeks | QA agent in pipeline, state archival, Atlas sessions |
| **Phase 2** | 1-3 months | RAG over quotes, pricing sanity checks, outcome linking |
| **Phase 3** | 3-6 months | Dual-LLM for all Tier 3/4, Security Officer role, night shift patterns |

---

#### Immediate Actions Proposed (Phase 0)

1. **Disable bypass mode for user issues** - Update `autonomous_issue_resolver.py`
2. **Add staging-only guardrail** - Check `settings.environment` before auto-commits
3. **Introduce QA as required phase** - Update `/quoted-run` workflow

---

**Executive Council Instructions**:
1. Read full consultant brief: `docs/2025-12-03-autonomous-operations-consultant-brief.md`
2. Each executive provides recommendation on Q1-Q5 with rationale
3. CEO synthesizes into final decision
4. If unanimous on Phase 0 actions → implement immediately
5. If split → escalate to Founder

**Impact of Delay**: Every autonomous cycle with current architecture carries prompt injection risk. Consultant identifies this as "Lethal Trifecta" scenario.

**Founder Response**:
>

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
