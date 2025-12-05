# Engineering State

**Last Updated**: 2025-12-04 10:30 PST
**Updated By**: Autonomous AI (CEO)

---

## Quick Links (Split for Readability)

| File | Contents | When to Read |
|------|----------|--------------|
| `ENGINEERING_STATE.md` | Active work only | Always - start here |
| `DISCOVERY_BACKLOG.md` | All DISC-XXX items | When planning new work |
| `DEPLOYMENT_LOG.md` | Recent deployments | When checking what shipped |
| `DECISION_QUEUE.md` | Pending founder decisions | Before major changes |
| `ARCHIVE/` | Historical completed work | Reference only |

---

## ⚠️ Current Product Reality (AGENTS MUST READ)

**Last verified**: 2025-12-04

This section is the **authoritative source** for what features actually exist in production. Some planning documents contain aspirational specs that were never built. Always check here first.

| Feature | Status | Reality |
|---------|--------|---------|
| **Demo mode** | ANIMATION ONLY | `demo.html` shows animated walkthrough. Does NOT generate quotes. Users must sign up to use product. |
| **Quote generation** | ✅ WORKING | Voice → AI → PDF quote generation is fully functional |
| **Magic link auth** | ✅ WORKING | Email-based passwordless login |
| **Stripe billing** | ✅ WORKING | Starter/Pro/Team plans, trial tracking |
| **Referral system** | ✅ WORKING | Referral codes, share link, rewards |
| **Pricing brain** | ✅ WORKING | Category management, AI analysis, learning |
| **PostHog analytics** | ✅ WORKING | Event tracking, funnels |
| **First quote celebration** | ✅ WORKING | Confetti modal on first quote |
| **PDF download** | ✅ WORKING | Professional PDF generation |
| **Pricing sanity check** | ✅ WORKING | Statistical bounds on quote generation, flags/blocks hallucinations |

**Common misunderstandings**:
- "Demo mode" ≠ "try before signup". The demo is an animation showing how the product works, NOT functional quote generation without auth.
- Some specs in `BETA_SPRINT.md` describe planned features that were never fully implemented.

---

## Current Sprint

**Sprint**: 2 (100 Users)
**Goal**: 100 active beta testers by December 16
**Dates**: 2025-12-02 to 2025-12-16
**Strategy Doc**: `BETA_SPRINT.md`

---

## Deployment Status

| Environment | URL | Status |
|-------------|-----|--------|
| **Production** | https://quoted.it.com | LIVE ✅ |
| **Railway** | Auto-deploys on push to `main` | Active |

---

## Active Work

| Ticket | Description | Status | Assignee |
|--------|-------------|--------|----------|
| MOBILE-001 | Mobile App Strategy (iOS + Android) | **QUEUED** | Strategic |
| QA-001 | QA Fleet Implementation | **READY** | Autonomous |
| DISC-013 | Animation Distribution Strategy | **READY** | Growth |
| DISC-014 | Buildxact Competitive Defense | **READY** | Strategy |
| DISC-028 | PDF Template Library | **READY** | Product |

---

## Strategic Initiatives

### MOBILE-001: Native Mobile Apps (iOS + Android) 📱

**Source**: Founder (2025-12-03)
**Priority**: HIGH - Strategic for long-term viability
**Status**: QUEUED - Planning phase

**Rationale**: Contractors work from trucks and job sites, not desks. Voice-first + mobile is natural fit.

**Phased Approach**:

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| **Phase 0** | Now | Add PWA manifest (2h) - instant "Add to Home Screen" |
| **Phase 1** | Q1 2025 | React Native app (single codebase iOS + Android) |
| **Phase 2** | Q2 2025 | Native enhancements (camera, offline, push) |

**Architecture Ready**:
- ✅ Backend is REST API (mobile-ready)
- ✅ Magic link auth works on mobile
- ✅ PDF generation is server-side
- ⚠️ Voice input needs native Web Speech equivalent

**Executive Council Review Requested**: Full analysis of build vs buy, timeline, resource requirements.

---

## Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| No automated tests | MEDIUM | Planned post-beta |

---

## Architecture Summary

**Stack**: FastAPI + PostgreSQL + Claude AI + Railway
**Frontend**: Vanilla JS SPA (index.html, landing.html)
**Key Services**: Quote generation, PDF, Stripe billing, Resend email

**Key Files**:
- `backend/services/claude_service.py` - AI quote generation
- `backend/services/pdf_service.py` - PDF generation
- `backend/services/billing.py` - Stripe integration
- `frontend/index.html` - Main app
- `frontend/landing.html` - Marketing page

---

## QA Protocol

Before deploying, run: `/run-qa smoke`
For major changes: `/run-qa full`

See `.claude/commands/run-qa.md` for full QA fleet documentation.

---

## File Structure (Post-Refactor)

```
quoted/
├── ENGINEERING_STATE.md      # THIS FILE - Active work only (~100 lines)
├── DISCOVERY_BACKLOG.md      # All DISC-XXX items (~300 lines)
├── DEPLOYMENT_LOG.md         # Recent deployments (~100 lines)
├── DECISION_QUEUE.md         # Pending founder decisions
├── COMPANY_STATE.md          # Strategic overview
├── BETA_SPRINT.md            # Current sprint goals
├── CLAUDE.md                 # Project context for Claude
├── ARCHIVE/                  # Historical reference
│   └── ENGINEERING_STATE_FULL_2025-12-03.md
└── .claude/commands/
    ├── quoted-discover.md    # Discovery cycle
    └── run-qa.md             # QA fleet
```

---

## Environment Variables

Required in Railway (already configured):
```
ANTHROPIC_API_KEY, OPENAI_API_KEY, SESSION_SECRET, ENVIRONMENT
STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET
STRIPE_STARTER_PRODUCT_ID, STRIPE_PRO_PRODUCT_ID, STRIPE_TEAM_PRODUCT_ID
RESEND_API_KEY, POSTHOG_API_KEY
```

---

## On-Call

**Primary**: Autonomous AI Engineering
**Escalation**: Eddie (Founder) for Type 3-4 decisions
