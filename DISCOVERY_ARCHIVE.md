# Discovery Archive

**Purpose**: Historical record of all DEPLOYED tickets. Searchable for "have we done this before?" checks.
**Created**: 2025-12-21
**Last Updated**: 2025-12-24

---

## Usage Notes

- **For AI agents**: Grep this file before proposing new work to avoid duplicates
- **For humans**: Reference for what features exist and when they shipped
- **Linked from**: DISCOVERY_BACKLOG.md (active work only)

---

## Archive by Category

### CRM System (DISC-085 through DISC-092) - Deployed 2025-12-12

Complete voice-operated CRM implementation.

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-085 | Voice CRM Design Document | 2025-12-12 |
| DISC-086 | Customer Model & Database Migration | 2025-12-12 |
| DISC-087 | Customer Aggregation & Deduplication | 2025-12-12 |
| DISC-088 | Customer API Endpoints | 2025-12-12 |
| DISC-089 | Customer UI - List & Detail Views | 2025-12-12 |
| DISC-090 | CRM Voice Command Integration | 2025-12-12 |
| DISC-091 | Backfill Existing Quotes to Customers | 2025-12-12 |
| DISC-092 | CRM Task & Reminder System | 2025-12-12 |

---

### Pricing & Billing (DISC-098, DISC-071)

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-098 | Simplified Single-Tier Pricing ($9/mo or $59/yr) | 2025-12-19 |
| DISC-071 | Quote-to-Invoice Conversion | 2025-12-15 |

---

### Learning System (DISC-052, DISC-054, DISC-068)

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-052 | Hybrid Learning Format + Priority Selection | 2025-12-05 |
| DISC-054 | Dynamic Learning Rate | 2025-12-05 |
| DISC-068 | Auto-Detect New Categories & Notify User | 2025-12-10 |

---

### Infrastructure (DISC-077, DISC-078, DISC-079)

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-077 | Railway Preview Environments | 2025-12-08 |
| DISC-078 | Feature Flag Foundation (PostHog) | 2025-12-08 |
| DISC-079 | Emergency Runbook | 2025-12-08 |

---

### User Dashboard & Onboarding (DISC-093, DISC-095, DISC-084)

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-093 | Codex Executive UX Review | 2025-12-12 |
| DISC-095 | User Dashboard - Home Base After Login | 2025-12-15 |
| DISC-084 | Onboarding Trade Type List UX | 2025-12-12 |

---

### PDF & Quote Features (DISC-028, DISC-067, DISC-072, DISC-080)

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-028 | PDF Template Library (8 templates) | 2025-12-05 |
| DISC-067 | Free-Form Timeline & Terms Fields | 2025-12-10 |
| DISC-072 | PDF Template Polish & Robustness | 2025-12-15 |
| DISC-080 | Account Default Timeline & Terms | 2025-12-12 |

---

### Landing Page & Growth (DISC-096, DISC-097, DISC-099, DISC-100)

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-096 | Demo Learning Explanation | 2025-12-18 |
| DISC-097 | Landing Page CRM Feature Messaging | 2025-12-18 |
| DISC-099 | Direct Founder Support Channel | 2025-12-19 |
| DISC-100 | Pricing Intelligence for Novices Messaging | 2025-12-21 |

---

### Bug Fixes

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-094 | Fix "Join Waitlist" Button Broken Link | 2025-12-15 |
| DISC-082 | Referral Links Lead to 404 | 2025-12-12 |
| DISC-083 | Line Item Quantity/Cost UX Fix | 2025-12-12 |
| DISC-066 | PDF Generation Failure in Production | 2025-12-08 |
| DISC-065 | Line Item Quantity Field | 2025-12-06 |
| DISC-064 | Quote Generation Success Feedback | 2025-12-06 |
| DISC-056 | Confidence Badge Clipped Behind Nav | 2025-12-06 |
| DISC-051 | Quote Confidence Badge Positioning | 2025-12-05 |

---

### UX Improvements

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-036 | Keyboard Shortcuts for Power Users | 2025-12-05 |
| DISC-035 | Learning System Trust Indicators | 2025-12-05 |
| DISC-029 | Demo Quote Screenshot Sharing | 2025-12-03 |
| DISC-030 | Email Signature Viral Acceleration | 2025-12-03 |

---

### Strategic & Competitive

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-014 | Buildxact Competitive Defense | 2025-12-08 |
| DISC-063 | Horizontal Market Positioning Strategy | 2025-12-06 |
| DISC-069 | Go-to-Market Readiness Assessment | 2025-12-10 |

---

### Proposify Domination - Wave 1-3 (Dec 24, 2025)

Complete competitive feature parity with Proposify: quote sharing, accept/reject, e-signatures, invoicing, background jobs.

| Wave | Features | Commit | Deployed |
|------|----------|--------|----------|
| Wave 1 | Invoice public view, Quote accept/reject, E-signatures | 737ea24 | 2025-12-24 |
| Wave 2 | Quote analytics, View count tracking, Expiration banners | 8eac322 | 2025-12-24 |
| Wave 3 | Background scheduler (APScheduler), Task reminders, First-view notifications | 1852885 | 2025-12-24 |

**Hotfixes**:
- Email FROM domain fix (quoted.it → quoted.it.com) - 1d5d8d8
- Invoice email sending fix - af56d8a
- Feature flag default fix - c71d131

---

### Autonomous AI Infrastructure (DISC-101, 107, 108)

