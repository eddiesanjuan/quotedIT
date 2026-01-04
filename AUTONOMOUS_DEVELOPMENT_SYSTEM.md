# Autonomous Development System

> How Quoted uses AI-native slash commands and multi-agent orchestration to implement features with minimal human intervention.

**Last Updated**: 2024-12-24
**System Version**: v3.0 (Context-Aware Self-Improving Audits)

---

## Executive Summary

Quoted has evolved a development methodology where AI agents autonomously discover opportunities, audit systems, design solutions, and implement features—with the human founder serving as strategic reviewer rather than task manager.

The system achieves this through three innovations:

1. **Thin Orchestrator Architecture** - Lightweight commanders that spawn specialized subagents
2. **State Persistence** - Progress survives across sessions via markdown state files
3. **Self-Improving Audits (v3.0)** - Known Issues Registry prevents re-discovering the same problems

---

## The Slash Command Ecosystem

### Core Commands

| Command | Purpose | Agent Pattern |
|---------|---------|---------------|
| `/orchestrate-proposify-domination` | Full-cycle competitive feature development | 6-phase orchestrator with delta audits |
| `/quoted-discover` | Opportunity discovery from multiple perspectives | 3 parallel Discovery Council agents |
| `/orchestrate-prod-ready` | Production readiness implementation | Batched PR orchestration |
| `/add-ticket` | Quick ticket addition to backlog | Single-shot, auto-READY status |
| `/run-qa` | Autonomous QA across all domains | 6 parallel testing agents |

### The Thin Orchestrator Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Thin)                          │
│  • Reads state file                                             │
│  • Determines current phase                                     │
│  • Spawns subagent(s) with focused prompts                      │
│  • Updates state file with results                              │
│  • Preserves own context for coordination                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUBAGENT (Full Context)                      │
│  • Receives focused task prompt                                 │
│  • Has full 200K context budget                                 │
│  • Performs deep analysis/implementation                        │
│  • Returns structured findings                                  │
│  • Context released after completion                            │
└─────────────────────────────────────────────────────────────────┘
```

**Why This Works**: The orchestrator never fills its context with implementation details. It stays light, spawns heavy workers, and persists state to files. This allows arbitrarily complex work across multiple sessions.

---

## State Persistence Architecture

### State Files

Each orchestrator maintains a companion state file:

```
.claude/commands/orchestrate-proposify-domination.md  → .claude/proposify-domination-state.md
.claude/commands/orchestrate-prod-ready.md            → .claude/prod-ready-state.md
```

### State File Structure

```markdown
# Feature Name - State Tracker

## Current Phase
**Phase**: 2 - Design
**Last Updated**: 2024-12-24
**Status**: In progress

## Phase Progress
- [x] Phase 1: Deep Audit (COMPLETE)
- [ ] Phase 2: 10x Design (IN PROGRESS)
- [ ] Phase 3: Technical Specs
...

## Findings Summary
[Accumulated knowledge from previous phases]

## Blockers
[Items awaiting human decision]

## Decisions Log
| Date | Decision | Rationale |
```

**Key Insight**: The state file IS the memory. When a new session starts, the orchestrator reads this file and knows exactly where to resume.

---

## v3.0: Self-Improving Audit Cycles

### The Problem v3.0 Solves

**v2.1 Behavior**: Full audits ran every time, re-discovering the same known issues:
- "Invoice 404 found!" (We know)
- "Quote accept/reject missing!" (We know)
- "Status never transitions!" (We know)

This wasted context, time, and created noise that buried NEW discoveries.

### The Solution: Known Issues Registry

v3.0 introduces a **baseline** of documented issues that audits should NOT re-report:

```markdown
## Known Issues Registry (Baseline: 2024-12-24)

