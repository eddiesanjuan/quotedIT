# Autonomous Company Ideas - Session Handoff

> From a separate Claude Code session discussing how to run Quoted as an autonomous AI company.
> Please integrate these ideas with whatever structure already exists.

## Core Concept

Run Quoted through **Claude Code CLI with structured prompts** instead of building infrastructure. Extended runs on Max subscription, user interacts occasionally to approve queued decisions.

## Key Ideas Discussed

### 1. Decision Tiering
| Stakes | Action | Examples |
|--------|--------|----------|
| **Low** | Auto-execute, log it | Bug fixes with passing tests, support responses |
| **Medium** | Execute + notify | Feature tweaks, A/B tests |
| **High** | Queue for human approval | Pricing changes, major features |
| **Critical** | Stop + alert immediately | Security issues, data integrity |

### 2. DECISION_QUEUE.md as Control Interface
A markdown file with checkboxes where agents queue decisions for human review. User checks boxes to approve, then agents execute. Makes it "extremely quick and easy" to take action.

### 3. Agent Modes via Slash Commands
- `/run-product` - Bug fixes, feedback processing, learning injection
- `/run-growth` - Content creation, lead analysis, marketing
- `/run-ops` - Support tickets, monitoring, billing
- `/run-ceo` - Strategic review, cross-domain coordination
- `/run-full-cycle` - All agents in sequence

### 4. File-Based State (No Infrastructure)
```
company/
├── DECISION_QUEUE.md    # Pending human decisions
├── ACTION_LOG.md        # What agents did
├── COMPANY_STATE.md     # Metrics dashboard
├── LEARNINGS.md         # Accumulated pricing knowledge
└── inbox/               # Items to process (feedback, errors, leads)
```

### 5. Self-Improvement Loop
User feedback → Agent analyzes → Pattern detection → Learning injection → Pricing model improves → Logged to LEARNINGS.md

### 6. Daily Workflow Envisioned
- **Morning (5 min)**: Review DECISION_QUEUE.md, approve/reject
- **Anytime**: Kick off `/run-full-cycle`, runs for hours autonomously
- **Weekly**: Strategic review, check LEARNINGS.md and metrics

## What This Session Didn't Have Context On

- What file structure already exists
- What agent prompts are already written
- How learning system integration currently works
- Any existing slash commands or automation

## Request

Please review what's already been built and integrate these ideas where they make sense. The goal is an AI-run company that:
1. Self-debugs based on user feedback
2. Autonomously improves pricing accuracy
3. Queues executive decisions for quick human action
4. Runs extended cycles with minimal human interaction
