# Agent Harness Improvements - Ticket Creation Handoff

**Created**: 2025-12-21
**Purpose**: Create READY tickets in ENGINEERING_STATE.md for agent harness reliability improvements
**Action**: ADD TICKETS ONLY - Do not implement

---

## Context for Ticket Creation

These improvements address two problems from agent harness research:

1. **Bounded Attention**: Same mistakes repeat because handoffs don't capture "what broke and how we fixed it"
2. **Reliability Compounding**: 95% reliability per step → 36% over 20 steps without checkpoints

**Source**: Analysis of "Are Agent Harnesses Bringing Back Vibe Coding?" video applied to Quoted's multi-agent architecture.

---

## Instructions

Add the following tickets to `ENGINEERING_STATE.md` under the backlog section with status `READY`.

Use prefix `INFRA-` for infrastructure/architecture tickets.

---

## Tickets to Create

### INFRA-001: Create HANDOFF.md for Inter-Session Context

**Status**: READY
**Priority**: P1
**Type**: Infrastructure

**Description**:
Create `HANDOFF.md` file for capturing inter-session context, modeled after Anthropic's `claude_progress.txt` pattern. This file should be updated at the end of each autonomous cycle.

**Acceptance Criteria**:
- [ ] HANDOFF.md created in quoted/ root
- [ ] Template includes: Last Session Summary, Failed & Fixed section, Next Priority, Watch Out For, System State
- [ ] "Failed & Fixed" section is mandatory - captures what broke and how it was resolved
- [ ] Includes git HEAD hash, pytest status, deploy status

**Why**: Prevents repeated mistakes by ensuring each session knows what the previous session learned.

---

### INFRA-002: Add Git Log to Agent Priming

**Status**: READY
**Priority**: P1
**Type**: Infrastructure

**Description**:
Update all agent prompts to include git log reading as part of their priming/context-gathering phase. Agents should run `git log --oneline -10` and read HANDOFF.md before starting work.

**Files to Update**:
- agents/backend-engineer.md
- agents/frontend-engineer.md
- agents/content-writer.md
- agents/ceo-orchestrator.md
- agents/cgo.md, cpo.md, cfo.md, cmo.md

**Acceptance Criteria**:
- [ ] All agent files have "Priming" section added
- [ ] Priming includes: Read HANDOFF.md, run git log, check git status, read ENGINEERING_STATE.md, read learning file
- [ ] Order is explicit: priming happens BEFORE task selection

**Why**: Git history is underutilized memory. Recent commits provide context on what's been built.

---

### INFRA-003: Add Regression Checkpoint to Autonomous Loop

**Status**: READY
**Priority**: P1
**Type**: Infrastructure

**Description**:
Add Phase 2.5 (Checkpoint) to `/quoted-run` workflow. Before any commit, pytest must pass. If tests fail, agent must fix or document in HANDOFF.md before proceeding.

**File to Update**:
- .claude/commands/quoted-run.md

**Acceptance Criteria**:
- [ ] Phase 2.5 added between execution and commit
- [ ] pytest runs with `-x --tb=short` flags
- [ ] If tests fail: agent cannot commit, must fix or escalate
- [ ] Failures logged to HANDOFF.md "Failed & Fixed" section
- [ ] Frontend sanity check included for frontend changes

**Why**: Gates commits on test pass. Catches failures before they compound across cycles.

---

### INFRA-004: Add Strategic Human Checkpoints

**Status**: READY
**Priority**: P2
**Type**: Infrastructure

**Description**:
Modify `/quoted-run` orchestrator to pause every 3 cycles for founder review. Generate summary to DECISION_QUEUE.md with checkbox for continue/pause/stop. Auto-continue after 30 minutes for Type 1-2 work only.

**File to Update**:
- .claude/commands/quoted-run.md

**Acceptance Criteria**:
- [ ] Cycle counter tracks completed cycles
- [ ] After every 3 cycles, execution pauses
- [ ] Summary written to DECISION_QUEUE.md with checkboxes
- [ ] Summary includes: cycles completed, tasks done, test status, remaining backlog
- [ ] Auto-continue logic: 30-min timeout for Type 1-2 work, wait indefinitely for Type 3-4
- [ ] Founder can check "Continue", "Pause", or "Stop"

**Why**: Strategic human-in-the-loop prevents runaway compound errors in long autonomous runs.

---

### INFRA-005: Enforce Learning File Updates

**Status**: READY
**Priority**: P2
**Type**: Infrastructure

**Description**:
Add mandatory "Before Completing" section to all agent prompts requiring them to update their learning file if they discovered anything new (bug workaround, gotcha, pattern, failure fix).

**Files to Update**:
- All files in agents/ directory

**Acceptance Criteria**:
- [ ] All agents have "Before Completing" section
- [ ] Section lists which learning file each agent updates
- [ ] Format specified: Date | Learning | Source table
- [ ] Examples of good vs bad learnings provided
- [ ] Explicitly states this is NOT optional

**Why**: Accumulated learning is Quoted's moat. Agents must contribute to knowledge base or future agents repeat mistakes.

---

### INFRA-006: Update Architecture Documentation

**Status**: READY
**Priority**: P3
**Type**: Documentation

**Description**:
Update AUTONOMOUS_ARCHITECTURE.md and MULTI_AGENT_ARCHITECTURE.md to document the new reliability engineering patterns: compound reliability problem, mitigation strategies, checkpoint flow.

**Files to Update**:
- AUTONOMOUS_ARCHITECTURE.md
- MULTI_AGENT_ARCHITECTURE.md

**Acceptance Criteria**:
- [ ] "Reliability Engineering" section added
- [ ] Compound reliability math explained (95% per step → 36% over 20 steps)
- [ ] All mitigation strategies documented
- [ ] Checkpoint flow diagram added
- [ ] References HANDOFF.md, learning files, human checkpoints

**Why**: Future agents and humans need to understand why these patterns exist.

---

## Ticket Summary

| Ticket | Title | Priority | Status |
|--------|-------|----------|--------|
| INFRA-001 | Create HANDOFF.md for Inter-Session Context | P1 | READY |
| INFRA-002 | Add Git Log to Agent Priming | P1 | READY |
| INFRA-003 | Add Regression Checkpoint to Autonomous Loop | P1 | READY |
| INFRA-004 | Add Strategic Human Checkpoints | P2 | READY |
| INFRA-005 | Enforce Learning File Updates | P2 | READY |
| INFRA-006 | Update Architecture Documentation | P3 | READY |

---

## Notes

- All tickets are READY (pre-approved by founder)
- Implementation order: INFRA-001 through INFRA-006
- P1 tickets address immediate reliability concerns
- P2/P3 tickets are important but less urgent
- Do NOT implement - only add tickets to backlog
