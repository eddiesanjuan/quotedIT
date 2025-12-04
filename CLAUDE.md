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
| `/quoted-discover` | Generate new tasks/opportunities for backlog |
| `/run-qa` | Run QA test fleet (requires browser profile) |

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
| `DISC-XXX` | Discovery (proposed, not approved) |
| `INFRA-XXX` | Infrastructure |

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
| Starter | `prod_TXB6SKP96LAlcM` | $29/mo |
| Pro | `prod_TXB6du0ylntvVV` | $49/mo |
| Team | `prod_TXB6aO5kvAD4uV` | $99/mo |

## Key Conventions

1. **Mobile-first**: All UI changes must work at 375px
2. **Safe DOM**: Use `document.createElement()` not `innerHTML` for user data
3. **PostHog tracking**: Add events for key user actions
4. **Error handling**: All API calls need try/catch with user-friendly errors
5. **Accessibility**: Buttons need hover states, forms need labels

## QA Before Deploying

Run `/run-qa smoke` before pushing to main. For major changes, run `/run-qa full`.

See `.claude/commands/run-qa.md` for full QA protocol.

## MCP Profiles

For browser testing, switch to browser profile:
```bash
cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant
./.claude-mcp-profiles/switch-profile.sh browser
# Restart Claude Code
```
