# Baton Pass

> **Purpose**: Accumulated wisdom across all sessions. Read at session start, update at session end.
> **Created**: 2026-01-05 (DISC-156: Self-Improvement Evolution)
> **Philosophy**: The system should remember hard-won lessons, not relearn them.

This document is **different from LEARNING_MEMORY.md**:
- LEARNING_MEMORY.md = Structured data (patterns, scores, metrics)
- BATON_PASS.md = Narrative wisdom (context, decisions, gotchas)

**Read this at every session start. Update at every session end.**

---

## Architecture Decisions (Don't Revisit)

> Major decisions that were made for good reasons. Don't waste time reconsidering these.

| Date | Decision | Alternatives Considered | Why This Choice | Revisit If |
|------|----------|------------------------|-----------------|------------|
| 2026-01-05 | State files in git over database | PostgreSQL, Redis, S3 | Simpler, auditable, no infra | Scale exceeds git limits |
| 2026-01-05 | LEARNING_MEMORY.md in project root | In .ai-company/, in docs/ | Maximum visibility, all agents read | Never (it's fine here) |
| 2026-01-05 | Quality Gate threshold 18/25 | 15, 20 | 18 = "B grade" - not perfect but solid | If too many false negatives |
| 2026-01-05 | 5 quality dimensions (1-5 each) | 3 dimensions, 10-point scale | Granular enough, fast to score | If missing important aspects |

### Why These Decisions Matter

The meta-agent is explicitly forbidden from reopening architecture decisions without strong evidence. If you find yourself wanting to change one of these, ask:

1. Is there new information that invalidates the original reasoning?
2. Has the context significantly changed?
3. Would Eddie explicitly want this reconsidered?

If not all three → Don't change it.

---

## Known Gotchas

> Hard-won operational knowledge. These are the "I wish someone had told me" items.

### Codebase Gotchas

| Area | Gotcha | Why | Workaround |
|------|--------|-----|------------|
| PDF | WeasyPrint requires inline CSS | External stylesheets don't work | Use `style=""` attributes |
| Auth | JWT tokens expire silently | No automatic refresh | Check token validity before API calls |
| Frontend | index.html is SPA, landing.html is static | Different patterns | Check which file you're editing |
| PostHog | Events need explicit tracking | Not automatic | Add `posthog.capture()` for new features |
| Railway | Preview URLs follow pattern | pr-{N}-quoted-it.up.railway.app | Construct URL from PR number |

### Process Gotchas

| Process | Gotcha | Why | Workaround |
|---------|--------|-----|------------|
| PRs | 4 open PRs exist from previous runs | Incomplete runs | Handle open PRs before new work |
| Backlog | DISCOVERY_BACKLOG.md conflicts | Multiple agents updating | Batch updates at session end |
| Testing | Playwright requires browser MCP profile | Different MCP config | Switch profile before testing |
| Commits | Always use heredoc for messages | Special characters break | See CLAUDE.md example |

### Integration Gotchas

| Service | Gotcha | Impact | Solution |
|---------|--------|--------|----------|
| Stripe | Webhook events may arrive out of order | State confusion | Check timestamps, handle idempotently |
| Resend | Rate limits are strict | Emails fail silently | Implement exponential backoff |
| Claude API | Token limits for long contexts | Truncated prompts | Summarize relevant sections |

---

## Agent Personalities

> What prompting approaches work best for each agent. Learned through observation.

### Code Agent

**Works Well**:
- Explicit file paths (not "the main file")
- Scope boundaries ("ONLY change X, do NOT touch Y")
- Reference to existing patterns ("follow the pattern in auth.py")

**Doesn't Work**:
- Vague instructions ("make it better")
- Multiple unrelated tasks in one ticket
- Assumptions about state ("the user is logged in")

**Quirks**:
- Over-engineers if not constrained
- Adds comments/docstrings that weren't asked for
- Sometimes creates abstractions for one-time code

### Discovery Agent

**Works Well**:
- Clear categories for discoveries
- Explicit output format requirements
- Reference to DISCOVERY_BACKLOG.md structure

**Doesn't Work**:
- Open-ended exploration without bounds
- "Find problems" without categories
- Expecting implementation (it only discovers)

### Meta Agent

**Works Well**:
- Structured analysis prompts
- Clear improvement categories (LOW/MEDIUM/HIGH risk)
- Reference to evolution-log format

**Doesn't Work**:
- Asking it to modify its own spec (forbidden)
- Expecting real-time changes (weekly cadence)
- Vague improvement goals

---

## Eddie's Preferences

> What the founder cares about most. Inferred from feedback and CLAUDE.md.

### Strong Preferences (HIGH Confidence)

| Preference | Evidence | Implication |
|------------|----------|-------------|
| Mobile-first | CLAUDE.md explicit | Test at 375px before desktop |
| No over-engineering | CLAUDE.md explicit | Only make requested changes |
| Safe DOM manipulation | CLAUDE.md explicit | createElement over innerHTML |
| PostHog tracking | CLAUDE.md explicit | Add events for new features |
| Transparency | Constitution | Explain reasoning in commits |

### Inferred Preferences (MEDIUM Confidence)

| Preference | Evidence | Implication |
|------------|----------|-------------|
| Autonomy over perfection | DISC-156 request | Prefer working over polished |
| Self-improvement | DISC-156 request | System should learn and adapt |
| Full deployment testing | ai-run-deep v2 | Don't stop at PR creation |

### Unknown Preferences (Need Clarification)

| Question | Why It Matters | Default Until Clarified |
|----------|----------------|------------------------|
| Preferred PR size? | Bundling decisions | Max 3 tickets or 500 LOC |
| Testing depth? | Time vs coverage tradeoff | Smoke test minimum |
| Quality threshold? | 18/25 vs stricter | 18/25 (current) |

---

## Recent Session Summaries

> Last 5 sessions: what was done, what was learned. Newest first.

### Session 5: 2026-01-05 (DISC-156) - COMPLETE

**Goal**: Implement self-improvement evolution (5 gaps to close)

**Accomplished**:
1. Phase 1: Quality Gate added to ai-run-deep.md (Step 9.5)
2. Phase 2: LEARNING_MEMORY.md created with full structure
3. Phase 3: BATON_PASS.md created (this file)
4. Phase 4: Meta-agent enhanced for self-modifying specs
5. Phase 5: Work-based stop conditions with checkpointing and resume

**Learned**:
- The meta-agent already exists but doesn't actively improve other agents → Now it can
- learnings.md exists in code agent but is mostly empty → Now have LEARNING_MEMORY.md
- 4 open PRs from previous runs need attention → Note for next session
- Phased implementation works well for meta-improvements (validate each step)

**Carry Forward**:
- Address 4 open PRs (DISC-134, DISC-144, DISC-140, DISC-103)
- First quality gate test should be on a simple ticket to validate the rubric
- Monitor first self-improvement trigger from meta-agent

---

### Session Template

```markdown
### Session N: YYYY-MM-DD (DISC-XXX) - STATUS

**Goal**: [One sentence]

**Accomplished**:
1. [What was done]
2. [What was done]

**Learned**:
- [Insight that future sessions should know]
- [Gotcha discovered]

**Carry Forward**:
- [What the next session should do]
- [Unfinished business]
```

---

## Context for Next Session

> Write this at session end. Read by next session start.

### Immediate Context

**Last Worked On**: DISC-156 (Self-Improvement Evolution)
**Status**: COMPLETE - All 5 phases implemented, PR created
**Open PRs**: 5 (DISC-156 new + 4 from previous: DISC-134, DISC-144, DISC-140, DISC-103)

### What To Do Next

1. Test DISC-156 PR on Railway preview deployment
2. Run quality gate on DISC-156 itself (meta-test!)
3. Merge DISC-156 if passing
4. Address 4 older open PRs (prioritize by age)
5. Test quality gate on a simple ticket to validate rubric

### Important Files Modified This Session

| File | Change | Status |
|------|--------|--------|
| .claude/commands/ai-run-deep.md | Quality gate, learning injection, work-based stops | Modified |
| LEARNING_MEMORY.md | New file - outcome memory system | Created |
| BATON_PASS.md | New file - cross-session wisdom | Created |
| .ai-company/agents/meta/AGENT.md | Self-modifying spec capability | Modified |
| docs/SELF_IMPROVEMENT_EVOLUTION.md | Implementation notes | Modified |

### Warnings for Next Session

- 4 older open PRs may have merge conflicts with main
- Quality gate hasn't been tested yet - first run is the real test
- DISC-156 is large (~1000 LOC change) - review carefully
- Self-modifying agent capability is new - monitor first trigger closely

---

## Pruning Guidelines

> Keep this document useful by removing stale entries.

### When to Prune

| Section | Prune When |
|---------|------------|
| Architecture Decisions | Never (these are permanent record) |
| Known Gotchas | Fixed in codebase |
| Agent Personalities | Proven incorrect |
| Eddie's Preferences | Explicitly contradicted |
| Session Summaries | >5 sessions old (archive to LEARNING_MEMORY.md) |
| Context for Next Session | After it's been read and actioned |

### Pruning Process

1. Move stale session summaries to LEARNING_MEMORY.md (Session Outcomes section)
2. Remove gotchas that are no longer relevant
3. Update "Context for Next Session" with fresh context
4. Keep document under 500 lines (current: ~200)

---

*This document is the institutional memory. Treat it with care.*
