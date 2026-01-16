# /quoted-run Architecture

How the autonomous development command works.

## Overview

`/quoted-run` is a **thin orchestrator** that invokes specialized agents to move work through the development lifecycle. It never writes code directly—it coordinates.

```
/quoted-run
    │
    └── Spawns: orchestrator agent
                    │
                    ├── auditor (x3, parallel)
                    ├── developer (wave-based, parallel)
                    ├── qa-agent (gates)
                    └── developer (deploy)
```

## Core Principle

**Orchestrator coordinates. Agents implement.**

| Orchestrator Does | Orchestrator Does NOT |
|-------------------|----------------------|
| Read backlog & state | Write code |
| Spawn agents | Edit files |
| Synthesize outputs | Make commits |
| Present decisions | Deploy without QA |
| Update state file | Skip gates |

## Data Flow

```
DISCOVERY_BACKLOG.md          .claude/quoted-run-state.md
        │                              │
        ▼                              ▼
    [READY tickets]  ──────►  [Session state]
        │                              │
        ▼                              ▼
   Implementation  ──────────►  Deployed
```

**Source of Truth:** `DISCOVERY_BACKLOG.md`
- DISCOVERED → awaiting approval (don't touch)
- READY → approved for implementation
- COMPLETE → implemented, pending deploy
- DEPLOYED → live in production

## Agent Types

| Agent | Purpose | Spawned In |
|-------|---------|------------|
| `auditor` | Analyze codebase with specific lens | Phase 2 |
| `developer` | Implement features, create PRs, deploy | Phase 4, 6, 8 |
| `qa-agent` | Test features, verify deployments | Phase 5, 7 |

## Phase Structure

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: ORIENT                                             │
│ Read backlog, count READY tickets, check for specific args  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: AUDIT (Parallel)                                   │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │   Growth    │ │   Product   │ │  Tech Debt  │            │
│ │   Auditor   │ │   Auditor   │ │   Auditor   │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
│ Conversion,     UX friction,    Security,                   │
│ acquisition     mobile, errors  code quality                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: SYNTHESIS & DECISION GATE                          │
│ Merge findings → Rank by severity → Present to founder      │
│ [HUMAN APPROVAL REQUIRED]                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: IMPLEMENTATION (Wave-Based)                        │
│ Wave 1: Independent tasks (parallel developers)             │
│ Wave 2: Dependent tasks (after Wave 1 completes)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: QA GATE                                            │
│ qa-agent tests all features                                 │
│ Fail → developer fixes → re-test (max 3 attempts)           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 6: PREVIEW DEPLOY                                     │
│ developer creates PR → Railway preview auto-deploys         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 7: PREVIEW VERIFICATION                               │
│ qa-agent tests preview URL with Playwright                  │
│ Fail → developer fixes → push → re-test                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 8: PRODUCTION DEPLOY                                  │
│ developer merges PR → Railway production auto-deploys       │
│ Verify health endpoint                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 9: STATE UPDATE                                       │
│ Update state file, move tickets READY → DEPLOYED            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 10: CONTINUE CHECK                                    │
│ Report results → Ask founder: continue? (y/n)               │
│ Yes → Loop to Phase 2                                       │
└─────────────────────────────────────────────────────────────┘
```

## Usage

| Command | Behavior |
|---------|----------|
| `/quoted-run` | Full autonomous cycle |
| `/quoted-run DISC-071` | Specific ticket (skips audit) |
| `/quoted-run DISC-071 DISC-072` | Multiple tickets |
| `/quoted-run --resume` | Continue from state file |
| `/quoted-run --status` | Show state only |
| `/quoted-run --infinite` | Run until READY queue empty |
| `/quoted-run --pr-only` | Stop after PR creation |

## State Persistence

State file: `.claude/quoted-run-state.md`

Updated after every phase for:
- **Resumability** - continue after context clear
- **Visibility** - founder can check progress
- **Audit trail** - what happened when

## Quality Gates

Two mandatory QA gates prevent broken deploys:

1. **Phase 5** - Test on local/branch before PR
2. **Phase 7** - Test on Railway preview before production

Both use `qa-agent` with Playwright browser tools.

## Emergency Stop

```bash
touch .ai-company/EMERGENCY_STOP
# or
/ai-stop
```

Orchestrator checks for stop file before each phase.

## Key Files

| File | Purpose |
|------|---------|
| `DISCOVERY_BACKLOG.md` | Source of truth for all tickets |
| `.claude/quoted-run-state.md` | Session state for resume |
| `.claude/commands/quoted-run.md` | Command definition |

## Design Philosophy

1. **Backlog-driven** - All work comes from DISCOVERY_BACKLOG.md
2. **Human gates** - Founder approves before implementation
3. **Wave-based parallelism** - Independent work runs simultaneously
4. **Mandatory QA** - No deploy without verification
5. **Iteration over planning** - Ship fast, learn, iterate
