# Self-Improvement Evolution Roadmap

> **For**: Quoted Claude Code Instance
> **Purpose**: Transform `/ai-run-deep` into a true self-improving autonomous system
> **Created**: 2026-01-05
> **Authority**: Founder-approved strategic initiative

## Context

Boris Chernney (Claude Code creator) achieved 100% AI-written commits over 30 days (259 PRs, 497 commits). The difference between Quoted's current system and that level is **the intelligence layer** - self-evaluation, learning from outcomes, and self-modification.

Your `/ai-run-deep` command already has:
- Multi-agent architecture (code, growth, ops, support, meta, finance, discovery)
- Full autonomy loop (implement → PR → preview test → merge → production test)
- Ralph Wiggum self-healing execution
- Railway preview deployment testing
- Priority-based task selection
- Constitutional completion promises

**You are 90% there.** This document outlines the 10% gap.

---

## The Five Gaps to Close

### Gap 1: LLM-as-Judge Quality Gate

**Current state**: Playwright tests verify functionality. No AI evaluation of work quality.

**Target state**: Before merge, a separate evaluation pass scores the work against a rubric. Below-threshold work is rejected and regenerated.

**Implementation direction**:
- Add evaluation phase between PREVIEW_TESTING and MERGE
- Create rubric: Completeness, Code Quality, Scope Discipline, Edge Cases, Testing
- Set threshold (suggest 18/25)
- Rejection triggers return to IMPLEMENTATION with specific feedback
- Track scores in a log for trend analysis

**Key insight**: This catches architectural mistakes that pass functional tests.

---

### Gap 2: Outcome Memory (Learning Loop)

**Current state**: Each agent run is stateless. Success/failure doesn't influence future behavior.

**Target state**: A persistent learning memory captures what worked, what failed, and why.

**Implementation direction**:
- Create `LEARNING_MEMORY.md` in project root
- Structure: Successful Patterns, Failed Patterns, User Feedback, Performance Trends
- After each deployment, log outcome (success/rollback/issues)
- Inject relevant entries into agent prompts before execution
- Weekly summary of agent performance by type

**Key insight**: The system should get smarter over time, not reset each run.

---

### Gap 3: Self-Modifying Agent Specs

**Current state**: Meta-agent exists but doesn't rewrite other agent definitions.

**Target state**: When an agent consistently underperforms on a rubric dimension, the system improves that agent's spec.

**Implementation direction**:
- Trigger: Same rubric dimension fails 3+ times for an agent
- Process: Analyze failures → Draft improved spec → Regression test on historical tickets → Deploy if improved
- Constraint: Max 1 spec change per day (prevent thrashing)
- Log all spec changes with rationale
- Human escalation if improvement attempts fail

**Key insight**: This is "Claude Code improving Claude Code" - the core differentiator.

---

### Gap 4: Work-Based Stop Conditions

**Current state**: `MAX_ITERATIONS` stops the system after N cycles regardless of remaining work.

**Target state**: System runs until work is genuinely complete, with intelligent pausing.

**Implementation direction**:
- Replace iteration limit with queue-based stopping
- If queue empty: Run discovery agent, check again
- If still empty: Work complete, stop gracefully
- Long-run checkpointing (8+ hours → save state, allow resume)
- Critical failure → immediate stop with human alert

**Key insight**: Boris's Claude Code runs for hours/days. The system should stop when done, not when tired.

---

### Gap 5: Baton Pass Document

**Current state**: State files are snapshots. Context is lost between major sessions.

**Target state**: A living document accumulates wisdom across all sessions.

**Implementation direction**:
- Create `BATON_PASS.md` - read at session start, update at session end
- Sections: Architecture Decisions, Known Gotchas, Agent Personalities, What Eddie Cares About, Session History
- Captures "what I learned" not just "what I did"
- Grows over time, pruned when stale

**Key insight**: The system should remember hard-won lessons, not relearn them.

