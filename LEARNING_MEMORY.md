# Learning Memory

> **Purpose**: Persistent memory that captures what worked, what failed, and why.
> **Created**: 2026-01-05 (DISC-156: Self-Improvement Evolution)
> **Updated By**: AI agents automatically after each deployment
> **Version**: 2.0 (with decay scoring and size limits)

This file is the AI company's institutional memory. It enables:
1. **Pattern recognition** across runs (what approaches consistently work)
2. **Failure avoidance** (don't repeat known mistakes)
3. **Meta-agent improvement triggers** (when same failures repeat)
4. **Context injection** into agent prompts (relevant learnings before action)

---

## Maintenance Metadata

> Read by Step 0.5 (Maintenance) to determine if pruning is needed.

```yaml
last_maintenance: 2026-01-05
next_maintenance_due: 2026-01-12
total_entries: 8
archive_count: 0
```

---

## Scoring & Decay Rules

> How patterns age and get archived automatically.

### Reuse Score System

| Score | Level | Behavior |
|-------|-------|----------|
| 7+ | HIGH_VALUE | Always inject into prompts |
| 4-6 | MEDIUM_VALUE | Inject only if category matches current work |
| 1-3 | LOW_VALUE | Inject only if explicitly relevant |
| 0 | ARCHIVED | Move to LEARNING_ARCHIVE.md |

### Decay Rules

```
INITIAL_SCORE: 5 (new patterns start here)

WEEKLY_DECAY: -1 (every 7 days without reference)

BOOST_ON_USE: +1 (when pattern is referenced in successful work)
BOOST_ON_REPEAT: +2 (when same pattern succeeds again)

MAX_SCORE: 10 (prevents runaway inflation)
MIN_SCORE: 0 (triggers archival)
```

### Section Limits

| Section | Max Entries | Archive Trigger |
|---------|-------------|-----------------|
| Successful Patterns (per agent) | 15 | Oldest by score archived |
| Failed Patterns (per type) | 15 | Oldest by date archived |
| Quality Evaluation History | 20 | Oldest archived |
| Session Outcomes | 30 | Oldest archived |

**When a section exceeds its limit**: Archive lowest-scored (or oldest) entries to LEARNING_ARCHIVE.md before adding new ones.

---

## Successful Patterns

> Approaches that consistently lead to good outcomes. Agents should REPEAT these.
> **Total entries**: 3 | **Limit**: 15 per agent type

### By Agent Type

#### Code Agent
<!-- MAX 15 entries. Archive oldest when full. -->

| Date | Ticket | Pattern | Why It Worked | Score |
|------|--------|---------|---------------|-------|
| 2026-01-05 | DISC-156 | Phased implementation of meta-capabilities | Reduces risk, allows validation at each step | 5 |

#### Discovery Agent
<!-- MAX 15 entries -->

| Date | Ticket | Pattern | Why It Worked | Score |
|------|--------|---------|---------------|-------|
| - | - | _No patterns yet_ | - | - |

#### Meta Agent
<!-- MAX 15 entries -->

| Date | Ticket | Pattern | Why It Worked | Score |
|------|--------|---------|---------------|-------|
| - | - | _No patterns yet_ | - | - |

#### Ops Agent
<!-- MAX 15 entries -->

| Date | Ticket | Pattern | Why It Worked | Score |
|------|--------|---------|---------------|-------|
| - | - | _No patterns yet_ | - | - |

### By Ticket Category

#### Infrastructure/Meta
<!-- MAX 15 entries -->

| Date | Ticket | Pattern | Why It Worked | Score |
|------|--------|---------|---------------|-------|
| 2026-01-05 | DISC-156 | Implement in phases, validate each before next | Catches issues early, easier rollback | 5 |

#### Frontend/UX
<!-- MAX 15 entries -->

| Date | Ticket | Pattern | Why It Worked | Score |
|------|--------|---------|---------------|-------|
| - | - | _No patterns yet_ | - | - |

#### Backend/API
<!-- MAX 15 entries -->

| Date | Ticket | Pattern | Why It Worked | Score |
|------|--------|---------|---------------|-------|
| - | - | _No patterns yet_ | - | - |

#### PDF/Formatting
<!-- MAX 15 entries -->

| Date | Ticket | Pattern | Why It Worked | Score |
|------|--------|---------|---------------|-------|
| - | - | _No patterns yet_ | - | - |

#### Auth/Billing
<!-- MAX 15 entries -->

| Date | Ticket | Pattern | Why It Worked | Score |
|------|--------|---------|---------------|-------|
| - | - | _No patterns yet_ | - | - |

### Architecture Decisions

> Permanent record - these don't decay but inform future decisions.

| Date | Decision | Outcome | Confidence |
|------|----------|---------|------------|
| 2026-01-05 | State files over database for agent memory | Simpler, git-tracked, no migration overhead | 90% |
| 2026-01-05 | LEARNING_MEMORY.md in project root | Accessible to all agents, part of git history | 85% |
| 2026-01-05 | Decay scoring for pattern relevance | Prevents bloat, keeps relevant patterns fresh | 80% |

---

## Failed Patterns

> Approaches that consistently lead to poor outcomes. Agents should AVOID these.
> **Total entries**: 0 | **Limit**: 15 per failure type

### By Failure Type

#### Scope Creep
<!-- MAX 15 entries. Patterns where agent did more than asked. -->

| Date | Ticket | Failure | Root Cause | Lesson | Repeat Count |
|------|--------|---------|------------|--------|--------------|
| - | - | _No failures yet_ | - | - | 0 |

#### Quality Issues
<!-- MAX 15 entries. Code quality, testing, edge case failures. -->

| Date | Ticket | Failure | Root Cause | Lesson | Repeat Count |
|------|--------|---------|------------|--------|--------------|
| - | - | _No failures yet_ | - | - | 0 |

#### Integration Failures
<!-- MAX 15 entries. API, deployment, environment issues. -->

| Date | Ticket | Failure | Root Cause | Lesson | Repeat Count |
|------|--------|---------|------------|--------|--------------|
| - | - | _No failures yet_ | - | - | 0 |

#### Production Incidents
<!-- MAX 15 entries. Things that broke in prod. -->

| Date | Ticket | Incident | Impact | Root Cause | Prevention |
|------|--------|----------|--------|------------|------------|
| - | - | _No incidents yet_ | - | - | - |

### Quality Dimension Failures

> Track which quality dimensions fail repeatedly (triggers meta-agent improvement).

| Dimension | Fail Count (30 days) | Last Failed | Trigger Status |
|-----------|---------------------|-------------|----------------|
| Completeness | 0 | - | OK |
| Code Quality | 0 | - | OK |
| Scope Discipline | 0 | - | OK |
| Edge Cases | 0 | - | OK |
| Testing | 0 | - | OK |

**Trigger threshold**: 3 failures in same dimension → Meta-agent intervention

---

## Agent Performance (Rolling 30 Days)

> Weekly summary updated by Meta Agent. Automatically resets each 30-day period.

### Current Period: 2026-01-05 to 2026-02-04

| Agent | Tasks | Success Rate | Avg Quality Score | Common Issues |
|-------|-------|--------------|-------------------|---------------|
| Code | 1 | 100% | 23/25 | _Baseline established_ |
| Discovery | 0 | N/A | N/A | _No data yet_ |
| Ops | 0 | N/A | N/A | _No data yet_ |
| Support | 0 | N/A | N/A | _No data yet_ |
| Growth | 0 | N/A | N/A | _No data yet_ |
| Finance | 0 | N/A | N/A | _No data yet_ |
| Meta | 0 | N/A | N/A | _No data yet_ |

### Trend Indicators

| Metric | Last Week | This Week | Trend |
|--------|-----------|-----------|-------|
| First-attempt PR success rate | N/A | 100% | NEW |
| Average quality score | N/A | 23/25 | NEW |
| Rollback rate | N/A | 0% | NEW |
| Human intervention required | N/A | 0 | NEW |

---

## Quality Evaluation History

> Logged automatically during Quality Evaluation phase (Step 9.5)
> **Total entries**: 1 | **Limit**: 20 (oldest archived when exceeded)

### 2026-01-05 DISC-156: Self-Improvement Evolution

| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness | 5 | All 5 phases implemented as specified |
| Code Quality | 5 | Clean markdown, consistent formatting |
| Scope Discipline | 4 | Stayed focused, minor additions for completeness |
| Edge Cases | 4 | Covered main scenarios, some edge cases implicit |
| Testing | 5 | Meta-tested quality gate on itself |
| **TOTAL** | **23/25** | **PASS** |

---

## User Feedback

> Direct quotes and feedback from Eddie about quality, preferences, and priorities.
> These don't decay - Eddie's preferences are always relevant.

### Positive Feedback

| Date | Context | Feedback | Insight |
|------|---------|----------|---------|
| 2026-01-05 | DISC-156 creation | "Become a fully autonomous, self-improving system" | Eddie values autonomy and self-improvement |
| 2026-01-05 | Guardrails request | "Don't just become huge bloated messes" | Eddie values lean, maintainable systems |

### Constructive Feedback

| Date | Context | Feedback | Action Taken |
|------|---------|----------|--------------|
| - | _Feedback will populate this_ | - | - |

### Eddie's Preferences (Inferred)

| Preference | Confidence | Source | Always Inject |
|------------|------------|--------|---------------|
| Mobile-first design | HIGH | CLAUDE.md conventions | Yes |
| Safe DOM manipulation | HIGH | CLAUDE.md conventions | Yes |
| PostHog tracking for features | HIGH | CLAUDE.md conventions | Yes |
| Avoid over-engineering | HIGH | CLAUDE.md conventions | Yes |
| Lean, maintainable systems | HIGH | Direct feedback | Yes |

---

## Improvement Triggers

> Conditions that should trigger meta-agent self-improvement actions.

### Active Triggers

| Trigger | Condition | Agent Affected | Status |
|---------|-----------|----------------|--------|
| QUALITY_FAILURE_PATTERN | Same quality dimension fails 3+ times | Code | NOT_TRIGGERED |
| ROLLBACK_RATE_HIGH | >5% rollback rate over 7 days | Code/Ops | NOT_TRIGGERED |
| REPEAT_FAILURE | Same failure pattern 3+ times | Any | NOT_TRIGGERED |
| LOW_CONFIDENCE | Agent confidence <60% on 5+ decisions | Any | NOT_TRIGGERED |

### Triggered Improvements

| Date | Trigger | Agent | Action Taken | Result |
|------|---------|-------|--------------|--------|
| - | _Improvements will populate this_ | - | - | - |

---

## Session Outcomes

> Brief log of each significant session outcome.
> **Total entries**: 1 | **Limit**: 30 (oldest archived when exceeded)

| Date | Session Type | Tickets | Outcome | Quality Avg | Notes |
|------|--------------|---------|---------|-------------|-------|
| 2026-01-05 | Deep Run | DISC-156 | SUCCESS | 23/25 | Self-improvement evolution + guardrails |

---

## Meta Notes

> High-level observations for future sessions to understand.

### System Health

- **Learning System Status**: ACTIVE (decay scoring enabled)
- **Last Meta-Agent Analysis**: Never run
- **Improvement Backlog**: Empty
- **Archive Status**: LEARNING_ARCHIVE.md created, 0 entries

### Known Limitations

1. Quality scoring is LLM self-evaluation (not external validation)
2. Success/failure classification is binary (no nuance)
3. Pattern matching relies on category tags (no semantic search yet)
4. Decay scoring requires manual maintenance step execution

### Future Enhancements (Backlog)

1. [ ] Add A/B testing framework for prompt improvements
2. [ ] Integrate production metrics (error rates, latency) into outcome scoring
3. [ ] Add automated pattern clustering for failure analysis
4. [ ] Connect to PostHog for user-facing outcome metrics
5. [ ] Semantic search for pattern retrieval (embeddings)

---

*This document is updated automatically by the AI system. Manual edits are preserved.*
*Archive: See LEARNING_ARCHIVE.md for aged-out patterns.*
