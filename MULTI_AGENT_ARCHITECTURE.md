# Quoted Multi-Agent Architecture

**Purpose**: Enable autonomous AI company operations with minimal context bloat
**Created**: 2025-12-02
**Updated**: 2025-12-02

---

## The Problem

The original monolithic prompt approach had issues:
- 26K token prompt fills context quickly
- Single context tries to be CEO + Engineer + Marketer
- As work happens, context sprawls and loses coherence
- No accumulated learning between sessions

## The Solution: Multi-Agent + Shared Knowledge

### Complete Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DISCOVERY LAYER                                  │
│                      (/quoted-discover)                                  │
│                                                                          │
│  Purpose: Generate new work when backlog is empty                        │
│                                                                          │
│    ┌────────────┐  ┌────────────┐  ┌────────────┐                       │
│    │  Product   │  │   Growth   │  │  Strategy  │                       │
│    │  Discovery │  │  Discovery │  │  Discovery │                       │
│    └──────┬─────┘  └─────┬──────┘  └─────┬──────┘                       │
│           │              │               │                               │
│           └──────────────┼───────────────┘                               │
│                          ▼                                               │
│               ┌──────────────────┐                                      │
│               │ ENGINEERING_STATE │ ← Tasks with DISCOVERED status       │
│               │    (Backlog)      │                                      │
│               └─────────┬─────────┘                                      │
│                         │                                                │
│                   Founder Review                                         │
│                   (DISCOVERED → READY)                                   │
│                         │                                                │
└─────────────────────────┼────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXECUTION LAYER                                  │
│                         (/quoted-run)                                    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    PHASE 0: EXECUTIVE COUNCIL                       │ │
│  │                     (Parallel Prioritization)                       │ │
│  │                                                                     │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │ │
│  │  │   CGO   │ │   CPO   │ │   CFO   │ │   CMO   │                   │ │
│  │  │ Growth  │ │ Product │ │ Finance │ │Marketing│                   │ │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘                   │ │
│  │       │           │           │           │                         │ │
│  │       └───────────┴─────┬─────┴───────────┘                         │ │
│  │                         ▼                                           │ │
│  │              ┌──────────────────┐                                   │ │
│  │              │ Prioritized Work │                                   │ │
│  │              └────────┬─────────┘                                   │ │
│  └───────────────────────┼─────────────────────────────────────────────┘ │
│                          ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    PHASE 1: CEO SYNTHESIS                           │ │
│  │                                                                     │ │
│  │  - Collects executive recommendations                              │ │
│  │  - Selects tasks based on consensus/priority                       │ │
│  │  - Spawns execution agents                                         │ │
│  └───────────────────────┬─────────────────────────────────────────────┘ │
│                          ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    PHASE 2: EXECUTION                               │ │
│  │                    (Parallel Implementation)                        │ │
│  │                                                                     │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐                         │ │
│  │  │  Backend  │ │ Frontend  │ │  Content  │                         │ │
│  │  │  Engineer │ │ Engineer  │ │  Writer   │                         │ │
│  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘                         │ │
│  │        │             │             │                                │ │
│  │        └─────────────┼─────────────┘                                │ │
│  │                      ▼                                              │ │
│  │              Completed Tasks + Commits                              │ │
│  └───────────────────────┬─────────────────────────────────────────────┘ │
│                          ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    PHASE 3: STATE UPDATE + LOOP                     │ │
│  │                                                                     │ │
│  │  - Update ENGINEERING_STATE.md                                     │ │
│  │  - Update ACTION_LOG.md                                            │ │
│  │  - Git commit and push                                             │ │
│  │  - Loop back to Phase 0 if backlog not empty                       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

### Workflow Summary

**Phase 1: Discovery** (`/quoted-discover`)
- Spawns Product, Growth, and Strategy discovery agents in parallel
- Each agent identifies opportunities and proposes tasks
- Tasks written to ENGINEERING_STATE.md with `DISCOVERED` status
- Founder reviews and approves (changes to `READY`)

**Phase 2: Execution** (`/quoted-run`)
- Phase 0: Executive Council (CGO, CPO, CFO, CMO) evaluates and prioritizes READY tasks
- Phase 1: CEO synthesizes recommendations, selects work
- Phase 2: Execution agents (Backend, Frontend, Content) implement in parallel
- Phase 3: Update state, commit, push, loop until backlog empty

---

## Agent Catalog

### Executive Council (Advisory - Parallel Prioritization)

| Agent | File | Purpose | Output |
|-------|------|---------|--------|
| **CGO** | `agents/cgo.md` | Growth implications, acquisition, activation, retention | `CGO_AUDIT_RESULT` |
| **CPO** | `agents/cpo.md` | Product-message fit, claim validation, UX reality check | `CPO_AUDIT_RESULT` |
| **CFO** | `agents/cfo.md` | Unit economics, pricing strategy, financial sustainability | `CFO_AUDIT_RESULT` |
| **CMO** | `agents/cmo.md` | Brand positioning, messaging strength, competitive risk | `CMO_AUDIT_RESULT` |

**When Used**: Phase 0 of `/quoted-run` - evaluates tasks before execution

### Execution Team (Implementation - Parallel Execution)

