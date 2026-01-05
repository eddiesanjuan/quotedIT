# AI Civilization - Deep Agent Run (Ralph Wiggum Loop)

Execute an agent in a self-healing loop using Ralph Wiggum plugin. Supports direct task execution, ticket targeting, and smart queue management.

---

## Arguments

Parse from $ARGUMENTS:
- `agent`: Which agent to run (support, ops, code, growth, meta, finance, discovery, full, overnight)
- `task`: Optional - direct task description OR ticket ID (e.g., "add duplicate button" or "DISC-113")
- `--max`: Optional max iterations override
- `--track`: Create a DISC ticket for tracking (when using direct task)
- `--urgent`: Priority tier 1 (founder-urgent)
- `--skip-empty`: Skip agents with empty queues (default for full/overnight)

## Usage Examples

```bash
# === DIRECT TASK EXECUTION (Founder Fast Path) ===
/ai-run-deep code "add duplicate quote button"     # Immediate implementation
/ai-run-deep code "fix login bug" --urgent         # Highest priority
/ai-run-deep code "add dark mode" --track          # Creates DISC-XXX and implements

# === TICKET TARGETING ===
/ai-run-deep code DISC-113                         # Implement specific ticket
/ai-run-deep code DISC-113,DISC-114,DISC-115       # Multiple tickets

# === STANDARD AGENT RUNS ===
/ai-run-deep support                               # Clear support inbox
/ai-run-deep ops                                   # Health check
/ai-run-deep code                                  # Process READY queue by priority
/ai-run-deep code --max=5                          # Custom iteration limit
/ai-run-deep discovery                             # Find new opportunities
/ai-run-deep growth                                # Process content queue

# === FULL COMPANY RUNS ===
/ai-run-deep full                                  # All agents, smart skip
/ai-run-deep full --no-skip                        # Force run all agents
/ai-run-deep overnight                             # Extended overnight run
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

| Agent | Completion Promise | Max Iterations |
|-------|-------------------|----------------|
| support | `INBOX PROCESSED AND ESCALATIONS HANDLED` | 5 |
| ops | `HEALTH GREEN AND INCIDENTS RESOLVED` | 10 |
| code | `CODE QUEUE EMPTY AND TESTS PASSING` | 3 |
| growth | `CONTENT QUEUE PROCESSED` | 5 |
| meta | `WEEKLY ANALYSIS COMPLETE` | 2 |
| finance | `FINANCIAL SYNC COMPLETE` | 3 |
| discovery | `DISCOVERY CYCLE COMPLETE` | 3 |

---

## Instructions

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

## Priority Queue (Code Agent only)
[Sorted list of work items by priority tier]

## Constitutional Limits
- Max iterations: {MAX_ITERATIONS}
- Current iteration: {current}
- Emergency stop: Check `.ai-company/EMERGENCY_STOP` before each action

## Your Task
Execute your responsibilities until complete. When genuinely finished:
1. Update your state.md with results
2. Output your completion promise: <promise>{COMPLETION_PROMISE}</promise>

If NOT complete after this iteration:
1. Update state.md with progress
2. Update iteration.md with current count
3. DO NOT output completion promise
4. The loop will continue automatically

## CRITICAL
- Only output <promise>...</promise> when work is GENUINELY complete
- False promises violate Constitution Article IX
- Iteration files track progress across context resets
```

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

### Step 9: Report Results

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

---

## Emergency Stop

At any point:
- `/ai-stop` - Halt everything
- `touch .ai-company/EMERGENCY_STOP` - File-based halt
- `/ralph-wiggum:cancel-ralph` - Cancel current loop
