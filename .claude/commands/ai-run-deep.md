# AI Civilization - Deep Agent Run (Ralph Wiggum Loop)

Execute an agent in a self-healing loop using Ralph Wiggum plugin. This runs locally with automatic retry until completion or max iterations.

---

## Arguments

Parse from $ARGUMENTS:
- `agent`: Which agent to run (support, ops, code, growth, meta, finance, full)
- `--max`: Optional max iterations override (defaults to Constitutional limit)

## Usage Examples

```
/ai-run-deep support         # Deep run support agent until inbox clear
/ai-run-deep ops             # Deep run ops until health green
/ai-run-deep code            # Deep run code until queue empty
/ai-run-deep code --max=5    # Deep run code with custom limit
/ai-run-deep full            # Full company operation (all agents)
/ai-run-deep overnight       # Overnight full company run
```

## Completion Promises (from Constitution Article IX)

| Agent | Completion Promise | Max Iterations |
|-------|-------------------|----------------|
| support | `INBOX PROCESSED AND ESCALATIONS HANDLED` | 5 |
| ops | `HEALTH GREEN AND INCIDENTS RESOLVED` | 10 |
| code | `CODE QUEUE EMPTY AND TESTS PASSING` | 3 |
| growth | `CONTENT QUEUE PROCESSED` | 5 |
| meta | `WEEKLY ANALYSIS COMPLETE` | 2 |
| finance | `FINANCIAL SYNC COMPLETE` | 3 |

## Instructions

### Step 1: Validate and Setup

1. Parse $ARGUMENTS to get agent name
2. Validate agent is one of: support, ops, code, growth, meta, finance, full, overnight
3. Check for emergency stop: `.ai-company/EMERGENCY_STOP`
4. If emergency stop exists, halt and report

### Step 2: Load Agent Context

Read the agent's specification and current state:
```
.ai-company/agents/{agent}/AGENT.md
.ai-company/agents/{agent}/state.md
.ai-company/agents/{agent}/iteration.md
```

### Step 3: Build Loop Prompt

For single agent, construct the prompt:

```markdown
You are executing the Quoted {Agent} Agent in deep mode.

## Your Specification
[Contents of AGENT.md]

## Current State
[Contents of state.md]

## Current Iteration
[Contents of iteration.md or "iteration: 1"]

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

### Step 4: Invoke Ralph Wiggum Loop

Use the Ralph Wiggum plugin skill to start the loop:

```
/ralph-wiggum:ralph-loop
```

With the constructed prompt above.

The loop will:
1. Execute the agent prompt
2. Check for completion promise in output
3. If found: Stop loop, report success
4. If not found: Continue next iteration
5. If max iterations reached: Stop loop, escalate

### Step 5: Full Company Mode

For `/ai-run-deep full` or `/ai-run-deep overnight`:

Run agents in dependency order:
1. **ops** first (health baseline)
2. **support** (clear inbox)
3. **finance** (sync metrics)
4. **code** (process code queue)
5. **growth** (process content)
6. **meta** (if Sunday, weekly analysis)

Between each agent:
- Check for emergency stop
- Log completion to `.ai-company/state/deep-run-{timestamp}.md`
- 30 second cooldown

### Step 6: Monitor and Report

Create a live status display:

```
+--------------------------------------------------------------+
|  AI CIVILIZATION - DEEP RUN                                    |
+--------------------------------------------------------------+

Agent: {agent name}
Mode: Ralph Wiggum Loop
Completion Promise: {promise}

Iteration: {current} / {max}
Status: {running/complete/stopped}

Progress:
  [1] Started: 10:30:00 - Processed 5 tickets
  [2] Started: 10:32:15 - Processed 3 more tickets
  [3] Started: 10:34:30 - COMPLETE - Promise output

Result: SUCCESS / ESCALATE / EMERGENCY_STOP

State File: .ai-company/agents/{agent}/state.md
+--------------------------------------------------------------+
```

## Emergency Stop

At any point during deep run:
- User can run `/ai-stop` to halt
- Or create file: `touch .ai-company/EMERGENCY_STOP`
- Or use Ralph's built-in: `/ralph-wiggum:cancel-ralph`

## Overnight Mode

For `/ai-run-deep overnight`:

1. Set MAX_ITERATIONS higher (Constitutional max * 2)
2. Enable all agents
3. Log everything to `.ai-company/logs/overnight-{date}.md`
4. Generate morning briefing when complete
5. Send summary to Eddie's email (if configured)

Overnight is designed to be started before bed:
```bash
# Start overnight run
/ai-run-deep overnight

# It will run until:
# 1. All agents report complete
# 2. Emergency stop triggered
# 3. Any agent exceeds doubled max iterations
```

## Output Log Format

Create/append to `.ai-company/state/deep-run-log.md`:

```markdown
# Deep Run Log

## {timestamp} - {agent}
- **Mode**: deep / full / overnight
- **Iterations**: {count}
- **Result**: complete / escalate / emergency_stop
- **Promise**: {if output}
- **Duration**: {minutes}
- **Summary**: {one line}
```

## Integration with /quoted-run

For maximum overnight power, combine with discovery:

```
/ai-run-deep overnight && /quoted-discover --auto-approve
```

This runs the entire company overnight AND generates new work for tomorrow.
