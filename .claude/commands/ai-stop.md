# AI Civilization - Emergency Stop

Immediately halt all AI Civilization operations (local and cloud).

---

## Arguments

Parse from $ARGUMENTS:
- `--reason`: Optional reason for the stop
- `--cloud`: Also cancel any running GitHub Action workflows
- `--local`: Only stop local Ralph loops (default)
- `--all`: Stop everything (local + cloud)

## Usage Examples

```
/ai-stop                           # Stop local loops
/ai-stop --reason="going to bed"   # Stop with reason logged
/ai-stop --cloud                   # Stop cloud workflows only
/ai-stop --all                     # Stop everything everywhere
/ai-stop --all --reason="bug found" # Full stop with reason
```

## Instructions

### Step 1: Create Emergency Stop File

```bash
# Create the emergency stop file
echo "EMERGENCY_STOP" > .ai-company/EMERGENCY_STOP
echo "---" >> .ai-company/EMERGENCY_STOP
echo "timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> .ai-company/EMERGENCY_STOP
echo "reason: {reason or 'Manual stop'}" >> .ai-company/EMERGENCY_STOP
echo "triggered_by: Eddie via /ai-stop" >> .ai-company/EMERGENCY_STOP
```

This file is checked by:
- All GitHub Action workflows before self-dispatch
- All local Ralph loops before each iteration
- The main loop coordinator before dispatching agents

### Step 2: Cancel Local Ralph Loop (if running)

Invoke the Ralph Wiggum cancel skill:

```
/ralph-wiggum:cancel-ralph
```

This immediately stops any active Ralph loop in the current session.

### Step 3: Cancel Cloud Workflows (if --cloud or --all)

Cancel any running AI Civilization workflows:

```bash
# Get all running workflows
RUNNING=$(gh run list --status in_progress --json databaseId,workflowName -q '.[] | select(.workflowName | startswith("AI Civilization")) | .databaseId')

# Cancel each one
for RUN_ID in $RUNNING; do
  echo "Cancelling run $RUN_ID..."
  gh run cancel $RUN_ID
done
```

### Step 4: Update State Files

Update the global state to reflect the stop:

```bash
# Update current state
cat >> .ai-company/state/current.md << EOF

---
## EMERGENCY STOP ACTIVATED
- **Time**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- **Reason**: {reason}
- **Scope**: {local/cloud/all}
- **Status**: All loops halted

To resume operations:
1. Review state files in .ai-company/agents/*/state.md
2. Delete .ai-company/EMERGENCY_STOP
3. Run /ai-status to verify
4. Run /ai-run or /ai-run-deep to restart
EOF
```

### Step 5: Log the Stop

Append to deep-run-log:

```bash
cat >> .ai-company/state/deep-run-log.md << EOF

## $(date -u +%Y-%m-%dT%H:%M:%SZ) - EMERGENCY STOP
- **Scope**: {local/cloud/all}
- **Reason**: {reason or 'Manual stop'}
- **Cancelled Runs**: {count}
EOF
```

### Step 6: Display Confirmation

```
+--------------------------------------------------------------+
|  AI CIVILIZATION - EMERGENCY STOP                              |
+--------------------------------------------------------------+

  Status: ALL OPERATIONS HALTED

  Scope: {local/cloud/all}
  Reason: {reason}
  Time: {timestamp}

  Actions Taken:
  [x] Created .ai-company/EMERGENCY_STOP file
  [x] Cancelled local Ralph loop
  [x] Cancelled {N} cloud workflows (if --cloud/--all)
  [x] Updated state files
  [x] Logged to deep-run-log.md

  TO RESUME:
  1. rm .ai-company/EMERGENCY_STOP
  2. /ai-status (verify state)
  3. /ai-run {agent} or /ai-run-deep {agent}

+--------------------------------------------------------------+
```

## Resuming After Stop

To resume normal operations:

1. **Review what happened**:
   ```
   /ai-status
   ```

2. **Check agent states**:
   - `.ai-company/agents/*/state.md` - Each agent's last state
   - `.ai-company/agents/*/iteration.md` - Where they were in the loop

3. **Remove the stop file**:
   ```bash
   rm .ai-company/EMERGENCY_STOP
   ```

4. **Verify clean state**:
   ```
   /ai-status
   ```

5. **Resume operations**:
   ```
   /ai-run-deep {agent}  # Continue where left off
   # or
   /ai-run {agent}       # Single cloud run
   ```

## Safety Notes

- Emergency stop is **persistent** - survives context resets
- All agents check for this file **before** taking any action
- Cloud workflows check **before** self-dispatching
- The file must be manually removed to resume
- Reason is logged for audit trail

## Quick Reference

| Command | Effect |
|---------|--------|
| `/ai-stop` | Stop local loops |
| `/ai-stop --all` | Stop everything |
| `/ai-stop --cloud` | Stop only cloud |
| `rm .ai-company/EMERGENCY_STOP` | Allow resume |
| `/ai-status` | Check current state |
