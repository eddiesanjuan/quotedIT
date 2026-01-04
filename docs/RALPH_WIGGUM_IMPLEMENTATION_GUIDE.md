# Ralph Wiggum Integration Guide for Quoted Workflows

**Purpose**: How to use the already-installed Ralph Wiggum plugin with `/quoted-run` for fully autonomous overnight execution.

**Key Insight**: Ralph Wiggum is ALREADY INSTALLED. We don't need to build custom infrastructure - just configure `/quoted-run` to work with it.

---

## TL;DR - The 3 Things You Need To Do

1. **Add completion promise** to `/quoted-run.md` final report
2. **Invoke via Ralph loop** instead of directly
3. **Set max iterations** to control costs

That's it. The plugin handles everything else.

---

## What's Already Installed

### Plugin Status: ACTIVE

```json
// ~/.claude/settings.json
{
  "enabledPlugins": {
    "ralph-wiggum@claude-plugins-official": true  // ✅ INSTALLED
  }
}
```

### Available Commands

| Command | Purpose |
|---------|---------|
| `/ralph-wiggum:ralph-loop` | Start a Ralph loop with any prompt |
| `/ralph-wiggum:cancel-ralph` | Cancel an active loop |
| `/ralph-wiggum:help` | Show help |

### What The Plugin Provides (You Get This For Free)

- **State file management**: `.claude/ralph-loop.local.md`
- **Stop hook integration**: Intercepts session exit automatically
- **Completion promise detection**: Looks for `<promise>TEXT</promise>`
- **Iteration counting**: Tracks loop iterations
- **Max iterations enforcement**: Stops at limit if set

---

## Implementation: 3 Steps

### Step 1: Add Completion Promise to `/quoted-run.md`

**File**: `.claude/commands/quoted-run.md`

**Location**: At the very end of the FINAL REPORT section (around line 915)

**Add this block**:

```markdown
## FINAL REPORT

═══════════════════════════════════════════════════════════
QUOTED RUN SESSION COMPLETE
═══════════════════════════════════════════════════════════

[... existing report content ...]

═══════════════════════════════════════════════════════════

<!--
  RALPH WIGGUM COMPLETION SIGNAL
  Only output this when ALL of the following are TRUE:
  - All targeted tickets have been processed (completed OR blocked with reason)
  - All completed work has been merged to main
  - Production health check passed
  - State files (DISCOVERY_BACKLOG.md) have been updated

  DO NOT output this promise if work remains incomplete.
  The Ralph loop will feed the same prompt back to you to continue.
-->
<promise>ALL READY TICKETS PROCESSED AND DEPLOYED</promise>
```

**Critical Rule**: The promise text must be a TRUE statement when output. The agent must genuinely believe all work is complete before outputting it.

### Step 2: Invoke `/quoted-run` Via Ralph Loop

Instead of running `/quoted-run` directly, invoke it through Ralph:

```bash
# Basic overnight run
/ralph-wiggum:ralph-loop Execute /quoted-run to process all READY tickets in the backlog --completion-promise 'ALL READY TICKETS PROCESSED AND DEPLOYED' --max-iterations 50

# Single ticket with loop
/ralph-wiggum:ralph-loop Execute /quoted-run DISC-071 --completion-promise 'ALL READY TICKETS PROCESSED AND DEPLOYED' --max-iterations 20

# Multiple specific tickets
/ralph-wiggum:ralph-loop Execute /quoted-run DISC-071 DISC-072 DISC-073 --completion-promise 'ALL READY TICKETS PROCESSED AND DEPLOYED' --max-iterations 30
```

### Step 3: Set Appropriate Max Iterations

| Scenario | Recommended Max | Rationale |
|----------|-----------------|-----------|
| Single small ticket | 5-10 | Should complete in 1-3 iterations |
| Single complex ticket | 10-20 | May need retries for preview verification |
| 2-3 tickets | 20-30 | Allow for sequential completion |
| Full backlog run | 50-100 | Overnight processing of multiple tickets |
| Unlimited | 0 (or omit) | Dangerous - only for monitored sessions |

**Cost Estimation**:
- Each iteration: ~50-100K tokens
- At current API pricing: ~$0.50-1.50 per iteration
- 50 iterations max: ~$25-75 maximum spend

---