| Agent | File | Purpose | Output |
|-------|------|---------|--------|
| **Backend Engineer** | `agents/backend-engineer.md` | FastAPI, Python, database, AI integrations | `BACKEND_ENGINEER_RESULT` |
| **Frontend Engineer** | `agents/frontend-engineer.md` | HTML/CSS/JS, responsive design, accessibility | `FRONTEND_ENGINEER_RESULT` |
| **Content Writer** | `agents/content-writer.md` | Marketing copy, emails, blog posts, social | `CONTENT_WRITER_RESULT` |

**When Used**: Phase 2 of `/quoted-run` - implements approved work

### Orchestrator

| Agent | File | Purpose | Output |
|-------|------|---------|--------|
| **CEO** | `agents/ceo-orchestrator.md` | Reads state, spawns agents, aggregates results, updates state | `CEO_SESSION_SUMMARY` |

**When Used**: Coordinates all phases of `/quoted-run`

### Discovery Team (Work Generation - Parallel Discovery)

| Agent | File | Purpose | Output |
|-------|------|---------|--------|
| **Product Discovery** | `agents/product-discovery.md` | Finds product improvements, friction points, feature gaps | `PRODUCT_DISCOVERIES` |
| **Growth Discovery** | `agents/growth-discovery.md` | Finds funnel opportunities, activation improvements, retention levers | `GROWTH_DISCOVERIES` |
| **Strategy Discovery** | `agents/strategy-discovery.md` | Finds strategic opportunities, competitive insights, market positioning | `STRATEGY_DISCOVERIES` |

**When Used**: `/quoted-discover` - generates new work when backlog is empty

---

## Knowledge Files (Learning Cores)

Location: `quoted/knowledge/`

Each domain accumulates learnings that persist across sessions:

| File | Domain | Updated By |
|------|--------|------------|
| `backend-learning.md` | Codebase patterns, API gotchas | Backend Engineer |
| `frontend-learning.md` | UI patterns, responsive tricks | Frontend Engineer |
| `marketing-learning.md` | Messaging that resonates, channel insights | Content Writer, CMO |
| `cgo-learning.md` | Growth strategies that work | CGO |
| `cpo-learning.md` | Product decisions, feature learnings | CPO |
| `cfo-learning.md` | Pricing insights, unit economics | CFO |
| `cmo-learning.md` | Positioning learnings, competitive intel | CMO |

**Pattern**: Agents read their learning file at start, add to it when they learn something new.

---

## Shared State Files

| File | Purpose | Who Updates |
|------|---------|-------------|
| `COMPANY_STATE.md` | Strategic overview, current stage | CEO |
| `DECISION_QUEUE.md` | Type 3-4 decisions needing founder input | Any agent |
| `ACTION_LOG.md` | Audit trail of all agent actions | All agents |
| `ENGINEERING_STATE.md` | Tech status, task backlog, deployments | Engineers, CEO |
| `BETA_SPRINT.md` | Current sprint goals and metrics | CEO |

---

## Slash Commands

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `/quoted-discover` | Discovery cycle - generates tasks | When backlog is empty or weekly refresh |
| `/quoted-run` | Execution cycle - builds from backlog | When READY tasks exist |
| `/quoted-backend` | Direct backend engineer session | Quick backend-only work |
| `/quoted-run-product` | Focus on product improvements | Product-focused sprint |
| `/quoted-run-growth` | Focus on marketing/growth | Growth-focused sprint |

### Recommended Workflow

```
1. Run /quoted-discover
   └── Generates DISCOVERED tasks in ENGINEERING_STATE.md

2. Founder Reviews
   └── Changes status: DISCOVERED → READY (or deletes/modifies)

3. Run /quoted-run
   └── Executive Council prioritizes → CEO selects → Agents execute
   └── Loops until backlog empty

4. Repeat from step 1
```

---

## Decision Flow

| Type | Description | Action | Example |
|------|-------------|--------|---------|
| **Type 1** | Safe, reversible | Execute immediately | Bug fix, docs |
| **Type 2** | Standard practice | Execute, report after | Feature work in sprint |
| **Type 3** | Significant impact | Add to DECISION_QUEUE, await approval | Architecture change |
| **Type 4** | Strategic/irreversible | Founder decision only | Pricing, external service signup |

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

---

## Parallel Execution Pattern

Multiple agents can run simultaneously in a single message:

```
Single message with multiple Task tool calls:
├── Task 1: Backend Engineer fixing bug
├── Task 2: Frontend Engineer improving UI
└── Task 3: Content Writer creating post

All run in parallel, return together.
```

**When to parallelize**:
- Tasks are independent (no shared state)
- No dependencies between results
- Similar priority level

---

## Task Tool Spawning Pattern

```python
Task tool parameters:
  subagent_type: "general-purpose"
  model: "sonnet"  # or "haiku" for simple tasks
  prompt: |
    [Agent prompt contents from agents/*.md]

    ## Current Task
    [Specific task description]
```

---

## Adding New Agents

1. Create `quoted/agents/new-agent.md` with:
   - Role description
   - Files to read for context
   - Audit/execution framework
   - Output format
2. Create `quoted/knowledge/new-domain-learning.md` if needed
3. Add spawning pattern to relevant command
4. Update this architecture doc

---

## Limitations

- Agents cannot communicate directly (only via state files)
- CEO must aggregate results manually
- Learning files must be explicitly updated
- No real-time coordination between parallel agents

---

## Metrics (Action Log)

Track agent performance in ACTION_LOG.md:
- Tasks completed per cycle
- Commits per session
- Decision type distribution
- Executive consensus rate
