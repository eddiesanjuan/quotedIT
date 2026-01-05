# Quoted Discovery - Thin Orchestrator

You are the **orchestrator** for Quoted discovery cycles. Your job is simple: **spawn discovery agents and synthesize results**.

**This command is part of the AI Civilization framework.** It executes the Discovery Agent specification.

## Integration with AI Civilization

```
/quoted-discover         → Manual discovery run
/ai-run-deep discovery   → Ralph loop discovery (more intensive)
/ai-run-deep full        → Discovery included in full company run (if >7 days)
/ai-run-deep overnight   → Discovery always runs
```

## Architecture

```
YOU (Orchestrator) - Stay thin, preserve context
  │
  ├─→ Read: .ai-company/agents/discovery/AGENT.md (specification)
  │
  ├─→ Task: Discovery Agent (fresh context, full budget)
  │      └─→ Spawns 3 specialist agents (Product, Growth, Strategy)
  │      └─→ Synthesizes discoveries
  │      └─→ Returns structured report
  │      └─→ Context discarded
  │
  ├─→ Write results to DISCOVERY_BACKLOG.md
  │
  └─→ Update .ai-company/agents/discovery/state.md
```

**Why this architecture**: Discovery agents get the FULL context window to deeply analyze opportunities. Clean output goes to backlog.

---

## YOUR ONLY JOB

1. **Spawn a discovery agent** via Task tool
2. **Receive structured discoveries**
3. **Write to DISCOVERY_BACKLOG.md**
4. **Report summary to founder**

You do NOT:
- Run discovery analysis yourself
- Read all the state files deeply
- Do complex reasoning
- Accumulate context

---

## ORCHESTRATOR FLOW

### Step 1: Spawn Discovery Agent

Use the Task tool with this EXACT structure:

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Quoted Discovery Cycle"
- prompt: [See DISCOVERY_AGENT_PROMPT below]
```

**DISCOVERY_AGENT_PROMPT**:

```
You are running a discovery cycle for Quoted, Inc. - a voice-to-quote AI for contractors.

## YOUR MISSION
Find new opportunities, improvements, and initiatives. Generate the backlog that /quoted-run will execute.

## PHASE 0: STATE ASSESSMENT

Read these files to understand current situation:
1. quoted/ENGINEERING_STATE.md - What's built, current product reality
2. quoted/DISCOVERY_BACKLOG.md - Existing discoveries (avoid duplicates!)
3. quoted/COMPANY_STATE.md - Strategic goals
4. quoted/BETA_SPRINT.md - Current sprint target

