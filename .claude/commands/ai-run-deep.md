# AI Civilization - Deep Agent Run (Ralph Wiggum Loop)

Execute an agent in a self-healing loop using Ralph Wiggum plugin. Supports direct task execution, ticket targeting, and smart queue management.

**v2.0 - Full Autonomy Mode**: Now supports end-to-end autonomous deployment with Railway preview testing, production testing, and batched backlog updates.

---

## Core Philosophy: True Autonomy

The `/ai-run-deep` command should run until **ALL work is deployed, merged, and tested**. This means:

1. **Don't stop at PR creation** - PRs are intermediate artifacts, not completion
2. **Test on Railway preview** - Every PR gets browser-tested on its preview deployment
3. **Merge only after preview passes** - No untested code reaches production
4. **Test production after merge** - Verify the merge didn't break anything
5. **Batch backlog updates** - Update DISCOVERY_BACKLOG.md ONCE at the end to avoid git conflicts

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FULL AUTONOMY LOOP                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│   │ Implement │ -> │ Create   │ -> │ Wait for │ -> │ Test on  │     │
│   │ Tickets   │    │ PR       │    │ Preview  │    │ Preview  │     │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│                                           │                          │
│                                           v                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│   │ Update   │ <- │ Test on  │ <- │ Merge    │ <- │ Pass?    │     │
│   │ Backlog  │    │ Prod     │    │ to Main  │    │ Y/N      │     │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│        │                                                             │
│        v                                                             │
│   COMPLETE (all tickets deployed, tested, backlog updated)          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Arguments

Parse from $ARGUMENTS:
- `agent`: Which agent to run (support, ops, code, growth, meta, finance, discovery, full, overnight)
- `task`: Optional - direct task description OR ticket ID (e.g., "add duplicate button" or "DISC-113")
- `--max`: Optional max iterations override
- `--track`: Create a DISC ticket for tracking (when using direct task)
- `--urgent`: Priority tier 1 (founder-urgent)
- `--skip-empty`: Skip agents with empty queues (default for full/overnight)

### Escape Hatches (reduce automation when needed):
- `--pr-only`: Stop after PR creation, skip testing/merging (for manual review)
- `--no-bundle`: Force separate PRs per ticket (disable auto-bundling)
- `--skip-prod-test`: Skip production testing after merge (minor changes only)

### Extended Runtime Flags (DISC-156):
- `--infinite`: Disable iteration limits, run until work complete or critical failure
- `--resume`: Resume from latest checkpoint file
- `--resume=FILE`: Resume from specific checkpoint file
- `--checkpoint-interval=HOURS`: Override default checkpoint interval (default: 8 for normal, 4 for infinite)

**Note**: Full autonomy (test preview → merge → test production → update backlog) is the DEFAULT. Bundling is AUTOMATIC when sensible. Use escape hatches only when you need less automation.

## Usage Examples

```bash
# === DIRECT TASK EXECUTION (Founder Fast Path) ===
/ai-run-deep code "add duplicate quote button"     # Full cycle: implement → test → merge → verify
/ai-run-deep code "fix login bug" --urgent         # Highest priority, full cycle
/ai-run-deep code "add dark mode" --track          # Creates DISC-XXX, full cycle

# === TICKET TARGETING ===
/ai-run-deep code DISC-113                         # Full cycle for specific ticket
/ai-run-deep code DISC-113,DISC-114,DISC-115       # Auto-bundles into 1-2 PRs, full cycle

# === STANDARD AGENT RUNS (Full Autonomy is Default) ===
/ai-run-deep code                                  # Process READY queue → test → merge → verify all
/ai-run-deep code --max=5                          # Custom iteration limit, still full cycle
/ai-run-deep full                                  # All agents with full deployment testing

# === OTHER AGENTS ===
/ai-run-deep support                               # Clear support inbox
/ai-run-deep ops                                   # Health check
/ai-run-deep discovery                             # Find new opportunities
/ai-run-deep growth                                # Process content queue

# === ESCAPE HATCHES (when you need less automation) ===
/ai-run-deep code --pr-only                        # Just create PRs, don't test/merge (manual review)
/ai-run-deep code DISC-113 --no-bundle             # Force separate PR even if bundling makes sense
/ai-run-deep code --skip-prod-test                 # Skip production testing (minor changes)

# === FULL COMPANY RUNS ===
/ai-run-deep full --no-skip                        # Force run all agents regardless of queue
/ai-run-deep overnight                             # Extended overnight run

# === EXTENDED RUNTIME (DISC-156) ===
/ai-run-deep code --infinite                       # Run until work complete (no iteration limit)
/ai-run-deep code --resume                         # Resume from latest checkpoint
/ai-run-deep overnight --infinite                  # Full overnight with infinite runtime
```

## Priority Tiers (Code Agent)

When processing work, Code Agent follows this priority order:

| Tier | Source | Description |
|------|--------|-------------|
| **1 - FOUNDER** | Direct command with `--urgent` | Eddie said do it NOW |
| **2 - FOUNDER** | Direct command (no flag) | Eddie initiated, high priority |
| **3 - URGENT** | Tickets tagged `urgent` or `bug` | Production issues |
| **4 - READY-HIGH** | READY tickets with `HIGH` impact | High-value features |
| **5 - READY** | Standard READY tickets | Normal queue |
| **6 - BACKLOG** | Lower priority items | When queue is empty |

## Completion Promises (from Constitution Article IX)

| Agent | Completion Promise | Default Max | Work-Based Override |
|-------|-------------------|-------------|---------------------|
| support | `INBOX PROCESSED AND ESCALATIONS HANDLED` | 5 | Until inbox empty |
| ops | `HEALTH GREEN AND INCIDENTS RESOLVED` | 10 | Until health green |
| code | `CODE QUEUE DEPLOYED AND PRODUCTION VERIFIED` | 10 | Until READY queue empty |
| code (--pr-only) | `CODE QUEUE EMPTY AND PRS CREATED` | 3 | Until READY queue empty |
| growth | `CONTENT QUEUE PROCESSED` | 5 | Until content queue empty |
| meta | `WEEKLY ANALYSIS COMPLETE` | 2 | Fixed (weekly cadence) |
| finance | `FINANCIAL SYNC COMPLETE` | 3 | Fixed (deterministic) |
| discovery | `DISCOVERY CYCLE COMPLETE` | 3 | Fixed (bounded exploration) |

