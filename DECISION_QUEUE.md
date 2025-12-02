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
