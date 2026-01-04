# Create Orchestrator

Create a **thin, context-resilient orchestrator** that:
- Uses Task tool to spawn real sub-agents (NEVER does work directly)
- Follows CI/CD pattern (branch → PR → test → merge → verify production)
- Survives context compaction via self-sufficient state file
- Always includes production verification and re-audit

## Usage

```
/create-orchestrator [description of what to orchestrate]
```

## Examples

```
/create-orchestrator to fix all issues from the Codex audit
/create-orchestrator to implement GROWTH-001 premium setup tier
/create-orchestrator to refactor the billing system
```

---

## ⚠️ THIN ORCHESTRATOR PATTERN (MANDATORY)

**Orchestrators MUST NOT perform substantive work directly. ALL work is done by spawned Task agents.**

### Orchestrator Responsibilities (ONLY):
- ✅ Read and update state file
- ✅ Spawn Task agents for each phase using the Task tool
- ✅ Wait for agent completion using TaskOutput
- ✅ Update state file with results
- ✅ Decide phase transitions
- ✅ Synthesize findings across agents

### Orchestrator MUST NOT:
- ❌ Read code files directly (spawn agent)
- ❌ Make browser interactions directly (spawn agent)
- ❌ Write code directly (spawn agent)
- ❌ Run tests directly (spawn agent)
- ❌ Generate reports directly (spawn agent)
- ❌ Analyze logs directly (spawn agent)

### Correct Execution Pattern:
```
1. Read state file → determine current phase
2. Spawn Task agent(s) with detailed prompt(s)
3. If parallel: spawn multiple agents, use run_in_background: true
4. Wait for TaskOutput (blocking or polling)
5. Update state file with findings/results
6. Repeat for next agent/phase
```

### Anti-Pattern (WRONG):
```
Phase 3: Implementation
1. Read the code files myself
2. Make the changes myself
3. Run the tests myself
4. Record the results
```
**This defeats the purpose of orchestration!**

---

## ⚠️ Browser Automation for Subagents (CRITICAL)

**Subagents have different tool availability than the main context.** Include this in ALL orchestrators that need browser testing.

### Working Pattern for Subagents:
```
1. FIRST: Call mcp__claude-in-chrome__tabs_context_mcp to get valid tab IDs
2. REUSE: Navigate existing tabs (don't create new ones if possible)
3. SCREENSHOTS: Use mcp__claude-in-chrome__computer with action: "screenshot"
4. NAVIGATION: Use mcp__claude-in-chrome__navigate with valid tabId
5. FALLBACK: If browser fails, fall back to code inspection
```

### ❌ DO NOT USE in Subagents:
- `mcp__claude-in-chrome__browser_snapshot` - NOT available to subagents
- `mcp__plugin_playwright_playwright__*` - Conflicts with Claude-in-Chrome

### ✅ Subagent Browser Tools (Verified Working):
```
mcp__claude-in-chrome__tabs_context_mcp    # Get tab context (ALWAYS FIRST)
mcp__claude-in-chrome__navigate            # Go to URL (requires tabId)
mcp__claude-in-chrome__computer            # Screenshots, clicks, typing
mcp__claude-in-chrome__resize_window       # Viewport testing
mcp__claude-in-chrome__read_console_messages  # JS errors
mcp__claude-in-chrome__read_network_requests  # API calls
mcp__claude-in-chrome__find                # Find elements by description
mcp__claude-in-chrome__form_input          # Fill form fields
mcp__claude-in-chrome__read_page           # Read page accessibility tree
mcp__claude-in-chrome__get_page_text       # Extract page text
```

### Screenshot Pattern for Subagent Prompts:
```markdown
BROWSER SETUP:
1. Call mcp__claude-in-chrome__tabs_context_mcp to get available tabs
2. Use an existing tab or note if you need to create one
3. For screenshots, use: mcp__claude-in-chrome__computer with action: "screenshot"
4. DO NOT use browser_snapshot (not available to subagents)
5. If browser tools fail, fall back to code inspection using Read/Grep
```

---

## What It Creates

1. **State File** (`.claude/[name]-state.md`)
   - Complete context for any agent to resume
   - Phase checklist with agent tasks
   - "Next Step" section for immediate resume
   - Accumulated findings section

2. **Command File** (`.claude/commands/orchestrate-[name].md`)
   - Thin coordinator (~150-200 lines)
   - MANDATORY thin orchestrator section at top
   - Task tool prompts for each phase
   - Browser patterns section (if browser testing needed)
   - Rollback and resume instructions

---

## Process

When invoked, I will:

1. **Understand the goal** - What needs to be done?
2. **Identify source material** - Audit report, discovery backlog, spec?
3. **Break into phases** - Group related work, max 4-6 agents per phase
4. **Add mandatory phases**:
   - Pre-flight (tools, branch)
   - Implementation phases
   - Backend testing
   - PR creation
   - Browser QA (if UI involved)
   - Merge decision
   - Production verification
   - Re-audit (if applicable)
   - Completion

5. **Create files** - State file + command file
6. **Provide execution instructions**

---

## Orchestrator Template Structure

Every orchestrator command file MUST include:

```markdown
# Orchestrate [Name]

[Brief description]

## Quick Start
[Usage commands]

---

## ⚠️ THIN ORCHESTRATOR PATTERN (MANDATORY)

**This orchestrator MUST NOT perform substantive work directly. ALL work is done by spawned Task agents.**

### Orchestrator Responsibilities (ONLY):
- ✅ Read and update state file
- ✅ Spawn Task agents for each phase
- ✅ Wait for agent completion
- ✅ Update state file with results
- ✅ Decide phase transitions

### Orchestrator MUST NOT:
- ❌ [List relevant anti-patterns]

---

## ⚠️ Browser Automation for Subagents (if applicable)
[Include browser patterns section]

---

## Phase Structure
[Table of phases]

---

## Phase N: [Name]

### Agent NA: [Task Name]
```markdown
TASK: [Clear objective]

BROWSER SETUP (if needed):
1. Call mcp__claude-in-chrome__tabs_context_mcp first
2. Use computer tool for screenshots (not browser_snapshot)
3. Fall back to code inspection if browser fails

STEPS:
[Numbered steps]

OUTPUT:
[Expected deliverable format]
```

---

## State File Location
`.claude/[name]-state.md`

## Resume Procedures
[How to resume after context loss]

## Rollback Procedures
[How to recover from failures]
```

---

## Key Principles

### Thin Coordinator Pattern
The orchestrator itself is ~150-200 lines. Each phase spawns a Task agent with a focused prompt. **Work is done by agents, not in main context.**

### Self-Sufficient State File
Any Claude instance should be able to read ONLY the state file and know exactly what to do next. Include:
- Current phase
- Completed agents with outcomes
- Accumulated findings
- Next step (explicit)
- Blockers if any

### CI/CD Is Non-Negotiable
- Create feature branch (never commit to main directly)
- Test before merge
- Verify production after merge
- Re-audit for new holes

### Task Tool for Everything
```
Phase work       → Task tool spawn
QA testing       → Task tool spawn
Fix issues       → Task tool spawn
Generate report  → Task tool spawn
```

**Never execute phase work in the main orchestrator context.**

### Parallel Execution
When agents are independent, spawn them in parallel:
```
Task(agent1, run_in_background: true)
Task(agent2, run_in_background: true)
Task(agent3, run_in_background: true)
# Then collect with TaskOutput
```

### Graceful Degradation
Include fallback instructions in every browser-related agent:
- If browser fails → code inspection
- If code unclear → ask orchestrator to clarify
- If completely blocked → report blocker in output

---

## Invocation

$ARGUMENTS