**Note**: Code agent default is full autonomy (10 iterations) to allow for preview testing, merging, and production verification. Use `--pr-only` for faster runs that just create PRs.

---

## Work-Based Stop Conditions (DISC-156)

> **Philosophy**: The system should stop when done, not when tired. Boris Chernney's Claude Code ran for days - ours should too.

### Stop Condition Hierarchy

**OLD (Iteration-Based)**:
```
Stop when: iteration >= MAX_ITERATIONS
Problem: May stop with work remaining
```

**NEW (Work-Based)**:
```
Stop when: work is genuinely complete OR critical failure OR human interrupt
Continue while: work remains AND no critical failures
```

### Work-Based Logic

```python
def should_continue(agent, current_iteration):
    # ALWAYS STOP if:
    if emergency_stop_file_exists():
        return False, "EMERGENCY_STOP"
    if critical_failure_detected():
        return False, "CRITICAL_FAILURE"
    if daily_budget_exceeded():  # $50/day limit
        return False, "BUDGET_EXCEEDED"

    # WORK-BASED CHECKS by agent:
    if agent == "code":
        ready_queue = count_ready_tickets()
        open_prs = count_open_prs()
        if ready_queue == 0 and open_prs == 0:
            return False, "WORK_COMPLETE"
        return True, f"{ready_queue} tickets, {open_prs} PRs remaining"

    if agent == "support":
        inbox_count = count_inbox_items()
        if inbox_count == 0:
            return False, "INBOX_EMPTY"
        return True, f"{inbox_count} items in inbox"

    if agent == "ops":
        health_status = check_production_health()
        if health_status == "GREEN":
            return False, "HEALTH_GREEN"
        return True, f"Health: {health_status}"

    # FALLBACK to iteration limit for bounded agents:
    if current_iteration >= MAX_ITERATIONS[agent]:
        return False, "MAX_ITERATIONS"

    return True, "Continuing"
```

### Discovery Fallback

When the code agent's READY queue is empty:

```markdown
## Empty Queue Handling

IF ready_queue == 0 AND open_prs == 0:
    1. Check when discovery last ran
    2. IF discovery ran < 1 hour ago:
       - Work is genuinely complete
       - Output completion promise
    3. IF discovery ran >= 1 hour ago:
       - Run discovery agent first
       - Check if new tickets were created
       - IF new tickets: Continue processing
       - IF no new tickets: Work complete
```

This prevents the system from stopping when there might be discoverable work.

### Long-Run Checkpointing

For runs exceeding 8 hours:

```markdown
## Checkpoint Protocol

CHECKPOINT TRIGGER: Running > 8 hours continuously

CHECKPOINT ACTIONS:
1. Save full state to `.ai-company/state/CHECKPOINT-{timestamp}.md`
2. Include:
   - Current phase and progress
   - Tickets completed this run
   - Tickets remaining
   - Open PRs and their status
   - Quality evaluation scores
   - Any blockers or issues
3. Log checkpoint event
4. Continue running (checkpoint is a save, not a stop)

RESUME CAPABILITY:
/ai-run-deep code --resume

This reads the latest checkpoint and continues from that state.
```

### Checkpoint File Format

```markdown
# AI Civilization Checkpoint - {timestamp}

## Run Metadata
- Started: {original start time}
- Checkpoint Time: {now}
- Duration: {hours:minutes}
- Agent: {agent name}
- Mode: {full-autonomy/pr-only/etc}

## Progress Summary
- Tickets Completed: {N}
- Tickets Remaining: {M}
- PRs Created: {list}
- PRs Merged: {list}
- Quality Scores: {avg}

## Current State
- Active Ticket: DISC-XXX
- Active Phase: {IMPLEMENTATION/PREVIEW/QUALITY/MERGE/PRODUCTION}
- Last Action: {description}

## Work Queue (Remaining)
1. DISC-YYY: {title} - {status}
2. DISC-ZZZ: {title} - {status}

## To Resume
1. Read this checkpoint
2. Continue from Active Phase
3. Process remaining work queue

## Files Modified Since Checkpoint
{list of files touched}
```

### Resume Command

```bash
# Resume from latest checkpoint
/ai-run-deep code --resume

# Resume from specific checkpoint
/ai-run-deep code --resume=CHECKPOINT-20260105-143022.md
```

Resume logic:
1. Find latest (or specified) checkpoint file
2. Load state: current ticket, phase, remaining queue
3. Skip already-completed work
4. Continue from interrupted point

### Stop Condition Summary