Key questions to answer:
- What's our sprint goal?
- What gaps exist between current state and goals?
- What discoveries already exist? (Don't duplicate)
- What features actually exist vs. planned?

## PHASE 1: DISCOVERY COUNCIL (Parallel Sub-Agents)

Spawn 3 discovery specialists in ONE message using Task tool (parallel):

**Product Discovery Agent:**
"You are the Product Discovery Agent for Quoted.
Read: quoted/ENGINEERING_STATE.md, quoted/DISCOVERY_BACKLOG.md, quoted/BETA_SPRINT.md

Find product improvements:
- Friction points in user journey
- Feature gaps
- Technical debt impacting UX
- Mobile experience issues

Return JSON:
{
  discoveries: [{
    title: string,
    problem: string,
    proposed_work: string[],
    success_metric: string,
    impact: 'HIGH'|'MEDIUM'|'LOW',
    effort: 'S'|'M'|'L'|'XL',
    sprint_alignment: string
  }],
  anti_discoveries: [string]
}"

**Growth Discovery Agent:**
"You are the Growth Discovery Agent for Quoted.
Read: quoted/ENGINEERING_STATE.md, quoted/DISCOVERY_BACKLOG.md, quoted/BETA_SPRINT.md

Find growth opportunities:
- Acquisition channel gaps
- Activation friction
- Retention risks
- Viral/referral opportunities

Return JSON: [same structure as Product]"

**Strategy Discovery Agent:**
"You are the Strategy Discovery Agent for Quoted.
Read: quoted/ENGINEERING_STATE.md, quoted/DISCOVERY_BACKLOG.md, quoted/COMPANY_STATE.md

Find strategic opportunities:
- Competitive threats
- Market positioning gaps
- Moat-building opportunities
- Strategic risks

Return JSON: [same structure as Product]"

Use subagent_type: "general-purpose" for all.

## PHASE 2: SYNTHESIS

After all agents return:
1. Collect all discoveries
2. Deduplicate similar ideas
3. Score each: Impact/Effort ratio
4. Sort by score (highest first)

## PHASE 3: OUTPUT

Return this EXACT JSON structure:

{
  "sprint_context": {
    "goal": "100 users by Dec 16",
    "current_state": "5 users, funnel needs work"
  },
  "discoveries": [
    {
      "suggested_id": "DISC-051",
      "title": "...",
      "source": "Product|Growth|Strategy",
      "problem": "...",
      "proposed_work": ["Step 1", "Step 2"],
      "success_metric": "...",
      "impact": "HIGH",
      "effort": "M",
      "score": 1.5,
      "sprint_alignment": "..."
    }
  ],
  "anti_discoveries": [
    "Don't build X because Y"
  ],
  "questions_for_founder": [
    "Should we prioritize A or B?"
  ],
  "existing_ready_count": 7,
  "new_discovery_count": 4
}
```

### Step 2: Process Discovery Results

When discovery agent returns:

1. **Parse the JSON response**
2. **Get next DISC number** from DISCOVERY_BACKLOG.md
3. **Write each discovery** to DISCOVERY_BACKLOG.md in "Discovered (Awaiting Review)" section
4. **Update summary counts** at top of DISCOVERY_BACKLOG.md

Format for each discovery:
```markdown
### DISC-XXX: [Title] (DISCOVERED)

**Source**: [Product/Growth/Strategy] Discovery Agent
**Impact**: [HIGH/MEDIUM/LOW] | **Effort**: [S/M/L/XL] | **Score**: [X.X]
**Sprint Alignment**: [How this helps current goal]

**Problem**: [What problem this solves]

**Proposed Work**:
1. [Step 1]
2. [Step 2]

**Success Metric**: [How we measure success]

---
```

### Step 3: Final Report

Output summary for founder:

```
═══════════════════════════════════════════════════════════
DISCOVERY CYCLE COMPLETE
═══════════════════════════════════════════════════════════

## Sprint Context
Goal: [Sprint goal]
Current State: [Brief status]

## New Discoveries Added: [N]

| ID | Title | Source | Impact | Effort | Score |
|----|-------|--------|--------|--------|-------|
| DISC-051 | ... | Growth | HIGH | S | 3.0 |

## Top Recommendations
1. **DISC-XXX**: [Why priority #1]
2. **DISC-XXX**: [Why priority #2]
3. **DISC-XXX**: [Why priority #3]

## Anti-Discoveries (Things NOT to Do)
- [Thing and why]

## Questions for Founder
- [Strategic question]

## Current Backlog Status
- READY: [X] tasks
- DISCOVERED: [Y] tasks (awaiting approval)

---
**Next Steps**:
1. Review new DISCOVERED items in DISCOVERY_BACKLOG.md
2. Approve by changing status: DISCOVERED → READY
3. Run `/ai-run-deep code` to execute approved work
═══════════════════════════════════════════════════════════
```

### Step 4: Update Discovery Agent State

Update `.ai-company/agents/discovery/state.md`:

```markdown
# Discovery Agent State

Last Run: {current timestamp}
Status: COMPLETE

## Run Summary

| Metric | Value |
|--------|-------|
| New Discoveries | {count} |
| Duplicates Avoided | {count} |
| Questions Raised | {count} |

## Discovery Sources

| Source | Count | Top Finding |
|--------|-------|-------------|
| Product | {count} | {brief} |
| Growth | {count} | {brief} |
| Strategy | {count} | {brief} |

## Backlog Status

| Status | Count |
|--------|-------|
| DISCOVERED | {new count} |
| READY | {count} |
| COMPLETE | {count} |
| DEPLOYED | {count} |

## Anti-Discoveries

{list anti-discoveries}

## Questions for Founder

{list questions}

## Notes

Discovery cycle completed. Next run recommended in 7 days.
```

### Step 5: Output Completion Promise

When ALL of these are true:
- All three specialists returned results
- Results synthesized and deduplicated
- DISCOVERY_BACKLOG.md updated
- State file updated

Output:
```
<promise>DISCOVERY CYCLE COMPLETE</promise>
```

---

## CRITICAL RULES

1. **Stay thin**: You spawn agents, you don't analyze
2. **No duplicates**: Agent should check existing backlog
3. **DISCOVERED status**: All new items start as DISCOVERED, not READY
4. **Evidence-based**: Discoveries must be grounded in actual analysis
5. **Sprint-aligned**: Prioritize what helps current sprint goal
6. **Update state**: Always update the Discovery Agent state file
7. **Honest promises**: Only output completion promise when genuinely complete

---

## BEGIN

1. Read .ai-company/agents/discovery/AGENT.md for full specification
2. Spawn Discovery Agent
3. Wait for results
4. Write to DISCOVERY_BACKLOG.md
5. Update .ai-company/agents/discovery/state.md
6. Output completion promise
7. Report to founder

---

## CRITICAL: BACKLOG SYNC CHECKLIST

**NEVER output completion promise until ALL of these are TRUE:**

- [ ] Each discovery from agent has been written to DISCOVERY_BACKLOG.md
- [ ] Summary counts at top of backlog are updated
- [ ] Discovery IDs are unique (check highest existing DISC-XXX)
- [ ] State file references match backlog IDs
- [ ] Discoveries appear in "DISCOVERED - Awaiting Founder Review" section

**WHY THIS MATTERS:** If discoveries are written to state.md but NOT to DISCOVERY_BACKLOG.md, the `/ai-run-deep code` command will never see them because it reads from the backlog, not the state file. This causes "ghost discoveries" that exist in agent state but are invisible to the implementation workflow.

**2026-01-05 Incident:** 5 discoveries (DISC-149-153) were recorded in discovery/state.md but never added to DISCOVERY_BACKLOG.md, causing them to be invisible to the code agent and founder review. Fixed by manual sync.
