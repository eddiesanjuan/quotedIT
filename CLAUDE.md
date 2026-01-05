# CLAUDE.md - Quoted, Inc.

This file provides guidance for Claude Code when working in the Quoted codebase.

## Project Overview

**Quoted** is a voice-to-quote SaaS for contractors. Users describe a job verbally, and AI generates a professional PDF quote using their personalized pricing model.

**Live URL**: https://quoted.it.com

## Architecture

```
quoted/
├── backend/                 # FastAPI backend
│   ├── api/                 # API endpoints
│   │   ├── auth.py          # Magic link authentication
│   │   ├── billing.py       # Stripe subscriptions
│   │   ├── contractors.py   # User profiles, logo upload
│   │   ├── onboarding.py    # Pricing interview/quick setup
│   │   ├── quotes.py        # Quote generation
│   │   └── referral.py      # Referral system
│   ├── services/            # Business logic
│   │   ├── claude_service.py    # AI quote generation
│   │   ├── pdf_service.py       # PDF generation
│   │   ├── billing.py           # Stripe integration
│   │   ├── learning.py          # Pricing learning system
│   │   └── email_service.py     # Resend emails
│   ├── models/              # SQLAlchemy models
│   └── config.py            # Environment config
├── frontend/
│   ├── index.html           # Main app (SPA)
│   ├── landing.html         # Marketing landing page
│   ├── demo.html            # Try-before-signup demo
│   ├── help.html            # FAQ/Help center
│   ├── terms.html           # Terms of Service
│   └── privacy.html         # Privacy Policy
├── ENGINEERING_STATE.md     # Active work tracking
├── COMPANY_STATE.md         # Strategic overview
├── BETA_SPRINT.md           # Current sprint goals
├── DECISION_QUEUE.md        # Pending founder decisions
└── ACTION_LOG.md            # Work history
```

## Key Commands

### Slash Commands (`.claude/commands/`)

| Command | Purpose |
|---------|---------|
| `/add-ticket <description>` | Add ticket to backlog as READY (auto-approved). Does NOT start implementation. |
| `/quoted-discover` | Generate new tasks/opportunities for backlog |
| `/run-qa` | Run QA test fleet (requires browser profile) |
| `/orchestrate-proposify-domination` | Multi-phase competitive feature orchestrator (see Strategic Commands section) |
| `/orchestrate-prod-ready` | Production readiness checklist orchestrator |
| `/orchestrate-learning-excellence` | Transform learning system to Anthropic showcase quality (see Strategic Commands section) |

**Quick ticket examples**:
- `/add-ticket voice command to duplicate a quote`
- `/add-ticket PDF footer looks cramped on mobile`
- `/add-ticket add support for multiple addresses per customer`

### Development

```bash
# Backend (from backend/)
uvicorn main:app --reload --port 8000

# Frontend is served statically by FastAPI
```

### Deployment

Railway auto-deploys on push to `main` branch.

## State Files

Always read these before making changes:

1. **ENGINEERING_STATE.md** - Active tickets, deployments, technical debt
2. **COMPANY_STATE.md** - Vision, strategy, current phase
3. **BETA_SPRINT.md** - Sprint goals and metrics
4. **DECISION_QUEUE.md** - Items awaiting founder approval

## Ticket Naming

| Prefix | Area |
|--------|------|
| `PAY-XXX` | Payment/billing |
| `FEAT-XXX` | Features |
| `BUG-XXX` | Bug fixes |
| `UX-XXX` | User experience |
| `GROWTH-XXX` | Growth/conversion |
| `ONBOARD-XXX` | Onboarding |
| `DISC-XXX` | Discovery backlog items |
| `INFRA-XXX` | Infrastructure |

**DISC ticket statuses**:
- **DISCOVERED**: AI-proposed, awaiting founder review
- **READY**: Approved for implementation (includes founder-requested via `/add-ticket`)
- **COMPLETE**: Implemented, pending deploy
- **DEPLOYED**: Live in production (move to DISCOVERY_ARCHIVE.md)

