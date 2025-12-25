# Engineering State

**Last Updated**: 2025-12-24 (E2E verified)
**Updated By**: Autonomous AI (CEO)

---

## Quick Links (Split for Readability)

| File | Contents | When to Read |
|------|----------|--------------|
| `ENGINEERING_STATE.md` | Active work only | Always - start here |
| `DISCOVERY_BACKLOG.md` | All DISC-XXX items | When planning new work |
| `DEPLOYMENT_LOG.md` | Recent deployments | When checking what shipped |
| `DECISION_QUEUE.md` | Pending founder decisions | Before major changes |
| `COMPANY_STATE.md` | Strategic overview, metrics | Weekly review |
| `ARCHIVE/` | Historical completed work | Reference only |

## Update Discipline (MANDATORY)

| Document | Update Triggers |
|----------|-----------------|
| **ENGINEERING_STATE.md** | After deployment, sprint change, architecture change |
| **DISCOVERY_BACKLOG.md** | Task discovered, status change (READY→COMPLETE→DEPLOYED) |
| **DECISION_QUEUE.md** | Type 3/4 decision needed, decision resolved |
| **COMPANY_STATE.md** | Weekly minimum, strategic change, new learnings |

**Deployment checklist:**
1. Update DISCOVERY_BACKLOG.md (mark DEPLOYED)
2. Update ENGINEERING_STATE.md (Recently Deployed section)
3. Log learnings in COMPANY_STATE.md if applicable

---

## ⚠️ Current Product Reality (AGENTS MUST READ)

**Last verified**: 2025-12-24 (Full E2E test completed)

This section is the **authoritative source** for what features actually exist in production. Some planning documents contain aspirational specs that were never built. Always check here first.

### Core Features (Original)
| Feature | Status | Reality |
|---------|--------|---------|
| **Demo mode** | ANIMATION ONLY | `demo.html` shows animated walkthrough. Does NOT generate quotes. Users must sign up to use product. |
| **Quote generation** | ✅ WORKING | Voice → AI → PDF quote generation is fully functional |
| **Magic link auth** | ✅ WORKING | Email-based passwordless login |
| **Stripe billing** | ✅ WORKING | $9/mo or $59/year unlimited, trial tracking |
| **Referral system** | ✅ WORKING | Referral codes, share link, rewards |
| **Pricing brain** | ✅ WORKING | Category management, AI analysis, learning |
| **PostHog analytics** | ✅ WORKING | Event tracking, funnels, feature flags |
| **First quote celebration** | ✅ WORKING | Confetti modal on first quote |
| **PDF download** | ✅ WORKING | Professional PDF generation |
| **PDF templates** | ✅ WORKING | 8 templates + accent colors, tier-gated (DISC-028) |
| **Pricing sanity check** | ✅ WORKING | Statistical bounds on quote generation |

### Wave 1-3 Features (Proposify Domination - Dec 2024)
| Feature | Status | Reality |
|---------|--------|---------|
| **Quote sharing** | ✅ E2E VERIFIED | Share link generation, public view, email sharing |
| **Quote accept/reject** | ✅ E2E VERIFIED | Customer acceptance with typed e-signature (name, IP, timestamp) |
| **Quote-to-Invoice** | ✅ E2E VERIFIED | One-click conversion from won quotes |
| **Invoice emailing** | ⚠️ CODE WORKS | Email template ready, Resend domain `quoted.it.com` needs verification |
| **Shared invoice view** | ✅ E2E VERIFIED | Public `/invoice/{token}` page works |
| **Mark invoice paid** | ✅ E2E VERIFIED | Payment method + reference number tracked |
| **Invoice PDF download** | ✅ E2E VERIFIED | Professional invoice PDF generation |
| **View count tracking** | ✅ WORKING | View count badge on quote cards, persisted in DB |
| **Expiration banners** | ✅ WORKING | Soft expiration warnings on shared quotes |
| **Background scheduler** | ✅ WORKING | APScheduler running (task reminders, quote follow-ups) |
| **Task creation** | ✅ E2E VERIFIED | Full CRUD with title, type, priority, due date, customer linking |
| **Task completion** | ✅ E2E VERIFIED | Checkbox completion, status updates |
| **CRM system** | ✅ E2E VERIFIED | Customer create/view/edit, tags, notes, quote history |

