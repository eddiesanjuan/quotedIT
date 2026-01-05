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
| code | `CODE QUEUE DEPLOYED AND PRODUCTION VERIFIED` | 10 |
| code (--pr-only) | `CODE QUEUE EMPTY AND PRS CREATED` | 3 |
| growth | `CONTENT QUEUE PROCESSED` | 5 |
| meta | `WEEKLY ANALYSIS COMPLETE` | 2 |
| finance | `FINANCIAL SYNC COMPLETE` | 3 |
| discovery | `DISCOVERY CYCLE COMPLETE` | 3 |

**Note**: Code agent default is full autonomy (10 iterations) to allow for preview testing, merging, and production verification. Use `--pr-only` for faster runs that just create PRs.

---

## Instructions

### Step 0: Handle Existing Open PRs (Priority)

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

### Step 10: Merge to Production

Only after preview tests pass:

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
│                    FULL AUTONOMY ORCHESTRATION FLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PHASE 1: IMPLEMENTATION                                                     │
│  ├── Read READY queue from DISCOVERY_BACKLOG.md                             │
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
│  └── All PRs must pass preview tests before Phase 3                         │
│                                                                              │
│  PHASE 3: MERGE                                                              │
│  ├── For each PR that passed preview tests:                                 │
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
│  └── Record production test results                                         │
│                                                                              │
│  PHASE 5: FINALIZATION                                                       │
│  ├── Batch update DISCOVERY_BACKLOG.md:                                     │
│  │   ├── Change all completed tickets: READY → DEPLOYED                     │
│  │   ├── Update summary counts                                              │
│  │   └── Single commit                                                      │
│  ├── Move DEPLOYED tickets to DISCOVERY_ARCHIVE.md                          │
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

---

## Emergency Stop

At any point:
- `/ai-stop` - Halt everything
- `touch .ai-company/EMERGENCY_STOP` - File-based halt
- `/ralph-wiggum:cancel-ralph` - Cancel current loop