---

## Implementation Phases

### Phase 1: Quality Gate (Week 1)
**Priority**: Highest impact, lowest risk

Add to `ai-run-deep.md` after PREVIEW_TESTING:

```markdown
## PHASE 2.5: QUALITY EVALUATION

Before merge, evaluate the implementation:

EVALUATION RUBRIC:
1. COMPLETENESS (1-5): Does it fully address the ticket requirements?
2. CODE QUALITY (1-5): Clean, readable, maintainable, follows conventions?
3. SCOPE DISCIPLINE (1-5): Stayed focused or over-engineered?
4. EDGE CASES (1-5): Error states and boundaries handled?
5. TESTING (1-5): Right things tested at right level?

THRESHOLD: 18/25 minimum to proceed

IF score < 18:
    - Log failure reason to LEARNING_MEMORY.md
    - Return to IMPLEMENTATION with specific feedback
    - Increment retry counter (max 2 retries per ticket)

IF score >= 18:
    - Log success to LEARNING_MEMORY.md
    - Proceed to MERGE
```

### Phase 2: Learning Memory (Week 2)

Create `LEARNING_MEMORY.md`:

```markdown
# Learning Memory

## Successful Patterns
<!-- Format: [Date] [Ticket] - [What worked] -->

## Failed Patterns
<!-- Format: [Date] [Ticket] - [What failed] - [Root cause] - [Lesson] -->

## Agent Performance (Rolling 30 Days)
| Agent | Success Rate | Common Failures |
|-------|--------------|-----------------|

## User Feedback
<!-- Direct quotes from Eddie about quality/preferences -->
```

Modify agent prompts to read relevant sections before execution.

### Phase 3: Baton Pass (Week 2, parallel)

Create `BATON_PASS.md`:

```markdown
# Baton Pass

## Architecture Decisions (Don't Revisit)
<!-- Format: [Date] Chose X over Y because [reason] -->

## Known Gotchas
<!-- Hard-won operational knowledge -->

## Agent Personalities
<!-- What prompting approaches work best for each agent -->

## Eddie's Preferences
<!-- What the founder cares about most -->

## Recent Session Summaries
<!-- Last 5 sessions: what was done, what was learned -->
```

### Phase 4: Self-Improvement Loop (Week 3-4)

Enhance meta-agent capabilities:

```markdown
## META-AGENT ENHANCEMENT

TRIGGER CONDITIONS:
- Agent scores < 15 on 3 consecutive evaluations
- Same rubric dimension fails 3+ times
- User explicitly flags agent underperformance

IMPROVEMENT PROCESS:
1. Analyze failure patterns from LEARNING_MEMORY.md
2. Identify specific weaknesses in current agent spec
3. Draft improved spec with targeted fixes
4. Test improved spec on 3 historical tickets (regression)
5. Compare scores: improved vs. original
6. IF improvement confirmed (>10% better): Deploy new spec
7. ELSE: Escalate to human with analysis

CONSTRAINTS:
- Max 1 spec modification per day
- Never modify Constitution (Article I-X)
- Log all changes with rationale
- Rollback capability required
```

### Phase 5: Infinite Runtime (Week 4)

Replace iteration-based stopping:

```markdown
## STOP CONDITIONS V2

CONTINUE WHILE:
- READY queue has items, OR
- READY queue empty but last discovery was > 1 hour ago

STOP WHEN:
- Queue exhausted AND discovery found nothing new
- Critical failure detected
- Human interruption received

CHECKPOINT WHEN:
- Running > 8 hours continuously
- Save full state to CHECKPOINT.md
- Can resume with `/ai-run-deep --resume`

NEVER STOP FOR:
- Iteration count alone
- Time of day (unless checkpointing)
- Non-critical failures (use Ralph Wiggum loop)
```

---

## Decision Authority

You have **full autonomy** to decide HOW to implement these capabilities. This document describes WHAT is needed and WHY, not the exact implementation.

