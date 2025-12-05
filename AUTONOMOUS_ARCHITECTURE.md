# Quoted Autonomous Architecture

## The Problem

Running multi-cycle autonomous operations in a single conversation causes **context compactification** - the conversation summarizes itself 5-6 times, losing nuance and degrading quality.

## The Solution

**Thin orchestrators** that spawn **sub-agents** for each cycle. Each sub-agent gets a fresh, full context window. State handoff happens via files, not conversation memory.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR LAYER                        │
│                   (Thin, stays minimal)                      │
│                                                              │
│   /quoted-run           /quoted-discover                     │
│        │                       │                             │
│        ▼                       ▼                             │
│   ┌─────────┐            ┌─────────┐                        │
│   │  Loop   │            │  Spawn  │                        │
│   │  until  │            │  once   │                        │
│   │  done   │            │         │                        │
│   └────┬────┘            └────┬────┘                        │
└────────┼─────────────────────┼──────────────────────────────┘
         │                     │
         ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    SUB-AGENT LAYER                           │
│               (Fresh context per cycle)                      │
│                                                              │
│   ┌──────────────┐       ┌──────────────┐                   │
│   │ Cycle Agent  │       │ Discovery    │                   │
│   │              │       │ Agent        │                   │
│   │ • Reads state│       │              │                   │
│   │ • Spawns execs       │ • Reads state│                   │
│   │ • Executes   │       │ • Spawns 3   │                   │
│   │ • Returns JSON       │   specialists│                   │
│   │ • Discarded  │       │ • Returns JSON                   │
│   └──────┬───────┘       └──────┬───────┘                   │
│          │                      │                            │
│          ▼                      ▼                            │
│   ┌──────────────────────────────────────┐                  │
│   │         SUB-SUB-AGENT LAYER          │                  │
│   │                                       │                  │
│   │  CGO  CPO  CFO  CMO    Product Growth Strategy          │
│   │   │    │    │    │         │      │      │              │
│   │   └────┴────┴────┘         └──────┴──────┘              │
│   │   (parallel executives)    (parallel discovery)          │
│   └──────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
         │                     │
         ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                         │
│                   (State files = memory)                     │
│                                                              │
│   ENGINEERING_STATE.md    DISCOVERY_BACKLOG.md               │
│   COMPANY_STATE.md        ACTION_LOG.md                      │
│   DECISION_QUEUE.md       BETA_SPRINT.md                     │
│                                                              │
│   • Orchestrator reads to check for work                     │
│   • Sub-agents read for context                              │
│   • Sub-agents write results                                 │
│   • State persists across cycles                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Principles

### 1. Orchestrators Stay Thin
The orchestrator's only job:
- Read state to check for work
- Spawn sub-agent via Task tool
- Log results
- Loop or stop

Orchestrators do NOT:
- Run complex analysis
- Execute tasks directly
- Accumulate context

### 2. Sub-Agents Get Fresh Context
Each cycle spawns as a new sub-agent with:
- Full context window (~200K tokens)
- No inherited cruft from previous cycles
- Clean slate for deep analysis

When the sub-agent completes:
- Only the structured JSON report returns
- All internal reasoning is discarded
- Context is "compactified" at the clean boundary

### 3. State Files Are Memory
Sub-agents can't share context directly. Instead:
- **Before cycle**: Read state files for current situation
- **During cycle**: Work with full context freedom
- **After cycle**: Write results to state files

This is like employees sharing a wiki instead of trying to remember everything.

### 4. Parallel Where Possible
Within each cycle, work parallelizes:
- Executive council: 4 agents in parallel (CGO, CPO, CFO, CMO)
- Discovery specialists: 3 agents in parallel
- Execution: Multiple task agents in parallel

### 5. Structured Handoffs
Sub-agents return structured JSON, not prose:
```json
{
  "tasks_completed": [...],
  "blockers": [...],
  "should_continue": true,
  "remaining_work": 5
}
```

This ensures the orchestrator gets exactly what it needs to decide next steps.

## Commands

| Command | Type | Purpose |
|---------|------|---------|
| `/quoted-run` | Multi-cycle orchestrator | Execute READY backlog items |
| `/quoted-discover` | Single-cycle orchestrator | Generate new backlog items |
| `/quoted-run-product` | Single-cycle orchestrator | Product/engineering focus |
| `/quoted-run-growth` | Single-cycle orchestrator | Growth/marketing focus |

## Benefits

1. **No context degradation**: Each cycle is fresh
2. **Unlimited cycles**: Can run 10, 20, 50 cycles without quality loss
3. **Clean handoffs**: JSON reports are unambiguous
4. **Parallelization**: Sub-agents work concurrently
5. **Debuggability**: State files show exactly what happened

## Tradeoffs

1. **More API calls**: Each sub-agent is a separate call
2. **Latency per cycle**: Spawning sub-agents adds overhead
3. **Prompt duplication**: Context must be re-read each cycle
4. **Token cost**: Fresh context means re-reading state files

These tradeoffs are worth it because **quality > speed** for autonomous operations that make real changes.