## How The Loop Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. You invoke /ralph-wiggum:ralph-loop with quoted-run     │
│  2. Plugin creates state file: .claude/ralph-loop.local.md  │
│  3. Claude executes /quoted-run workflow                    │
│  4. At end of session:                                      │
│       ├── Stop hook intercepts exit                         │
│       ├── Reads last output for <promise>...</promise>      │
│       ├── If promise found → Clean up, allow exit           │
│       └── If NOT found → Block exit, feed SAME prompt back  │
│  5. Claude sees its own work (in files, git, state docs)    │
│  6. Claude continues from where it left off                 │
│  7. Repeat until completion or max_iterations               │
└─────────────────────────────────────────────────────────────┘
```

### State File Location

The Ralph plugin creates: `.claude/ralph-loop.local.md`

```yaml
---
active: true
iteration: 3
max_iterations: 50
completion_promise: "ALL READY TICKETS PROCESSED AND DEPLOYED"
started_at: "2026-01-03T22:00:00Z"
---

Execute /quoted-run to process all READY tickets in the backlog
```

### Monitoring Progress

```bash
# Check current iteration
grep '^iteration:' .claude/ralph-loop.local.md

# View full state
head -10 .claude/ralph-loop.local.md

# Watch live progress (in another terminal)
tail -f quoted/QUOTED_RUN_LIVE.md
```

---

## Completion Promise Rules

### When The Agent SHOULD Output The Promise

The agent should only output `<promise>ALL READY TICKETS PROCESSED AND DEPLOYED</promise>` when:

1. **All targeted tickets processed** - Either completed OR blocked with documented reason
2. **Work merged to production** - PR merged, production deploy successful
3. **Health check passed** - Production is healthy
4. **State files updated** - DISCOVERY_BACKLOG.md shows DEPLOYED status

### When The Agent MUST NOT Output The Promise

- Work is still in progress
- Preview verification failed (needs retry)
- Production health check failed
- Tickets remain in READY status
- There are unresolved blockers that can be fixed

### What Happens If Agent Doesn't Output Promise

1. Stop hook detects missing promise
2. Session exit is blocked
3. Same prompt is fed back
4. Agent sees: "🔄 Ralph iteration 4 | To stop: output <promise>ALL READY TICKETS PROCESSED AND DEPLOYED</promise>"
5. Agent reviews its work in files (QUOTED_RUN_LIVE.md, git history, state files)
6. Agent continues working from where it left off

---

## Integration With Existing Quoted Workflows

### `/quoted-run` Already Has

| Feature | Status | Notes |
|---------|--------|-------|
| Phase-based execution | ✅ Works | 8 phases, well-structured |
| Progress logging | ✅ Works | QUOTED_RUN_LIVE.md |
| Branch-first workflow | ✅ Works | Preview verification |
| State file updates | ✅ Works | Updates DISCOVERY_BACKLOG.md |
| Worker agent spawning | ✅ Works | Uses Task tool |

### What Ralph Adds

| Feature | Provided By | Notes |
|---------|-------------|-------|
| Loop until complete | Ralph plugin | Stop hook blocks premature exit |
| Iteration tracking | Ralph plugin | State file with counter |
| Max iterations | Ralph plugin | Cost/time control |
| Completion signal | Need to add | `<promise>` tag in final report |
| Self-review | Built-in | Agent sees its work in files |

### Why This Works Well

The `/quoted-run` workflow already:
- Writes progress to `QUOTED_RUN_LIVE.md` (agent can review)
- Commits work to git (agent can see history)
- Updates state files (agent knows what's done)
- Has clear phases (agent knows where it is)

Ralph just adds the loop mechanism - the agent naturally picks up where it left off because its work is persisted in files.

---

## Recommended Invocation Patterns

### Pattern 1: Overnight Full Backlog Run

```
/ralph-wiggum:ralph-loop Execute /quoted-run to process ALL READY tickets. Work through each ticket, create PRs, verify on preview, merge to production. Update state files when done. --completion-promise 'ALL READY TICKETS PROCESSED AND DEPLOYED' --max-iterations 100
```

### Pattern 2: Focused Single Ticket

```
/ralph-wiggum:ralph-loop Execute /quoted-run DISC-071 to implement and deploy this specific ticket. --completion-promise 'ALL READY TICKETS PROCESSED AND DEPLOYED' --max-iterations 15
```

### Pattern 3: Sprint Batch

```
/ralph-wiggum:ralph-loop Execute /quoted-run DISC-071 DISC-072 DISC-073 DISC-074 to implement this sprint's tickets. --completion-promise 'ALL READY TICKETS PROCESSED AND DEPLOYED' --max-iterations 50
```

### Pattern 4: With Explicit Context

```
/ralph-wiggum:ralph-loop You are executing /quoted-run for Quoted, a voice-to-quote SaaS. Process all READY tickets in DISCOVERY_BACKLOG.md. For each ticket: create feature branch, implement, test on Railway preview, merge to production, update state files. Review QUOTED_RUN_LIVE.md to see your previous progress. Continue until all READY tickets are DEPLOYED. --completion-promise 'ALL READY TICKETS PROCESSED AND DEPLOYED' --max-iterations 75
```

---

## Emergency Controls

### Cancel Active Loop

```
/ralph-wiggum:cancel-ralph
```

This removes the state file and allows the session to exit normally.

### Manual State File Removal

```bash
rm .claude/ralph-loop.local.md
```

### Check If Loop Is Active

```bash
cat .claude/ralph-loop.local.md 2>/dev/null || echo "No active loop"
```

---

## Troubleshooting

### Loop Exits Too Early

**Symptom**: Session ends before work is complete

**Causes**:
1. Agent output the completion promise prematurely
2. State file was corrupted or deleted
3. Max iterations was too low

**Solution**:
- Ensure completion promise is only output when work is truly complete
- Check the final report for the `<promise>` tag
- Increase max_iterations

### Loop Never Exits

**Symptom**: Keeps running past reasonable iterations

**Causes**:
1. Completion promise never output
2. Work genuinely incomplete (blockers)
3. Promise text doesn't match exactly

**Solution**:
- Use `/ralph-wiggum:cancel-ralph` to stop
- Check `QUOTED_RUN_LIVE.md` for blockers
- Verify promise text matches exactly

### Agent Doesn't See Previous Work

**Symptom**: Each iteration starts fresh, not continuing

**This shouldn't happen because**:
- `/quoted-run` writes to `QUOTED_RUN_LIVE.md`
- Git commits persist between iterations
- State files persist

**If it does happen**:
- Ensure `QUOTED_RUN_LIVE.md` is being written to
- Check git status for uncommitted work
- Add explicit "review your previous work" in the prompt

---

## Minimal Change Checklist

To enable Ralph Wiggum with `/quoted-run`:

- [ ] Add `<promise>ALL READY TICKETS PROCESSED AND DEPLOYED</promise>` to end of FINAL REPORT in `/quoted-run.md`
- [ ] Add comment explaining when to output the promise
- [ ] Add `.claude/ralph-loop.local.md` to `.gitignore` (if not already)
- [ ] Test with single ticket and low max_iterations first

That's it. No custom stop hooks, no custom state management, no parallel infrastructure.

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│  RALPH WIGGUM + QUOTED-RUN QUICK REFERENCE                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  START A RUN:                                              │
│  /ralph-wiggum:ralph-loop Execute /quoted-run              │
│    --completion-promise 'ALL READY TICKETS PROCESSED...'   │
│    --max-iterations 50                                     │
│                                                            │
│  MONITOR:                                                  │
│  tail -f quoted/QUOTED_RUN_LIVE.md                         │
│  grep '^iteration:' .claude/ralph-loop.local.md            │
│                                                            │
│  CANCEL:                                                   │
│  /ralph-wiggum:cancel-ralph                                │
│                                                            │
│  COMPLETION SIGNAL:                                        │
│  <promise>ALL READY TICKETS PROCESSED AND DEPLOYED</promise>│
│                                                            │
│  STATE FILE:                                               │
│  .claude/ralph-loop.local.md                               │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Appendix: The Only Code Change Needed

### File: `.claude/commands/quoted-run.md`

### Location: End of FINAL REPORT section (around line 915)

### Change:

```diff
  ## Recommendations
  [What should be prioritized next - as DISCOVERED, for founder approval]
  ═══════════════════════════════════════════════════════════
+
+ <!--
+   RALPH WIGGUM COMPLETION SIGNAL
+   Only output when ALL of these are TRUE:
+   - All targeted tickets processed (completed OR blocked with documented reason)
+   - All completed work merged to main
+   - Production health check passed
+   - State files updated with DEPLOYED status
+
+   If ANY work remains, DO NOT output this. Ralph will loop you back.
+ -->
+ <promise>ALL READY TICKETS PROCESSED AND DEPLOYED</promise>
```

---

*Document Version: 2.0*
*Updated: 2026-01-03*
*Key Change: Removed custom infrastructure - uses existing Ralph Wiggum plugin*
