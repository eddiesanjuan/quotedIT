# AI Company Orchestration State

Build and deploy a fully autonomous AI-operated company for Quoted, Inc.

## Status

| Field | Value |
|-------|-------|
| **Current Phase** | 0 (Ready to Start) |
| **Started** | - |
| **Last Updated** | 2025-12-29 |

## Phase Completion

- [ ] **Phase 0: Setup**
  - [ ] Agent 0A: Initialize AI Company Infrastructure

- [ ] **Phase 1: Event Collector**
  - [ ] Agent 1A: Create Event Collector Endpoint
  - [ ] Agent 1B: Wire Webhook Sources

- [ ] **Phase 2: Support Agent**
  - [ ] Agent 2A: Support Agent Core
  - [ ] Agent 2B: Support Knowledge Base
  - [ ] Agent 2C: Support Integration

- [ ] **Phase 3: Ops Agent**
  - [ ] Agent 3A: Ops Agent Core
  - [ ] Agent 3B: Monitoring Integration
  - [ ] Agent 3C: Fix Generation Pipeline

- [ ] **Phase 4: Growth Agent**
  - [ ] Agent 4A: Growth Agent Core
  - [ ] Agent 4B: Content Templates

- [ ] **Phase 5: Finance Agent**
  - [ ] Agent 5A: Finance Agent Core
  - [ ] Agent 5B: Financial Reporting

- [ ] **Phase 6: Decision Queue**
  - [ ] Agent 6A: Decision Queue System
  - [ ] Agent 6B: Decision Execution

- [ ] **Phase 7: Operating Rhythm**
  - [ ] Agent 7A: Scheduled Execution (launchd)
  - [ ] Agent 7B: Morning Briefing Generator

- [ ] **Phase 8: Integration Testing**
  - [ ] Agent 8A: End-to-End Flow Testing
  - [ ] Agent 8B: Failure Mode Testing

- [ ] **Phase 9: Production Launch**
  - [ ] Agent 9A: Production Deployment
  - [ ] Agent 9B: Monitoring & Alerting

## Progress Summary

| Phase | Status | Agents | Notes |
|-------|--------|--------|-------|
| 0 | NOT_STARTED | 0/1 | |
| 1 | NOT_STARTED | 0/2 | |
| 2 | NOT_STARTED | 0/3 | |
| 3 | NOT_STARTED | 0/3 | |
| 4 | NOT_STARTED | 0/2 | |
| 5 | NOT_STARTED | 0/2 | |
| 6 | NOT_STARTED | 0/2 | |
| 7 | NOT_STARTED | 0/2 | |
| 8 | NOT_STARTED | 0/2 | |
| 9 | NOT_STARTED | 0/2 | |

**Total**: 0/21 agents complete

## Architecture

```
EDDIE'S MAC (Claude Code Runtime)
├── Company Brain (orchestrator)
│   ├── Support Agent → Customer communications
│   ├── Ops Agent → System monitoring
│   ├── Growth Agent → Content & campaigns
│   └── Finance Agent → Revenue tracking
│
├── State Directory (.ai-company/)
│   ├── state/ → Operational state
│   ├── queues/ → Events, decisions, actions
│   ├── agents/ → Per-agent state
│   ├── knowledge/ → Playbooks, customers
│   └── logs/ → Full audit trail
│
└── Scheduled Execution (launchd)
    ├── Every 30 min → Main loop
    ├── 6 AM → Morning briefing
    └── 6 PM → Evening summary

CLOUD (Minimal - Railway)
├── Event Collector → Webhook receiver
├── Quoted App → The product
└── External APIs → Stripe, Resend, PostHog
```

## Constitutional Framework

The AI Company operates under explicit constitutional rules:

### Autonomy Boundaries

**Can Act Autonomously:**
- Answer FAQ-type questions
- Create internal tickets
- Generate drafts (not publish)
- Monitor and alert
- Generate reports

**Requires Approval:**
- Customer-facing communications (beyond FAQ)
- Any financial transaction
- Any code deployment
- Any content publishing
- Any decision involving >$50

**Forbidden (Never):**
- Access personal accounts
- Make legal commitments
- Share customer data externally
- Bypass security measures
- Deceive customers

### Escalation Triggers

Escalate immediately if:
- Customer mentions lawyer/legal
- Security incident detected
- Revenue impact > $100
- Sentiment < -0.5
- Confidence < 70%

## Operating Rhythm

| Time | Activity |
|------|----------|
| 6:00 AM | Morning briefing generated |
| 6:30 AM | Eddie reviews decisions (5-10 min) |
| Every 30 min | Process events, execute actions |
| 6:00 PM | Evening summary generated |
| Sunday 6 PM | Weekly strategic review |

## Key Decisions Made

(Logged during execution)

## Infrastructure Requirements

### Mac Setup
- Claude Code subscription (existing)
- launchd agents for scheduling
- ~/.ai-company-logs/ for logging

### Railway Additions
- Event collector endpoint (~50 lines Python)
- Environment variables for webhooks
- Twilio integration for urgent notifications

### External Services
- Stripe webhook → Event collector
- Resend webhook → Event collector
- Twilio → SMS notifications

## Cost Analysis

| Component | Cost | Notes |
|-----------|------|-------|
| Claude Code | Existing subscription | No additional cost |
| Railway | Existing plan | Minimal additional load |
| Twilio | ~$1/month | Only for critical alerts |
| **Total Additional** | **~$1/month** | |

## Success Criteria

### Operational
- [ ] Events processed within 30 min
- [ ] Critical events notified within 5 min
- [ ] System uptime > 99%

### Efficiency
- [ ] 80%+ tickets handled autonomously
- [ ] Decision time < 2 min average
- [ ] Zero missed critical events

### Anthropic Showcase
- [ ] Full audit trail
- [ ] Constitutional compliance
- [ ] Human-in-loop working
- [ ] Demonstrable to Anthropic

## The Anthropic Story

**Tagline**: "We built a company that runs on Claude."

**The pitch**:
> "Quoted is a SaaS company operated almost entirely by Claude. The AI handles
> customer support, monitors systems, generates content, tracks finances, and
> proposes improvements. The human founder spends 10 minutes a day making key
> decisions. Everything else is autonomous, fully auditable, and aligned with
> responsible AI principles. This is what human-AI collaboration looks like."

**Key differentiators**:
1. No external frameworks - pure Claude Code
2. Constitutional AI in production
3. Human judgment for important decisions
4. Complete transparency (git audit trail)
5. Economically viable (near-zero additional cost)

## Resume Instructions

When continuing this orchestration:

1. Read this state file
2. Check which phases/agents are complete
3. Resume from first incomplete agent
4. Update state after each completion
5. Commit state changes to git