**CRITICAL**: These issues are ALREADY DOCUMENTED. Audits should:
- Verify they still exist (haven't been fixed)
- Look for ADDITIONAL issues NOT in this list
- NOT re-report these as new findings

### Critical Issues (P0)
| ID | Issue | Location | Status |
|----|-------|----------|--------|
| KI-001 | Invoice share link returns 404 | invoices.py:638-639 | OPEN |
| KI-002 | Quote accept/reject workflow missing | quote-view.html | OPEN |
| KI-003 | Quote status never transitions | database.py:325 | OPEN |

### High Priority Issues (P1)
| ID | Issue | Location | Status |
|----|-------|----------|--------|
| KI-004 | view_count not persisted | share.py:335-349 | OPEN |
| KI-005 | Task reminders are dead code | database.py:585 | OPEN |
...
```

### Delta Audit Prompts

Audit subagents receive explicit instructions referencing the baseline:

```markdown
## Your Task: DELTA Audit of [System]

### CRITICAL CONTEXT
The following issues are ALREADY KNOWN and DOCUMENTED:
- KI-001: Invoice 404 (invoices.py:638-639)
- KI-002: Quote accept/reject missing
...

### Your Output Should Include:
1. **Verification**: Do the known issues still exist? (Don't re-explain, just confirm)
2. **NEW Findings**: Issues NOT in the known list above
3. **Regressions**: Did anything that was working break?

### DO NOT:
- Re-report known issues as new discoveries
- Spend context explaining documented problems
- Repeat the baseline back to me
```

### Verified Working Baseline

Alongside known issues, v3.0 tracks **what works**:

```markdown
## Verified Working Baseline

### Quote Sharing (GROWTH-003)
**Working Features**:
- Email share with PDF attachment (share.py:167-185)
- Shareable link generation (share.py:257-271)
- Public quote view endpoint (share.py:310-371)
- PostHog event tracking (share.py:196-210)

### CRM System (DISC-085-092)
**Status**: 🟢 GREEN - Fully Functional
**Working Features**:
- Customer CRUD API (17 endpoints)
- Voice command routing (7 intents)
- Quote-to-customer auto-linking
```

**Audit Instruction**: "Verify these still work. Only report if something REGRESSED."

---

## Multi-Agent Discovery Council

### How `/quoted-discover` Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     DISCOVERY ORCHESTRATOR                       │
│                      (Thin Coordinator)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ PRODUCT  │   │  GROWTH  │   │ STRATEGY │
        │  AGENT   │   │  AGENT   │   │  AGENT   │
        └──────────┘   └──────────┘   └──────────┘
              │               │               │
              ▼               ▼               ▼
        "5 feature      "5 conversion   "5 competitive
         ideas"          blockers"       opportunities"
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    ┌─────────────────┐
                    │ DISCOVERY_BACKLOG│
                    │     .md          │
                    └─────────────────┘
```

### Parallel Agent Prompts

Each agent gets a focused lens:

**Product Agent**:
> "You are a Product Manager. Analyze the current feature set and identify 5 high-impact improvements that would delight existing users."

**Growth Agent**:
> "You are a Growth Engineer. Identify 5 friction points in the signup→activation→retention funnel that are costing us users."

**Strategy Agent**:
> "You are a Competitive Strategist. Given Proposify's feature set, identify 5 differentiation opportunities where Quoted can win."

### Output Format

All agents output standardized DISC tickets:

```markdown
### DISC-XXX: [Title]
**Status**: DISCOVERED
**Priority**: P1
**Effort**: M (1-2 days)
**Impact**: HIGH - [Measurable outcome]
**Technical Notes**: [Implementation hints]
**Dependencies**: [Related tickets]
```

---

## The Autonomous Development Lifecycle

### Full Cycle: Opportunity → Production

```
1. DISCOVER (/quoted-discover)
   │ Discovery Council spawns 3 parallel agents
   │ Output: 15 new DISC tickets in backlog
   ▼
2. PRIORITIZE (Human Review)
   │ Founder reviews DISCOVERY_BACKLOG.md
   │ Approves tickets: DISCOVERED → READY
   ▼
3. AUDIT (/orchestrate-proposify-domination Phase 1)
   │ Delta audits against Known Issues Registry
   │ Output: Synthesis with NEW findings only
   ▼
4. DESIGN (/orchestrate-proposify-domination Phase 2)
   │ 10x designs that address mapped KI-XXX issues
   │ Output: Detailed feature specs
   ▼
5. SPEC (/orchestrate-proposify-domination Phase 3)
   │ Technical specifications with test plans
   │ Output: Implementation-ready specs
   ▼
6. IMPLEMENT (/orchestrate-proposify-domination Phase 4)
   │ Wave-based implementation with PR batching
   │ Output: Working code in feature branches
   ▼
7. QA (/run-qa)
   │ 6 parallel QA agents test all domains
   │ Output: BUG-XXX tickets for failures
   ▼
8. RELEASE (/orchestrate-proposify-domination Phase 6)
   │ Staged rollout with feature flags
   │ Output: Production deployment
```

### Human Touchpoints

The system is designed for **strategic human review**, not task management:

| Phase | Human Role |
|-------|------------|
| Discovery | Review & approve tickets (DISCOVERED → READY) |
| Audit Synthesis | Answer founder questions, confirm priorities |
| Design Review | Approve architectural decisions |
| QA Failures | Triage bugs, decide fix priority |
| Release | Monitor rollout, decide rollback |

---

## QA Fleet Architecture

### How `/run-qa` Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        QA ORCHESTRATOR                           │
│                       (Test Dispatcher)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────┬─────────┬─┴─────────┬─────────┬─────────┐
        ▼         ▼         ▼           ▼         ▼         ▼
   ┌────────┐┌────────┐┌────────┐ ┌────────┐┌────────┐┌────────┐
   │ AUTH   ││ QUOTE  ││ SHARE  │ │ BILLING││  CRM   ││ INVOICE│
   │ TESTS  ││ TESTS  ││ TESTS  │ │ TESTS  ││ TESTS  ││ TESTS  │
   └────────┘└────────┘└────────┘ └────────┘└────────┘└────────┘
        │         │         │           │         │         │
        ▼         ▼         ▼           ▼         ▼         ▼
   [PASS/FAIL][PASS/FAIL][PASS/FAIL][PASS/FAIL][PASS/FAIL][PASS/FAIL]
```

### Auto-Ticketing on Failure

When a QA agent finds a bug:

1. Agent creates `BUG-XXX` ticket with reproduction steps
2. Ticket added to `ENGINEERING_STATE.md` with priority
3. Slack notification (if configured)
4. Blocks release phase if critical

---

## Infrastructure for Autonomous AI

### Current Capabilities (DISC-101-108)

| Ticket | Feature | Status |
|--------|---------|--------|
| DISC-101 | LLM-as-Judge evaluation framework | COMPLETE |
| DISC-102 | Risk classification (LOW/MEDIUM/HIGH/PROHIBITED) | READY |
| DISC-103 | Complexity detection for auto-breakdown | READY |
| DISC-104 | Git worktree isolation | READY |
| DISC-105 | Memory/learning system | READY |
| DISC-106 | Safety net (pre-deploy checks) | READY |
| DISC-107 | Session continuity protocol | COMPLETE |
| DISC-108 | Regression gate | COMPLETE |

### Risk Classification (DISC-102)

Actions are classified by risk level:

| Risk Level | Examples | AI Behavior |
|------------|----------|-------------|
| **LOW** | Read files, run tests, create branches | Auto-execute |
| **MEDIUM** | Edit non-critical files, create PRs | Execute with logging |
| **HIGH** | Edit auth/billing, modify DB schema | Suggest only, await approval |
| **PROHIBITED** | Delete production data, modify secrets | Block entirely |

---

## Production Access

### Railway CLI Integration

All Claude instances have full production diagnostics:

```bash
railway logs                              # Real-time production logs
railway logs -n 100                       # Last 100 lines
railway logs -n 100 --filter "@level:error"  # Filter for errors
railway variables                         # Check environment variables
railway status                            # Deployment status
```

This enables AI agents to diagnose production issues without human intermediation.

---

## Key Learnings

### What Makes This Work

1. **State files are the source of truth** - Not conversation history
2. **Thin orchestrators preserve context** - Heavy work goes to subagents
3. **Baselines prevent thrashing** - Known issues registry stops re-discovery
4. **Parallel agents multiply throughput** - 3-6 agents working simultaneously
5. **Human reviews strategy, not tasks** - Approval gates at phase boundaries
6. **Everything is markdown** - Human-readable, version-controlled, AI-parseable

### Anti-Patterns Avoided

- ❌ Putting all work in one context (overflows)
- ❌ Expecting LLMs to remember across sessions (they don't)
- ❌ Re-auditing known issues (wastes time)
- ❌ Human task management (doesn't scale)
- ❌ Monolithic commands (can't parallelize)

---

## Future Evolution

### Planned Enhancements

1. **Auto-approval for LOW risk** - Skip human review for safe operations
2. **Learning from corrections** - When human overrides AI, capture the pattern
3. **Cross-project knowledge** - Share learnings between orchestrators
4. **Predictive discovery** - Anticipate issues before they're reported
5. **Self-healing deployments** - Auto-rollback on regression detection

---

*This document describes the autonomous development system powering Quoted's AI-native development workflow. The system continues to evolve with each iteration.*
