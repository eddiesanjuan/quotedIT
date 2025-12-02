# Quoted Multi-Agent Architecture

**Purpose**: Enable autonomous AI company operations with minimal context bloat
**Created**: 2025-12-02

---

## The Problem

The original monolithic prompt approach had issues:
- 26K token prompt fills context quickly
- Single context tries to be CEO + Engineer + Marketer
- As work happens, context sprawls and loses coherence
- No accumulated learning between sessions

## The Solution: Multi-Agent + Shared Knowledge

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (CEO)                        │
│  - Reads state files                                        │
│  - Prioritizes work                                         │
│  - Spawns specialized agents via Task tool                  │
│  - Aggregates results                                       │
│  - Updates state                                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│  Backend  │ │ Frontend  │ │  Content  │ │   More    │
│  Engineer │ │ Engineer  │ │  Writer   │ │  Agents   │
│  (~2K)    │ │  (~2K)    │ │  (~2K)    │ │   ...     │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └───────────┘
      │             │             │
      ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│  Backend  │ │ Frontend  │ │ Marketing │
│  Learning │ │  Learning │ │  Learning │
│  Core     │ │  Core     │ │  Core     │
└───────────┘ └───────────┘ └───────────┘
```

## Key Components

### 1. Shared State Files (Coordination)

| File | Purpose | Who Updates |
|------|---------|-------------|
| `COMPANY_STATE.md` | Strategic overview | CEO |
| `DECISION_QUEUE.md` | Pending approvals | Anyone |
| `ACTION_LOG.md` | Audit trail | All agents |
| `ENGINEERING_STATE.md` | Tech status | Engineers |
| `PRODUCT_STATE.md` | Backlog | Product |

### 2. Agent Prompts (Role Definition)

Location: `quoted/agents/`

Each agent has a small (~2K token) focused prompt:
- `backend-engineer.md`
- `frontend-engineer.md`
- `content-writer.md`
- `ceo-orchestrator.md`

### 3. Knowledge Files (Learning Cores)

Location: `quoted/knowledge/`

Each domain accumulates knowledge:
- `backend-learning.md` - Codebase patterns, gotchas
- `frontend-learning.md` - UI patterns, standards
- `marketing-learning.md` - What messaging works

Agents read their learning file at start, add to it at end.

## How It Works

### Standard Flow

1. **Activate via Slash Command**: `/quoted-run`
2. **CEO Reads State**: Understands current situation
3. **CEO Identifies Work**: Approved decisions, bugs, backlog
4. **CEO Spawns Agents**: Via Task tool, in parallel when possible
5. **Agents Execute**: Each in fresh context with focused prompt
6. **Agents Return Results**: Structured output format
7. **CEO Aggregates**: Updates state files, queues decisions
8. **CEO Reports**: Summary of session

### Parallel Execution

Multiple agents can run simultaneously:
```
Single message with multiple Task tool calls:
├── Task 1: Backend Engineer fixing bug
├── Task 2: Content Writer creating post
└── Task 3: Frontend Engineer improving UI

All run in parallel, return together.
```

### Decision Flow

```
Agent encounters decision
        │
        ▼
   Type 1-2? ──YES──▶ Execute immediately
        │
       NO
        │
        ▼
   Add to DECISION_QUEUE.md
        │
        ▼
   Continue other work
        │
        ▼
   Eddie checks DECISION_QUEUE.md
        │
        ▼
   Marks [x] to approve
        │
        ▼
   Next session picks up approval
```

## Slash Commands

| Command | What It Does |
|---------|-------------|
| `/quoted-run` | Full autonomous cycle (CEO orchestrates) |
| `/quoted-backend` | Direct backend engineer session |
| `/quoted-run-product` | Focus on product improvements |
| `/quoted-run-growth` | Focus on marketing/growth |

## Why This Works Better

### Before (Monolithic)
- 26K prompt + state files + code = context fills fast
- CEO thinking mixed with implementation details
- No learning accumulation

### After (Multi-Agent)
- CEO: 4K prompt, delegates via Task tool
- Agents: 2K prompt each, fresh context per task
- Learning files grow and persist
- Parallel execution for independent work

## Adding New Agents

1. Create `quoted/agents/new-agent.md` with role definition
2. Create `quoted/knowledge/new-domain-learning.md` if needed
3. Add spawning pattern to CEO orchestrator
4. Agent reads learning file, updates it after work

## Configuration

### Task Tool Spawning

```python
Task tool parameters:
  subagent_type: "general-purpose"
  model: "sonnet"  # or "haiku" for simple tasks
  prompt: |
    [Agent prompt contents]

    ## Current Task
    [Specific task description]
```

### Learning File Updates

Agents should add learnings in format:
```markdown
### YYYY-MM-DD: Title
[What was learned and why it matters]
```

## Limitations

- Agents cannot communicate directly (only via state files)
- CEO must aggregate results manually
- Learning files must be explicitly updated
- No real-time coordination between parallel agents

## Future Improvements

- [ ] Automatic learning file updates from agent results
- [ ] Cross-agent knowledge sharing
- [ ] Scheduled autonomous runs (cron)
- [ ] Webhook integration for external triggers