### Production Infrastructure (Dec 2024)
| Feature | Status | PR |
|---------|--------|-----|
| **Database connection pooling** | ✅ DEPLOYED | PR #9 |
| **Multi-worker Uvicorn** | ✅ DEPLOYED | PR #9 |
| **XSS fix in customer autocomplete** | ✅ DEPLOYED | PR #9 |
| **Auth fix on contractor endpoints** | ✅ DEPLOYED | PR #9 |
| **CORS regex tightening** | ✅ DEPLOYED | PR #9 |
| **Stripe webhook error handling** | ✅ DEPLOYED | PR #9 |
| **JWT refresh token security** | ✅ DEPLOYED | PR #10 |
| **S3 file storage** | ✅ DEPLOYED | PR #11 |
| **Redis caching** | ✅ DEPLOYED | PR #12 |
| **Rate limiting** | ✅ DEPLOYED | PR #12 |
| **Health checks** | ✅ DEPLOYED | PR #12 |
| **Audit logging** | ✅ DEPLOYED | PR #13 |

**Common misunderstandings**:
- "Demo mode" ≠ "try before signup". The demo is an animation showing how the product works, NOT functional quote generation without auth.
- Invoice email sending requires Resend domain verification for `quoted.it.com` - the code works.

---

## Current Sprint

**Sprint**: 3 (Product Polish & Infrastructure)
**Goal**: Production-ready with complete feature set
**Dates**: 2025-12-17 to 2025-12-31
**Focus**: Wave 1-3 Proposify Domination features DEPLOYED

**Sprint 2 Outcome** (Dec 2-16): Core infrastructure completed. Sprint 3 focus shifted to competitive feature parity (Proposify Domination initiative).

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
| CONFIG-001 | Resend domain verification for `quoted.it.com` | **🔴 FOUNDER ACTION** | Eddie |
| DISC-033 | Reddit Contractor Launch Post | **READY** | 🔴 FOUNDER ACTION |
| MOBILE-001 | Mobile App Strategy (iOS + Android) | **QUEUED** | Strategic |

### Recently Deployed (2025-12-24) - E2E Verified

| Ticket | Description | Commits |
|--------|-------------|---------|
| WAVE-3 | Background jobs, task reminders, first-view notifications | 1852885 |
| WAVE-2 | Quote analytics, expiration banners, view tracking | 8eac322 |
| WAVE-1 | Invoice public view, quote accept/reject with e-signatures | 737ea24 |
| HOTFIX | Email FROM address corrected to `quoted.it.com` | 1d5d8d8 |
| HOTFIX | Invoice email sending - fixed import + added method | af56d8a |
| HOTFIX | Invoicing feature flag default set to TRUE | c71d131 |

### Previously Deployed (2025-12-23)

| Ticket | Description | Commits |
|--------|-------------|---------|
| PR #13 | Production governance layer (audit logging) | df7f072 |
| PR #12 | Production resilience (rate limiting, health checks, caching) | aa69e36 |
| PR #11 | Production data layer (S3, Redis) | 20196eb |
| PR #10 | JWT refresh token security hardening | 836d80e |
| PR #9 | Foundation & Critical Security (connection pooling, XSS fix, CORS) | a41e2da |
| DISC-112 | Remove beta slots scarcity | 2aa08e5 |

### Previously Deployed (2025-12-12)

| Ticket | Description | Commits |
|--------|-------------|---------|
| DISC-093 | Codex UX Review - 3 high-impact fixes | e4f2f6c |
| DISC-084 | Trade Type List UX (popular at top, alphabetical) | 9dae270 |
| DISC-085-092 | Voice CRM System (full implementation) | multiple |
| DISC-082 | Referral Links 404 Fix (CRITICAL) | 2620866 |
| DISC-083 | Line Item Quantity/Cost UX Fix | 2a5ba8b |
| DISC-080 | Account Default Timeline & Terms Settings | d641e45 |

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