| Condition | Action | Can Resume? |
|-----------|--------|-------------|
| Work complete | Output promise, stop gracefully | N/A (done) |
| EMERGENCY_STOP | Stop immediately | Yes, after stop cleared |
| Critical failure | Stop, alert founder | Yes, after fix |
| Budget exceeded | Stop, wait for reset | Yes, next day |
| Checkpoint (8hr) | Save state, continue | N/A (doesn't stop) |
| Human interrupt | Stop, save state | Yes |

### Infinite Runtime Mode

For overnight/weekend runs with `--infinite`:

```bash
/ai-run-deep code --infinite
```

This mode:
1. Disables iteration limits entirely
2. Runs until work complete OR critical failure OR human stop
3. Checkpoints every 4 hours (instead of 8)
4. Sends status update emails every 8 hours (if configured)
5. Automatically runs discovery when queue empty
6. Only stops for: EMERGENCY_STOP, budget, or genuine completion

**Constitutional Override**: Even in infinite mode, the $50/day budget limit applies. This prevents runaway costs.

---

## Instructions

### Step 0: Session Initialization

**BEFORE any work, load session context and check system state.**

#### 0.0 Load Baton Pass

Read `BATON_PASS.md` for accumulated wisdom:

```bash
# Read the full baton pass document
cat BATON_PASS.md

# Key sections to absorb:
# - "Context for Next Session" → What was the last session working on?
# - "Known Gotchas" → What to avoid?
# - "Eddie's Preferences" → What matters most?
# - "Warnings for Next Session" → Any blockers?
```

**Why This Matters**: The baton pass contains hard-won lessons from previous sessions. Not reading it means potentially repeating mistakes or missing context.

#### 0.1 Handle Existing Open PRs (Priority)

**BEFORE processing any new work, check for and handle existing open PRs.**

```bash
# Check for open PRs from previous runs
OPEN_PRS=$(gh pr list --state open --json number,title,headRefName --jq '.[] | "\(.number)|\(.title)|\(.headRefName)"')

if [ -n "$OPEN_PRS" ]; then
  echo "Found open PRs from previous runs - these take priority"
fi
```

#### 0.1 PR_PENDING Priority Queue

Open PRs represent work that's 90% done - just needs testing and merging. Process these FIRST:

1. **List open PRs**: `gh pr list --state open`
2. **For each open PR**:
   - Get preview URL from Railway
   - Wait for preview deployment
   - Run Playwright tests
   - If tests PASS → Merge PR
   - If tests FAIL → Fix on branch, push, retry (up to 3x)
3. **After all PRs handled** → Continue to new work

#### 0.2 Backlog Sync

Check DISCOVERY_BACKLOG.md for `PR_PENDING` status tickets:

```bash
grep "PR_PENDING" DISCOVERY_BACKLOG.md
```

These tickets have open PRs and should be processed before READY tickets.

**Priority Order**:
1. PR_PENDING tickets (existing PRs needing test/merge)
2. READY tickets (new implementation work)

#### 0.5 Learning Memory Maintenance

**Weekly maintenance prevents bloat and keeps patterns relevant.**

```bash
# Read maintenance metadata from LEARNING_MEMORY.md
LAST_MAINTENANCE=$(grep "last_maintenance:" LEARNING_MEMORY.md | cut -d: -f2 | xargs)
NEXT_DUE=$(grep "next_maintenance_due:" LEARNING_MEMORY.md | cut -d: -f2 | xargs)
TODAY=$(date +%Y-%m-%d)

# Check if maintenance is due (7+ days since last)
if [[ "$TODAY" > "$NEXT_DUE" ]] || [[ "$TODAY" == "$NEXT_DUE" ]]; then
  echo "Learning memory maintenance due - running cleanup"
  MAINTENANCE_REQUIRED=true
else
  echo "Learning memory maintenance not due until $NEXT_DUE"
  MAINTENANCE_REQUIRED=false
fi
```

**IF MAINTENANCE_REQUIRED:**

1. **Decay Pattern Scores**:
   - For each pattern in "Successful Patterns" sections:
     - Subtract 1 from Score column
     - If Score <= 0: Move to LEARNING_ARCHIVE.md

2. **Enforce Section Limits**:
   ```
   | Section | Limit | Action if Exceeded |
   |---------|-------|-------------------|
   | Successful Patterns (per agent) | 15 | Archive lowest-scored |
   | Failed Patterns (per type) | 15 | Archive oldest |
   | Quality Evaluation History | 20 | Archive oldest |
   | Session Outcomes | 30 | Archive oldest |
   ```

3. **Archive Process**:
   ```markdown
   # Move to LEARNING_ARCHIVE.md with format:
   | Archived Date | Original Date | Category | Pattern | Final Score | Reason |
   | {today} | {original_date} | {category} | {pattern} | {score} | Decay/Limit |
   ```

4. **Update Metadata**:
   ```yaml
   last_maintenance: {today}
   next_maintenance_due: {today + 7 days}
   total_entries: {count}
   archive_count: {count}
   ```

5. **Reset Quality Dimension Counters** (if 30+ days old):
   - Reset "Fail Count (30 days)" to 0 for all dimensions
   - Clear "Last Failed" dates older than 30 days

**WHY THIS MATTERS**: Without maintenance, LEARNING_MEMORY.md grows unbounded. Decay scoring ensures only relevant patterns remain active while preserving historical data in the archive.

---

### Step 1: Parse Arguments

```
$ARGUMENTS parsing:
- First word = agent name
- If second word exists and doesn't start with "--":
  - If matches DISC-XXX pattern → ticket targeting mode
  - Else → direct task mode (treat as task description)
- Parse flags: --max=N, --track, --urgent, --skip-empty, --no-skip
```

### Step 2: Check Emergency Stop

```bash
if [ -f ".ai-company/EMERGENCY_STOP" ]; then
  echo "EMERGENCY STOP active. Run /ai-status for details."
  exit 0
fi
```

### Step 3: Route by Mode

#### Mode A: Direct Task Execution

When a task description is provided (e.g., `/ai-run-deep code "add duplicate button"`):

1. **Create ephemeral task** (or DISC ticket if `--track`):
   ```markdown
   # Ephemeral Task (Founder-Initiated)

   **Created**: {timestamp}
   **Priority**: FOUNDER {1 if --urgent, else 2}
   **Description**: {task description}
   **Track**: {DISC-XXX if --track, else "ephemeral"}
   ```

2. **If --track flag**, add to DISCOVERY_BACKLOG.md:
   ```markdown
   ### DISC-{next}: {task description}
   **Status**: READY
   **Source**: Founder Direct (/ai-run-deep)
   **Priority**: FOUNDER
   ```

3. **Build Code Agent prompt with this task as ONLY focus**:
   ```markdown
   ## FOUNDER DIRECTIVE (Priority 1)

   Eddie has directly requested this task. Implement immediately.

   **Task**: {description}
   **Tracking**: {DISC-XXX or ephemeral}

   Do NOT process other queue items. Focus solely on this task.
   When complete, output: <promise>FOUNDER TASK COMPLETE</promise>
   ```

4. **Execute via Ralph loop** (max 5 iterations for founder tasks)

#### Mode B: Ticket Targeting

When DISC-XXX pattern detected (e.g., `/ai-run-deep code DISC-113`):

1. **Read ticket(s) from DISCOVERY_BACKLOG.md**
2. **Validate ticket exists and is READY** (or force if founder command)
3. **Build Code Agent prompt with specific ticket(s)**:
   ```markdown
   ## TARGETED TICKETS

   Implement these specific tickets in order:

   1. DISC-113: {title}
      {full ticket content}

   Do NOT process other queue items.
   When all targeted tickets complete: <promise>TARGETED WORK COMPLETE</promise>
   ```

4. **Execute via Ralph loop**

#### Mode C: Standard Queue Processing

When no task/ticket specified (e.g., `/ai-run-deep code`):

1. **Read agent state and queue**
2. **Apply priority sorting** (see Priority Tiers above)
3. **Build standard agent prompt**
4. **Execute via Ralph loop**

### Step 4: Smart Queue Skip (Full/Overnight Mode)

For `/ai-run-deep full` or `overnight`, check each agent's queue before running:

```markdown
## Pre-Run Queue Check

| Agent | Queue Status | Action |
|-------|--------------|--------|
| ops | Always run | RUN (health is continuous) |
| support | Inbox: {count} | {RUN if >0, SKIP if 0} |
| finance | Last sync: {time} | {RUN if >24h, SKIP if recent} |
| discovery | Last run: {time} | {RUN if >7d, SKIP if recent} |
| code | READY queue: {count} | {RUN if >0, SKIP if 0} |
| growth | Content queue: {count} | {RUN if >0, SKIP if 0} |
| meta | Day: {weekday} | {RUN if Sunday, SKIP otherwise} |
```

**How to check queues:**

- **support**: Check Resend inbox count or `.ai-company/agents/support/state.md`
- **finance**: Check `Last Sync` timestamp in `.ai-company/agents/finance/state.md`
- **discovery**: Check `Last Run` in `.ai-company/agents/discovery/state.md`
- **code**: Count READY tickets in `DISCOVERY_BACKLOG.md`
- **growth**: Check `Content Queue` in `.ai-company/agents/growth/state.md`
- **meta**: Check if today is Sunday

**If `--no-skip`**: Run all agents regardless of queue status.

### Step 5: Full Company Mode Execution Order

```
/ai-run-deep full

Execution sequence:
1. ops (health baseline) - ALWAYS
2. support (clear inbox) - if inbox > 0
3. finance (sync metrics) - if last sync > 24h
4. discovery (find work) - if last run > 7 days
5. code (implement READY) - if READY queue > 0
6. growth (content) - if content queue > 0
7. meta (weekly review) - if Sunday

Between each agent:
- Check for EMERGENCY_STOP
- Log to .ai-company/state/deep-run-{timestamp}.md
- 30 second cooldown
```

### Step 6: Overnight Mode

For `/ai-run-deep overnight`:

1. **Extended limits**: Constitutional max * 2
2. **Force discovery**: Run even if recent
3. **Full logging**: `.ai-company/logs/overnight-{date}.md`
4. **Morning briefing**: Generate when complete
5. **Email summary**: Send to Eddie (if configured)

```
Overnight stops when:
1. All agents report complete (all promises output)
2. EMERGENCY_STOP triggered
3. Any agent exceeds doubled max iterations
4. Unrecoverable error occurs
```

### Step 7: Build Agent Prompt

For standard agent runs, construct:

```markdown
You are executing the Quoted {Agent} Agent in deep mode.

## Your Specification
[Contents of .ai-company/agents/{agent}/AGENT.md]

## Current State
[Contents of .ai-company/agents/{agent}/state.md]

## Current Iteration
[Contents of iteration.md or "iteration: 1"]

## Relevant Learnings (from LEARNING_MEMORY.md)
[Inject relevant sections based on agent type and current task]

### For Code Agent, include:
- Recent Quality Evaluation failures (avoid repeating)
- Successful patterns for similar ticket types
- Any failed patterns to avoid
- Eddie's relevant preferences

### For Other Agents, include:
- Agent-specific performance trends
- Recent failures in their domain
- Triggered improvement actions

## Priority Queue (Code Agent only)
[Sorted list of work items by priority tier]

## Constitutional Limits
- Max iterations: {MAX_ITERATIONS}
- Current iteration: {current}
- Emergency stop: Check `.ai-company/EMERGENCY_STOP` before each action

## Your Task
Execute your responsibilities until complete. When genuinely finished:
1. Update your state.md with results
2. Log outcome to LEARNING_MEMORY.md (success/failure with context)
3. Output your completion promise: <promise>{COMPLETION_PROMISE}</promise>

If NOT complete after this iteration:
1. Update state.md with progress
2. Update iteration.md with current count
3. DO NOT output completion promise
4. The loop will continue automatically

## CRITICAL
- Only output <promise>...</promise> when work is GENUINELY complete
- False promises violate Constitution Article IX
- Iteration files track progress across context resets
- Always log outcomes to LEARNING_MEMORY.md for future learning
```

### Step 7.1: Learning Memory Injection

**Category-based retrieval ensures relevant patterns without context bloat.**

Before each agent run, extract relevant learnings using these rules:

#### Determine Ticket Category

First, classify the current ticket:

```
TICKET_CATEGORIES = {
  "Frontend/UX": keywords like "button", "modal", "CSS", "landing", "mobile", "UI"
  "Backend/API": keywords like "endpoint", "API", "database", "webhook", "server"
  "PDF/Formatting": keywords like "PDF", "quote", "invoice", "template", "format"
  "Auth/Billing": keywords like "login", "Stripe", "payment", "subscription", "auth"
  "Infrastructure/Meta": keywords like "deploy", "CI", "agent", "config", "system"
}

# Match ticket description to category
CURRENT_CATEGORY = best_match(ticket_description, TICKET_CATEGORIES)
CURRENT_AGENT = agent_type  # code, discovery, ops, etc.
```

#### Score-Based Retrieval

```
RETRIEVAL RULES (from LEARNING_MEMORY.md):

1. HIGH_VALUE patterns (Score >= 7):
   → ALWAYS inject regardless of category

2. MEDIUM_VALUE patterns (Score 4-6):
   → Inject ONLY IF:
     - Pattern is from same agent type (e.g., Code Agent patterns for code work), OR
     - Pattern is from same ticket category (e.g., PDF patterns for PDF ticket)

3. LOW_VALUE patterns (Score 1-3):
   → Inject ONLY IF:
     - Pattern directly mentions current ticket ID, OR
     - Pattern description contains exact keyword match to ticket

4. ARCHIVED patterns (Score 0):
   → NEVER inject (these are in LEARNING_ARCHIVE.md)
```

#### What to Extract

```bash
# From LEARNING_MEMORY.md, extract:

## ALWAYS INJECT (regardless of score):
- "Eddie's Preferences (Inferred)" table → All rows marked "Always Inject: Yes"
- "Quality Dimension Failures" → Any dimension with Fail Count >= 2
- Last 3 entries from "Quality Evaluation History"

## CATEGORY-FILTERED:
- "Successful Patterns > By Agent Type > {CURRENT_AGENT}" → Score >= 4 patterns
- "Successful Patterns > By Ticket Category > {CURRENT_CATEGORY}" → Score >= 4 patterns
- "Failed Patterns > By Failure Type" → Any with Repeat Count >= 2

## CONTEXT LIMIT:
- Max 10 patterns total (prioritize by score, then recency)
- Max 500 tokens for injection block
```

#### Injection Format

```markdown
RELEVANT_LEARNINGS=$(cat <<'EOF'
### ALWAYS APPLY (Eddie's Preferences)
- Mobile-first design (test at 375px)
- Safe DOM manipulation (createElement, not innerHTML)
- Avoid over-engineering - only make requested changes
- Lean, maintainable systems

### QUALITY WARNINGS (Recent Issues)
{If any dimension has Fail Count >= 2}
- ⚠️ {Dimension}: Failed {N} times recently. Pay extra attention.

### PATTERNS TO FOLLOW (Score {N}/10)
{From matching agent + category, highest scored first}
- {Pattern}: {Why it worked}

### PATTERNS TO AVOID (Repeat Count: {N})
{From failed patterns with repeat count >= 2}
- {Failure}: {Lesson learned}

### RECENT EVALUATIONS (Context)
{Last 3 quality evaluations, summarized}
- DISC-XXX: {score}/25 - {key takeaway}
EOF
)
```

#### Why Category-Based Retrieval Matters

| Old Approach | New Approach |
|--------------|--------------|
| Read everything | Filter by relevance |
| All patterns injected | Only Score >= 4 for category |
| Context bloat over time | Max 10 patterns, 500 tokens |
| No decay | Weekly decay keeps fresh |

This creates a focused feedback loop where relevant past performance influences future behavior without overwhelming context.

### Step 8: Invoke Ralph Wiggum Loop

```
/ralph-wiggum:ralph-loop
```

The loop will:
1. Execute the agent prompt
2. Check for completion promise in output
3. If found: Stop loop, report success
4. If not found: Continue next iteration
5. If max iterations reached: Stop loop, escalate

### Step 8.5: VERIFY SPEC COMPLIANCE (CRITICAL)

**After EVERY agent run, verify the agent actually followed its spec.**

Run these checks based on agent type:

#### Discovery Agent Verification
```bash
# 1. Check DISCOVERY_BACKLOG.md was modified
git diff HEAD~1 DISCOVERY_BACKLOG.md | head -20

# 2. If state.md shows "New Discoveries: N" but backlog unchanged → FAIL
grep "New Discoveries" .ai-company/agents/discovery/state.md
git diff HEAD~1 DISCOVERY_BACKLOG.md | wc -l
```

**FAILURE MODE**: If state.md shows discoveries were found but DISCOVERY_BACKLOG.md wasn't updated, the discovery agent violated its spec. DO NOT accept completion promise. Force another iteration with explicit instruction to write to backlog.

#### Code Agent Verification
```bash
# 1. Check PRs were created for completed work
gh pr list --state open --author "@me"

# 2. If tickets marked COMPLETE, PRs should exist
grep "COMPLETE" DISCOVERY_BACKLOG.md

# 3. Verify tests pass
pytest -x --tb=short 2>/dev/null || echo "No pytest"
```

**FAILURE MODE**: If tickets marked COMPLETE but no PR exists, or tests failing, don't accept completion promise.

#### Ops Agent Verification
```bash
# 1. Health endpoint returns 200
curl -s https://quoted.it.com/health | jq .status

# 2. Check for unacknowledged errors in logs
railway logs -n 50 | grep -i error | head -5
```

**FAILURE MODE**: If health is not GREEN but agent claimed completion, don't accept.

#### Full Run Verification
After all agents complete, run final verification:
```bash
# 1. Production is healthy
curl -s https://quoted.it.com/health

# 2. All open PRs are reviewed/merged or have clear status
gh pr list --state open

# 3. State files are in sync with reality
cat .ai-company/agents/*/state.md | grep -E "(Status|Last Run)"
```

**IF VERIFICATION FAILS**: Do NOT report success. Instead:
1. Log the verification failure
2. Force another agent iteration with explicit fix instruction
3. Or escalate to founder if max iterations reached

### Step 9: Railway Preview Testing (v2.0)

**CRITICAL**: PRs are NOT complete until tested on Railway preview deployment.

#### 9.1 Get Preview URL

After PR creation, Railway automatically creates a preview deployment. Get the URL:

```bash
# Get PR preview URL from Railway
PR_NUMBER=$(gh pr view --json number -q .number)
PREVIEW_URL=$(railway status --json | jq -r '.environments[] | select(.name | contains("pr-'$PR_NUMBER'")) | .url')

# Or construct from convention: pr-{number}-quoted-it.up.railway.app
PREVIEW_URL="https://pr-${PR_NUMBER}-quoted-it.up.railway.app"

# Wait for deployment to be ready (up to 5 minutes)
for i in {1..30}; do
  if curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL/health" | grep -q "200"; then
    echo "Preview ready at $PREVIEW_URL"
    break
  fi
  echo "Waiting for preview deployment... ($i/30)"
  sleep 10
done
```

#### 9.2 Run Playwright Tests on Preview

Use Playwright browser automation to test the preview deployment:

```markdown
## Preview Test Suite

For each PR, run these tests on the preview URL:

### Authentication Flow
1. Navigate to {PREVIEW_URL}
2. Click "Get Started" button
3. Enter test email (use disposable: test+{timestamp}@quoted.it.com)
4. Verify magic link is sent (check Resend logs or use webhook)
5. Complete auth flow
6. Verify dashboard loads

### Core Feature Tests
1. **Quote Creation**:
   - Click "New Quote"
   - Enter voice input (or text fallback)
   - Verify quote generates
   - Verify PDF downloads

2. **Settings**:
   - Navigate to Settings
   - Verify logo upload works
   - Verify profile save works

3. **Feature-Specific Tests**:
   - Test whatever feature the PR implements
   - E.g., if DISC-134 (Social Login), test Google OAuth button

### Smoke Test (Minimum)
1. Landing page loads (200 OK)
2. Health endpoint returns healthy
3. Can reach auth page
4. JavaScript console has no errors
```

#### 9.3 Playwright Integration

Use the MCP Playwright tools for browser testing:

```javascript
// Example: Test quote creation flow
await mcp__plugin_playwright_playwright__browser_navigate({ url: PREVIEW_URL });
await mcp__plugin_playwright_playwright__browser_snapshot({});
// Look for "Get Started" button in snapshot
await mcp__plugin_playwright_playwright__browser_click({ element: "Get Started button", ref: "..." });
// Continue through flow...
```

**Test Results Logging**:
```markdown
## Preview Test Results - PR #{number}

| Test | Status | Notes |
|------|--------|-------|
| Landing loads | ✅ PASS | 200 OK in 1.2s |
| Health check | ✅ PASS | All services healthy |
| Auth flow | ✅ PASS | Magic link sent |
| Quote creation | ✅ PASS | PDF generated |
| Feature: {specific} | ✅ PASS | Working as expected |

**Overall**: PASS - Ready for merge
```

#### 9.4 Preview Test Failure Handling

If ANY preview test fails:
1. DO NOT merge the PR
2. Log the failure with screenshots
3. Create fix commit on the same branch
4. Push and wait for new preview deployment
5. Re-run preview tests
6. Repeat until all tests pass OR max iterations reached

### Step 9.5: Quality Evaluation (LLM-as-Judge)

**CRITICAL**: Before merge, evaluate implementation quality. This catches architectural mistakes that pass functional tests.

#### 9.5.1 Quality Rubric

Score each dimension 1-5:

```markdown
## QUALITY EVALUATION - PR #{number}

### 1. COMPLETENESS (1-5)
Does it fully address the ticket requirements?
- 5: All requirements met, edge cases handled
- 4: Core requirements met, minor gaps
- 3: Most requirements met, some gaps
- 2: Partial implementation, significant gaps
- 1: Incomplete, major requirements missing

Score: __

### 2. CODE QUALITY (1-5)
Clean, readable, maintainable, follows conventions?
- 5: Excellent - could be a code example
- 4: Good - follows patterns, minor issues
- 3: Acceptable - works but could be cleaner
- 2: Below average - technical debt introduced
- 1: Poor - hard to read, doesn't follow conventions

Score: __

### 3. SCOPE DISCIPLINE (1-5)
Stayed focused or over-engineered?
- 5: Perfect scope - only what was needed
- 4: Minimal scope creep, justified additions
- 3: Some unnecessary additions
- 2: Significant over-engineering
- 1: Massive scope creep, unrelated changes

Score: __

### 4. EDGE CASES (1-5)
Error states and boundaries handled?
- 5: All edge cases considered and handled
- 4: Most edge cases handled
- 3: Common edge cases handled
- 2: Some edge cases missed
- 1: Edge cases ignored

Score: __

### 5. TESTING (1-5)
Right things tested at right level?
- 5: Comprehensive, appropriate test coverage
- 4: Good coverage, minor gaps
- 3: Basic happy path tested
- 2: Minimal testing
- 1: No tests or broken tests

Score: __

---
**TOTAL**: __/25
**THRESHOLD**: 18/25 minimum to proceed
**VERDICT**: PASS/FAIL
```

#### 9.5.2 Evaluation Process

```markdown
BEFORE merging any PR:

1. READ the full diff: `gh pr diff {number}`
2. REVIEW against the ticket requirements
3. SCORE each dimension honestly (be critical, not generous)
4. IF total >= 18: Proceed to merge
5. IF total < 18: Return to implementation with specific feedback

SCORING NOTES:
- Be honest, not optimistic. Underscoring is better than overscoring.
- A "3" is acceptable, not a failure. 4-5 are for genuinely good work.
- Score what IS, not what you intended.
```

#### 9.5.3 Quality Failure Handling

If score < 18:

```markdown
## Quality Evaluation Failed - PR #{number}

**Total Score**: {score}/25 (below 18 threshold)
**Weakest Dimension**: {dimension with lowest score}

### Specific Issues:
1. {Issue 1 with line reference}
2. {Issue 2 with line reference}
...

### Required Improvements:
1. {What must change to pass}
2. {What must change to pass}
...

### Action:
1. Do NOT merge
2. Return to IMPLEMENTATION phase
3. Fix the specific issues above
4. Push new commits to same branch
5. Re-run preview tests
6. Re-evaluate quality
7. Retry counter: {N}/3 (max 3 attempts per ticket)

If retry counter = 3 and still failing:
- Mark ticket as BLOCKED
- Escalate to founder with quality analysis
- Continue with other tickets
```

#### 9.5.4 Quality Logging

Log ALL evaluations to `LEARNING_MEMORY.md` (created in Phase 2):

```markdown
## [YYYY-MM-DD] DISC-XXX Quality Evaluation

| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness | X | {brief note} |
| Code Quality | X | {brief note} |
| Scope Discipline | X | {brief note} |
| Edge Cases | X | {brief note} |
| Testing | X | {brief note} |
| **TOTAL** | **X/25** | **{PASS/FAIL}** |

{If failed: What was the issue? What was the fix?}
```

This creates a dataset for the meta-agent to analyze patterns.

---

### Step 10: Merge to Production

Only after preview tests pass AND quality evaluation passes (>= 18/25):

```bash
# Merge the PR
gh pr merge $PR_NUMBER --squash --delete-branch

# Wait for production deployment (Railway auto-deploys main)
echo "Waiting for production deployment..."
for i in {1..30}; do
  DEPLOY_STATUS=$(railway status --json | jq -r '.deployments[0].status')
  if [ "$DEPLOY_STATUS" = "SUCCESS" ]; then
    echo "Production deployment complete"
    break
  fi
  echo "Deploying... ($i/30)"
  sleep 10
done
```

### Step 11: Production Testing (v2.0)

**CRITICAL**: After merge, verify production is healthy.

#### 11.1 Production Smoke Test

```bash
PROD_URL="https://quoted.it.com"

# 1. Health check
curl -s "$PROD_URL/health" | jq .

# 2. Landing page
curl -s -o /dev/null -w "%{http_code}" "$PROD_URL"

# 3. API status
curl -s "$PROD_URL/api/status" | jq .
```

#### 11.2 Production Browser Tests

Run the same Playwright test suite on production:

```markdown
## Production Test Suite

1. Navigate to https://quoted.it.com
2. Verify landing page loads correctly
3. Test auth flow (use test account or create new)
4. Verify feature from merged PR works
5. Check console for errors
6. Verify PostHog events are firing
```

#### 11.3 Production Test Failure Handling

If production tests fail after merge:
1. **CRITICAL**: This is a production incident
2. Check if rollback is needed (feature flag disable or revert commit)
3. Log the incident in `.ai-company/incidents/`
4. Create hotfix ticket if needed
5. Alert founder via escalation

### Step 12: Automatic PR Bundling (v2.0)

Bundling is **AUTOMATIC** when it makes sense. Use `--no-bundle` to disable.

#### 12.1 When to Auto-Bundle

The orchestrator automatically bundles tickets when:

```markdown
## Auto-Bundle Triggers

1. **Multiple tickets in same run**
   - Processing 2+ tickets from READY queue → consider bundling

2. **Same-area tickets** (highest priority for bundling):
   - Multiple frontend-only changes → bundle into 1 PR
   - Multiple backend-only changes → bundle into 1 PR
   - Mixed frontend+backend → separate PRs (safer)

3. **Related functionality**:
   - Tickets that touch same files → bundle
   - Tickets that depend on each other → bundle in order

4. **Explicit targeting**:
   - `/ai-run-deep code DISC-113,DISC-114` → always bundles these together
```

#### 12.2 Bundle Rules

```markdown
## Bundle Limits

1. **Max 3 tickets per PR** (keeps reviews manageable)
2. **Max 500 lines changed per PR** (larger = split)
3. **Never bundle across unrelated domains** (auth + PDF = separate)

## Bundle Naming
- Branch: `quoted-run/bundle-{timestamp}`
- PR Title: "Bundle: DISC-XXX, DISC-YYY, DISC-ZZZ"
- Each ticket gets its own commit within the bundle
```

#### 12.2 Bundle Implementation

```bash
# Create bundle branch
git checkout -b quoted-run/bundle-$(date +%s) main

# Implement all tickets on same branch
# ... code changes for DISC-113 ...
git add . && git commit -m "feat(DISC-113): {description}"

# ... code changes for DISC-114 ...
git add . && git commit -m "feat(DISC-114): {description}"

# Create single PR for bundle
gh pr create --title "Bundle: DISC-113, DISC-114" --body "..."
```

#### 12.3 Bundle Testing

Each ticket in bundle must be individually testable:
1. Test each feature separately on preview
2. Test features don't conflict
3. Only merge if ALL features pass

### Step 13: Batched Backlog Updates (v2.0)

**CRITICAL**: To avoid git conflicts when running parallel agents, update DISCOVERY_BACKLOG.md only ONCE at the end.

#### 13.1 Track Completed Work In-Memory

During the run, track completed tickets in state file only:

```markdown
## .ai-company/state/run-{timestamp}.md

### Completed Tickets (Pending Backlog Update)
| Ticket | PR # | Status | Merged |
|--------|------|--------|--------|
| DISC-113 | #45 | TESTED | ✅ |
| DISC-114 | #45 | TESTED | ✅ |
| DISC-115 | #46 | TESTED | ✅ |
```

#### 13.2 Batch Update at End

Only after ALL work is merged and tested:

```markdown
## Backlog Update Script

1. Read run state file
2. For each completed ticket:
   - Change status from READY → DEPLOYED
3. Update summary counts
4. Move DEPLOYED tickets to DISCOVERY_ARCHIVE.md
5. Single commit: "chore: Batch backlog update - DISC-113, 114, 115 deployed"
```

#### 13.3 Why Batched Updates

Previous failure mode:
- 4 parallel agents each try to update DISCOVERY_BACKLOG.md
- Git conflicts on every push
- Agents get stuck in conflict resolution loops

New approach:
- Agents write to their own state files (no conflicts)
- Single backlog update at orchestration end
- Clean git history

### Step 14: Full Autonomy Execution Flow (v2.0)

This is the **DEFAULT** behavior for all code agent runs. Use `--pr-only` to disable.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FULL AUTONOMY ORCHESTRATION FLOW (v3.0)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PHASE 1: IMPLEMENTATION                                                     │
│  ├── Read READY queue from DISCOVERY_BACKLOG.md                             │
│  ├── Inject relevant learnings from LEARNING_MEMORY.md                      │
│  ├── For each ticket (or bundle if --bundle):                               │
│  │   ├── Create feature branch                                              │
│  │   ├── Implement the feature                                              │
│  │   ├── Run local tests (pytest)                                           │
│  │   ├── Create PR                                                          │
│  │   └── Record in run state file (NOT backlog yet)                         │
│  └── Continue until READY queue exhausted OR max iterations                 │
│                                                                              │
│  PHASE 2: PREVIEW TESTING                                                    │
│  ├── For each open PR:                                                       │
│  │   ├── Wait for Railway preview deployment                                │
│  │   ├── Run Playwright test suite on preview URL                           │
│  │   ├── If FAIL: Fix, push, re-test (up to 3 attempts)                     │
│  │   └── Record test results in run state file                              │
│  └── All PRs must pass preview tests before Phase 2.5                       │
│                                                                              │
│  PHASE 2.5: QUALITY EVALUATION (LLM-as-Judge) **NEW**                       │
│  ├── For each PR that passed preview tests:                                 │
│  │   ├── Read full diff: gh pr diff {number}                                │
│  │   ├── Score against rubric (Completeness, Code Quality, Scope,           │
│  │   │                         Edge Cases, Testing) - 1-5 each              │
│  │   ├── THRESHOLD: 18/25 minimum                                           │
│  │   ├── If score < 18: Return to IMPLEMENTATION with feedback              │
│  │   ├── Log evaluation to LEARNING_MEMORY.md                               │
│  │   └── Max 3 retry attempts per ticket                                    │
│  └── Only PRs scoring ≥18/25 proceed to Phase 3                             │
│                                                                              │
│  PHASE 3: MERGE                                                              │
│  ├── For each PR that passed quality evaluation:                            │
│  │   ├── Merge to main (squash)                                             │
│  │   ├── Wait for production deployment                                     │
│  │   └── Record merge in run state file                                     │
│  └── All PRs merged sequentially                                            │
│                                                                              │
│  PHASE 4: PRODUCTION TESTING                                                 │
│  ├── Wait for all deploys to complete                                       │
│  ├── Run Playwright test suite on production                                │
│  ├── Verify all features work                                               │
│  ├── If FAIL: Create rollback/hotfix ticket, escalate                       │
│  ├── Record production test results                                         │
│  └── Log outcome (success/rollback) to LEARNING_MEMORY.md                   │
│                                                                              │
│  PHASE 5: FINALIZATION                                                       │
│  ├── Batch update DISCOVERY_BACKLOG.md:                                     │
│  │   ├── Change all completed tickets: READY → DEPLOYED                     │
│  │   ├── Update summary counts                                              │
│  │   └── Single commit                                                      │
│  ├── Move DEPLOYED tickets to DISCOVERY_ARCHIVE.md                          │
│  ├── Update BATON_PASS.md with session learnings                            │
│  ├── Update agent state file with final results                             │
│  └── Output completion promise                                              │
│                                                                              │
│  COMPLETION PROMISE (Full Autonomy):                                         │
│  <promise>CODE QUEUE DEPLOYED AND PRODUCTION VERIFIED</promise>             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Failure Modes & Recovery

| Phase | Failure | Recovery |
|-------|---------|----------|
| Implementation | Tests fail | Fix code, retry up to 3x |
| Implementation | Can't implement | Mark ticket BLOCKED, continue others |
| Preview Test | Feature broken | Fix on branch, push, re-test |
| Preview Test | 3 attempts fail | Skip ticket, escalate to founder |
| Quality Eval | Score < 18/25 | Return to implementation with specific feedback |
| Quality Eval | 3 retries fail | Mark BLOCKED, escalate with quality analysis |
| Quality Eval | Pattern detected | Log to LEARNING_MEMORY.md for meta-agent analysis |
| Merge | Conflict | Rebase, resolve, retry |
| Production Test | Feature broken | Rollback via feature flag or revert |
| Production Test | Critical failure | EMERGENCY_STOP, alert founder |

#### Run State File Format

```markdown
# Deep Run State - {timestamp}

## Configuration
- Mode: full-autonomy
- Flags: --deploy --bundle
- Max Iterations: 10

## Phase Status
| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| Implementation | COMPLETE | 15:00 | 15:45 |
| Preview Testing | COMPLETE | 15:45 | 16:00 |
| Merge | COMPLETE | 16:00 | 16:10 |
| Production Testing | COMPLETE | 16:10 | 16:20 |
| Finalization | COMPLETE | 16:20 | 16:22 |

## Tickets Processed
| Ticket | PR # | Preview | Merged | Prod Test |
|--------|------|---------|--------|-----------|
| DISC-113 | #45 | ✅ | ✅ | ✅ |
| DISC-114 | #45 | ✅ | ✅ | ✅ |
| DISC-115 | #46 | ✅ | ✅ | ✅ |

## Final Status
- Tickets Completed: 3
- PRs Merged: 2
- Production Health: GREEN
- Backlog Updated: YES
```

### Step 15: Report Results

```
+==============================================================================+
|  AI CIVILIZATION - DEEP RUN COMPLETE                                          |
+==============================================================================+

Mode: {direct-task / ticket / queue / full / overnight}
Agent: {agent name}
Task: {description or "queue processing"}

Iterations: {count} / {max}
Result: {SUCCESS / ESCALATE / EMERGENCY_STOP}
Promise: {completion promise if output}

{If direct task with --track}
Ticket Created: DISC-{XXX}
Status: {COMPLETE / IN_PROGRESS}

{If code agent}
PRs Created: {list}
Tickets Completed: {list}
Remaining in Queue: {count}

{If code agent (Full Autonomy - Default)}
## Deployment Pipeline Results
| Phase | Status | Duration |
|-------|--------|----------|
| Implementation | ✅ COMPLETE | 45 min |
| Preview Testing | ✅ COMPLETE | 15 min |
| Merge | ✅ COMPLETE | 10 min |
| Production Testing | ✅ COMPLETE | 10 min |
| Finalization | ✅ COMPLETE | 2 min |

PRs Created: {list}
PRs Merged: {list}
Preview Tests: {passed}/{total}
Production Tests: {passed}/{total}
Tickets Deployed: {list}
Backlog Updated: YES (single batch commit)

{If full run}
| Agent | Status | Iterations | Notes |
|-------|--------|------------|-------|
| ops | COMPLETE | 1 | Health green |
| support | SKIPPED | 0 | Inbox empty |
| finance | COMPLETE | 2 | Synced $X MRR |
| discovery | COMPLETE | 1 | Found 3 opportunities |
| code | ESCALATE | 3 | 2/5 tickets done |
| growth | SKIPPED | 0 | Queue empty |
| meta | SKIPPED | 0 | Not Sunday |

+==============================================================================+
```

---

## Quick Reference

| You Want | Command |
|----------|---------|
| Add feature immediately | `/ai-run-deep code "description"` |
| Add feature with tracking | `/ai-run-deep code "description" --track` |
| Urgent fix | `/ai-run-deep code "fix X" --urgent` |
| Specific ticket | `/ai-run-deep code DISC-113` |
| Multiple tickets | `/ai-run-deep code DISC-113,DISC-114` |
| Process READY queue | `/ai-run-deep code` |
| Full company run | `/ai-run-deep full` |
| Overnight autonomous | `/ai-run-deep overnight` |
| Find new work | `/ai-run-deep discovery` |
| Emergency stop | `/ai-stop` |
| **Escape Hatches** | |
| PR only (skip test/merge) | `/ai-run-deep code --pr-only` |
| Force separate PRs | `/ai-run-deep code --no-bundle` |
| Skip production testing | `/ai-run-deep code --skip-prod-test` |
| **Extended Runtime (DISC-156)** | |
| Run until work complete | `/ai-run-deep code --infinite` |
| Resume from checkpoint | `/ai-run-deep code --resume` |
| Long overnight run | `/ai-run-deep overnight --infinite` |

---

## Emergency Stop

At any point:
- `/ai-stop` - Halt everything
- `touch .ai-company/EMERGENCY_STOP` - File-based halt
- `/ralph-wiggum:cancel-ralph` - Cancel current loop
