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
| 2026-01-05 | Decay scoring (weekly -1) | No decay, faster decay | Weekly is observable, patterns stay ~5 weeks | If patterns age too fast/slow |
| 2026-01-05 | Category-based retrieval | Semantic search, full injection | Simple, no infra, deterministic | If categories don't capture relevance |
| 2026-01-05 | 15 patterns per agent limit | 10, 25, unlimited | 15 is enough history without bloat | If running out of space for valuable patterns |
| 2026-01-05 | External forcing function for autonomy | Self-enforced stop conditions | LLMs rationalize stopping early; external wrapper verifies reality | Never (fundamental insight) |
| 2026-01-05 | Belt-and-suspenders enforcement | External only, Hook only | Hook catches Claude, wrapper catches hook failures | If causing issues |

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
| Autonomy | Claude rationalizes stopping early | Optimizes for "looking done" | Use external wrapper to verify reality |
| Autonomy | Stop hooks only work once per session | `stop_hook_active` prevents loops | Wrapper re-invokes with continuation prompt |

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

### Session 9: 2026-01-06 (DISC-158/159) - COMPLETE

**Goal**: Fix quote edit bug and implement floating save UX

**Accomplished**:
1. Fixed ROOT CAUSE bug: `currentQuote` → `currentDetailQuote` in removeLineItem() and saveQuoteChanges()
2. Fixed keyboard shortcuts referencing undefined functions
3. Implemented floating save dialogue with CSS animation (transform/opacity transitions)
4. Followed full autonomy workflow: PR #50 → Quality eval (21/25) → Merge → Production test

**Learned**:
- Variable reference errors cause silent JS failures - always verify variables are declared
- User emphasized following proper deployment workflows (`/quoted-run`, `/ai-run-deep` skills)
- Railway preview URLs not always available - proceed with code-based quality eval

**Carry Forward**:
- 5 READY tickets remain in queue
- Floating save UX should be manually tested by founder on production

---

### Session 8: 2026-01-05 (Autonomous Architecture) - COMPLETE

**Goal**: Build infrastructure for truly autonomous operation (inspired by Auto-Claude)

**Accomplished**:
1. Created `run_quoted_autonomous.sh` - external forcing function that keeps invoking Claude until work genuinely complete
2. Created `check-work-complete.py` - Stop hook that blocks premature stopping
3. Added `.claude/settings.json` with Stop hook configuration
4. Created `AUTONOMOUS_ARCHITECTURE.md` documentation
5. Analyzed Auto-Claude architecture from video transcript

**Learned**:
- **Critical insight**: LLMs rationalize stopping early. Self-enforced stop conditions fail.
- External wrapper checks reality (READY count, PR count) not Claude's claims
- Claude Code Stop hooks can block stopping, but `stop_hook_active` prevents infinite loops
- Belt-and-suspenders: Hook catches Claude, wrapper catches hook failures, wrapper re-invokes
- Auto-Claude uses worktree isolation per task - future enhancement for us

**Carry Forward**:
- Test autonomous runner: `./.ai-company/scripts/run_quoted_autonomous.sh 1 code`
- The Stop hook only activates when `autonomous-checkpoint.md` exists (autonomous mode flag)
- Future: Add worktree isolation, AI merge conflict resolution, semantic memory

---

### Session 7: 2026-01-05 (Full Run - PR Cleanup) - COMPLETE

**Goal**: Execute `/ai-run-deep full` to clear 4 PR_PENDING tickets and deploy

**Accomplished**:
1. Ops Agent health check - Production GREEN
2. Quality evaluated 4 PRs (23, 23, 24, 21 out of 25 - all PASS)
3. Merged PRs #41, #43, #44; closed #42 as duplicate (subset of #44)
4. Deployed DISC-103 (Complexity Detection), DISC-134 (Social Login), DISC-140 (Monitoring Agent), DISC-144 (Landing Messaging)
5. Production tested - all features working, new landing copy live, Google auth endpoint ready