Agent reliability engineering for autonomous development cycles.

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-101 | LLM-as-Judge for Autonomous Cycles | 2025-12-23 |
| DISC-107 | Session Context Continuity (HANDOFF.md) | 2025-12-23 |
| DISC-108 | Regression Gate Before Commits | 2025-12-23 |

---

### Production Infrastructure PRs 9-13 (Dec 23, 2025)

Production-readiness hardening: security, caching, storage, audit logging.

| PR | Features | Deployed |
|----|----------|----------|
| PR #9 | Database connection pooling, Multi-worker Uvicorn, XSS fix, CORS tightening | 2025-12-23 |
| PR #10 | JWT refresh token security hardening | 2025-12-23 |
| PR #11 | S3 file storage | 2025-12-23 |
| PR #12 | Redis caching, Rate limiting, Health checks | 2025-12-23 |
| PR #13 | Audit logging | 2025-12-23 |

---

### Demo & Growth (DISC-110, DISC-112)

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-110 | Interactive Demo Product Tour for /try page | 2025-12-22 |
| DISC-112 | Remove Beta Slots Scarcity - Let Product Stand Alone | 2025-12-23 |

**Note**: DISC-111 (Anti-ERP Job Fulfillment Tracking) exists but was in a stash - now recovered and READY in backlog.

---

### SEO & Content (Dec 24, 2025)

| Feature | Commits | Deployed |
|---------|---------|----------|
| SEO Blog - 7 industry-specific quoting guides | 8239a80 | 2025-12-24 |
| sitemap.xml, robots.txt, blog routes | 21b8a26 | 2025-12-24 |

---

### UX Excellence Sprint (DISC-114 through DISC-123, DISC-125-130) - Dec 27-30, 2025

Major UX audit and fixes batch deployed.

| Ticket | Title | Deployed |
|--------|-------|----------|
| DISC-114 | Add Terms/Privacy to Quick Signup Form | 2025-12-27 |
| DISC-115 | Display Loyalty Tier Badges on CRM Cards | 2025-12-27 |
| DISC-116 | Add Outstanding Invoices Dashboard Widget | 2025-12-27 |
| DISC-117 | Send Quote Rejection Notifications Always | 2025-12-27 |
| DISC-118 | Add og:image Tags to Blog Articles | 2025-12-27 |
| DISC-119 | Mobile WCAG 2.5.5 Touch Target Compliance | 2025-12-27 |
| DISC-120 | Unified Auth Flow with Legal Compliance | 2025-12-27 |
| DISC-121 | Learning System Outcome Loop (Win/Loss Tracking) | 2025-12-27 |
| DISC-122 | Delete Line Item with Learning | 2025-12-27 |
| DISC-123 | Quantity/Unit Edits Should Trigger Learning + Save | 2025-12-27 |
| DISC-125 | Blog Article Formatting Fixes | 2025-12-28 |
| DISC-126 | Customer Identification UX - Bulletproof Matching | 2025-12-29 |
| DISC-127 | Logo Aspect Ratio Squished on Upload | 2025-12-28 |
| DISC-128 | Founder Notifications for Signups & Demo Usage | 2025-12-30 |
| DISC-129 | Demo Premium Template - Ultra-Polished First Impression | 2025-12-29 |
| DISC-130 | PDF Line Spacing Polish - Improved Text Readability | 2025-12-30 |
| DISC-131 | Demo Page Dictation Examples | 2025-12-30 |
| DISC-132 | Interactive Clarifying Questions | 2025-12-30 |
| DISC-135 | Post-Job Pricing Reflection Loop | 2025-12-31 |

---

### Autonomous Infrastructure (DISC-102, 104, 106) - Jan 5, 2026

Git worktree isolation and safety frameworks for autonomous operations.

| Ticket | Title | PR | Deployed |
|--------|-------|-----|----------|
| DISC-102 | Action Risk Classification Framework | #38 | 2026-01-05 |
| DISC-104 | Git Worktree Isolation for Autonomous Ops | #36 | 2026-01-05 |
| DISC-106 | Safety Net Architecture - 5-Layer Defense | #37 | 2026-01-05 |

---

### Handyman Mike Storytelling (DISC-113) - Partial Dec 30, 2025

| Ticket | Title | Status |
|--------|-------|--------|
| DISC-113 | Handyman Mike Workflow Storytelling | Partial - Time Savings Calculator only |

Remaining work: Story-based tour, pre-seeded demo data, workflow animation, marketing assets.

---

### Trial System Audit (DISC-161) - Jan 7, 2026

Production-ready trial enforcement with automated email reminders.

| Ticket | Title | PR | Deployed |
|--------|-------|-----|----------|
| DISC-161 | Trial System Audit - Production-Ready Enforcement | #51 | 2026-01-07 |

**Changes**:
- Fixed trial reminder email pricing ($29 → $9/month)
- Added `send_trial_expired_email` function
- Added `check_trial_reminders` scheduler job (daily 11am UTC)
- Added `trial_reminder_sent` column to User model
- Added PostHog tracking for `trial_reminder_sent` and `trial_expired` events

---

## Full Ticket Count by Status

| Status | Count | Notes |
|--------|-------|-------|
| DEPLOYED | 85+ | All in this archive |
| Remaining Active | 45 | In DISCOVERY_BACKLOG.md (READY + DISCOVERED + COMPLETE) |

---

## Search Patterns for AI Agents

When checking for duplicates, search for:
- Feature keywords (e.g., "CRM", "invoice", "PDF")
- User actions (e.g., "voice command", "edit", "delete")
- UI elements (e.g., "button", "modal", "dashboard")

---

*This archive is append-only. New DEPLOYED tickets are added during /quoted-run Phase 7 state updates.*