## Backlog Hygiene Protocol - CRITICAL

**The backlog must ALWAYS reflect reality.** This is non-negotiable.

### When to Update DISCOVERY_BACKLOG.md

Update the backlog whenever you:
1. **Implement a ticket** → Change status to COMPLETE
2. **Deploy code** → Change status to DEPLOYED, then move to DISCOVERY_ARCHIVE.md
3. **Do ad-hoc work** → If it relates to a ticket, update that ticket's status
4. **Fix bugs or make improvements** → Create a ticket if one doesn't exist, mark appropriately
5. **End a session** → Verify any work done is reflected in backlog

### Before Every Commit

Ask yourself: *"Does DISCOVERY_BACKLOG.md accurately reflect what I just did?"*

If you implemented DISC-XXX, that ticket should be COMPLETE.
If you deployed something, those tickets should be DEPLOYED → archived.

### Session-End Checklist

Before the conversation ends (user says thanks, goodbye, or moves on):
1. List any work completed this session
2. Verify each piece of work is reflected in DISCOVERY_BACKLOG.md
3. If counts changed, update the Summary section
4. If DEPLOYED tickets exist in backlog, migrate to DISCOVERY_ARCHIVE.md

### The Golden Rule

**If code was committed, the backlog MUST be updated in the same session.**

No exceptions. No "I'll do it later." The backlog is the source of truth for what's done and what's pending.

## External Services

| Service | Purpose | Dashboard |
|---------|---------|-----------|
| Railway | Hosting | railway.app |
| Stripe | Payments | dashboard.stripe.com |
| Resend | Email | resend.com |
| PostHog | Analytics | posthog.com |
| Cloudflare | DNS/SSL | cloudflare.com |

## Pricing (Production)

**Single-tier pricing** (DISC-098): $9/month or $59/year - unlimited quotes

## Key Conventions

1. **Mobile-first**: All UI changes must work at 375px
2. **Safe DOM**: Use `document.createElement()` not `innerHTML` for user data
3. **PostHog tracking**: Add events for key user actions
4. **Error handling**: All API calls need try/catch with user-friendly errors
5. **Accessibility**: Buttons need hover states, forms need labels

## QA Before Deploying

Run `/run-qa smoke` before pushing to main. For major changes, run `/run-qa full`.

See `.claude/commands/run-qa.md` for full QA protocol.

## Feature Flags (DISC-078)

New features ship behind PostHog feature flags for gradual rollout and instant rollback.

### Flag Discipline

1. **New features ship behind flags** (default: false)
2. **Enable for Eddie first** (48 hours validation)
3. **Enable for all users** after validation
4. **Remove flag** after 2 weeks stable in production
5. **Never ship broken code** "behind a flag" - code must work

### Flag Naming

Convention: `{feature}_enabled`

| Flag Key | Feature | Default |
|----------|---------|---------|
| `invoicing_enabled` | DISC-071 Quote-to-Invoice | false |
| `new_pdf_templates` | DISC-072 PDF Template Polish | false |
| `voice_template_customization` | DISC-070 Voice PDF Customization | false |

### Frontend Usage

```javascript
// Check if feature is enabled
if (isFeatureEnabled('invoicing_enabled')) {
    showInvoiceButton();
}

// Callback-based approach
showFeature('new_pdf_templates',
    () => { /* show new templates */ },
    () => { /* show old templates */ }
);
```

### Backend Usage

```python
from backend.services.feature_flags import is_feature_enabled

# Generic check
if is_feature_enabled("invoicing_enabled", user_id=contractor.id):
    return {"invoicing_available": True}

# Convenience functions
from backend.services.feature_flags import is_invoicing_enabled
if is_invoicing_enabled(contractor.id):
    # ...
```

### Rollback

