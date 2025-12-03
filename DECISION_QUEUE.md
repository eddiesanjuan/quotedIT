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

### DECISION-006: Pricing Strategy Review - Are We Too Expensive?
**Type**: 4 (Strategic - Pricing)
**Added**: 2025-12-02 20:45 PST
**Requested By**: Founder

**Context**: Founder is questioning whether current pricing ($29/mo Starter, $49/mo Pro) is too high. The economics of producing quotes (AI API costs) are looking very affordable.

**Founder's Guidance**:
- "I would rather raise prices than be drastically off to the side of people feeling it's too expensive."
- "I want it to be a total no-brainer so that maintenance for me is pretty low."
- **Translation**: Price low enough that there's zero friction, no price objection handling, minimal churn due to cost. The value is real, but the goal is frictionless adoption and low support burden—not maximizing per-user revenue right now.

**Current Pricing**:
| Plan | Price | Quotes/mo | Per Extra Quote |
|------|-------|-----------|-----------------|
| Starter | $29/mo | 75 | $0.50 |
| Pro | $49/mo | 200 | $0.35 |

**Key Questions for Executive Council**:
1. What are the actual unit economics per quote? (AI costs, infrastructure)
2. How does our pricing compare to competitor alternatives (manual quoting time, other tools)?
3. What's the perceived value vs. actual cost for a contractor?
4. Should we lower prices to accelerate adoption during beta?
5. What pricing would feel like a "no-brainer" for target users?

**Considerations**:
- Beta goal: 100 users by Dec 16 - lower prices could accelerate
- Building trust early may be more valuable than optimizing revenue
- Can always raise prices later, but lowering after setting high is harder psychologically
- Contractors are price-sensitive but value time savings highly

**Options**:
- [ ] **A) Keep Current Pricing** - $29/$49 is reasonable, focus on value messaging
- [ ] **B) Lower Starter Plan** - e.g., $19/mo to reduce friction
- [ ] **C) Lower Both Plans** - e.g., $19/$39 to be more aggressive
- [ ] **D) Freemium Model** - Free tier with limited quotes, paid for more
- [ ] **E) Other** - (specify below)

**Executive Analysis Requested**: Full council review with:
- CFO: Unit economics breakdown
- CMO: Competitive pricing analysis
- CGO: Impact on conversion/adoption
- CPO: User perception research

**Founder Response**:
>

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