Suggested approach:
1. Read this document fully
2. Assess current `ai-run-deep.md` structure
3. Design your implementation approach
4. Implement Phase 1 first (quick win, proves the pattern)
5. Iterate through remaining phases
6. Update this document with implementation notes

---

## Success Metrics

Track these to measure progress toward "100% Claude Code" level:

| Metric | Current | Target |
|--------|---------|--------|
| First-attempt PR success rate | Unknown | >85% |
| Rollback rate | Unknown | <5% |
| Human intervention required | Frequent | Rare |
| Self-improvement events | 0 | 2-3/week |
| Continuous run duration | ~1 hour | 4-8 hours |

---

## Questions to Resolve

As you implement, document decisions on:

1. Where should LEARNING_MEMORY.md live? (Root? docs/?)
2. How granular should rubric scoring be? (1-5? 1-10?)
3. Should spec modifications require human approval initially?
4. What's the right checkpoint interval for long runs?
5. How should the baton pass document be pruned over time?

---

## Implementation Notes (DISC-156)

**Implemented**: 2026-01-05
**Version**: v3.0 of ai-run-deep.md

### Decisions Made

| Question | Decision | Reasoning |
|----------|----------|-----------|
| LEARNING_MEMORY.md location | Project root | Maximum visibility, all agents can read |
| Rubric scoring | 1-5 per dimension (5 dimensions = 25 max) | Granular enough, fast to score |
| Spec modifications | LOW risk = auto, MEDIUM/HIGH = queue for Eddie | Matches existing constitution pattern |
| Checkpoint interval | 8 hours (4 for infinite mode) | Long enough to be useful, short enough for safety |
| Baton pass pruning | Sessions >5 old → archive to LEARNING_MEMORY | Keep document under 500 lines |

### Phase Implementation Status

| Phase | Status | Files Modified |
|-------|--------|----------------|
| Phase 1: Quality Gate | COMPLETE | `.claude/commands/ai-run-deep.md` |
| Phase 2: Learning Memory | COMPLETE | `LEARNING_MEMORY.md` (new), `ai-run-deep.md` |
| Phase 3: Baton Pass | COMPLETE | `BATON_PASS.md` (new), `ai-run-deep.md` |
| Phase 4: Self-Modifying Specs | COMPLETE | `.ai-company/agents/meta/AGENT.md` |
| Phase 5: Work-Based Stops | COMPLETE | `ai-run-deep.md` |

### New Capabilities Added

1. **Quality Gate (Step 9.5)**: LLM-as-judge evaluation before merge
   - 5 dimensions: Completeness, Code Quality, Scope Discipline, Edge Cases, Testing
   - Threshold: 18/25 minimum to proceed
   - Max 3 retries per ticket

2. **Learning Memory Injection (Step 7.1)**: Relevant patterns injected into prompts
   - Successful patterns to follow
   - Failed patterns to avoid
   - Eddie's preferences

3. **Self-Modifying Meta-Agent**: Can now modify other agent specs
   - Trigger: Same dimension fails 3+ times
   - Constraint: Max 1 modification per day per agent
   - Never: Constitution, own spec, safety limits

4. **Work-Based Stop Conditions**: Run until work complete
   - Discovery fallback when queue empty
   - Checkpointing every 8 hours
   - Resume capability with `--resume`
   - Infinite mode with `--infinite`

### Success Metrics Baseline

| Metric | Baseline (Pre-DISC-156) | Target |
|--------|------------------------|--------|
| First-attempt PR success rate | Unknown | >85% |
| Rollback rate | Unknown | <5% |
| Human intervention required | Frequent | Rare |
| Self-improvement events | 0 | 2-3/week |
| Continuous run duration | ~1 hour | 4-8 hours |

*Track these over the next 30 days to measure improvement.*

---

*This document is a living artifact. Update it as implementation progresses.*
