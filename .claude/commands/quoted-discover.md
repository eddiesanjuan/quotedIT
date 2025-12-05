# Quoted Discovery Cycle

You are initiating a **discovery cycle** for Quoted, Inc. - the work generation layer of an autonomous AI company.

## Purpose

Generate new tasks, opportunities, and initiatives that feed into the execution layer (`/quoted-run`).

Unlike the execution layer which clears a backlog, discovery **creates** the backlog.

## Discovery Protocol

### Phase 0: State Assessment

Read state files to understand the current situation (files split for readability):

**Start here:**
- `ENGINEERING_STATE.md` - Active work only (~100 lines) - READ FIRST
  - ⚠️ **CRITICAL**: Read the "Current Product Reality" section before making ANY assumptions about what features exist

**Then context files:**
- `DISCOVERY_BACKLOG.md` - All DISC-XXX items, existing discoveries (~300 lines)
- `DEPLOYMENT_LOG.md` - Recent deployments (~100 lines)
- `COMPANY_STATE.md` - Strategic overview, current goals
- `BETA_SPRINT.md` - Current sprint goals and metrics (NOTE: Some specs are aspirational, not implemented)
- `DECISION_QUEUE.md` - Pending decisions

Key questions:
- What's our current sprint goal? (e.g., "100 users by Dec 16")
- What's working? What's not?
- What gaps exist between current state and goals?
- What discoveries are already in the backlog? (Avoid duplicates)
- **What features actually exist** vs. what was planned? (Check Current Product Reality table)

### Phase 1: Discovery Council (Parallel)

Spawn 3 discovery agents in parallel using the Task tool:

**1. Product Discovery Agent** (`agents/product-discovery.md`)
- Reviews user feedback, support issues, feature requests
- Identifies friction points in current product
- Proposes product improvements with business case

**2. Growth Discovery Agent** (`agents/growth-discovery.md`)
- Analyzes growth funnel and metrics goals
- Identifies acquisition/activation/retention opportunities
- Proposes growth experiments with expected impact

**3. Strategy Discovery Agent** (`agents/strategy-discovery.md`)
- Reviews competitive landscape and market trends
- Identifies strategic opportunities and risks
- Proposes strategic initiatives or pivots

Each agent returns structured discoveries:
```
DISCOVERIES:
1. [Title] - [Impact: HIGH/MEDIUM/LOW]
   Problem: [What problem this solves]
   Proposed Task: [What to build/do]
   Success Metric: [How we'd measure success]
   Effort: [T-shirt size: S/M/L/XL]
```

### Phase 2: Synthesis & Prioritization

After all agents return:

1. **Collect all discoveries** from the three agents
2. **Deduplicate** similar ideas
3. **Score each discovery**:
   - Impact on sprint goals (HIGH=3, MEDIUM=2, LOW=1)
   - Effort required (S=1, M=2, L=3, XL=4)
   - Impact/Effort ratio = score
4. **Generate task tickets** for top discoveries

### Phase 3: Output to Discovery Backlog

Write discovered tasks to `DISCOVERY_BACKLOG.md` in the "Discovered (Awaiting Review)" section with:
- Ticket ID (DISC-XXX) - Use next available number
- Title and description
- Priority based on scoring
- Source (which discovery agent)
- Status: `DISCOVERED` (not `READY` - awaiting founder review)

**Also update the Summary table** at the top of `DISCOVERY_BACKLOG.md` with new counts.

Format:
```markdown
## DISC-001: [Title] (DISCOVERED)

**Source**: [Product/Growth/Strategy] Discovery Agent
**Impact**: [HIGH/MEDIUM/LOW] | **Effort**: [S/M/L/XL]
**Sprint Alignment**: [How this helps current sprint goal]

**Problem**: [What problem this solves]

**Proposed Work**:
1. [Step 1]
2. [Step 2]

**Success Metric**: [How we measure success]
```

### Phase 4: Summary Report

Output a summary for the founder:

```
DISCOVERY_REPORT:

## Sprint Context
Current Goal: [Sprint goal]
Current State: [Brief status]

## Discoveries Found
| ID | Title | Source | Impact | Effort | Score |
|----|-------|--------|--------|--------|-------|
| DISC-001 | ... | Product | HIGH | M | 1.5 |

## Top Recommendations
1. DISC-XXX: [Why this is priority #1]
2. DISC-XXX: [Why this is priority #2]
3. DISC-XXX: [Why this is priority #3]

## Questions for Founder
- [Any strategic questions that emerged]

---
Next: Review DISC-XXX tasks in DISCOVERY_BACKLOG.md
Approve by changing status from DISCOVERED → READY
Then run `/quoted-run` to execute
```

## Key Principles

1. **Discovery creates, execution consumes** - This command fills the backlog
2. **Scored, not arbitrary** - Every discovery has impact/effort scoring
3. **Founder review gate** - DISCOVERED status means "proposed, not approved"
4. **Sprint-aligned** - Prioritize discoveries that help current sprint goals
5. **Diverse perspectives** - Three agents catch different opportunity types
6. **Reality-based** - NEVER assume features exist based on specs; always verify against Current Product Reality table
7. **Production health is critical** - Any proposed changes must not break existing functionality

## Production Safety

**Production is now live with real users.** All discoveries that become execution work must follow these safety rules:

1. **Verify before assuming** - Check `ENGINEERING_STATE.md` → "Current Product Reality" for what actually exists
2. **Test before deploy** - Run `/run-qa smoke` before any deployment
3. **Incremental changes** - Prefer small, testable changes over large refactors
4. **Rollback plan** - Every change should be easy to revert
5. **Monitor after deploy** - Check Railway logs and PostHog for issues post-deployment

## When to Run

- After clearing the backlog (execution has nothing to do)
- Weekly strategic refresh
- When sprint goals change
- After major product changes or user feedback

## Notes

- Discovery agents should be opinionated but evidence-based
- Prefer small, testable experiments over large initiatives
- Include "anti-discoveries" - things we should NOT do and why