**Learned**:
- Railway preview deployments not configured → Skip preview testing, use code-based quality eval
- PR #44 was a superset containing both DISC-134 AND DISC-140 → Merged #44, closed #42
- DISCOVERY_BACKLOG.md conflicts are trivial → Accept theirs, batch update at end
- Branch ancestry issues cause PR overlap → Check for overlapping files before merge order

**Carry Forward**:
- Google OAuth requires GOOGLE_OAUTH_CLIENT_ID env var to enable (button hides if not set)
- Monitoring agent runs on scheduler - first health check at 15 min mark
- Landing page has A/B test infrastructure ready for headline variants
- 7 READY tickets remain in queue

---

### Session 6: 2026-01-05 (Guardrails) - COMPLETE

**Goal**: Add decay scoring, size limits, and category-based retrieval to prevent learning memory bloat

**Accomplished**:
1. LEARNING_MEMORY.md v2.0: Added scoring system (1-10), category-based sections, hard limits per section
2. Created LEARNING_ARCHIVE.md for aged-out patterns
3. Added Step 0.5 (Maintenance) to ai-run-deep.md: Weekly decay, pruning, limit enforcement
4. Updated Step 7.1 (Injection): Category-based retrieval with score filtering and token limits

**Learned**:
- Original implementation had no mechanism to prevent unlimited growth → Now has explicit limits
- "Inject relevant patterns" was too vague → Now has concrete scoring rules and category matching
- Decay scoring (weekly -1) ensures only genuinely useful patterns stay active
- Architecture decision: Keep markdown-based (auditable, git-friendly) vs database/vector store

**Carry Forward**:
- Watch first maintenance run (due 2026-01-12) to validate decay works correctly
- Observe pattern score evolution over 2-3 weeks
- May need to tune limits (15 per agent, 20 evaluations, 30 sessions) based on actual usage

---

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

**Last Worked On**: DISC-158 (Quote edit bug fix) + DISC-159 (Floating save UX)
**Status**: DEPLOYED - PR #50 merged, production verified GREEN
**Open PRs**: 0 (all cleared)

### What To Do Next

1. **5 READY tickets remain in queue** - Continue processing backlog:
   - DISC-113: Handyman Mike Workflow (L effort, HIGH impact)
   - DISC-033: Reddit Launch Post (M effort, FOUNDER ACTION)
   - DISC-070: Voice-Driven PDF Templates (XL effort)
   - DISC-074: Alternative Acquisition Channels (BRAINSTORM)
   - DISC-081: QuickBooks Integration (BRAINSTORM)
   - DISC-105: Learning Memory System - Dual Architecture (XL effort)
   - DISC-154: Google Ads Creative Refresh (L effort)
2. Test the autonomous runner: `./.ai-company/scripts/run_quoted_autonomous.sh 1 code`
3. Consider testing the floating save UX on production manually

### Important Files Modified This Session

| File | Purpose | Status |
|------|---------|--------|
| `frontend/index.html` | Bug fix (currentQuote→currentDetailQuote) + Floating Save UX | DEPLOYED |
| `DISCOVERY_BACKLOG.md` | Updated DISC-158/159 to DEPLOYED | Complete |
| `LEARNING_MEMORY.md` | Logged quality evaluation (21/25) | Complete |

### Autonomous Infrastructure Overview

```
┌─────────────────────────────────────────────────────────┐
│  run_quoted_autonomous.sh (External Wrapper)            │
│  ├── Checks: READY tickets, open PRs, PR_PENDING        │
│  ├── Loops until: work genuinely complete               │
│  ├── Re-invokes Claude with continuation prompts        │
│  └── Logs to: .ai-company/logs/                         │
├─────────────────────────────────────────────────────────┤
│  check-work-complete.py (Stop Hook - Belt)              │
│  ├── Only active when: autonomous-checkpoint.md exists  │
│  ├── Blocks stopping if: work remains                   │
│  └── Allows stop if: genuinely complete                 │
└─────────────────────────────────────────────────────────┘
```

### Warnings for Next Session

- Stop hook requires restart of Claude Code to take effect (hook captured at startup)
- The hook only activates in autonomous mode (when checkpoint file exists)
- Budget limit is $50/day - hardcoded in wrapper script
- Consecutive failure limit is 3 - then it stops to avoid infinite loops

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
