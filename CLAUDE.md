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
│   │   ├── beta.py          # Beta spots counter
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
- **DEPLOYED**: Live in production

## External Services

| Service | Purpose | Dashboard |
|---------|---------|-----------|
| Railway | Hosting | railway.app |
| Stripe | Payments | dashboard.stripe.com |
| Resend | Email | resend.com |
| PostHog | Analytics | posthog.com |
| Cloudflare | DNS/SSL | cloudflare.com |

## Stripe Products (Production)

| Plan | Product ID | Price |
|------|------------|-------|
| Starter | `prod_TXB6SKP96LAlcM` | $19/mo (75 quotes, $0.50 overage) |
| Pro | `prod_TXB6du0ylntvVV` | $39/mo (200 quotes, $0.35 overage) |
| Team | `prod_TXB6aO5kvAD4uV` | $79/mo (Unlimited, no overage) |

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

## MCP Profiles

For browser testing, switch to browser profile:
```bash
cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant
./.claude-mcp-profiles/switch-profile.sh browser
# Restart Claude Code
```