1. Go to [PostHog Dashboard](https://app.posthog.com)
2. Feature Flags → Find flag → Disable
3. Takes effect in ~30 seconds

See `docs/EMERGENCY_RUNBOOK.md` for full rollback procedures.

## Deployment Workflow

1. Create feature branch
2. Push → PR → Railway auto-deploys preview
3. Test on preview URL (10 min smoke test)
4. Merge to main → auto-deploy to production
5. Monitor PostHog/Sentry for 5 min

For incidents, see `docs/EMERGENCY_RUNBOOK.md`.

## Railway CLI Access

**Full production access is available via Railway CLI.** Use this for diagnostics, viewing logs, and checking environment variables.

### Quick Commands

```bash
# View production logs (real-time streaming)
railway logs

# View last 100 lines (no streaming)
railway logs -n 100

# Filter for errors only
railway logs -n 100 --filter "@level:error"

# Check environment variables
railway variables

# Check deployment status
railway status

# Open Railway dashboard
railway open

# Run a command in production environment
railway run python -c "from backend.config import settings; print(settings.environment)"
```

### Common Diagnostics

**"Quotes not visible" / Auth issues:**
```bash
# Check if JWT_SECRET_KEY is set
railway variables | grep JWT

# View recent auth-related logs
railway logs -n 200 --filter "jwt OR auth OR token"
```

**Database connection issues:**
```bash
# Check DATABASE_URL is set
railway variables | grep DATABASE

# View database errors
railway logs -n 200 --filter "database OR postgres OR sql"
```

**API errors:**
```bash
# View errors
railway logs -n 500 --filter "@level:error"
```

### Linked Project

The CLI is linked to:
- **Workspace**: eddiesanjuan's Projects
- **Project**: quoted.It
- **Environment**: production
- **Service**: web (FastAPI app)

---

## Strategic Commands

### `/orchestrate-proposify-domination`

Multi-phase competitive feature development orchestrator. Builds features that make Quoted superior to Proposify.

**Current State**: Phase 1 Complete (Audits done, awaiting founder review)
**State File**: `.claude/proposify-domination-state.md`

```bash
# Check status and continue
/orchestrate-proposify-domination

# Run specific phase
/orchestrate-proposify-domination --phase=2

# Status only
/orchestrate-proposify-domination --status
```

**Phases**:
1. **Context Loading** - Baseline understanding
2. **Deep Audit** - Verify technical reality (COMPLETE)
3. **10x Design** - Design superior features
4. **Technical Specs** - Detailed implementation specs
5. **Implementation** - Build in waves
6. **QA** - Test all features
7. **Release** - Staged rollout

**Key Findings from Phase 1**:
- Invoice share link returns 404 (CRITICAL)
- Quote accept/reject workflow missing (CRITICAL)
- Task reminders are dead code
- CRM system is fully functional (GREEN)

### `/orchestrate-learning-excellence`

Transform Quoted's learning system into an Anthropic showcase example of human-AI collaboration. Creates an impassable competitive moat through intelligent, transparent, outcome-aware learning.

**Current State**: Ready to Begin
**State File**: `.claude/learning-excellence-state.md`

```bash
# Check status and continue
/orchestrate-learning-excellence

# Run specific phase
/orchestrate-learning-excellence --phase=2

# Status only
/orchestrate-learning-excellence --status
```

**Phases**:
1. **Context Loading** - Architecture deep dive
2. **Reality Audit** - Analyze production learning quality
3. **Quality Framework** - Statement quality scoring
4. **Smart Injection** - Relevance-based selection (replace "last 7")
5. **Outcome Loop** - Learn from quote wins/losses
6. **Cross-Category** - Transfer patterns across job types
7. **Confidence & Explanation** - Transparent AI reasoning

**Anthropic Showcase Principles**:
- Human-AI collaboration (enhance, never replace)
- Interpretable AI (explainable pricing)
- Honest uncertainty (confidence scores)
- Aligned incentives (optimizes for contractor success)
- Privacy-preserving intelligence (network effects without exposure)

---

## MCP Profiles

For browser testing, switch to browser profile:
```bash
cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant
./.claude-mcp-profiles/switch-profile.sh browser
# Restart Claude Code
```
