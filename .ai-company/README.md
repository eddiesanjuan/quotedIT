# Quoted AI Company

An autonomous AI-operated company infrastructure powered by Claude.

## Overview

This system runs Quoted, Inc. with minimal human intervention. AI handles:
- **Support**: Customer tickets, emails, feedback
- **Operations**: Monitoring, alerts, fixes, deployments
- **Growth**: Content, campaigns, analytics
- **Finance**: Revenue tracking, invoices, forecasts

Eddie spends ~10 minutes daily on a decision queue. Everything else is autonomous.

## Architecture

```
EVENT SOURCES            RAILWAY               GITHUB ACTIONS          EDDIE'S MAC
━━━━━━━━━━━━━━━━        ━━━━━━━━━━━━          ━━━━━━━━━━━━━━━        ━━━━━━━━━━━━━
• Stripe webhooks   →   Event Gateway    →    Scheduled runs     →    Decision queue
• Resend webhooks   →   (classify,           (every 30 min)          (morning review)
• PostHog events    →    store,               ↓
• App events        →    dispatch)            Claude Code runs
                         ↓                    State changes → Git commits
                    Critical → SMS
                    Urgent → Dispatch
```

## Quick Start

### For Eddie (Daily Operations)

```bash
# Morning: Review decisions (5-10 min)
git pull
/ai-company decide

# Check status anytime
/ai-company status

# Force a run
/ai-company run
```

### For Monitoring

```bash
# View recent activity
cat .ai-company/logs/execution/$(date +%Y-%m-%d).md

# Check decision queue
cat .ai-company/queues/decisions.md

# View metrics
cat .ai-company/state/metrics.md
```

## Directory Structure

```
.ai-company/
├── CONSTITUTION.md          # The rules AI must follow
├── README.md                 # This file
├── state/                    # Current operational state
│   ├── current.md           # Overall state
│   ├── metrics.md           # Key metrics
│   └── last-run.json        # Last execution metadata
├── queues/                   # Work queues
│   ├── events.md            # Incoming events
│   ├── decisions.md         # Awaiting Eddie
│   ├── actions.md           # Ready to execute
│   └── completed.md         # Archive
├── agents/                   # Specialist agents
│   ├── support/             # Customer communication
│   ├── ops/                 # System operations
│   ├── growth/              # Content & campaigns
│   └── finance/             # Revenue & reporting
├── knowledge/                # Knowledge base
│   ├── product/             # Product info
│   ├── customers/           # Customer data
│   ├── playbooks/           # How to handle situations
│   └── voice/               # Brand voice
├── logs/                     # Audit trail
│   ├── execution/           # What AI did
│   ├── decisions/           # What Eddie decided
│   └── audit/               # Full trail
├── config/                   # Configuration
│   ├── boundaries.md        # Autonomy limits
│   ├── escalation.md        # When to escalate
│   └── notifications.md     # Alert settings
└── briefings/                # Generated briefings
```

## Commands

| Command | Description |
|---------|-------------|
| `/ai-company` | Main loop - process events, run agents |
| `/ai-company decide` | Interactive decision queue |
| `/ai-company status` | Current state and metrics |
| `/ai-company briefing` | Generate morning/evening briefing |
| `/ai-company review` | Generate weekly review |
| `/ai-company urgent` | Handle urgent event |
| `/ai-company run` | Force full cycle |

## Constitutional Framework

The AI operates under explicit constitutional rules (see CONSTITUTION.md):

### Can Act Autonomously
- Answer FAQ questions
- Create internal tickets
- Generate drafts (not publish)
- Monitor and alert
- Generate reports

### Requires Eddie's Approval
- Customer-facing communications
- Any financial transaction
- Any code deployment
- Any content publishing
- Decisions involving >$50

### Never (Forbidden)
- Access personal accounts
- Make legal commitments
- Share customer PII
- Bypass security
- Deceive customers

## Operating Rhythm

| Time | What Happens |
|------|--------------|
| Every 30 min | GitHub Actions runs Claude Code |
| 6:00 AM | Morning briefing generated |
| 6:30 AM | Eddie reviews decisions (5-10 min) |
| 6:00 PM | Evening summary generated |
| Sunday 6 PM | Weekly strategic review |

## The Anthropic Story

> "This is Quoted - a SaaS company that runs on Claude.
>
> Every 30 minutes, GitHub Actions wakes up Claude Code. It processes
> customer emails, monitors infrastructure, tracks revenue, generates
> content. Critical events trigger immediate runs. SMS for emergencies.
>
> The founder spends 10 minutes each morning on a decision queue - quick
> approvals for things the AI isn't certain about. Everything else is
> autonomous.
>
> Every AI action is a git commit. Full audit trail. Constitutional
> rules the AI follows. Human judgment for what matters.
>
> Total additional cost? About $10/month. The AI runs the company."

## Support

For issues with the AI Company system:
- Check `.ai-company/logs/` for recent activity
- Review CONSTITUTION.md for rules
- Run `/ai-company status` for diagnostics
